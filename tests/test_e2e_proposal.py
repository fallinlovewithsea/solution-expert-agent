import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_llm_response():
    """通用 LLM mock"""
    mock_llm = MagicMock()

    def mock_invoke(prompt):
        response = MagicMock()

        # S2: 需求诊断
        if "沟通记录" in prompt:
            response.content = '{"client_name": "飞鹤", "industry": "母婴", "sub_category": "婴幼儿奶粉", "pain_points": ["内容质量差","KOS矩阵缺失"], "goals": ["行业声量第一","提升转化率"], "budget_range": "200万", "timeline": "6个月", "scope": "KOS矩阵搭建+内容运营", "competitors": ["伊利","君乐宝"], "brand_assets": {}}'
        # S4: 客户洞察
        elif "客户需求" in prompt:
            response.content = '{"core_pain_points": ["内容质量差","KOS矩阵缺失","竞品挤压明显"], "market_opportunities": ["母婴赛道增长红利","成分党内容需求旺盛","KOS矩阵空白机会"], "growth_model_mapping": "母婴KOS种草模型V3", "strategy_direction": "以成分党专业测评切入，搭建KOS矩阵，实现内容种草到转化闭环", "summary": "飞鹤在小红书母婴赛道面临内容质量与矩阵规模双重挑战，需通过专业测评+KOS矩阵实现突破"}'
        # S5: 方案设计
        elif "方案设计" in prompt:
            response.content = '{"proposal_title": "飞鹤母婴KOS矩阵解决方案", "sections": [{"title": "行业洞察", "content": "母婴行业分析"}, {"title": "客户诊断", "content": "飞鹤现状诊断"}, {"title": "解决方案", "content": "KOS矩阵方案"}, {"title": "执行计划", "content": "6个月执行计划"}, {"title": "预算与ROI", "content": "200万预算分配"}], "executive_summary": "飞鹤KOS矩阵方案摘要"}'
        # S7: 内容生成
        elif "内容生成" in prompt:
            response.content = '{"slides": [{"title": "封面", "content": "飞鹤方案"}, {"title": "行业洞察", "content": "母婴行业"}, {"title": "客户诊断", "content": "飞鹤诊断"}, {"title": "解决方案", "content": "KOS矩阵"}, {"title": "执行计划", "content": "6个月计划"}, {"title": "预算", "content": "200万"}, {"title": "案例", "content": "成功案例"}, {"title": "团队", "content": "执行团队"}, {"title": "预期效果", "content": "ROI预测"}, {"title": "下一步", "content": "行动计划"}], "slide_count": 10}'
        # S3/XHS LLM 分析
        elif "小红书数据分析专家" in prompt:
            response.content = '{"content_themes": [{"theme": "产品测评", "ratio": 0.35}, {"theme": "使用教程", "ratio": 0.25}, {"theme": "种草推荐", "ratio": 0.20}], "audience_interest": ["产品成分与安全性", "性价比对比", "使用效果真实反馈"], "hot_elements": "封面采用对比图+大字标题", "sentiment_overview": "正面 65% / 中性 25% / 负面 10%", "content_gap": ["专业深度测评内容不足", "KOS矩阵账号密度低"], "recommended_angles": ["打造成分党专业测评人设", "高频互动问答提升信任"]}'
        else:
            response.content = "{}"

        return response

    mock_llm.invoke = mock_invoke
    return mock_llm


