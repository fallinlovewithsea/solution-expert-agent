from unittest.mock import patch, MagicMock
from app.skills.s5_proposal_design import S5ProposalDesign, ProposalDesignInput


def test_s5_basic_execution():
    """基本执行测试（mock LLM）"""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = '{"operation_strategy": {"industry_insight": "母婴行业KOS矩阵趋势", "client_diagnosis": "测试诊断", "competitor_benchmark": "", "growth_strategy": "测试策略", "platform_strategy": "", "execution_plan": []}, "tool_empowerment": {"product_capability": "", "tech_architecture": "", "budget_planning": ""}, "case_display": [], "implementation_path": [], "full_proposal": "测试方案"}'

    with patch("app.llm.get_llm", return_value=mock_llm):
        mock_llm.invoke.return_value = mock_response
        skill = S5ProposalDesign()
        result = skill.run(ProposalDesignInput(
            client_insight={"core_pain_points": ["内容效率低"], "summary": "test"},
            insight_report={"industry_analysis": {}, "competitor_analysis": []},
            requirement_document={"client_name": "测试品牌", "industry": "母婴"},
        ))
    assert result.success is True
    assert result.full_proposal != ""


def test_s5_case_display_fallback():
    """当 LLM 未返回 case_display 时，应使用默认案例"""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    # 不返回 case_display
    mock_response.content = '{"operation_strategy": {}, "tool_empowerment": {}, "implementation_path": [], "full_proposal": "test"}'

    with patch("app.llm.get_llm", return_value=mock_llm):
        mock_llm.invoke.return_value = mock_response
        skill = S5ProposalDesign()
        result = skill.run(ProposalDesignInput(
            client_insight={"core_pain_points": [], "summary": "test"},
            insight_report={"industry_analysis": {}, "competitor_analysis": []},
            requirement_document={"client_name": "测试品牌", "industry": "母婴"},
        ))
    assert result.success is True
    assert result.case_display != []
    assert any("飞鹤" in c["case_name"] for c in result.case_display)


def test_s5_default_cases_muying():
    """母婴行业默认案例"""
    skill = S5ProposalDesign()
    cases = skill._build_default_cases(ProposalDesignInput(
        client_insight={},
        insight_report={},
        requirement_document={"industry": "母婴"},
    ))
    assert len(cases) >= 2
    assert any("飞鹤" in c["case_name"] for c in cases)


def test_s5_default_cases_jiaju():
    """家居家装行业默认案例"""
    skill = S5ProposalDesign()
    cases = skill._build_default_cases(ProposalDesignInput(
        client_insight={},
        insight_report={},
        requirement_document={"industry": "家居家装"},
    ))
    assert len(cases) >= 1
    assert any("林氏" in c["case_name"] for c in cases)


def test_s5_default_cases_auto():
    """汽车行业默认案例"""
    skill = S5ProposalDesign()
    cases = skill._build_default_cases(ProposalDesignInput(
        client_insight={},
        insight_report={},
        requirement_document={"industry": "汽车"},
    ))
    assert len(cases) >= 2
    assert any("利星行" in c["case_name"] for c in cases)


def test_s5_default_phases():
    """默认实施路径应有4个阶段"""
    skill = S5ProposalDesign()
    phases = skill._build_default_phases(ProposalDesignInput(
        client_insight={}, insight_report={}, requirement_document={},
    ))
    assert len(phases) == 4
    assert any("Phase 1" in p["phase"] for p in phases)
    assert any("Phase 4" in p["phase"] for p in phases)


def test_s5_llm_fallback():
    """LLM JSON 解析失败时的降级"""
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "这不是合法的 JSON"

    with patch("app.llm.get_llm", return_value=mock_llm):
        mock_llm.invoke.return_value = mock_response
        skill = S5ProposalDesign()
        result = skill.run(ProposalDesignInput(
            client_insight={}, insight_report={}, requirement_document={},
        ))
    assert result.success is True
    assert result.full_proposal == "这不是合法的 JSON"