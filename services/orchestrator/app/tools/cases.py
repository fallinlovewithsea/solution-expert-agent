class CaseRetrievalTool:
    """Retrieve and rank cases for proposal composition."""

    def search(self, brief: dict, decision_map: dict) -> list[dict]:
        from skills.s6_case_match import S6CaseMatch, CaseMatchInput

        result = S6CaseMatch().run(CaseMatchInput(
            industry=brief.get("industry", ""),
            customer_type=brief.get("sub_category", ""),
            pain_points=(
                decision_map.get("core_pain_points")
                or brief.get("pain_points")
                or []
            ),
            solution_modules=decision_map.get("recommended_modules", []) or [],
        ))
        return result.matched_cases
