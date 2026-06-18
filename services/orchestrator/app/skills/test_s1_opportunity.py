from app.skills.s1_opportunity import S1OpportunityAssessment, OpportunityInput


def test_s1_known_client():
    """已知客户应返回 GO 和 custom 类型"""
    skill = S1OpportunityAssessment()
    result = skill.run(OpportunityInput(
        initial_requirements="飞鹤需要KOS矩阵升级方案",
    ))
    assert result.success is True
    assert result.go_or_no_go == "GO"
    assert result.project_type == "custom"
    assert result.confidence_score >= 0.8


def test_s1_new_client():
    """新客户应返回 GO 但 general 类型"""
    skill = S1OpportunityAssessment()
    result = skill.run(OpportunityInput(
        initial_requirements="新品牌需要小红书营销方案",
    ))
    assert result.success is True
    assert result.go_or_no_go == "GO"
    assert result.project_type == "general"
    assert result.confidence_score < 0.7
    assert len(result.risk_factors) > 0


def test_s1_industry_extraction():
    """行业提取测试"""
    skill = S1OpportunityAssessment()
    result = skill.run(OpportunityInput(
        industry="母婴",
        initial_requirements="母婴品牌需要KOS方案",
    ))
    assert result.success is True
    assert result.go_or_no_go == "GO"


def test_s1_risk_factors():
    """风险因素应包含行业风险"""
    skill = S1OpportunityAssessment()
    result = skill.run(OpportunityInput(
        industry="大健康",
        budget_range="50-100万",
        initial_requirements="新客户健康品类",
    ))
    assert result.success is True
    assert any("合规" in r for r in result.risk_factors)
    assert any("预算" in r for r in result.risk_factors)


def test_s1_known_clients_list():
    """确认已知客户列表完整性"""
    assert len(S1OpportunityAssessment.KNOWN_CLIENTS) == 17
    assert "飞鹤" in S1OpportunityAssessment.KNOWN_CLIENTS
    assert "a2" in S1OpportunityAssessment.KNOWN_CLIENTS
    assert "极氪" in S1OpportunityAssessment.KNOWN_CLIENTS