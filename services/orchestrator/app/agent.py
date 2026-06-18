from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END
from app.skills.s2_requirement import S2RequirementDiagnosis, RequirementInput
from app.skills.s3_industry_insight import S3IndustryInsight, IndustryInsightInput
from app.skills.s4_client_insight import S4ClientInsight, ClientInsightInput
from app.skills.s5_proposal_design import S5ProposalDesign, ProposalDesignInput
from app.skills.s7_content_gen import S7ContentGeneration, ContentGenInput
from app.skills.s8_format_output import S8FormatOutput, FormatOutputInput


class AgentState(TypedDict):
    user_input: str
    requirement_document: dict
    insight_report: dict
    industry_analysis: dict
    competitor_analysis: list
    client_diagnosis: dict
    growth_analysis: dict
    client_insight: dict
    full_proposal: dict
    matched_cases: list
    slides: list
    brand_assets: dict
    slides_url: str
    docx_url: str
    pptx_path: str
    messages: Annotated[Sequence[str], operator.add]
    current_stage: str
    needs_human_review: bool
    # ── 新增：记忆层字段 ──
    user_id: str
    session_id: str
    client_history: dict
    user_preferences: dict


def create_proposal_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("s2_requirement", run_s2_requirement)
    workflow.add_node("s3_industry_insight", run_s3_industry_insight)
    workflow.add_node("s4_client_insight", run_s4_client_insight)
    workflow.add_node("s5_proposal_design", run_s5_proposal_design)
    workflow.add_node("s7_content_gen", run_s7_content_gen)
    workflow.add_node("s8_format_output", run_s8_format_output)
    workflow.add_node("human_review", human_review_node)

    workflow.set_entry_point("s2_requirement")
    workflow.add_edge("s2_requirement", "s3_industry_insight")
    workflow.add_edge("s3_industry_insight", "s4_client_insight")
    workflow.add_edge("s4_client_insight", "s5_proposal_design")
    workflow.add_edge("s5_proposal_design", "s7_content_gen")
    workflow.add_edge("s7_content_gen", "s8_format_output")
    workflow.add_edge("s8_format_output", "human_review")
    workflow.add_edge("human_review", END)

    return workflow.compile()


def run_s2_requirement(state: AgentState) -> AgentState:
    skill = S2RequirementDiagnosis()
    result = skill.run(RequirementInput(communication_records=state["user_input"]))
    state["requirement_document"] = result.model_dump()
    state["current_stage"] = "s2_requirement"
    state["messages"].append(
        f"[S2] 需求诊断完成: {result.client_name} - {result.industry}"
    )
    # 记录搜索偏好
    try:
        from app.db.memory import MemoryStore
        memory = MemoryStore()
        uid = state.get("user_id", "default_user")
        memory.record_search(uid, result.client_name)
        memory.record_industry(uid, result.industry)
    except Exception:
        pass
    return state


def run_s3_industry_insight(state: AgentState) -> AgentState:
    """S3: 行业洞察 — 小红书数据采集 + LLM 深度分析"""
    req = state["requirement_document"]
    skill = S3IndustryInsight()

    result = skill.run(IndustryInsightInput(
        industry=req.get("industry", ""),
        category=req.get("sub_category", ""),
        competitors=req.get("competitors", []),
        client_name=req.get("client_name", ""),
    ))

    state["insight_report"] = result.model_dump()
    state["industry_analysis"] = result.industry_analysis
    state["competitor_analysis"] = result.competitor_analysis
    state["client_diagnosis"] = result.client_diagnosis
    state["growth_analysis"] = result.growth_analysis
    state["current_stage"] = "s3_industry_insight"
    state["messages"].append(
        f"[S3] 行业洞察完成: {result.summary[:80]}..."
    )
    return state


def run_s4_client_insight(state: AgentState) -> AgentState:
    skill = S4ClientInsight()
    result = skill.run(ClientInsightInput(
        requirement_document=state["requirement_document"],
        insight_report=state.get("insight_report", {}),
    ))
    state["client_insight"] = result.model_dump()
    state["current_stage"] = "s4_client_insight"
    state["messages"].append("[S4] 客户洞察完成")
    return state


def run_s5_proposal_design(state: AgentState) -> AgentState:
    skill = S5ProposalDesign()
    result = skill.run(ProposalDesignInput(
        client_insight=state["client_insight"],
        insight_report=state.get("insight_report", {}),
        requirement_document=state["requirement_document"],
    ))
    state["full_proposal"] = result.model_dump()
    state["current_stage"] = "s5_proposal_design"
    state["messages"].append("[S5] 方案设计完成")
    return state


def run_s7_content_gen(state: AgentState) -> AgentState:
    skill = S7ContentGeneration()
    result = skill.run(ContentGenInput(
        full_proposal=state["full_proposal"],
        matched_cases=state.get("matched_cases", []),
        brand_assets=state.get("brand_assets", {}),
    ))
    state["slides"] = result.slides
    state["current_stage"] = "s7_content_gen"
    state["messages"].append(f"[S7] 内容生成完成: {result.slide_count} 页")
    return state


def run_s8_format_output(state: AgentState) -> AgentState:
    skill = S8FormatOutput()
    result = skill.run(FormatOutputInput(
        slides=state["slides"],
        brand_assets=state.get("brand_assets", {}),
    ))
    state["slides_url"] = getattr(result, "slides_url", "") or ""
    state["docx_url"] = getattr(result, "docx_url", "") or ""
    state["pptx_path"] = getattr(result, "pptx_path", "") or ""
    state["needs_human_review"] = True
    # 记录输出格式偏好
    try:
        from app.db.memory import MemoryStore
        memory = MemoryStore()
        uid = state.get("user_id", "default_user")
        if state.get("slides_url"):
            memory.record_output_format(uid, "slides")
        if state.get("pptx_path"):
            memory.record_output_format(uid, "pptx")
    except Exception:
        pass
    state["current_stage"] = "s8_format_output"
    state["messages"].append(f"[S8] 格式输出完成: success={result.success}")
    return state


def human_review_node(state: AgentState) -> AgentState:
    state["messages"].append(
        f"[审核] 方案已生成，请审阅:\n"
        f"  Slides: {state['slides_url']}\n"
        f"  Docx: {state['docx_url']}\n"
        f"  PPTX: {state['pptx_path']}"
    )
    return state