@pytest.mark.e2e
@patch("app.skills.s3_industry_insight.XHSCollector")
def test_full_proposal_workflow(mock_collector_class, mock_llm_response):
    """端到端测试：完整提案生成流程（含 S3 行业洞察）"""
    from unittest.mock import MagicMock

    # Mock XHSCollector 避免真实 HTTP 请求
    mock_collector = MagicMock()
    mock_collector_class.return_value = mock_collector

    mock_collector.search_industry.return_value = {
        "keywords": ["宝宝奶粉怎么选"],
        "notes": [],
        "analysis": {
            "note_count": 25,
            "total_likes": 12500,
            "content_themes": [{"theme": "产品测评", "ratio": 0.35}],
            "audience_interest": ["产品成分与安全性"],
            "hot_elements": "封面采用对比图",
            "sentiment_overview": "正面 65% / 中性 25% / 负面 10%",
            "content_gap": ["专业深度测评内容不足"],
            "recommended_angles": ["打造成分党专业测评人设"],
        },
        "collected_at": "2026-06-18T00:00:00",
    }

    mock_collector.search_competitor.return_value = {
        "brand": "伊利",
        "notes": [],
        "comments": [],
        "analysis": {
            "note_count": 40,
            "content_themes": [{"theme": "达人种草", "ratio": 0.40}],
            "kos_estimated_scale": 80,
            "publishing_frequency": "月均 60 篇",
            "engagement_rate": "3.2%",
            "strength": "内容矩阵稳定",
            "weakness": "内容同质化明显",
        },
        "collected_at": "2026-06-18T00:00:00",
    }

    mock_collector.search_client.return_value = {
        "account": "飞鹤",
        "notes": [],
        "comments": [],
        "analysis": {
            "note_count": 15,
            "account_health_score": 55,
            "content_quality_score": 45,
            "sentiment": {"positive": 0.65, "neutral": 0.25, "negative": 0.10},
            "key_issues": ["内容更新频率不稳定"],
            "improvement_areas": ["建立内容日历"],
        },
        "collected_at": "2026-06-18T00:00:00",
    }

    with patch("app.llm.get_llm", return_value=mock_llm_response):
        from app.agent import create_proposal_workflow

        workflow = create_proposal_workflow()
        initial_state = {
            "user_input": "飞鹤，母婴行业，想做小红书KOS矩阵，预算200万，6个月内完成",
            "requirement_document": {},
            "insight_report": {},
            "industry_analysis": {},
            "competitor_analysis": [],
            "client_diagnosis": {},
            "growth_analysis": {},
            "client_insight": {},
            "full_proposal": {},
            "matched_cases": [],
            "slides": [],
            "brand_assets": {},
            "slides_url": "",
            "docx_url": "",
            "pptx_path": "",
            "messages": [],
            "current_stage": "init",
            "needs_human_review": False,
        }

        result = workflow.invoke(initial_state)

        # 验证最终状态
        assert result["current_stage"] == "s8_format_output"
        assert result["needs_human_review"] is True
        assert len(result["messages"]) >= 6  # S2, S3, S4, S5, S7, S8, human_review

        # 验证各阶段消息
        messages = result["messages"]
        assert any("[S2]" in m for m in messages), "应包含 S2 需求诊断"
        assert any("[S3]" in m for m in messages), "应包含 S3 行业洞察"
        assert any("[S4]" in m for m in messages), "应包含 S4 客户洞察"
        assert any("[S5]" in m for m in messages), "应包含 S5 方案设计"
        assert any("[S7]" in m for m in messages), "应包含 S7 内容生成"
        assert any("[S8]" in m for m in messages), "应包含 S8 格式输出"
        assert any("[审核]" in m for m in messages), "应包含审核节点"

        # 验证 S3 输出
        assert result["insight_report"] != {}, "S3 应输出 insight_report"
        assert "industry_analysis" in result["insight_report"]
        assert "competitor_analysis" in result["insight_report"]
        assert "client_diagnosis" in result["insight_report"]
        assert "growth_analysis" in result["insight_report"]

        # 验证产出
        assert result["slides_url"] != ""
        assert result["pptx_path"] == "/data/exports/output.pptx"


