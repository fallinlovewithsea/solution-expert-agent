from app.skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Dict


class CaseMatchInput(SkillInput):
    industry: str
    customer_type: str = ""
    pain_points: List[str] = Field(default_factory=list)
    solution_modules: List[str] = Field(default_factory=list)


class CaseMatchOutput(SkillOutput):
    matched_cases: List[Dict] = Field(default_factory=list)
    recommendation: str = ""


class S6CaseMatch(BaseSkill):
    name = "s6_case_match"
    description = "案例匹配：基于行业+场景+玩法标签匹配最佳案例"

    def execute(self, input_data: CaseMatchInput) -> CaseMatchOutput:
        from app.db.database import get_db

        cases = []
        try:
            with get_db() as db:
                cursor = db.cursor()
                cursor.execute(
                    """SELECT * FROM case_labels
                       WHERE industry = %s
                       ORDER BY relevance_score DESC
                       LIMIT 5""",
                    (input_data.industry,),
                )
                rows = cursor.fetchall()

            cases = [
                {
                    "name": r["case_name"],
                    "relevance_score": r["relevance_score"],
                    "match_reason": f"同属{r['industry']}行业，{r['scene']}场景可复用",
                    "key_metrics": r["key_metrics"],
                    "source_url": r["source_url"],
                }
                for r in rows
            ]
        except Exception:
            pass

        recommendation = (
            f"建议引用 {cases[0]['name']}" if cases
            else "暂无匹配案例，建议使用通用案例模板"
        )

        return CaseMatchOutput(matched_cases=cases, recommendation=recommendation)