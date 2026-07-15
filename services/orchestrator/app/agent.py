from typing import Annotated, Literal, TypedDict
import operator

from langgraph.graph import END, StateGraph

from app.skills.brief import BriefInput, BriefSkill
from app.skills.insight import InsightInput, InsightSkill
from app.skills.proposal import ProposalInput, ProposalSkill


class AgentState(TypedDict, total=False):
    user_input: str
    user_id: str
    session_id: str
    requested_research_mode: Literal["auto", "fast", "full"]
    requested_output_formats: list[str]
    brief: dict
    qualification: dict
    missing_info: list[str]
    research_mode: Literal["fast", "full"]
    research_data: dict
    decision_map: dict
    limitations: list[str]
    proposal_spec: dict
    matched_cases: list[dict]
    review_status: Literal["not_started", "awaiting_input", "awaiting_review", "approved", "rejected"]
    review_comments: str
    outputs: dict
    archive_result: dict
    current_stage: str
    messages: Annotated[list[str], operator.add]


def create_proposal_workflow():
    """Create the draft-generation workflow with three business skills."""
    workflow = StateGraph(AgentState)
    workflow.add_node("brief", run_brief)
    workflow.add_node("decision_insight", run_decision_insight)
    workflow.add_node("proposal", run_proposal)
    workflow.add_node("awaiting_input", awaiting_input_node)
    workflow.add_node("awaiting_review", awaiting_review_node)

    workflow.set_entry_point("brief")
    workflow.add_conditional_edges(
        "brief",
        route_after_brief,
        {"ready": "decision_insight", "needs_input": "awaiting_input"},
    )
    workflow.add_edge("decision_insight", "proposal")
    workflow.add_edge("proposal", "awaiting_review")
    workflow.add_edge("awaiting_input", END)
    workflow.add_edge("awaiting_review", END)
    return workflow.compile()


def run_brief(state: AgentState) -> dict:
    result = BriefSkill().run(BriefInput(
        user_input=state["user_input"],
        research_mode=state.get("requested_research_mode", "auto"),
    ))
    return {
        "brief": result.brief,
        "qualification": result.qualification,
        "missing_info": result.missing_info,
        "research_mode": result.research_mode,
        "current_stage": "brief",
        "messages": [f"[需求简报] 已整理，研究模式：{result.research_mode}"],
    }


def route_after_brief(state: AgentState) -> str:
    return "needs_input" if state.get("missing_info") else "ready"


def awaiting_input_node(state: AgentState) -> dict:
    missing = "、".join(state.get("missing_info", []))
    return {
        "review_status": "awaiting_input",
        "current_stage": "awaiting_input",
        "messages": [f"[等待补充] 生成正式方案前需要确认：{missing}"],
    }


def run_decision_insight(state: AgentState) -> dict:
    result = InsightSkill().run(InsightInput(
        brief=state["brief"],
        research_mode=state.get("research_mode", "full"),
    ))
    return {
        "decision_map": result.decision_map,
        "research_data": result.research_data,
        "limitations": result.limitations,
        "current_stage": "decision_insight",
        "messages": ["[决策洞察] 已形成用户决策地图"],
    }


def run_proposal(state: AgentState) -> dict:
    result = ProposalSkill().run(ProposalInput(
        brief=state["brief"],
        decision_map=state["decision_map"],
        limitations=state.get("limitations", []),
    ))
    return {
        "proposal_spec": result.proposal_spec,
        "matched_cases": result.matched_cases,
        "current_stage": "proposal",
        "messages": [f"[方案生成] 已生成 {len(result.proposal_spec.get('slides', []))} 页审核稿"],
    }


def awaiting_review_node(state: AgentState) -> dict:
    return {
        "review_status": "awaiting_review",
        "current_stage": "awaiting_review",
        "messages": ["[等待审核] 审核通过后才能生成对外文件"],
    }
