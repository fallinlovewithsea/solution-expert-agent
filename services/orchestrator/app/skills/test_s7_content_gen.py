from app.skills.s7_content_gen import S7ContentGeneration, ContentGenInput


def test_s7_content_generation():
    skill = S7ContentGeneration()
    result = skill.run(ContentGenInput(
        full_proposal={"full_proposal": "test proposal"},
        matched_cases=[],
        brand_assets={},
    ))
    assert result.success is True
    assert result.slide_count == 10
    assert result.slides[0]["title"] == "封面"
    assert result.slides[0]["layout_type"] == "cover"
    assert result.slides[8]["layout_type"] == "timeline"


def test_s7_layout_mapping():
    skill = S7ContentGeneration()
    assert skill._get_layout("封面") == "cover"
    assert skill._get_layout("竞品对标") == "comparison_table"
    assert skill._get_layout("未知页面") == "default"