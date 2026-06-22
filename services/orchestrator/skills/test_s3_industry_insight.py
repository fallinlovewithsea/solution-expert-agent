from skills.s3_industry_insight import S3IndustryInsight, IndustryInsightInput


def test_s3_industry_keywords():
    """行业关键词映射测试"""
    skill = S3IndustryInsight()
    assert "母婴" in skill.INDUSTRY_KEYWORDS
    assert "奶粉" in skill.INDUSTRY_KEYWORDS["母婴"]
    assert "汽车" in skill.INDUSTRY_KEYWORDS
    assert "新能源" in skill.INDUSTRY_KEYWORDS["汽车"]


def test_s3_execute_basic():
    """基本执行测试"""
    skill = S3IndustryInsight()
    result = skill.run(IndustryInsightInput(
        industry="母婴",
        category="奶粉",
        competitors=["飞鹤", "英氏"],
        client_name="金领冠",
    ))
    assert result.success is True
    assert result.summary != ""
    assert "母婴" in result.summary


def test_s3_unknown_industry():
    """未知行业使用通用关键词"""
    skill = S3IndustryInsight()
    result = skill.run(IndustryInsightInput(
        industry="未知行业XYZ",
        competitors=[],
        client_name="",
    ))
    assert result.success is True


def test_s3_sentiment_analysis():
    """情感分析测试"""
    comments = [
        {"content": "这个产品很好用，推荐"},
        {"content": "一般般吧"},
        {"content": "太差了，后悔买了"},
    ]
    sentiment = S3IndustryInsight._sentiment_from_comments(comments)
    assert sentiment in ("正面为主", "负面为主", "中性")


def test_s3_empty_competitors():
    """空竞品列表测试"""
    skill = S3IndustryInsight()
    result = skill.run(IndustryInsightInput(
        industry="母婴",
        category="",
        competitors=[],
        client_name="",
    ))
    assert result.success is True
    assert result.competitor_analysis == []