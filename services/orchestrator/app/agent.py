from typing import TypedDict, Annotated, Sequence
import operator
from langgraph.graph import StateGraph, END
from skills.s1_opportunity import S1OpportunityAssessment, OpportunityInput
from skills.s2_requirement import S2RequirementDiagnosis, RequirementInput
from skills.s3_industry_insight import S3IndustryInsight, IndustryInsightInput
from skills.s4_client_insight import S4ClientInsight, ClientInsightInput
from skills.s5_proposal_design import S5ProposalDesign, ProposalDesignInput
from skills.s6_case_match import S6CaseMatch, CaseMatchInput
from skills.s7_content_gen import S7ContentGeneration, ContentGenInput
from skills.s8_format_output import S8FormatOutput, FormatOutputInput
from skills.s9_archive import S9Archive, ArchiveInput
from skills.progressive_questioner import ProgressiveQuestioner, ProgressiveQuestionerInput
from skills.s8_format_output import S8FormatOutput, FormatOutputInput
from skills.s9_archive import S9Archive, ArchiveInput


class AgentState(TypedDict):
    user_input: str
    # s1 商机评估结果
    opportunity_result: dict
    # s2 需求诊断结果
    requirement_document: dict
    # s3 行业洞察结果
    insight_report: dict
    industry_analysis: dict
    competitor_analysis: list
    client_diagnosis: dict
    growth_analysis: dict
    # s4 客户洞察结果
    client_insight: dict
    # s5 方案设计结果
    full_proposal: dict
    # s6 案例匹配结果
    matched_cases: list
    # s7 内容生成结果
    slides: list
    # s8 格式输出结果
    brand_assets: dict
    slides_url: str
    docx_url: str
    pptx_path: str
    # s9 归档结果
    archive_result: dict
    # 通用字段
    messages: Annotated[Sequence[str], operator.add]
    current_stage: str
    needs_human_review: bool
    # 渐进式提问控制
    needs_followup: bool           # 是否需要补充信息
    followup_hint: str             # 补充提示（给用户看的）
    asked_questions: list          # 已问过的问题（防重复）
    # 记忆层字段
    user_id: str
    session_id: str
    client_history: dict
    user_preferences: dict


def create_proposal_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("progressive_questioner", run_progressive_questioner)
    workflow.add_node("s1_opportunity", run_s1_opportunity)
    workflow.add_node("s2_requirement", run_s2_requirement)
    workflow.add_node("s3_industry_insight", run_s3_industry_insight)
    workflow.add_node("s4_client_insight", run_s4_client_insight)
    workflow.add_node("s5_proposal_design", run_s5_proposal_design)
    workflow.add_node("s6_case_match", run_s6_case_match)
    workflow.add_node("s7_content_gen", run_s7_content_gen)
    workflow.add_node("s8_format_output", run_s8_format_output)
    workflow.add_node("s9_archive", run_s9_archive)
    workflow.add_node("human_review", human_review_node)

    workflow.set_entry_point("progressive_questioner")
    workflow.add_conditional_edges(
        "progressive_questioner",
        route_from_questioner,
        {"s1_opportunity": "s1_opportunity", "progressive_questioner": "progressive_questioner", END: END}
    )

    # ── 分析层(S1-S4)：每一步后检查是否需要补充信息 ──
    workflow.add_edge("s1_opportunity", "s2_requirement")
    workflow.add_edge("s2_requirement", "s3_industry_insight")
    workflow.add_edge("s3_industry_insight", "s4_client_insight")

    # S4 之后：检查是否需要补充信息再进入方案层
    workflow.add_conditional_edges(
        "s4_client_insight",
        check_needs_followup,
        {"progressive_questioner": "progressive_questioner", "s5_proposal_design": "s5_proposal_design"}
    )

    # ── 方案层(S5-S7)：线性流转 ──
    workflow.add_edge("s5_proposal_design", "s6_case_match")
    workflow.add_edge("s6_case_match", "s7_content_gen")

    # S7 之后：检查是否需要调整内容
    workflow.add_conditional_edges(
        "s7_content_gen",
        check_needs_followup,
        {"progressive_questioner": "progressive_questioner", "s8_format_output": "s8_format_output"}
    )

    # ── 交付层(S8-S9) ──
    workflow.add_edge("s8_format_output", "s9_archive")
    workflow.add_edge("s9_archive", "human_review")
    workflow.add_edge("human_review", END)

    return workflow.compile()


