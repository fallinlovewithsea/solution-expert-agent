class ResearchTool:
    """Adapter around XHS collection; this is a tool, not a business skill."""

    def collect(self, brief: dict) -> dict:
        from skills.s3_industry_insight import S3IndustryInsight, IndustryInsightInput

        result = S3IndustryInsight().run(IndustryInsightInput(
            industry=brief.get("industry", ""),
            category=brief.get("sub_category", ""),
            competitors=brief.get("competitors", []) or [],
            client_name=brief.get("client_name", ""),
        ))
        if not getattr(result, "success", False):
            raise RuntimeError(getattr(result, "error", "小红书研究工具执行失败"))
        return result.model_dump()
