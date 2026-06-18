from app.skills.s6_case_match import S6CaseMatch, CaseMatchInput


def test_s6_match_by_industry():
    """按行业匹配测试"""
    skill = S6CaseMatch()
    result = skill.run(CaseMatchInput(
        industry="母婴",
        customer_type="",
        pain_points=[],
        solution_modules=[],
    ))
    assert result.success is True
    assert len(result.matched_cases) > 0
    # 母婴行业应该有大量匹配
    assert all(c["relevance_score"] >= 0.4 for c in result.matched_cases)


def test_s6_match_multi_dimension():
    """多维度匹配测试"""
    skill = S6CaseMatch()
    result = skill.run(CaseMatchInput(
        industry="母婴",
        customer_type="婴幼儿奶粉",
        pain_points=["搜索占位", "内容质量"],
        solution_modules=["KOS代发代管", "AIGC内容生成"],
    ))
    assert result.success is True
    assert len(result.matched_cases) > 0
    # 飞鹤和a2应该是最高分
    if result.matched_cases:
        top = result.matched_cases[0]
        assert top["relevance_score"] >= 0.4


def test_s6_match_empty():
    """无匹配行业测试"""
    skill = S6CaseMatch()
    result = skill.run(CaseMatchInput(
        industry="不存在的行业",
        customer_type="",
        pain_points=[],
        solution_modules=[],
    ))
    assert result.success is True
    # 仍然可能匹配到一些案例（行业是部分匹配）
    assert result.recommendation != ""


def test_s6_scoring():
    """打分配置测试"""
    skill = S6CaseMatch()
    # 完全匹配行业 + 客户类型 + 痛点 + 方案
    score = skill._calculate_score(
        case={
            "industry": "母婴",
            "customer_type": "婴幼儿奶粉",
            "pain_points": ["搜索占位", "内容质量"],
            "solution_modules": ["KOS代发代管", "AIGC内容生成"],
        },
        industry="母婴",
        customer_type="婴幼儿奶粉",
        pain_points=["搜索占位", "内容质量"],
        solution_modules=["KOS代发代管", "AIGC内容生成"],
    )
    assert score == 1.0


def test_s6_partial_scoring():
    """部分匹配打分测试"""
    skill = S6CaseMatch()
    score = skill._calculate_score(
        case={
            "industry": "母婴",
            "customer_type": "婴幼儿奶粉",
            "pain_points": ["搜索占位"],
            "solution_modules": ["KOS代发代管"],
        },
        industry="母婴",
        customer_type="婴幼儿辅食",
        pain_points=["搜索占位", "内容质量"],
        solution_modules=["KOS代发代管", "数据看板"],
    )
    assert 0.0 < score < 1.0