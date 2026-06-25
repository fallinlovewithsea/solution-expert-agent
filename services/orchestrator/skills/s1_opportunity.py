from skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Optional


class OpportunityInput(SkillInput):
    client_name: str = Field(default="", description="客户名称")
    industry: str = Field(default="", description="行业")
    budget_range: str = Field(default="", description="预算范围")
    initial_requirements: str = Field(description="初步需求描述")


class OpportunityOutput(SkillOutput):
    go_or_no_go: str = ""
    project_type: str = ""
    confidence_score: float = 0.0
    risk_factors: List[str] = Field(default_factory=list)
    recommendation: str = ""


class S1OpportunityAssessment(BaseSkill):
    name = "s1_opportunity"
    description = "商机评估：判断是否跟进 + 项目分类 + 风险评估，锚定客户决策恐惧层级预判推进障碍，运用组织权力结构分析和创新扩散S曲线定位客户"

    # 已知客户列表（从知识库中提取）
    KNOWN_CLIENTS = [
        "飞鹤", "英氏", "金领冠", "a2", "派特生物", "快克",
        "蒙牛", "老庙", "林氏家居", "可画", "董酒", "松达",
        "欧恩贝", "利星行", "领克", "极氪", "弘摩科技",
    ]

    INDUSTRY_RISK = {
        "母婴": ["竞争激烈，KOS矩阵同质化严重", "奶粉配方注册制政策风险"],
        "大健康": ["内容合规审查严格", "用户信任建立周期长"],
        "家居家装": ["决策周期长，转化链路复杂", "场景化内容生产成本高"],
        "汽车": ["新媒体渠道ROI量化困难", "经销商配合度参差不齐"],
        "酒类": ["广告法限制", "小红书平台品类限制"],
        "食品": ["食品安全事件风险", "品类竞争白热化"],
        "珠宝": ["高客单价低频消费", "信任背书要求高"],
        "设计": ["服务标准化难度大", "目标客户群体窄"],
        "技术": ["技术理解门槛高", "B2B决策链路长"],
    }

    def execute(self, input_data: OpportunityInput) -> OpportunityOutput:
        is_known = any(
            c in input_data.initial_requirements
            for c in self.KNOWN_CLIENTS
        )
        industry = input_data.industry or self._extract_industry(
            input_data.initial_requirements
        )

        if is_known:
            confidence = 0.85
            project_type = "custom"
            risks = []
        else:
            confidence = 0.55
            project_type = "general"
            risks = ["新客户，缺乏历史合作数据"]

        # 行业风险评估
        industry_risks = self.INDUSTRY_RISK.get(industry, [])
        risks.extend(industry_risks[:2])

        # 预算评估
        if input_data.budget_range:
            risks.append(f"预算范围：{input_data.budget_range}，需确认方案匹配度")

        # 心理学评估：客户变革意愿度（前景理论-损失厌恶判断）
        loss_aversion_signals = [
            "现状", "稳定", "安全", "风险", "担心", "不放心",
            "之前一直", "习惯了", "不想变", "再看看",
        ]
        challenger_signals = [
            "增长", "突破", "创新", "转型", "升级", "变革",
            "新赛道", "差异化", "机会", "领先",
        ]
        text = input_data.initial_requirements
        la_score = sum(1 for s in loss_aversion_signals if s in text)
        ch_score = sum(1 for s in challenger_signals if s in text)

        if la_score > ch_score:
            risks.append("客户损失厌恶倾向明显，提案需侧重'不做的风险'而非'做的好处'")
        elif ch_score >= 2:
            risks.append("客户变革意愿较高，可运用挑战者销售策略，侧重'增长机会'和'先发优势'")

        # 社会学评估：组织权力结构判断
        decision_maker_signals = ["总监", "VP", "副总裁", "总经理", "CEO", "CMO", "负责人"]
        influencer_signals = ["运营", "经理", "专员", "主管", "市场部"]
        dm_score = sum(1 for s in decision_maker_signals if s in text)
        inf_score = sum(1 for s in influencer_signals if s in text)
        if dm_score > inf_score:
            risks.append("对接角色为决策层，提案应集中在战略价值和ROI论证")
        elif inf_score > 0:
            risks.append("对接角色为执行层/影响层，需同时准备'向上汇报版本'和'执行落地版本'")

        # 社会学评估：创新扩散S曲线定位
        early_adopter_signals = ["试点", "尝试", "先行", "标杆", "引领", "第一步"]
        late_majority_signals = ["成熟", "验证", "稳定", "案例", "对标", "成功经验"]
        ea_score = sum(1 for s in early_adopter_signals if s in text)
        lm_score = sum(1 for s in late_majority_signals if s in text)
        if ea_score >= lm_score:
            risks.append(f"客户偏向早期采用者定位,提案需突出'先发优势'和'相对优势'(Diffusion of Innovations)")
        else:
            risks.append(f"客户偏向后期大众定位,提案需突出'同行验证'和'可观察性'(已有成功案例)")

        go = "GO" if confidence >= 0.5 else "NO_GO"
        recommendation = (
            "建议跟进，可复用已有行业经验和成功案例"
            if is_known
            else "建议跟进，需补充行业调研和需求确认"
        )

        return OpportunityOutput(
            go_or_no_go=go,
            project_type=project_type,
            confidence_score=confidence,
            risk_factors=risks,
            recommendation=recommendation,
        )

    def _extract_industry(self, text: str) -> str:
        """从文本中提取行业"""
        known = ["母婴", "大健康", "家居家装", "汽车", "酒类", "食品", "珠宝", "设计", "技术"]
        for k in known:
            if k in text:
                return k
        return "通用"