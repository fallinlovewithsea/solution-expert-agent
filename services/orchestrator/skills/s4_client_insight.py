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
    description = "客户洞察：整合需求诊断和行业洞察，运用焦虑推演法+矛盾归因法分析核心痛点与增长机会，结合系统思维的杠杆点和反馈循环定位高优干预点"

    def execute(self, input_data: ClientInsightInput) -> ClientInsightOutput:
        req = input_data.requirement_document
        insight = input_data.insight_report

        prompt = f"""基于以下信息，生成客户洞察汇总。要求运用「焦虑推演法」「矛盾归因法」进行分析。
同时运用系统思维的「杠杆点」和「反馈循环」理论定位最高效的干预点。

## 方法框架

### 焦虑推演法
三步穿透：
1. 复述——先准确复述客户主动表达的痛点，建立共鸣
2. 推演——对每个痛点向下推演：**"如果这个行业趋势持续下去，竞争格局会发生什么变化？"**
3. 归因——将所有推演结果汇聚到一个结构性挑战上

### 矛盾归因法
- 找出矛盾：旧规则下的合理投入，在新规则下效率差距正在拉大
- 归因到结构性转变：不是任何人的错误，是行业基础条件变了
- 给出窗口期判断

### 系统思维分析（新增）
**杠杆点定位**（Meadows 12级杠杆点）：
- 客户的痛点停留在哪个杠杆层级？
  - 参数级(价格/数量/速度)→低杠杆，竞争激烈
  - 反馈回路级(信息流/规则)→中杠杆，可建立优势
  - 范式级(行业认知/竞争规则)→高杠杆，提案的核心战场
- 提案应指向更高层级的杠杆点，而非同层竞争

**反馈循环诊断**（Senge系统思考）：
- 识别客户面临问题的反馈回路结构
  - 哪些是增强反馈(雪球效应)在恶化问题？
  - 哪些是平衡反馈(调节效应)在阻止改变？
- 提案的作用：打破旧的平衡反馈，建立新的增强反馈

### 关键红线
**永远不要将痛点归因于客户个人能力或决策失误。**

## 客户需求
{req}

## 行业洞察
{insight}

请分析并返回 JSON：
- core_pain_points: 核心痛点（3-5条，每条标注焦虑层级L1/L2/L3）
- fears: 焦虑穿透分析（三层结构：日常性焦虑/社会性焦虑/基本焦虑）
- structural_contradiction: 结构性矛盾分析（旧规则vs新规则）
- leverage_level: 杠杆点层级诊断（参数级/反馈回路级/范式级），判断客户当前关注的层面
- feedback_loops: 反馈循环分析（识别增强反馈和平衡反馈，提案应作用于哪个回路）
- market_opportunities: 市场机会（3-5条）
- growth_model_mapping: 匹配的增长模型
- strategy_direction: 策略方向建议
- summary: 一句话总结（用焦虑趋势语言表达）

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