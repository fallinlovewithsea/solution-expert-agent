from unittest.mock import patch, MagicMock
from app.skills.s4_client_insight import S4ClientInsight, ClientInsightInput


def test_s4_client_insight_instantiation():
    skill = S4ClientInsight()
    assert skill.name == "s4_client_insight"
    assert "客户洞察" in skill.description


def test_s4_client_insight_basic():
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = '{"core_pain_points": ["内容质量差", "导购参与率低"], "market_opportunities": ["品类增长", "KOS空白"], "growth_model_mapping": "KOS矩阵", "strategy_direction": "内容种草+AI赋能", "summary": "飞鹤需提升KOS矩阵效率"}'

    with patch("app.llm.get_llm", return_value=mock_llm):
        mock_llm.invoke.return_value = mock_response
        skill = S4ClientInsight()
        result = skill.run(ClientInsightInput(
            requirement_document={"client_name": "飞鹤", "industry": "母婴"},
            insight_report={"industry_trend": "婴幼奶粉品类增长"}
        ))
        assert result.success is True
        assert len(result.core_pain_points) >= 2
        assert result.growth_model_mapping == "KOS矩阵"