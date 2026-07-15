from fastapi import APIRouter, HTTPException

from app.skills.brief import BriefSkill
from app.skills.insight import InsightSkill
from app.skills.proposal import ProposalSkill


router = APIRouter()

CORE_SKILLS = {
    skill.name: {
        "name": skill.name,
        "description": skill.description,
        "type": "core_skill",
    }
    for skill in (BriefSkill(), InsightSkill(), ProposalSkill())
}

TOOLS = {
    "research": {"name": "research", "description": "小红书数据采集与研究", "type": "tool"},
    "case_retrieval": {"name": "case_retrieval", "description": "案例检索与排序", "type": "tool"},
    "export": {"name": "export", "description": "Slides、Docx、PPTX 按需输出", "type": "tool"},
    "archive": {"name": "archive", "description": "审核通过且取得项目结果后的复盘归档", "type": "lifecycle"},
}


@router.get("/")
async def list_skills():
    return {"skills": CORE_SKILLS, "tools": TOOLS, "status": "ok"}


@router.get("/{skill_name}")
async def get_skill(skill_name: str):
    item = CORE_SKILLS.get(skill_name) or TOOLS.get(skill_name)
    if item is None:
        raise HTTPException(status_code=404, detail=f"能力 '{skill_name}' 不存在")
    return item
