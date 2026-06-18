from app.skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import Optional, List


class RequirementInput(SkillInput):
    communication_records: str = Field(description="客户沟通记录或需求描述")
    rfp_document: Optional[str] = Field(default=None, description="招标文件内容（可选）")


class RequirementOutput(SkillOutput):
    client_name: str = ""
    industry: str = ""
    sub_category: str = ""
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    budget_range: str = ""
    timeline: str = ""
    scope: str = ""
    competitors: List[str] = Field(default_factory=list)
    brand_assets: dict = Field(default_factory=dict)
    missing_info: List[str] = Field(default_factory=list)


class S2RequirementDiagnosis(BaseSkill):
    name = "s2_requirement_diagnosis"
    description = "需求诊断：从客户沟通记录中提取结构化需求，生成需求文档"

    def execute(self, input_data: RequirementInput) -> RequirementOutput:
        prompt = self._build_prompt(input_data.communication_records)
        extracted = self._llm_extract(prompt)

        missing = []
        if not extracted.get("industry"):
            missing.append("请确认客户所属行业")
        if not extracted.get("budget_range"):
            missing.append("请确认预算范围")
        if not extracted.get("timeline"):
            missing.append("请确认项目时间线")

        return RequirementOutput(
            client_name=extracted.get("client_name", ""),
            industry=extracted.get("industry", ""),
            sub_category=extracted.get("sub_category", ""),
            pain_points=extracted.get("pain_points", []),
            goals=extracted.get("goals", []),
            budget_range=extracted.get("budget_range", ""),
            timeline=extracted.get("timeline", ""),
            scope=extracted.get("scope", ""),
            competitors=extracted.get("competitors", []),
            brand_assets=extracted.get("brand_assets", {}),
            missing_info=missing,
        )

    def _build_prompt(self, records: str) -> str:
        return f"""从以下客户沟通记录中提取结构化需求信息，返回 JSON 格式。

沟通记录：
{records}

请提取以下字段（缺失的字段留空）：
- client_name: 客户品牌名称
- industry: 所属行业
- sub_category: 细分品类
- pain_points: 客户痛点列表
- goals: 客户目标列表
- budget_range: 预算范围
- timeline: 项目时间线
- scope: 项目范围
- competitors: 竞品列表
- brand_assets: 品牌资源（PPT模板/设计规范/Logo等）

只返回 JSON，不要其他内容。"""

    def _llm_extract(self, prompt: str) -> dict:
        import json
        from app.llm import get_llm
        llm = get_llm(task_type="light")
        response = llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {}