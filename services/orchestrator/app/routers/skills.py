from fastapi import APIRouter
from app.skills.base import SkillRegistry

router = APIRouter()


@router.get("/")
async def list_skills():
    return {"skills": SkillRegistry.list_all(), "status": "ok"}


@router.get("/{skill_name}")
async def get_skill(skill_name: str):
    skill = SkillRegistry.get(skill_name)
    if skill is None:
        return {"error": f"Skill '{skill_name}' not found"}
    return skill.to_dict()