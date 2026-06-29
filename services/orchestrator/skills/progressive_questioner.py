"""
渐进式提问器 — 引导使用人员逐步完成方案构建

设计原则：
- 每次只问一个问题，每次推进一个认同层级
- 问题顺序 = 认同层级递进 L1→L2→L3→L4→L5
- 根据客户认知成熟度自动调整提问深度
- 每个阶段结束时判断是否通过，未通过则补充信息再问
"""

from skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Dict, Optional
from enum import Enum


class QuestionPhase(Enum):
    """提问阶段 — 对应认同层级"""
    L1_FORM = "L1_形式认同"       # 收集基础信息，建立专业形象
    L2_EXPRESS = "L2_表达认同"     # 理解客户处境，建立沟通共鸣
    L3_DIAGNOSE = "L3_诊断认同"    # 深入痛点，焦虑推演
    L4_SOLUTION = "L4_方案认同"    # 匹配方案，设计路径
    L5_BELIEF = "L5_信念认同"     # 闭合决策，锚定未来


class ProgressiveQuestionerInput(SkillInput):
    """渐进式提问输入"""
    user_response: str = Field(default="", description="用户对上一轮问题的回答")
    current_phase: str = Field(default="L1_FORM", description="当前阶段")
    collected_data: Dict = Field(default_factory=dict, description="已收集的数据")
    client_maturity: str = Field(default="unknown", description="客户认知成熟度")
    stuck_level: Optional[str] = Field(default=None, description="如果卡住了，是哪一级")


class ProgressiveQuestionerOutput(SkillOutput):
    """渐进式提问输出"""
    next_question: str = ""                          # 下一个问题
    phase: str = ""                                  # 当前在哪个阶段
    need_scrutiny: bool = False                      # 此阶段是否通过
    scrutiny_comment: str = ""                       # 阶段通过/卡住的评估
    collected_data: Dict = Field(default_factory=dict)
    ready_for_proposal: bool = False                 # 是否条件完备可生成方案
    proposal_brief: str = ""                         # 方案摘要（条件完备时生成）


