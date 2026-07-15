import json
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

import app

fake_llm_module = types.ModuleType("app.llm")
fake_llm_module.get_llm = MagicMock()
sys.modules["app.llm"] = fake_llm_module
setattr(app, "llm", fake_llm_module)

from app.skills.brief import BriefInput, BriefSkill
from app.skills.insight import InsightInput, InsightSkill
from app.skills.proposal import ProposalInput, ProposalSkill


def mock_llm(content: dict):
    llm = MagicMock()
    llm.invoke.return_value.content = json.dumps(content, ensure_ascii=False)
    return llm


class FakeResearchTool:
    def collect(self, brief: dict) -> dict:
        return {"industry_analysis": {"note_count": 10}, "client": brief["client_name"]}


class FakeCaseTool:
    def search(self, brief: dict, decision_map: dict) -> list[dict]:
        return [{"case_name": "飞鹤繁星计划", "industry": "母婴", "relevance_score": 0.9}]


class SimplifiedWorkflowTests(unittest.TestCase):
    def test_brief_skill_selects_fast_mode_for_known_client(self):
        extracted = {
            "client_name": "飞鹤",
            "industry": "母婴",
            "sub_category": "奶粉",
            "decision_problem": "用户如何验证奶粉选择",
            "pain_points": ["搜索承接不足"],
            "goals": ["提升搜索转化"],
            "budget_range": "200万",
            "timeline": "6个月",
            "scope": "小红书全案",
            "competitors": [],
            "output_formats": ["pptx"],
            "brand_assets": {},
        }
        with patch("app.llm.get_llm", return_value=mock_llm(extracted)):
            result = BriefSkill().run(BriefInput(user_input="飞鹤需要小红书方案"))

        self.assertTrue(result.ready_for_proposal)
        self.assertEqual(result.research_mode, "fast")
        self.assertTrue(result.qualification["known_client"])

    def test_brief_skill_stops_for_critical_missing_info(self):
        extracted = {
            "client_name": "",
            "industry": "",
            "decision_problem": "",
            "pain_points": [],
            "goals": [],
            "scope": "",
        }
        with patch("app.llm.get_llm", return_value=mock_llm(extracted)):
            result = BriefSkill().run(BriefInput(user_input="帮我做一个方案"))

        self.assertFalse(result.ready_for_proposal)
        self.assertIn("客户或品牌名称", result.missing_info)
        self.assertIn("所属行业", result.missing_info)

    def test_insight_skill_uses_research_tool_only_in_full_mode(self):
        decision_map = {
            "core_pain_points": ["信任不足"],
            "decision_questions": ["为什么选择这个品牌"],
            "search_intents": {"brand_terms": ["飞鹤"]},
            "evidence_requirements": ["真实体验"],
            "role_strategy": {"KOS": "承接搜索"},
            "conversion_paths": ["站内购买"],
            "market_opportunities": ["搜索验证"],
            "strategy_direction": "Feed + Search",
            "recommended_modules": ["搜索承接"],
        }
        with patch("app.llm.get_llm", return_value=mock_llm(decision_map)):
            result = InsightSkill(FakeResearchTool()).run(InsightInput(
                brief={"client_name": "飞鹤", "industry": "母婴"},
                research_mode="full",
            ))

        self.assertEqual(result.decision_map["strategy_direction"], "Feed + Search")
        self.assertEqual(result.research_data["client"], "飞鹤")

    def test_proposal_skill_creates_one_valid_proposal_spec(self):
        sections = ProposalSkill.SLIDE_SECTIONS
        spec = {
            "title": "飞鹤小红书营销方案",
            "executive_summary": "摘要",
            "strategy": {},
            "execution_plan": [],
            "product_mapping": [],
            "budget_plan": "200万",
            "implementation_path": [],
            "slides": [
                {"index": index, "section": section, "title": section, "layout_type": "default", "content": section}
                for index, section in enumerate(sections, 1)
            ],
            "assumptions": [],
        }
        with patch("app.llm.get_llm", return_value=mock_llm(spec)):
            result = ProposalSkill(FakeCaseTool()).run(ProposalInput(
                brief={"client_name": "飞鹤", "industry": "母婴"},
                decision_map={"core_pain_points": ["信任不足"]},
            ))

        self.assertEqual(len(result.proposal_spec["slides"]), 10)
        self.assertEqual(result.proposal_spec["matched_cases"][0]["case_name"], "飞鹤繁星计划")


if __name__ == "__main__":
    unittest.main()
