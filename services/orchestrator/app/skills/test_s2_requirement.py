from unittest.mock import patch, MagicMock
from app.skills.s2_requirement import S2RequirementDiagnosis, RequirementInput, RequirementOutput


def test_s2_input_output_types():
    skill = S2RequirementDiagnosis()
    assert skill.name == "s2_requirement_diagnosis"
    assert "需求诊断" in skill.description


def test_s2_requirement_diagnosis_basic():
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = '{"client_name": "飞鹤", "industry": "母婴", "sub_category": "婴幼儿奶粉", "pain_points": ["内容质量差"], "goals": ["行业声量第一"], "budget_range": "200万", "timeline": "6个月", "scope": "KOS矩阵", "competitors": ["伊利"], "brand_assets": {}}'

    with patch("app.llm.get_llm", return_value=mock_llm):
        mock_llm.invoke.return_value = mock_response
        skill = S2RequirementDiagnosis()
        result = skill.run(RequirementInput(
            communication_records="飞鹤，母婴行业，想做小红书KOS矩阵，预算200万"
        ))
        assert result.success is True
        assert result.client_name == "飞鹤"
        assert result.industry == "母婴"
        assert len(result.pain_points) >= 1
        assert isinstance(result.missing_info, list)