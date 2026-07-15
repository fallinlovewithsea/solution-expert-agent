from pydantic import BaseModel, Field


class ArchiveResult(BaseModel):
    success: bool = False
    updated_libraries: list[str] = Field(default_factory=list)
    review_report: str = ""
    error: str = ""


class ProposalArchiveTool:
    """Archive an approved proposal after a real project outcome exists."""

    def archive(
        self,
        proposal_spec: dict,
        brief: dict,
        review_comments: str,
        bid_result: str,
        user_id: str,
        session_id: str,
    ) -> ArchiveResult:
        if not bid_result.strip():
            return ArchiveResult(error="缺少真实竞标或项目结果，禁止归档")

        try:
            from skills.s9_archive import S9Archive, ArchiveInput

            result = S9Archive().run(ArchiveInput(
                final_proposal={
                    "client_name": brief.get("client_name", ""),
                    "industry": brief.get("industry", ""),
                    **proposal_spec,
                },
                review_comments=review_comments,
                bid_result=bid_result,
                user_id=user_id or "default_user",
                session_id=session_id,
            ))
            updated = getattr(result, "updated_libraries", []) or []
            return ArchiveResult(
                success=bool(updated),
                updated_libraries=updated,
                review_report=getattr(result, "review_report", "") or "",
                error="" if updated else "归档工具未成功更新任何知识库",
            )
        except Exception as exc:
            return ArchiveResult(error=f"归档失败：{exc}")
