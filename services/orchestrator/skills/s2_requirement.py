from skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import Optional, List


class RequirementInput(SkillInput):
    communication_records: str = Field(description="客户沟通记录或需求描述")
    rfp_document: Optional[str] = Field(default=None, description="招标文件内容（可选）")


class RequirementOutput(SkillOutput):
    client_name: str = ""
    industry: str = ""
    sub_category: str = ""
    pain_points: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    budget_range: str = ""
    timeline: str = ""
    scope: str = ""
    competitors: List[str] = Field(default_factory=list)
    brand_assets: dict = Field(default_factory=dict)
    missing_info: List[str] = Field(default_factory=list)


class S2RequirementDiagnosis(BaseSkill):
    name = "s2_requirement_diagnosis"
    description = "需求诊断：从客户沟通记录中提取结构化需求，运用恐惧三层穿透模型识别表层需求背后的真实恐惧"

    def execute(self, input_data: RequirementInput) -> RequirementOutput:
        prompt = self._build_prompt(input_data.communication_records)
        extracted = self._llm_extract(prompt)

        missing = []
        if not extracted.get("industry"):
            missing.append("请确认客户所属行业")
        if not extracted.get("budget_range"):
            missing.append("请确认预算范围")
        if not extracted.get("timeline"):
            missing.append("请确认项目时间线")

        return RequirementOutput(
            client_name=extracted.get("client_name", ""),
            industry=extracted.get("industry", ""),
            sub_category=extracted.get("sub_category", ""),
            pain_points=extracted.get("pain_points", []),
            goals=extracted.get("goals", []),
            budget_range=extracted.get("budget_range", ""),
            timeline=extracted.get("timeline", ""),
            scope=extracted.get("scope", ""),
            competitors=extracted.get("competitors", []),
            brand_assets=extracted.get("brand_assets", {}),
            missing_info=missing,
        )

    def _build_prompt(self, records: str) -> str:
        return f"""从以下客户沟通记录中提取结构化需求信息，返回 JSON 格式。
要求运用「恐惧三层穿透模型」分析客户表达内容背后的真实恐惧。
同时运用「组织权力结构理论」识别沟通中涉及的多角色及其关注点差异。

**分析框架**：
1. 第一层（日常性恐惧）：客户直接说出来的痛点——成本高、效率低、竞品压力大。这些是建立专业信任的基础。
2. 第二层（社会性恐惧）：客户隐约感受到但说不清楚的——怕失去话语权、怕预算被砍、怕被老板质疑能力。这些是提案的核心弹药。
3. 第三层（基本恐惧）：客户绝对不会说的——怕职业信誉受损、怕被行业淘汰。方案逻辑必须回应它。

**多角色分析**（社会学-组织权力结构）：
- 识别沟通中出现的不同角色（决策者/影响者/使用者/采购者）
- 注意不同角色的关注点差异：决策者关注ROI和风险，使用者关注易用性和效率
- 同一段话中不同角色提到的同一问题，背后的恐惧往往不同

**核心原则**：客户的痛点 = 恐惧，不是"想要"。"想要"只是恐惧被触发后的响应结果。找到恐惧，就找到了决策的开关。

沟通记录：
{records}

请提取以下字段（缺失的字段留空）：
- client_name: 客户品牌名称
- industry: 所属行业
- sub_category: 细分品类
- pain_points: 客户痛点列表（优先标注每个痛点对应的恐惧层级:L1/L2/L3）
- fears: 恐惧穿透分析，按三层结构列出
- roles: 多角色分析，列出涉及的角色及其关注点差异（社会学-组织权力结构）
- goals: 客户目标列表
- budget_range: 预算范围
- timeline: 项目时间线
- scope: 项目范围
- competitors: 竞品列表
- brand_assets: 品牌资源（PPT模板/设计规范/Logo等）

只返回 JSON，不要其他内容。"""

    def _llm_extract(self, prompt: str) -> dict:
        import json
        from app.llm import get_llm
        llm = get_llm(task_type="light")
        response = llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {}