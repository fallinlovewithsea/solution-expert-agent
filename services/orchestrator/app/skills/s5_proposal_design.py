from app.skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Optional, Dict


class ProposalDesignInput(SkillInput):
    client_insight: dict = Field(description="S4 客户洞察输出")
    insight_report: dict = Field(description="S3 行业洞察输出")
    requirement_document: dict = Field(description="S2 需求文档")


class ProposalDesignOutput(SkillOutput):
    operation_strategy: Dict = Field(default_factory=dict)
    tool_empowerment: Dict = Field(default_factory=dict)
    case_display: List[Dict] = Field(default_factory=list)
    implementation_path: List[Dict] = Field(default_factory=list)
    full_proposal: str = ""


class S5ProposalDesign(BaseSkill):
    name = "s5_proposal_design"
    description = "方案设计：生成品牌增长全案方案"

    PROPOSAL_FRAMEWORK = """
品牌增长全案方案结构：
1. 运营策略 + 执行方案
   - 行业洞察
   - 客户诊断
   - 竞品对标
   - 增长策略
   - 平台策略
   - 执行方案
2. 工具赋能 + 预算规划
   - 产品能力匹配
   - 技术架构
   - 预算规划
3. 案例展示
4. 实施路径 & 交付物
"""

    def execute(self, input_data: ProposalDesignInput) -> ProposalDesignOutput:
        prompt = f"""基于以下信息，按照标准提案框架生成品牌增长全案方案。

## 标准提案框架
{self.PROPOSAL_FRAMEWORK}

## 客户洞察
{input_data.client_insight}

## 行业洞察
{input_data.insight_report}

## 需求文档
{input_data.requirement_document}

请生成完整的品牌增长全案方案，返回 JSON：
- operation_strategy: 运营策略+执行方案（含 industry_insight, client_diagnosis, competitor_benchmark, growth_strategy, platform_strategy, execution_plan）
- tool_empowerment: 工具赋能+预算规划（含 product_capability, tech_architecture, budget_planning）
- implementation_path: 实施路径（含 phase, timeline, deliverables）
- full_proposal: 完整方案文本

只返回 JSON。"""

        extracted = self._llm_generate(prompt)
        return ProposalDesignOutput(**extracted)

    def _llm_generate(self, prompt: str) -> dict:
        import json
        from app.llm import get_llm
        llm = get_llm(task_type="heavy")
        response = llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"full_proposal": response.content}