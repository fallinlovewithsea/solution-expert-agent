"""Three core business skills for the simplified proposal workflow."""

from app.skills.brief import BriefSkill, BriefInput, BriefOutput
from app.skills.insight import InsightSkill, InsightInput, InsightOutput
from app.skills.proposal import ProposalSkill, ProposalInput, ProposalOutput

__all__ = [
    "BriefSkill",
    "BriefInput",
    "BriefOutput",
    "InsightSkill",
    "InsightInput",
    "InsightOutput",
    "ProposalSkill",
    "ProposalInput",
    "ProposalOutput",
]
