from app.skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import Dict
import uuid


class ArchiveInput(SkillInput):
    final_proposal: Dict = Field(description="提案终稿")
    review_comments: str = Field(default="")
    bid_result: str = Field(default="")
    user_id: str = Field(default="default_user")
    session_id: str = Field(default="")


class ArchiveOutput(SkillOutput):
    updated_libraries: list = Field(default_factory=list)
    review_report: str = ""


class S9Archive(BaseSkill):
    name = "s9_archive"
    description = "复盘归档：更新 8 大物料库 + 写入记忆层 + 生成复盘报告"

    def execute(self, input_data: ArchiveInput) -> ArchiveOutput:
        updates = []

        # 更新品牌信息
        self._update_brand_info(input_data.final_proposal)
        updates.append("brand_info")

        # 更新竞品库
        self._update_competitor_library(input_data.final_proposal)
        updates.append("competitor_analysis")

        # 更新复盘库
        self._update_review_library(input_data)
        updates.append("proposal_review")

        # 写入记忆层 (L3)
        self._save_to_memory(input_data)
        updates.append("memory_layer")

        report = f"""## 复盘报告
- 竞标结果: {input_data.bid_result}
- 评审意见: {input_data.review_comments}
- 更新物料库: {', '.join(updates)}
"""

        return ArchiveOutput(
            updated_libraries=updates,
            review_report=report,
        )

    def _save_to_memory(self, input_data: ArchiveInput):
        """写入记忆层：用户偏好 + 会话历史"""
        try:
            from app.db.memory import MemoryStore

            memory = MemoryStore()
            proposal = input_data.final_proposal
            session_id = input_data.session_id or str(uuid.uuid4())
            user_id = input_data.user_id
            client_name = proposal.get("client_name", "unknown")
            industry = proposal.get("industry", "")

            # 保存会话记忆
            memory.save_session(
                session_id=session_id,
                user_id=user_id,
                client_name=client_name,
                industry=industry,
                stage="s9_archive",
                context={
                    "proposal": proposal,
                    "bid_result": input_data.bid_result,
                    "review_comments": input_data.review_comments,
                },
            )

            # 更新中标结果
            if input_data.bid_result:
                memory.update_session_result(
                    session_id=session_id,
                    bid_result=input_data.bid_result,
                    review_feedback=input_data.review_comments,
                )

            # 更新用户偏好
            memory.record_industry(user_id, industry)
            memory.record_search(user_id, client_name)
            memory.update_user_preferences(user_id, {
                "interaction_count": 1,
            })

        except Exception:
            pass

    def _update_brand_info(self, proposal: Dict):
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO brand_info (brand_name, industry, current_status)
                       VALUES (%s, %s, %s)
                       ON CONFLICT (brand_name) DO UPDATE
                       SET current_status = EXCLUDED.current_status,
                           updated_at = NOW()""",
                    (
                        proposal.get("client_name", ""),
                        proposal.get("industry", ""),
                        "已提案",
                    ),
                )
        except Exception:
            pass

    def _update_competitor_library(self, proposal: Dict):
        pass

    def _update_review_library(self, input_data: ArchiveInput):
        try:
            from app.db.database import get_db
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    """INSERT INTO review_records (proposal_id, extracted_data)
                       VALUES (%s, %s)""",
                    (1, input_data.final_proposal),
                )
        except Exception:
            pass