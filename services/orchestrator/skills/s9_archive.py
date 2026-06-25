from skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Optional, Dict
import json
import uuid


class ArchiveInput(SkillInput):
    final_proposal: Dict = Field(description="最终方案")
    review_comments: str = Field(default="", description="审核意见")
    bid_result: str = Field(default="", description="中标结果")
    user_id: str = Field(default="default_user", description="用户ID")
    session_id: str = Field(default="", description="会话ID")


class ArchiveOutput(SkillOutput):
    updated_libraries: list = Field(default_factory=list)
    review_report: str = ""


class S9Archive(BaseSkill):
    name = "s9_archive"
    description = "复盘归档：更新品牌库、竞品库、复盘库 + 记忆层 + 恐惧校准 + 多轮博弈分析"

    def execute(self, input_data: ArchiveInput) -> ArchiveOutput:
        updated = []
        session_id = input_data.session_id or str(uuid.uuid4())[:8]

        # 1. 更新品牌信息
        if self._update_brand_info(input_data.final_proposal):
            updated.append("品牌库")

        # 2. 更新竞品库
        if self._update_competitor_library(input_data.final_proposal):
            updated.append("竞品库")

        # 3. 更新复盘库（含恐惧校准）
        proposal_id = self._update_review_library(
            input_data.final_proposal, input_data.review_comments, input_data.bid_result
        )
        if proposal_id:
            updated.append("复盘库")

        # 4. 恐惧校准：复盘客户真实决策恐惧是否与预期一致，更新恐惧映射库
        self._update_fear_mapping(input_data.final_proposal, input_data.bid_result)

        # 5. 写入记忆层
        self._save_to_memory(
            input_data.user_id, session_id, input_data.final_proposal,
            input_data.bid_result,
        )

        # 6. 生成复盘报告
        review_report = self._generate_review_report(
            input_data.final_proposal, input_data.review_comments,
            input_data.bid_result, updated,
        )

        return ArchiveOutput(updated_libraries=updated, review_report=review_report)

    # ── 品牌库更新 ─────────────────────────────────────────────

    def _update_brand_info(self, proposal: dict) -> bool:
        try:
            from app.db.database import get_db
            db = get_db()
            client_name = proposal.get("client_name", "")
            industry = proposal.get("industry", "")
            db.execute(
                "INSERT INTO brand_info (brand_name, industry, last_proposal, updated_at) "
                "VALUES (?, ?, ?, NOW()) "
                "ON CONFLICT (brand_name) DO UPDATE SET "
                "industry = excluded.industry, last_proposal = excluded.last_proposal, updated_at = NOW()",
                (client_name, industry, json.dumps(proposal, ensure_ascii=False)),
            )
            db.commit()
            return True
        except Exception as e:
            print(f"[S9] 品牌库更新失败: {e}")
            return False

    # ── 竞品库更新 ─────────────────────────────────────────────

    def _update_competitor_library(self, proposal: dict) -> bool:
        """更新竞品库：从方案中提取竞品信息并持久化"""
        try:
            from app.db.database import get_db
            db = get_db()

            # 从方案中提取竞品信息
            op_strategy = proposal.get("operation_strategy", {}) or {}
            competitor_benchmark = op_strategy.get("competitor_benchmark", "")
            competitors = op_strategy.get("competitors", []) or []

            if not competitor_benchmark and not competitors:
                return False

            # 写入竞品记录
            for comp in (competitors if isinstance(competitors, list) else []):
                comp_name = comp if isinstance(comp, str) else comp.get("name", str(comp))
                db.execute(
                    "INSERT INTO competitor_library (competitor_name, industry, benchmark_data, updated_at) "
                    "VALUES (?, ?, ?, NOW()) "
                    "ON CONFLICT (competitor_name) DO UPDATE SET "
                    "benchmark_data = excluded.benchmark_data, updated_at = NOW()",
                    (
                        comp_name,
                        proposal.get("industry", ""),
                        json.dumps({"benchmark": competitor_benchmark, "raw": comp}, ensure_ascii=False),
                    ),
                )

            db.commit()
            return True
        except Exception as e:
            print(f"[S9] 竞品库更新失败: {e}")
            return False

    # ── 复盘库更新 ─────────────────────────────────────────────

    def _update_review_library(
        self, proposal: dict, review_comments: str, bid_result: str,
    ) -> Optional[str]:
        try:
            from app.db.database import get_db
            db = get_db()
            review_id = str(uuid.uuid4())[:12]
            db.execute(
                "INSERT INTO review_records (review_id, client_name, industry, proposal_summary, review_comments, bid_result, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, NOW())",
                (
                    review_id,
                    proposal.get("client_name", ""),
                    proposal.get("industry", ""),
                    json.dumps(proposal, ensure_ascii=False),
                    review_comments,
                    bid_result,
                ),
            )
            db.commit()
            return review_id
        except Exception as e:
            print(f"[S9] 复盘库更新失败: {e}")
            return None

    # ── 记忆层写入 ─────────────────────────────────────────────

    def _save_to_memory(
        self, user_id: str, session_id: str, proposal: dict, bid_result: str,
    ):
        try:
            from app.db.memory import MemoryStore
            memory = MemoryStore()
            client_name = proposal.get("client_name", "")
            industry = proposal.get("industry", "")

            # 保存会话
            memory.save_session(
                session_id, user_id, client_name, industry,
                "复盘归档",
                json.dumps(proposal, ensure_ascii=False)[:500],
            )

            # 记录中标结果
            if bid_result:
                memory.record_bid_result(user_id, bid_result)

            # 更新交互次数
            memory.increment_interaction(user_id)
        except Exception as e:
            print(f"[S9] 记忆层写入失败: {e}")

    # ── 恐惧校准 ────────────────────────────────────────────────

    def _update_fear_mapping(self, proposal: dict, bid_result: str):
        """复盘客户真实决策恐惧是否与预期一致，更新恐惧映射库（认知失调校准）"""
        try:
            from app.db.database import get_db
            db = get_db()
            client_name = proposal.get("client_name", "")
            industry = proposal.get("industry", "")

            # 提取方案中的恐惧映射信息
            op_strategy = proposal.get("operation_strategy", {}) or {}
            fears = op_strategy.get("fears", {}) or {}

            if client_name and fears:
                db.execute(
                    "INSERT INTO fear_mapping (client_name, industry, fear_analysis, bid_result, created_at) "
                    "VALUES (?, ?, ?, ?, NOW())",
                    (
                        client_name,
                        industry,
                        json.dumps(fears, ensure_ascii=False),
                        bid_result or "",
                    ),
                )
                db.commit()
        except Exception as e:
            print(f"[S9] 恐惧校准写入失败: {e}")

    # ── 复盘报告生成 ───────────────────────────────────────────

    def _generate_review_report(
        self, proposal: dict, review_comments: str, bid_result: str, updated: list,
    ) -> str:
        parts = []
        client = proposal.get("client_name", "未知客户")
        industry = proposal.get("industry", "未知行业")
        parts.append(f"## {client} 项目归档报告")
        parts.append(f"- 行业：{industry}")
        parts.append(f"- 中标结果：{bid_result or '待定'}")
        if review_comments:
            parts.append(f"- 审核意见：{review_comments}")
        parts.append(f"- 更新模块：{', '.join(updated) if updated else '无'}")

        # 中标结果反映恐惧校准的准确性（认知失调理论+归因理论+多轮博弈）
        if bid_result == "中标":
            parts.append("- 恐惧校准✅：恐惧映射准确——我们对客户'日常性→社会性→基本恐惧'的穿透是精准的")
            parts.append("- 认知失调验证✅：提案成功在客户心中建立了'旧模式vs新规则'的失调结构")
            parts.append("- 外部归因策略✅：压力归因于外部行业变化而非客户能力的策略是有效的")
            parts.append("- 多轮博弈分析✅：第一阶段合作的信任已建立，为下一轮(续约/扩单)奠定了合作基础")
        elif bid_result == "未中标":
            parts.append("- 恐惧校准⚠️：建议复盘客户真实决策恐惧是否与预期一致，更新恐惧映射库")
            parts.append("- 归因理论复盘：判断恐惧时是否错归因于客户自身能力？应归因于外部行业变化")
            parts.append("- EPPM复盘：方案是否提供了足够的效能感知（反应效能+自我效能）？")
            parts.append("- 信号博弈复盘：我们的质量信号（前期投入/洞察/案例）是否足够强？竞品是否释放了更强的信号？")
            parts.append("- 多轮博弈复盘：这不是终点，而是下一轮的起点——本次建立的行业洞察和客户关系是下一轮博弈的筹码")
            parts.append("- 建议：补充客户反馈后对比预期恐惧与实际恐惧的差距")

        return "\n".join(parts)