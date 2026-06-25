from skills.base import BaseSkill, SkillInput, SkillOutput
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
    description = "方案设计：生成品牌增长全案方案，运用恐惧释放映射将每个方案模块对应一个恐惧释放，结合信号博弈设计质量信号"

    PROPOSAL_FRAMEWORK = """
品牌增长全案方案结构（采用三幕式叙事）：
1. 运营策略 + 执行方案
   - 行业洞察（恐惧趋势法：数据→趋势解读→规则变化→先行者）
   - 客户诊断（恐惧推演法：复述→推演结构性压力→归因行业转变）
   - 竞品对标（恐惧对照法：竞品动作→行业共识→你的机会）
   - 增长策略
   - 平台策略
   - 执行方案
2. 工具赋能 + 预算规划
   - 产品能力匹配（每个模块对应一个恐惧释放）
   - 技术架构
   - 预算规划
3. 案例展示（案例名称、行业、相关性、关键指标、参考价值、恐惧释放验证）
4. 实施路径 & 交付物（阶段化+可退出+对标验证+风险预判）
"""

    def execute(self, input_data: ProposalDesignInput) -> ProposalDesignOutput:
        prompt = f"""基于以下信息，按照标准提案框架生成品牌增长全案方案。

要求运用「恐惧释放映射」逻辑组织方案内容：
- 每一个方案模块都必须对应一个恐惧的释放
- 表达公式：恐惧[X] → 方案模块[Y] → 释放效果"你终于可以不用Z了"
- 实施规划的核心目标是交付安全感：阶段化（把不确定性装进可验证的盒子）+ 可退出（每个阶段结束可决定是否继续）+ 对标验证（已发生的案例消除不确定性）+ 风险预判（提前说出客户担忧的事）

**博弈论-信号博弈应用**：
- 方案中应包含"昂贵信号"元素——那些需要真实投入才能做到的交付物（如前期诊断报告、定制化POC、行业洞察白皮书）
- 这些信号能有效区分高质量方案与低质量方案（Spence信号模型）
- 避免过度承诺——过度承诺是廉价信号，长期会损害信誉

**社会学-创新扩散应用**：
- 根据客户在S曲线上的位置调整方案语言：
  - 早期采用者→突出"相对优势"和"先发优势"
  - 后期大众→突出"同行验证"和"可观察性"
- 方案中应明确体现五项关键要素：相对优势、兼容性、复杂性、可试用性、可观察性

**关键红线**：
1. 永远不要将痛点归因于客户个人能力或决策失误——使用行业性语言
2. 方案不是功能的罗列，而是恐惧的释放路径
3. 实施规划不是时间的排期，而是安全感的交付

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
- case_display: 案例展示列表，每项含 case_name, industry, relevance, key_metrics, reference_value
- implementation_path: 实施路径（含 phase, timeline, deliverables）
- full_proposal: 完整方案文本

只返回 JSON。"""

        extracted = self._llm_generate(prompt)

        # 确保 case_display 总是有值
        if not extracted.get("case_display"):
            extracted["case_display"] = self._build_default_cases(input_data)

        # 确保 implementation_path 有值
        if not extracted.get("implementation_path"):
            extracted["implementation_path"] = self._build_default_phases(input_data)

        return ProposalDesignOutput(**extracted)

    def _build_default_cases(self, input_data: ProposalDesignInput) -> List[Dict]:
        """LLM 未生成案例时，构建默认案例展示"""
        req = input_data.requirement_document
        industry = req.get("industry", "")
        cases = []

        if "母婴" in industry:
            cases = [
                {"case_name": "飞鹤繁星计划", "industry": "母婴", "relevance": "高",
                 "key_metrics": "KOS矩阵行业规模第一，5版本迭代",
                 "reference_value": "KOS矩阵规模化 + 搜索占位策略"},
                {"case_name": "a2至初KOS项目", "industry": "母婴", "relevance": "高",
                 "key_metrics": "15天15,000篇笔记，霸屏率70%",
                 "reference_value": "数据驱动复盘 + AB测试方法论"},
            ]
        elif "家居家装" in industry:
            cases = [
                {"case_name": "林氏家居KOS矩阵", "industry": "家居家装", "relevance": "高",
                 "key_metrics": "场景展示效果比单品好3倍",
                 "reference_value": "场景化内容 + KOS代发代管"},
            ]
        elif "汽车" in industry:
            cases = [
                {"case_name": "利星行汽车新媒体", "industry": "汽车", "relevance": "高",
                 "key_metrics": "微信+小红书双平台策略",
                 "reference_value": "双平台矩阵 + 线索转化"},
                {"case_name": "领克汽车KOS", "industry": "汽车", "relevance": "高",
                 "key_metrics": "新能源赛道快速布局",
                 "reference_value": "KOS矩阵 + 用户口碑"},
            ]

        if not cases:
            cases = [
                {"case_name": "飞鹤繁星计划", "industry": "母婴", "relevance": "中",
                 "key_metrics": "KOS矩阵行业规模第一",
                 "reference_value": "方法论参考：AIGC+代发代管+数据闭环"},
            ]

        return cases

    def _build_default_phases(self, input_data: ProposalDesignInput) -> List[Dict]:
        """构建默认实施路径（运用自我效能理论与禀赋效应设计安全感交付）"""
        return [
            {"phase": "Phase 1: 需求诊断与策略对齐", "timeline": "第1-2周",
             "deliverables": "需求诊断报告、增长策略文档",
             "safety_anchor": "测试期结束即自然退出点，可验证可行性后再决策"},  # 禀赋效应：建立初始拥有感
            {"phase": "Phase 2: 内容生产与账号搭建", "timeline": "第3-4周",
             "deliverables": "KOS矩阵搭建、AIGC内容生产",
             "safety_anchor": "对标已验证案例，已有成熟SOP可复用"},  # 替代性经验：自我效能理论
            {"phase": "Phase 3: 上线运营与数据监控", "timeline": "第5-8周",
             "deliverables": "内容发布、数据看板、AB测试",
             "safety_anchor": "阶段一成果已沉淀，投入成本已转化为资产"},  # 禀赋效应：已投入=已拥有
            {"phase": "Phase 4: 数据复盘与策略优化", "timeline": "第9-12周",
             "deliverables": "复盘报告、优化方案、SOP文档",
             "safety_anchor": "整套链路已跑通，可持续复制放大"},
        ]

    def _llm_generate(self, prompt: str) -> dict:
        import json
        from app.llm import get_llm
        llm = get_llm(task_type="heavy")
        response = llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"full_proposal": response.content}