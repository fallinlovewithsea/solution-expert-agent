from app.skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List


class OpportunityInput(SkillInput):
    client_name: str
    industry: str
    budget_range: str
    initial_requirements: str


class OpportunityOutput(SkillOutput):
    go_or_no_go: str = "go"
    project_type: str = ""
    confidence_score: float = 0.0
    risk_factors: List[str] = Field(default_factory=list)
    recommendation: str = ""


class S1OpportunityAssessment(BaseSkill):
    name = "s1_opportunity_assessment"
    description = "商机评估：判断是否跟进 + 项目分类"

    def execute(self, input_data: OpportunityInput) -> OpportunityOutput:
        from app.db.database import get_db

        is_existing = False
        try:
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    "SELECT * FROM brand_info WHERE brand_name = %s",
                    (input_data.client_name,),
                )
                existing = cursor.fetchone()
                is_existing = existing is not None
        except Exception:
            pass

        confidence = 0.85 if is_existing else 0.60

        return OpportunityOutput(
            go_or_no_go="go",
            project_type="custom" if is_existing else "general",
            confidence_score=confidence,
            risk_factors=[] if is_existing else ["新客户，缺乏历史合作数据"],
            recommendation="建议跟进" if confidence > 0.5 else "建议评估后再决定",
        )