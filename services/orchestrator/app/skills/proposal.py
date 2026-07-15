import json

from pydantic import BaseModel, Field

from app.skills.base import CoreSkill
from app.tools.cases import CaseRetrievalTool


class ProposalInput(BaseModel):
    brief: dict
    decision_map: dict
    limitations: list[str] = Field(default_factory=list)


class ProposalOutput(BaseModel):
    proposal_spec: dict = Field(default_factory=dict)
    matched_cases: list[dict] = Field(default_factory=list)
    elapsed_ms: float = 0.0


class ProposalSkill(CoreSkill[ProposalInput, ProposalOutput]):
    name = "proposal"
    description = "方案生成：一次生成策略、案例、实施路径与标准页面内容"

    SLIDE_SECTIONS = [
        "封面", "行业洞察", "客户诊断", "用户决策地图", "竞品对标",
        "解决方案", "工具赋能与预算", "案例展示", "实施路径", "团队介绍",
    ]

    def __init__(self, case_tool: CaseRetrievalTool | None = None):
        self.case_tool = case_tool or CaseRetrievalTool()

    def execute(self, input_data: ProposalInput) -> ProposalOutput:
        try:
            cases = self.case_tool.search(input_data.brief, input_data.decision_map)
        except Exception:
            cases = []

        spec = self._generate_spec(
            input_data.brief, input_data.decision_map, cases, input_data.limitations
        )
        spec["matched_cases"] = cases
        spec["limitations"] = input_data.limitations
        return ProposalOutput(proposal_spec=spec, matched_cases=cases)

    def _generate_spec(
        self, brief: dict, decision_map: dict, cases: list[dict], limitations: list[str]
    ) -> dict:
        prompt = f"""请生成一份可直接审核的小红书营销提案规范，只返回 JSON。

需求简报：{brief}
用户决策地图：{decision_map}
可引用案例：{cases[:5]}
数据局限：{limitations}

要求：
1. 以 Feed 内容发现 + Search 搜索验证双引擎组织方案；
2. 只引用输入中存在的案例和数据，不编造指标；
3. 输出唯一事实源 proposal_spec，正文和页面不得相互矛盾；
4. 页面固定为：{self.SLIDE_SECTIONS}。

JSON 字段：
- title
- executive_summary
- strategy: 含 objective、audience、decision_journey、role_plan、content_plan、search_plan、conversion_plan、measurement
- execution_plan: 分阶段执行动作
- product_mapping: 产品与工具能力匹配
- budget_plan: 已知预算则拆解，未知则说明待确认
- implementation_path: phase、timeline、deliverables
- slides: 10 项，每项含 index、section、title、layout_type、content
- assumptions: 所有假设和待确认事项
"""
        try:
            from app.llm import get_llm

            response = get_llm(task_type="heavy").invoke(prompt)
            parsed = self._parse_json(response.content)
            if self._valid_spec(parsed):
                return parsed
        except Exception:
            pass
        return self._fallback_spec(brief, decision_map, cases)

    @staticmethod
    def _parse_json(content: str) -> dict:
        text = content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip()
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}

    def _valid_spec(self, spec: dict) -> bool:
        slides = spec.get("slides", [])
        return bool(spec.get("title") and isinstance(slides, list) and len(slides) == len(self.SLIDE_SECTIONS))

    def _fallback_spec(self, brief: dict, decision_map: dict, cases: list[dict]) -> dict:
        brand = brief.get("client_name") or "品牌"
        industry = brief.get("industry") or "行业"
        section_content = {
            "封面": f"{brand}小红书营销解决方案",
            "行业洞察": decision_map.get("market_opportunities", []),
            "客户诊断": decision_map.get("core_pain_points", []),
            "用户决策地图": decision_map.get("decision_questions", []),
            "竞品对标": brief.get("competitors", []),
            "解决方案": decision_map.get("strategy_direction", ""),
            "工具赋能与预算": {"modules": decision_map.get("recommended_modules", []), "budget": brief.get("budget_range", "待确认")},
            "案例展示": cases[:3],
            "实施路径": ["策略对齐", "内容与矩阵搭建", "投放验证", "复盘优化"],
            "团队介绍": "易美传播营销能力与弘摩科技技术能力协同交付",
        }
        layouts = [
            "cover", "chart_focus", "bullet_cards", "journey", "comparison_table",
            "icon_grid", "grid_cards", "case_card", "timeline", "two_column",
        ]
        slides = []
        for index, section in enumerate(self.SLIDE_SECTIONS, start=1):
            content = section_content[section]
            slides.append({
                "index": index,
                "section": section,
                "title": f"{brand}｜{section}" if section != "封面" else f"{brand}小红书营销解决方案",
                "layout_type": layouts[index - 1],
                "content": content if isinstance(content, str) else json.dumps(content, ensure_ascii=False),
            })
        return {
            "title": f"{brand}小红书营销解决方案",
            "executive_summary": decision_map.get("strategy_direction", ""),
            "strategy": {
                "objective": brief.get("goals", []),
                "audience": brief.get("target_audience", "待确认"),
                "decision_journey": decision_map.get("decision_questions", []),
                "role_plan": decision_map.get("role_strategy", {}),
                "content_plan": "Feed 激发需求，内容提供决策证据",
                "search_plan": decision_map.get("search_intents", {}),
                "conversion_plan": decision_map.get("conversion_paths", []),
                "measurement": ["新增搜索", "搜索占位", "内容互动", "转化行为"],
            },
            "execution_plan": decision_map.get("recommended_modules", []),
            "product_mapping": [],
            "budget_plan": brief.get("budget_range") or "预算待确认",
            "implementation_path": [
                {"phase": "策略对齐", "timeline": "第1-2周", "deliverables": ["需求简报", "决策地图"]},
                {"phase": "内容与矩阵搭建", "timeline": "第3-4周", "deliverables": ["内容模板", "账号规划"]},
                {"phase": "投放验证", "timeline": "第5-8周", "deliverables": ["执行数据", "阶段复盘"]},
                {"phase": "复盘优化", "timeline": "持续", "deliverables": ["优化方案", "运营SOP"]},
            ],
            "slides": slides,
            "assumptions": [item for item in ("预算待确认" if not brief.get("budget_range") else "", "时间线待确认" if not brief.get("timeline") else "") if item],
        }
