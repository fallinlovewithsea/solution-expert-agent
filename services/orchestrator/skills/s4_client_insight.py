from skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Dict


class ClientInsightInput(SkillInput):
    requirement_document: dict = Field(description="S2 需求诊断输出")
    insight_report: dict = Field(description="S3 行业洞察输出")


class ClientInsightOutput(SkillOutput):
    core_pain_points: List[str] = Field(default_factory=list)
    market_opportunities: List[str] = Field(default_factory=list)
    growth_model_mapping: str = ""
    strategy_direction: str = ""
    summary: str = ""


class S4ClientInsight(BaseSkill):
    name = "s4_client_insight"
    description = "客户洞察：整合需求诊断和行业洞察，输出客户洞察汇总文档"

    def execute(self, input_data: ClientInsightInput) -> ClientInsightOutput:
        req = input_data.requirement_document
        insight = input_data.insight_report

        prompt = f"""基于以下信息，生成客户洞察汇总。

## 客户需求
{req}

## 行业洞察
{insight}

请分析并返回 JSON：
- core_pain_points: 核心痛点（3-5条）
- market_opportunities: 市场机会（3-5条）
- growth_model_mapping: 匹配的增长模型
- strategy_direction: 策略方向建议
- summary: 一句话总结

只返回 JSON。"""

        extracted = self._llm_analyze(prompt)
        return ClientInsightOutput(**extracted)

    def _llm_analyze(self, prompt: str) -> dict:
        import json
        from app.llm import get_llm
        llm = get_llm(task_type="heavy")
        response = llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {}