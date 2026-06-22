from skills.s7_content_gen import S7ContentGeneration, ContentGenInput


def test_s7_content_generation():
    skill = S7ContentGeneration()
    result = skill.run(ContentGenInput(
        full_proposal={"full_proposal": "test proposal"},
        matched_cases=[],
        brand_assets={"brand_name": "飞鹤", "industry": "母婴"},
    ))
    assert result.success is True
    assert result.slide_count == 10
    assert result.slides[0]["layout_type"] == "cover"
    assert result.slides[8]["layout_type"] == "timeline"
    # 标题应包含品牌名
    assert "飞鹤" in result.slides[0]["title"]
    # 内容不应为空
    assert result.slides[0]["content"] != ""


def test_s7_layout_mapping():
    skill = S7ContentGeneration()
    assert skill._get_layout("封面") == "cover"
    assert skill._get_layout("竞品对标") == "comparison_table"
    assert skill._get_layout("未知页面") == "default"


def test_s7_empty_brand():
    """空品牌名测试"""
    skill = S7ContentGeneration()
    result = skill.run(ContentGenInput(
        full_proposal={},
        matched_cases=[],
        brand_assets={},
    ))
    assert result.success is True
    assert result.slide_count == 10


def test_s7_with_matched_cases():
    """带匹配案例的内容生成"""
    skill = S7ContentGeneration()
    result = skill.run(ContentGenInput(
        full_proposal={},
        matched_cases=[
            {"case_name": "飞鹤繁星计划", "industry": "母婴", "relevance_score": 0.9,
             "match_reason": "行业匹配", "key_metrics": "KOS矩阵行业第一"},
        ],
        brand_assets={"brand_name": "测试品牌", "industry": "母婴"},
    ))
    assert result.success is True
    # 案例展示页应包含匹配的案例
    case_slide = [s for s in result.slides if s["section"] == "案例展示"]
    assert len(case_slide) == 1
    assert "飞鹤" in case_slide[0]["content"]