# ── S1: 商机评估 ──

def run_s1_opportunity(state: AgentState) -> AgentState:
    """S1: 商机评估 — 判断是否跟进 + 项目分类"""
    skill = S1OpportunityAssessment()
    result = skill.run(OpportunityInput(
        client_name="",
        industry="",
        budget_range="",
        initial_requirements=state["user_input"],
    ))
    state["opportunity_result"] = result.model_dump()
    state["current_stage"] = "s1_opportunity"
    state["messages"].append(
        f"[S1] 商机评估: {result.go_or_no_go} (置信度: {result.confidence_score})"
    )
    return state


# ── S2: 需求诊断 ──

def run_s2_requirement(state: AgentState) -> AgentState:
    skill = S2RequirementDiagnosis()
    result = skill.run(RequirementInput(communication_records=state["user_input"]))
    state["requirement_document"] = result.model_dump()
    state["current_stage"] = "s2_requirement"
    state["messages"].append(
        f"[S2] 需求诊断完成: {result.client_name} - {result.industry}"
    )
    try:
        from app.db.memory import MemoryStore
        memory = MemoryStore()
        uid = state.get("user_id", "default_user")
        memory.record_search(uid, result.client_name)
        memory.record_industry(uid, result.industry)
    except Exception:
        pass
    return state


# ── S3: 行业洞察 ──

def run_s3_industry_insight(state: AgentState) -> AgentState:
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


# ── S4: 客户洞察 ──

def run_s4_client_insight(state: AgentState) -> AgentState:
    skill = S4ClientInsight()
    result = skill.run(ClientInsightInput(
        requirement_document=state["requirement_document"],
        insight_report=state.get("insight_report", {}),
    ))
    state["client_insight"] = result.model_dump()
    state["current_stage"] = "s4_client_insight"

    # 检查关键分析是否缺失，触发中流转校准
    if not state["client_insight"].get("leverage_level") or \
       not state["client_insight"].get("structural_contradiction"):
        state["needs_followup"] = True
        state["followup_hint"] = "客户洞察分析缺少关键信息。请补充以下内容：\n- 客户当前的核心焦虑停留在哪个层面（日常性/社会性/基本焦虑）？\n- 行业正在发生什么结构性变化让客户感到压力？"
        state["messages"].append("[S4] ⚠️ 关键分析缺失，需要补充信息")
    else:
        state["needs_followup"] = False
        state["followup_hint"] = ""
        state["messages"].append("[S4] 客户洞察完成")

    return state


# ── S5: 方案设计 ──

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


# ── S6: 案例匹配 ──

def run_s6_case_match(state: AgentState) -> AgentState:
    req = state["requirement_document"]
    client_insight = state.get("client_insight", {})
    skill = S6CaseMatch()
    result = skill.run(CaseMatchInput(
        industry=req.get("industry", ""),
        customer_type=req.get("sub_category", ""),
        pain_points=client_insight.get("core_pain_points", []) or [],
        solution_modules=(
            state["full_proposal"].get("operation_strategy", {}) or {}
        ).get("execution_plan", []) or [],
    ))
    state["matched_cases"] = result.matched_cases
    state["current_stage"] = "s6_case_match"
    state["messages"].append(
        f"[S6] 案例匹配完成: 匹配到 {len(result.matched_cases)} 个案例 — {result.recommendation}"
    )
    return state


# ── S7: 内容生成 ──

def run_s7_content_gen(state: AgentState) -> AgentState:
    req = state["requirement_document"]
    skill = S7ContentGeneration()
    result = skill.run(ContentGenInput(
        full_proposal=state["full_proposal"],
        matched_cases=state.get("matched_cases", []),
        brand_assets={
            "brand_name": req.get("client_name", ""),
            "industry": req.get("industry", ""),
            "pain_points": req.get("pain_points", []),
            "competitors": req.get("competitors", []),
            **(state.get("brand_assets", {})),
        },
    ))
    state["slides"] = result.slides
    state["current_stage"] = "s7_content_gen"
    state["messages"].append(f"[S7] 内容生成完成: {result.slide_count} 页")
    return state


