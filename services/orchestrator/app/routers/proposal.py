from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.agent import create_proposal_workflow

router = APIRouter()


class ProposalRequest(BaseModel):
    user_input: str
    user_id: Optional[str] = None


class ProposalResponse(BaseModel):
    request_id: str
    status: str
    message: str


@router.get("/")
async def list_proposals():
    return {"proposals": [], "status": "ok"}


@router.post("/generate", response_model=ProposalResponse)
async def generate_proposal(req: ProposalRequest):
    import uuid
    request_id = str(uuid.uuid4())[:8]

    workflow = create_proposal_workflow()
    initial_state = {
        "user_input": req.user_input,
        "requirement_document": {},
        "insight_report": {},
        "client_insight": {},
        "full_proposal": {},
        "matched_cases": [],
        "slides": [],
        "brand_assets": {},
        "slides_url": "",
        "docx_url": "",
        "pptx_path": "",
        "messages": [],
        "current_stage": "init",
        "needs_human_review": False,
    }

    result = workflow.invoke(initial_state)

    return ProposalResponse(
        request_id=request_id,
        status="completed",
        message=f"提案已生成 | Slides: {result.get('slides_url')} | Docx: {result.get('docx_url')}",
    )


@router.get("/status/{request_id}")
async def get_proposal_status(request_id: str):
    return {"request_id": request_id, "status": "completed"}