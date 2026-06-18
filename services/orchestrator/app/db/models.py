from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BrandInfo(BaseModel):
    id: Optional[int] = None
    brand_name: str
    industry: str
    sub_category: Optional[str] = None
    contact_history: list = Field(default_factory=list)
    current_status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CaseLabel(BaseModel):
    id: Optional[int] = None
    case_name: str
    industry: str
    scene: str
    playbook: str
    customer_feedback: Optional[str] = None
    key_metrics: dict = Field(default_factory=dict)
    source_url: Optional[str] = None
    relevance_score: float = 0.0


class ProposalRecord(BaseModel):
    id: Optional[int] = None
    client_name: str
    industry: str
    project_type: str
    status: str = "draft"
    slides_url: Optional[str] = None
    docx_url: Optional[str] = None
    bid_result: Optional[str] = None
    review_notes: list = Field(default_factory=list)


class ReviewRecord(BaseModel):
    id: Optional[int] = None
    proposal_id: int
    success_factors: list = Field(default_factory=list)
    lessons_learned: list = Field(default_factory=list)
    improvements: list = Field(default_factory=list)
    extracted_data: dict = Field(default_factory=dict)


class RawDocument(BaseModel):
    id: Optional[int] = None
    doc_name: str
    doc_type: str
    source_folder: Optional[str] = None
    feishu_token: Optional[str] = None
    feishu_url: Optional[str] = None
    content: str
    collected_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class RawXhsData(BaseModel):
    id: Optional[int] = None
    collect_type: str
    target_name: str
    keywords: list = Field(default_factory=list)
    notes: list = Field(default_factory=list)
    comments: list = Field(default_factory=list)
    analysis: dict = Field(default_factory=dict)
    collected_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class KnowledgeRelation(BaseModel):
    id: Optional[int] = None
    source_type: str
    source_id: str
    target_type: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    created_at: Optional[datetime] = None


class UserPreference(BaseModel):
    id: Optional[int] = None
    user_id: str
    preferred_industries: list = Field(default_factory=list)
    preferred_templates: list = Field(default_factory=list)
    budget_range: Optional[str] = None
    output_formats: list = Field(default_factory=list)
    search_history: list = Field(default_factory=list)
    interaction_count: int = 0
    last_active_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SessionMemory(BaseModel):
    id: Optional[int] = None
    session_id: str
    user_id: str
    client_name: str
    industry: Optional[str] = None
    stage: Optional[str] = None
    proposal_id: Optional[int] = None
    review_feedback: Optional[str] = None
    bid_result: Optional[str] = None
    key_notes: Optional[str] = None
    context: dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None