# ── S8: 格式输出 ──

def run_s8_format_output(state: AgentState) -> AgentState:
    req = state["requirement_document"]
    skill = S8FormatOutput()
    result = skill.run(FormatOutputInput(
        slides=state["slides"],
        brand_assets={
            "brand_name": req.get("client_name", ""),
            "industry": req.get("industry", ""),
            **(state.get("brand_assets", {})),
        },
        brand_name=req.get("client_name", ""),
        proposal_title=f"{req.get('client_name', '品牌')}小红书KOS增长全案方案",
    ))
    state["slides_url"] = getattr(result, "slides_url", "") or ""
    state["docx_url"] = getattr(result, "docx_url", "") or ""
    state["pptx_path"] = getattr(result, "pptx_path", "") or ""
    state["needs_human_review"] = True
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


# ── S9: 复盘归档 ──

def run_s9_archive(state: AgentState) -> AgentState:
    req = state["requirement_document"]
    skill = S9Archive()
    result = skill.run(ArchiveInput(
        final_proposal={
            "client_name": req.get("client_name", ""),
            "industry": req.get("industry", ""),
            **state["full_proposal"],
        },
        review_comments="",
        bid_result="",
        user_id=state.get("user_id", "default_user"),
        session_id=state.get("session_id", ""),
    ))
    state["archive_result"] = result.model_dump()
    state["current_stage"] = "s9_archive"
    state["messages"].append(
        f"[S9] 归档完成: 更新了 {', '.join(result.updated_libraries)}"
    )
    return state


def check_needs_followup(state: AgentState) -> str:
    """检查当前阶段是否需要追问补充信息"""
    if state.get("needs_followup", False):
        return "progressive_questioner"
    return (
        "s5_proposal_design" if state["current_stage"].startswith("s4")
        else "s8_format_output" if state["current_stage"].startswith("s7")
        else "s5_proposal_design"
    )


# ── 渐进式提问（S0·入口 + 中流转校准）─


def run_progressive_questioner(state: AgentState) -> AgentState:
    """渐进式提问器：入口收集信息 + 中流转校准方向"""
    skill = ProgressiveQuestioner()
    user_input = state.get("user_input", "")
    current_stage = state.get("current_stage", "")
    needs_followup = state.get("needs_followup", False)
    followup_hint = state.get("followup_hint", "")

    # 中流转校准模式：有特定提示，针对性地问
    if needs_followup and followup_hint:
        state["messages"].append(f"[校准] {followup_hint}")
        state["needs_followup"] = False
        state["current_stage"] = current_stage  # 保持当前阶段不变
        return state

    # 入口模式：渐进式收集信息
    if not current_stage or current_stage in ("", "s0_L1_FORM"):
        phase = "L1_FORM"
    else:
        phase = current_stage.replace("s0_", "")

    collected = state.get("messages", [])
    collected_text = "\n".join(str(m) for m in collected[-5:]) if collected else ""

    result = skill.run(ProgressiveQuestionerInput(
        user_response=user_input,
        current_phase=phase,
        collected_data={"history": collected_text},
    ))

    if result.ready_for_proposal:
        state["current_stage"] = "s1_opportunity"
        state["user_input"] = f"{user_input}\n\n[方案摘要]\n{result.proposal_brief}"
        state["messages"].append("[提问器] ✅ 信息收集完毕，进入方案生成流程")
    else:
        state["current_stage"] = f"s0_{result.phase}"
        q = result.next_question
        if result.need_scrutiny:
            q = f"{result.scrutiny_comment}\n\n{q}" if q else result.scrutiny_comment
        state["messages"].append(f"[提问器] {q}")

    return state


def route_from_questioner(state: AgentState) -> str:
    """根据渐进式提问器的状态决定下一步"""
    stage = state.get("current_stage", "")
    if stage == "s1_opportunity":
        return "s1_opportunity"
    elif stage.startswith("s0_"):
        return "progressive_questioner"
    return END


# ── 人工审核节点 ──

def human_review_node(state: AgentState) -> AgentState:
    state["messages"].append(
        f"[审核] 方案已生成，请审阅:\n"
        f"  Slides: {state['slides_url']}\n"
        f"  Docx: {state['docx_url']}\n"
        f"  PPTX: {state['pptx_path']}"
    )
    return state