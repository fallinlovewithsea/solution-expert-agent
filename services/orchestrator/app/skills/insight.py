import json
from typing import Literal

from pydantic import BaseModel, Field

from app.skills.base import CoreSkill
from app.tools.research import ResearchTool


class InsightInput(BaseModel):
    brief: dict
    research_mode: Literal["fast", "full"] = "full"


class InsightOutput(BaseModel):
    decision_map: dict = Field(default_factory=dict)
    research_data: dict = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)
    elapsed_ms: float = 0.0


class InsightSkill(CoreSkill[InsightInput, InsightOutput]):
    name = "decision_insight"
    description = "决策洞察：围绕用户决策问题整合行业、搜索、竞品和客户证据"

    def __init__(self, research_tool: ResearchTool | None = None):
        self.research_tool = research_tool or ResearchTool()

    def execute(self, input_data: InsightInput) -> InsightOutput:
        limitations = []
        research_data: dict = {"mode": input_data.research_mode}

        if input_data.research_mode == "full":
            try:
                research_data = self.research_tool.collect(input_data.brief)
            except Exception as exc:
                limitations.append(f"实时研究不可用：{exc}")
                research_data = {"mode": "fallback", "error": str(exc)}
        else:
            limitations.append("快速模式未刷新小红书实时数据，使用现有需求与知识框架")

        decision_map = self._synthesize(input_data.brief, research_data)
        return InsightOutput(
            decision_map=decision_map,
            research_data=research_data,
            limitations=limitations,
        )

    def _synthesize(self, brief: dict, research_data: dict) -> dict:
        prompt = f"""你是小红书消费决策与售前策略专家。基于需求简报和研究数据，生成用户决策地图，只返回 JSON。

需求简报：{brief}
研究数据：{research_data}

必须以“内容发现激发需求、搜索验证、信任构建、转化承接”为主线，输出：
- core_pain_points: 核心业务痛点
- decision_questions: 用户做决定前必须回答的问题
- search_intents: 品牌词、品类词、功效词、场景词、问题词、竞品词
- evidence_requirements: 用户需要的事实、体验和社会证明
- role_strategy: KOL、KOC、KOS、品牌号的角色分工
- conversion_paths: 站内购买、站外电商、私域咨询、线下到店等承接路径
- market_opportunities: 市场机会
- strategy_direction: 总体策略方向
- recommended_modules: 建议采用的方案模块

不得编造研究数据中不存在的数字。"""
        try:
            from app.llm import get_llm

            response = get_llm(task_type="heavy").invoke(prompt)
            return self._parse_json(response.content)
        except Exception:
            return self._fallback_map(brief)

    @staticmethod
    def _parse_json(content: str) -> dict:
        text = content.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            if text.lstrip().startswith("json"):
                text = text.lstrip()[4:].lstrip()
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}

    @staticmethod
    def _fallback_map(brief: dict) -> dict:
        brand = brief.get("client_name", "品牌")
        industry = brief.get("industry", "所属行业")
        return {
            "core_pain_points": brief.get("pain_points", []) or [],
            "decision_questions": [
                f"用户为什么需要关注{industry}相关问题？",
                f"用户为什么应该相信并选择{brand}？",
            ],
            "search_intents": {
                "brand_terms": [brand] if brand else [],
                "category_terms": [brief.get("sub_category") or industry],
                "benefit_terms": [],
                "scenario_terms": [],
                "problem_terms": [],
                "competitor_terms": brief.get("competitors", []) or [],
            },
            "evidence_requirements": ["专业事实", "真实体验", "对比证据", "评论区答疑"],
            "role_strategy": {
                "KOL": "激发需求与建立专业认知",
                "KOC": "提供真实体验和社会证明",
                "KOS": "回答具体问题并承接高意向搜索",
                "品牌号": "沉淀权威产品与活动信息",
            },
            "conversion_paths": ["站内购买", "站外电商", "私域咨询", "线下到店"],
            "market_opportunities": [],
            "strategy_direction": "以用户决策问题为起点，联动 Feed 激发与 Search 验证",
            "recommended_modules": ["内容种草", "搜索承接", "评论区运营", "转化追踪"],
        }