@pytest.mark.unit
def test_s3_industry_insight_skill():
    """单元测试：S3 行业洞察"""
    from unittest.mock import patch, MagicMock

    mock_collector = MagicMock()
    mock_collector.search_industry.return_value = {
        "keywords": ["宝宝奶粉怎么选"],
        "notes": [
            {"note_id": "n1", "title": "宝宝奶粉测评", "likes": 500, "comments": 50, "collects": 100, "shares": 20},
            {"note_id": "n2", "title": "奶粉推荐", "likes": 300, "comments": 30, "collects": 80, "shares": 15},
        ],
        "analysis": {
            "note_count": 25,
            "total_likes": 12500,
            "content_themes": [{"theme": "产品测评", "ratio": 0.35}],
            "audience_interest": ["产品成分与安全性"],
            "hot_elements": "封面采用对比图",
            "sentiment_overview": "正面 65%",
            "content_gap": ["专业深度测评内容不足"],
            "recommended_angles": ["打造成分党专业测评人设"],
        },
    }

    mock_collector.search_competitor.return_value = {
        "brand": "伊利",
        "notes": [
            {"note_id": "c1", "title": "伊利奶粉怎么样", "likes": 400, "comments": 40, "collects": 60, "shares": 10},
        ],
        "comments": [{"content": "这个真的很好用！", "likes": 5}],
        "analysis": {
            "content_themes": [{"theme": "达人种草", "ratio": 0.40}],
            "kos_estimated_scale": 80,
            "strength": "内容矩阵稳定",
            "weakness": "内容同质化",
        },
    }

    mock_collector.search_client.return_value = {
        "account": "飞鹤",
        "notes": [
            {"note_id": "x1", "title": "飞鹤新品体验", "likes": 200, "comments": 20, "collects": 30, "shares": 5},
        ],
        "comments": [],
        "analysis": {
            "account_health_score": 55,
            "content_quality_score": 45,
            "sentiment": {"positive": 0.65, "neutral": 0.25, "negative": 0.10},
            "key_issues": ["内容更新频率不稳定"],
            "improvement_areas": ["建立内容日历"],
        },
    }

    with patch(
        "app.skills.s3_industry_insight.XHSCollector",
        return_value=mock_collector,
    ):
        from skills.s3_industry_insight import S3IndustryInsight, IndustryInsightInput

        skill = S3IndustryInsight()
        result = skill.run(IndustryInsightInput(
            industry="母婴",
            category="婴幼儿奶粉",
            competitors=["伊利"],
            client_name="飞鹤",
        ))

        assert result.success is True
        assert result.industry_analysis["note_count"] == 2
        assert result.industry_analysis["content_themes"][0]["theme"] == "产品测评"
        assert len(result.competitor_analysis) == 1
        assert result.competitor_analysis[0]["name"] == "伊利"
        assert result.competitor_analysis[0]["strength"] == "内容矩阵稳定"
        assert result.client_diagnosis["account_health_score"] == 55
        assert result.client_diagnosis["key_issues"] == ["内容更新频率不稳定"]
        assert "宝宝奶粉" in result.summary


@pytest.mark.unit
def test_xhs_collector_dev_mode():
    """单元测试：XHS 采集器开发模式"""
    import os
    os.environ["XHS_DEV_MODE"] = "true"

    # 重新导入以应用环境变量
    import importlib
    from skills import xhs_collector
    importlib.reload(xhs_collector)

    collector = xhs_collector.XHSCollector()
    assert collector.DEV_MODE is True

    # 行业采集
    result = collector.search_industry(["宝宝奶粉"])
    assert "notes" in result
    assert "analysis" in result
    assert len(result["notes"]) == 25
    assert "content_themes" in result["analysis"]
    assert len(result["analysis"]["content_themes"]) == 5

    # 竞品采集
    result = collector.search_competitor("伊利")
    assert result["brand"] == "伊利"
    assert len(result["notes"]) >= 20
    assert "comments" in result
    assert "analysis" in result
    assert "kos_estimated_scale" in result["analysis"]

    # 客户采集
    result = collector.search_client("飞鹤")
    assert result["account"] == "飞鹤"
    assert len(result["notes"]) >= 8
    assert "comments" in result
    assert "analysis" in result
    assert "account_health_score" in result["analysis"]

    # 清理
    del os.environ["XHS_DEV_MODE"]