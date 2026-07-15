from types import SimpleNamespace
from unittest.mock import patch

from app.agent import create_proposal_workflow


class FakeBriefSkill:
    def run(self, input_data):
        return SimpleNamespace(
            brief={
                "client_name": "飞鹤",
                "industry": "母婴",
                "pain_points": ["搜索承接不足"],
                "goals": ["提升转化"],
                "competitors": ["伊利"],
            },
            qualification={"known_client": True},
            missing_info=[],
            research_mode="fast",
        )


class FakeMissingBriefSkill:
    def run(self, input_data):
        return SimpleNamespace(
            brief={}, qualification={}, missing_info=["客户或品牌名称"], research_mode="full"
        )


class FakeInsightSkill:
    def run(self, input_data):
        return SimpleNamespace(
            decision_map={"strategy_direction": "Feed 激发 + Search 验证"},
            research_data={"mode": "fast"},
            limitations=["快速模式未刷新实时数据"],
        )


class FakeProposalSkill:
    def run(self, input_data):
        return SimpleNamespace(
            proposal_spec={
                "title": "飞鹤小红书营销解决方案",
                "slides": [{"index": index, "title": f"第{index}页"} for index in range(1, 11)],
            },
            matched_cases=[{"case_name": "飞鹤繁星计划"}],
        )


def test_simplified_workflow_stops_at_review_before_export_or_archive():
    with (
        patch("app.agent.BriefSkill", FakeBriefSkill),
        patch("app.agent.InsightSkill", FakeInsightSkill),
        patch("app.agent.ProposalSkill", FakeProposalSkill),
    ):
        result = create_proposal_workflow().invoke({
            "user_input": "飞鹤需要小红书营销方案",
            "requested_research_mode": "auto",
            "messages": [],
            "review_status": "not_started",
        })

    assert result["current_stage"] == "awaiting_review"
    assert result["review_status"] == "awaiting_review"
    assert len(result["proposal_spec"]["slides"]) == 10
    assert "outputs" not in result
    assert "archive_result" not in result


def test_simplified_workflow_stops_when_critical_information_is_missing():
    with patch("app.agent.BriefSkill", FakeMissingBriefSkill):
        result = create_proposal_workflow().invoke({
            "user_input": "帮我做一个方案",
            "requested_research_mode": "auto",
            "messages": [],
            "review_status": "not_started",
        })

    assert result["current_stage"] == "awaiting_input"
    assert result["review_status"] == "awaiting_input"
    assert result["missing_info"] == ["客户或品牌名称"]
    assert "proposal_spec" not in result
