from app.skills.base import BaseSkill, SkillInput, SkillOutput
from pydantic import Field
from typing import List, Dict


class ContentGenInput(SkillInput):
    full_proposal: dict = Field(description="S5 品牌增长全案方案")
    matched_cases: List[Dict] = Field(default_factory=list, description="S6 匹配案例")
    brand_assets: Dict = Field(default_factory=dict, description="品牌资源")


class ContentGenOutput(SkillOutput):
    slides: List[Dict] = Field(default_factory=list)
    slide_count: int = 0


class S7ContentGeneration(BaseSkill):
    name = "s7_content_generation"
    description = "内容生成：将方案转化为 Slide 级结构化内容"

    SLIDE_STRUCTURE = [
        "封面",
        "公司介绍",
        "行业洞察",
        "客户诊断",
        "竞品对标",
        "解决方案",
        "工具赋能与预算",
        "案例展示",
        "实施路径",
        "团队介绍",
    ]

    def execute(self, input_data: ContentGenInput) -> ContentGenOutput:
        slides = []
        for i, section in enumerate(self.SLIDE_STRUCTURE):
            slides.append({
                "index": i + 1,
                "title": section,
                "layout_type": self._get_layout(section),
                "content": self._generate_slide_content(
                    section, input_data.full_proposal, input_data.matched_cases
                ),
            })
        return ContentGenOutput(slides=slides, slide_count=len(slides))

    def _get_layout(self, section: str) -> str:
        layout_map = {
            "封面": "cover",
            "公司介绍": "two_column",
            "行业洞察": "chart_focus",
            "客户诊断": "bullet_cards",
            "竞品对标": "comparison_table",
            "解决方案": "icon_grid",
            "工具赋能与预算": "two_column",
            "案例展示": "case_card",
            "实施路径": "timeline",
            "团队介绍": "grid_cards",
        }
        return layout_map.get(section, "default")

    def _generate_slide_content(
        self, section: str, proposal: dict, cases: List[Dict]
    ) -> str:
        return f"<!-- {section} 内容由 LLM 生成 -->"