from typing import Literal, Optional
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent import create_proposal_workflow
from app.tools.archive import ProposalArchiveTool
from app.tools.export import ProposalExporter


router = APIRouter()

# MVP persistence. Replace with ProposalRecord storage when database.py is implemented.
PROPOSAL_RUNS: dict[str, dict] = {}


class ProposalRequest(BaseModel):
    user_input: str = Field(min_length=1)
    user_id: Optional[str] = None
    research_mode: Literal["auto", "fast", "full"] = "auto"
    output_formats: list[Literal["slides", "docx", "pptx"]] = Field(default_factory=lambda: ["pptx"])


class ProposalResponse(BaseModel):
    request_id: str
    status: str
    message: str
    missing_info: list[str] = Field(default_factory=list)
    proposal_spec: dict = Field(default_factory=dict)
    outputs: dict = Field(default_factory=dict)


class ReviewRequest(BaseModel):
    approved: bool
    comments: str = ""
    output_formats: Optional[list[Literal["slides", "docx", "pptx"]]] = None


class ArchiveRequest(BaseModel):
    bid_result: str = Field(min_length=1)
    review_comments: str = ""


@router.get("/")
async def list_proposals():
    proposals = [
        {
            "request_id": request_id,
            "status": state.get("review_status", state.get("current_stage", "unknown")),
            "client_name": state.get("brief", {}).get("client_name", ""),
        }
        for request_id, state in PROPOSAL_RUNS.items()
    ]
    return {"proposals": proposals, "status": "ok"}


@router.post("/generate", response_model=ProposalResponse)
async def generate_proposal(req: ProposalRequest):
    request_id = str(uuid.uuid4())[:8]
    initial_state = {
        "user_input": req.user_input,
        "user_id": req.user_id or "default_user",
        "session_id": request_id,
        "requested_research_mode": req.research_mode,
        "requested_output_formats": list(req.output_formats),
        "messages": [],
        "review_status": "not_started",
        "current_stage": "init",
    }

    result = dict(create_proposal_workflow().invoke(initial_state))
    PROPOSAL_RUNS[request_id] = result
    status = result.get("review_status", "unknown")

    if status == "awaiting_input":
        missing = result.get("missing_info", [])
        return ProposalResponse(
            request_id=request_id,
            status=status,
            message=f"需要补充：{'、'.join(missing)}",
            missing_info=missing,
        )

    return ProposalResponse(
        request_id=request_id,
        status=status,
        message="审核稿已生成，请审核后再导出对外文件",
        proposal_spec=result.get("proposal_spec", {}),
    )


@router.post("/{request_id}/review", response_model=ProposalResponse)
async def review_proposal(request_id: str, req: ReviewRequest):
    state = _get_run(request_id)
    if state.get("review_status") not in {"awaiting_review", "rejected"}:
        raise HTTPException(status_code=409, detail="当前状态不允许审核")

    state["review_comments"] = req.comments
    if not req.approved:
        state["review_status"] = "rejected"
        state["current_stage"] = "revision_required"
        return ProposalResponse(
            request_id=request_id,
            status="rejected",
            message="审核未通过，方案需要修改后重新提交",
            proposal_spec=state.get("proposal_spec", {}),
        )

    formats = req.output_formats or state.get("requested_output_formats", ["pptx"])
    export_result = ProposalExporter().export(
        state.get("proposal_spec", {}), state.get("brief", {}), list(formats)
    )
    state["outputs"] = export_result.outputs
    state["review_status"] = "approved"
    state["current_stage"] = "delivered" if export_result.success else "export_failed"

    message = "审核通过，文件已生成" if export_result.success else "审核通过，但文件生成失败"
    if export_result.errors:
        message += f"：{'；'.join(export_result.errors)}"
    return ProposalResponse(
        request_id=request_id,
        status=state["current_stage"],
        message=message,
        proposal_spec=state.get("proposal_spec", {}),
        outputs=state.get("outputs", {}),
    )


@router.post("/{request_id}/archive")
async def archive_proposal(request_id: str, req: ArchiveRequest):
    state = _get_run(request_id)
    if state.get("review_status") != "approved":
        raise HTTPException(status_code=409, detail="只有审核通过的最终方案可以归档")

    result = ProposalArchiveTool().archive(
        proposal_spec=state.get("proposal_spec", {}),
        brief=state.get("brief", {}),
        review_comments=req.review_comments or state.get("review_comments", ""),
        bid_result=req.bid_result,
        user_id=state.get("user_id", "default_user"),
        session_id=state.get("session_id", request_id),
    )
    state["archive_result"] = result.model_dump()
    if not result.success:
        raise HTTPException(status_code=503, detail=result.error)
    state["current_stage"] = "archived"
    return {
        "request_id": request_id,
        "status": "archived",
        "updated_libraries": result.updated_libraries,
        "review_report": result.review_report,
    }


@router.get("/status/{request_id}")
async def get_proposal_status(request_id: str):
    state = _get_run(request_id)
    return {
        "request_id": request_id,
        "status": state.get("current_stage", "unknown"),
        "review_status": state.get("review_status", "not_started"),
        "missing_info": state.get("missing_info", []),
        "outputs": state.get("outputs", {}),
        "messages": state.get("messages", []),
    }


def _get_run(request_id: str) -> dict:
    state = PROPOSAL_RUNS.get(request_id)
    if state is None:
        raise HTTPException(status_code=404, detail="提案任务不存在")
    return state