class ProgressiveQuestioner(BaseSkill):
    """渐进式提问器 — 引导方案构建"""
    name = "progressive_questioner"
    description = "渐进式提问：按认同层级L1→L5逐步收集信息，引导使用人员完成方案构建"

    # ── 各阶段的问题库 ─────────────────────────────

    PHASE_QUESTIONS = {
        QuestionPhase.L1_FORM: [
            "请告诉我客户品牌名称和所属行业",
            "你接触的是客户的什么角色（决策者/执行者/采购者）？",
            "客户是第一次做小红书营销，还是已经有矩阵在运营了？",
            "这次合作的预算是哪个范围？（50万以下/50-100万/100-300万/300万以上）",
            "项目有时间限制吗？预计什么时候需要看到结果？",
        ],
        QuestionPhase.L2_EXPRESS: [
            "客户最近的沟通中，有没有提到什么特别焦虑的点？比如"竞品都在投，我们不投怕落后"？",
            "客户在行业内处于什么位置——领先者、追赶者、还是新进入者？",
            "客户之前有没有尝试过类似的KOS或AIGC方案？效果如何？",
        ],
        QuestionPhase.L3_DIAGNOSE: [
            "客户最核心的痛点是什么？请用他们自己的话来描述",
            "如果这个痛点不解决，6个月后客户的生意会怎么样？",
            "行业内有没有其他人已经解决了这个问题？是什么让他们跑通了而客户没有？",
            "对于这个痛点，客户内部有没有不同意见？主要是谁在推动，谁在犹豫？",
        ],
        QuestionPhase.L4_SOLUTION: [
            "客户最关注的是哪个业务线？（AIGC/KOS托管/CID投放/评论区/SEO/用户运营）",
            "客户对"把账号交给我们代管"有过什么顾虑？",
            "你倾向推荐的方案组合是什么？为什么选这个组合？",
            "客户对方案验证有什么期待？他需要看到什么样的数据，就会决定推进？",
        ],
        QuestionPhase.L5_BELIEF: [
            "客户跟你聊得最多的是什么话题？是价格、方案细节，还是行业趋势？",
            "如果这个项目跑通了，客户在组织内会获得什么？这件事对他个人重要吗？",
            "你觉得客户现在的状态是'我还要再想想'还是'我拿什么说服老板'？",
            "下一步你计划怎么推动？需要什么支持？",
        ],
    }

    # ── 各阶段的通过标准 ──────────────────────────

    SCRUTINY_RULES = {
        QuestionPhase.L1_FORM: {
            "通过条件": ["已收集客户名称和行业", "已确认对接角色"],
            "卡住信号": ["只看资料", "反复问价格", "不回复"],
        },
        QuestionPhase.L2_EXPRESS: {
            "通过条件": ["已了解客户的焦虑点和行业位置"],
            "卡住信号": ["礼貌但不追问", "不主动分享信息", "只说官话"],
        },
        QuestionPhase.L3_DIAGNOSE: {
            "通过条件": ["客户对痛点描述产生了共鸣", "客户确认了'这个行业都在面临'的问题"],
            "卡住信号": ["你说得对，但情况不太一样", "我们这个行业特殊", "你说得有道理不过..."],
        },
        QuestionPhase.L4_SOLUTION: {
            "通过条件": ["客户对方案路径表示认可", "客户开始讨论具体执行细节"],
            "卡住信号": ["反复讨论价格", "要求更多案例", "你再出一版看看"],
        },
        QuestionPhase.L5_BELIEF: {
            "通过条件": ["客户愿意推进下一阶段", "客户讨论了内部的推广计划"],
            "卡住信号": ["我再跟老板商量一下", "我们再内部讨论讨论"],
        },
    }

    # ── 阶段流转顺序 ──────────────────────────────

    PHASE_ORDER = [
        QuestionPhase.L1_FORM,
        QuestionPhase.L2_EXPRESS,
        QuestionPhase.L3_DIAGNOSE,
        QuestionPhase.L4_SOLUTION,
        QuestionPhase.L5_BELIEF,
    ]

    def execute(self, input_data: ProgressiveQuestionerInput) -> ProgressiveQuestionerOutput:
        current_phase = input_data.current_phase
        collected = input_data.collected_data
        response = input_data.user_response.strip()

        # 保存用户回答
        if response:
            collected[f"q_{current_phase}_{len(collected)}"] = response

        # 确定当前阶段
        try:
            phase = QuestionPhase(current_phase)
        except ValueError:
            phase = QuestionPhase.L1_FORM

        # 获取当前阶段的问题列表和已问索引
        questions = self.PHASE_QUESTIONS[phase]
        q_index = sum(1 for k in collected if k.startswith(f"q_{phase.value}"))

        # 判断是否还有问题可问
        need_scrutiny = False
        scrutiny_comment = ""
        next_question = ""
        next_phase = current_phase

        # 检查是否到了需要审查的阶段节点
        # 每个阶段问 2-3 个问题后检查是否有足够的回答通过
        scrutiny_threshold = min(3, len(questions))
        if q_index >= scrutiny_threshold:
            need_scrutiny = True
            scrutiny_comment = self._evaluate_phase(collected, phase)

        # 确定下一个问题
        if q_index < len(questions) and not need_scrutiny:
            # 继续当前阶段
            next_question = questions[q_index]
        elif need_scrutiny:
            # 检查是否通过当前阶段
            passed = self._check_phase_pass(collected, phase)
            if passed:
                # 推进到下一阶段
                rules = self.SCRUTINY_RULES[phase]
                scrutiny_comment = rules.get("通过条件", ["阶段通过"])[0]
                next_idx = self.PHASE_ORDER.index(phase) + 1
                if next_idx < len(self.PHASE_ORDER):
                    next_phase = self.PHASE_ORDER[next_idx].value
                    next_question = self.PHASE_QUESTIONS[self.PHASE_ORDER[next_idx]][0]
                else:
                    # 全部阶段完成
                    next_question = ""
                    scrutiny_comment = "全部阶段通过，可以生成方案了"
            else:
                # 卡在当前阶段
                rules = self.SCRUTINY_RULES[phase]
                scrutiny_comment = f"当前阶段尚未通过。卡住信号：{rules.get('卡住信号', ['需要更多信息'])[0]}。建议补充以下信息：{questions[q_index] if q_index < len(questions) else questions[-1]}"
                next_question = questions[min(q_index, len(questions)-1)]
        else:
            # 所有问题都问完了
            need_scrutiny = True
            scrutiny_comment = "当前阶段信息收集完毕"

        # 判断是否可以生成方案
        ready = self._check_ready(collected, phase)

        proposal_brief = ""
        if ready:
            proposal_brief = self._build_proposal_brief(collected)

        return ProgressiveQuestionerOutput(
            next_question=next_question,
            phase=next_phase,
            need_scrutiny=need_scrutiny,
            scrutiny_comment=scrutiny_comment,
            collected_data=collected,
            ready_for_proposal=ready,
            proposal_brief=proposal_brief,
        )

    # ── 阶段评估 ──────────────────────────────────

    def _evaluate_phase(self, collected: Dict, phase: QuestionPhase) -> str:
        """评估当前阶段收集的信息"""
        answers = [v for k, v in collected.items() if k.startswith(f"q_{phase.value}")]
        if len(answers) >= 2:
            return f"已收集{len(answers)}轮回答，建议评估当前阶段是否通过"
        return "继续收集信息"

    def _check_phase_pass(self, collected: Dict, phase: QuestionPhase) -> bool:
        """检查阶段是否通过 — 简化规则：收集足够信息则通过"""
        answers = [v for k, v in collected.items() if k.startswith(f"q_{phase.value}")]
        if phase == QuestionPhase.L1_FORM:
            return any("客户" in a or "品牌" in a for a in answers) and len(answers) >= 2
        return len(answers) >= 2

    def _check_ready(self, collected: Dict, phase: QuestionPhase) -> bool:
        """判断是否已收集到足够信息生成方案"""
        # L4 阶段且收集了足够信息
        return (
            phase in [QuestionPhase.L4_SOLUTION, QuestionPhase.L5_BELIEF]
            or phase.value in ["L4_SOLUTION", "L5_BELIEF"]
        ) and len(collected) >= 6

    def _build_proposal_brief(self, collected: Dict) -> str:
        """根据收集的数据生成方案摘要"""
        keys = list(collected.keys())
        all_answers = [v for v in collected.values()]

        # 从已收集数据中提取关键信息
        brief_parts = ["## 方案摘要\n"]

        # 从回答中识别关键字段
        for text in all_answers:
            text = str(text)
            if any(k in text for k in ["母婴", "大健康", "家居家装", "汽车", "食品", "珠宝", "酒类"]):
                brief_parts.append(f"- 行业：{text}")
                break

        for text in all_answers:
            if "万" in str(text):
                brief_parts.append(f"- 预算：{text}")
                break

        brief_parts.append(f"- 已收集 {len(collected)} 轮信息，具备方案生成条件")
        brief_parts.append("- 建议调用 S1→S9 完整工作流生成方案")

        return "\n".join(brief_parts)
