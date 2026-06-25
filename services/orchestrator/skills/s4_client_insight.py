from skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Dict


class ClientInsightInput(SkillInput):
    requirement_document: dict = Field(description="S2 需求诊断输出")
    insight_report: dict = Field(description="S3 行业洞察输出")


class ClientInsightOutput(SkillOutput):
    core_pain_points: List[str] = Field(default_factory=list)
    market_opportunities: List[str] = Field(default_factory=list)
    growth_model_mapping: str = ""
    strategy_direction: str = ""
    summary: str = ""


class S4ClientInsight(BaseSkill):
    name = "s4_client_insight"
    description = "客户洞察：整合需求诊断和行业洞察，运用恐惧推演法+矛盾归因法分析核心痛点与增长机会"

    def execute(self, input_data: ClientInsightInput) -> ClientInsightOutput:
        req = input_data.requirement_document
        insight = input_data.insight_report

        prompt = f"""基于以下信息，生成客户洞察汇总。要求运用「恐惧推演法」和「矛盾归因法」进行分析。

## 方法框架

### 恐惧推演法
三步穿透：
1. 复述——先准确复述客户主动表达的痛点，建立共鸣
2. 推演——对每个痛点向下推演：**"如果这个行业趋势持续下去，竞争格局会发生什么变化？"** 推演的核心不是描述"你会遇到什么麻烦"，而是描述"这个行业正在经历什么转变"
3. 归因——将所有推演结果汇聚到一个结构性挑战上，需同时满足三个条件：行业性的、解释为什么所有痛点同时出现、指向需要被回应的新竞争规则

### 矛盾归因法
- 找出矛盾：旧规则下的合理投入，在新规则下效率差距正在拉大
- 归因到结构性转变：不是任何人的错误，是行业基础条件变了
- 给出窗口期判断：转变正在进行，窗口还在，但需要行动

### 关键红线
**永远不要将痛点归因于客户个人能力或决策失误。** 痛点描述的措辞应该指向"行业变化"、"模式局限"、"旧工具不够用"，而不是"你做得不好"。使用行业性语言：不说"你的KOL成本太高"说"流量成本持续上涨"；不说"你无法证明ROI"说"效果归因链路不完整"。

## 客户需求
{req}

## 行业洞察
{insight}

请分析并返回 JSON：
- core_pain_points: 核心痛点（3-5条，每条标注恐惧层级L1/L2/L3）
- fears: 恐惧穿透分析（三层结构：日常性恐惧/社会性恐惧/基本恐惧）
- structural_contradiction: 结构性矛盾分析（旧规则vs新规则）
- market_opportunities: 市场机会（3-5条）
- growth_model_mapping: 匹配的增长模型
- strategy_direction: 策略方向建议
- summary: 一句话总结（用恐惧趋势语言表达）

只返回 JSON。"""

        extracted = self._llm_analyze(prompt)
        return ClientInsightOutput(**extracted)

    def _llm_analyze(self, prompt: str) -> dict:
        import json
        from app.llm import get_llm
        llm = get_llm(task_type="heavy")
        response = llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {}