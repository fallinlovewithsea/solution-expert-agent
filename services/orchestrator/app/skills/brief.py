import json
from typing import Literal

from pydantic import BaseModel, Field

from app.skills.base import CoreSkill


ResearchMode = Literal["auto", "fast", "full"]


class BriefInput(BaseModel):
    user_input: str = Field(min_length=1)
    research_mode: ResearchMode = "auto"


class BriefOutput(BaseModel):
    brief: dict = Field(default_factory=dict)
    qualification: dict = Field(default_factory=dict)
    missing_info: list[str] = Field(default_factory=list)
    ready_for_proposal: bool = False
    research_mode: Literal["fast", "full"] = "full"
    elapsed_ms: float = 0.0


class BriefSkill(CoreSkill[BriefInput, BriefOutput]):
    name = "brief"
    description = "需求简报：提取需求、识别关键信息缺口并选择研究深度"

    KNOWN_CLIENTS = {
        "飞鹤", "英氏", "金领冠", "a2", "派特生物", "快克", "蒙牛", "老庙",
        "林氏家居", "可画", "董酒", "松达", "欧恩贝", "利星行", "领克", "极氪",
    }

    def execute(self, input_data: BriefInput) -> BriefOutput:
        brief = self._extract(input_data.user_input)
        missing = self._missing_info(brief)
        known_client = brief.get("client_name", "") in self.KNOWN_CLIENTS
        mode = self._resolve_research_mode(
            input_data.research_mode, input_data.user_input, brief, known_client
        )

        qualification = {
            "known_client": known_client,
            "project_type": "existing_client" if known_client else "new_client",
            "risk_flags": self._risk_flags(brief),
            "recommendation": (
                "可优先复用历史知识，按需刷新数据"
                if known_client
                else "建议补充行业与竞品研究后再形成正式方案"
            ),
        }
        return BriefOutput(
            brief=brief,
            qualification=qualification,
            missing_info=missing,
            ready_for_proposal=not missing,
            research_mode=mode,
        )

    def _extract(self, user_input: str) -> dict:
        prompt = f"""请把下面的客户需求整理成一份售前需求简报，只返回 JSON。

客户输入：
{user_input}

字段：
- client_name: 客户或品牌名称
- industry: 行业
- sub_category: 细分品类
- decision_problem: 本次需要解决的核心消费决策问题
- pain_points: 痛点列表
- goals: 目标列表
- budget_range: 预算范围
- timeline: 时间线
- scope: 项目范围
- competitors: 竞品列表
- output_formats: 希望交付的格式列表
- brand_assets: 已有品牌素材

缺失字段使用空字符串、空列表或空对象，不要推测。"""
        try:
            from app.llm import get_llm

            response = get_llm(task_type="light").invoke(prompt)
            return self._parse_json(response.content)
        except Exception:
            return self._fallback_extract(user_input)

    @staticmethod
    def _parse_json(content: str) -> dict:
        text = content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip()
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}

    @staticmethod
    def _fallback_extract(user_input: str) -> dict:
        industries = ["母婴", "大健康", "家居家装", "汽车", "酒类", "食品", "珠宝", "设计", "技术"]
        industry = next((name for name in industries if name in user_input), "")
        return {
            "client_name": "",
            "industry": industry,
            "sub_category": "",
            "decision_problem": "",
            "pain_points": [],
            "goals": [],
            "budget_range": "",
            "timeline": "",
            "scope": user_input,
            "competitors": [],
            "output_formats": [],
            "brand_assets": {},
        }

    @staticmethod
    def _missing_info(brief: dict) -> list[str]:
        missing = []
        if not brief.get("client_name"):
            missing.append("客户或品牌名称")
        if not brief.get("industry"):
            missing.append("所属行业")
        if not (
            brief.get("decision_problem")
            or brief.get("pain_points")
            or brief.get("goals")
            or brief.get("scope")
        ):
            missing.append("核心问题或项目目标")
        return missing

    @staticmethod
    def _resolve_research_mode(
        requested: ResearchMode, raw_input: str, brief: dict, known_client: bool
    ) -> Literal["fast", "full"]:
        if requested in ("fast", "full"):
            return requested
        high_risk_terms = ("竞标", "比稿", "全案", "行业洞察", "竞品分析", "实时数据")
        if not known_client or brief.get("competitors") or any(term in raw_input for term in high_risk_terms):
            return "full"
        return "fast"

    @staticmethod
    def _risk_flags(brief: dict) -> list[str]:
        flags = []
        if not brief.get("budget_range"):
            flags.append("预算未确认")
        if not brief.get("timeline"):
            flags.append("时间线未确认")
        if brief.get("industry") == "大健康":
            flags.append("需要额外合规审查")
        return flags
