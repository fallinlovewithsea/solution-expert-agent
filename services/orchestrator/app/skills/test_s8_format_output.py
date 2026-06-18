from app.skills.s8_format_output import S8FormatOutput, FormatOutputInput


def test_s8_brand_colors():
    """品牌色映射测试"""
    assert S8FormatOutput._brand_color("飞鹤") == "#1a5276"
    assert S8FormatOutput._brand_color("a2") == "#7b2d8b"
    assert S8FormatOutput._brand_color("未知品牌") == "#1a1a2e"


def test_s8_bg_colors():
    """背景色布局映射测试"""
    skill = S8FormatOutput()
    assert skill._get_bg_color("cover") == "#1a1a2e"
    assert skill._get_bg_color("comparison_table") == "#ffffff"
    assert skill._get_bg_color("case_card") == "#fff8f0"
    assert skill._get_bg_color("unknown") == "#ffffff"


def test_s8_execute_without_lark():
    """无 lark-cli 环境降级测试"""
    skill = S8FormatOutput()
    result = skill.run(FormatOutputInput(
        slides=[{"title": "test", "content": "content", "layout_type": "cover"}],
        brand_assets={},
        brand_name="飞鹤",
        output_formats=["pptx"],
    ))
    assert result.success is True


def test_s8_slide_xml_generation():
    """Slide XML 生成测试"""
    skill = S8FormatOutput()
    xml = skill._build_slide_xml({
        "title": "测试标题",
        "content": "测试内容",
        "layout_type": "cover",
    }, "飞鹤")
    assert "测试标题" in xml
    assert "测试内容" in xml
    assert "#1a5276" in xml  # 飞鹤品牌色


def test_s8_docx_content():
    """Docx 内容构建测试"""
    skill = S8FormatOutput()
    content = skill._build_docx_content(
        [{"title": "页面1", "content": "内容1"}],
        "飞鹤",
        "测试方案",
    )
    assert "飞鹤" in content
    assert "测试方案" in content
    assert "页面1" in content