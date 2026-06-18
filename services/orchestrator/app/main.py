from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import proposal, skills

app = FastAPI(
    title="解决方案专家 Agent",
    description="面向售前团队的自动化提案生成系统",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proposal.router, prefix="/api/proposal", tags=["proposal"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "solution-expert-agent"}