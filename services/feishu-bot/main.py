from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8000")


@app.post("/webhook")
async def feishu_webhook(request: Request):
    body = await request.json()
    challenge = body.get("challenge")
    if challenge:
        return {"challenge": challenge}

    event = body.get("event", {})
    message = event.get("message", {})
    content = message.get("content", "{}")
    import json
    text = json.loads(content).get("text", "")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ORCHESTRATOR_URL}/api/proposal/generate",
            json={"user_input": text},
        )
        result = resp.json()

    return {"message": result.get("message", "提案生成中...")}


@app.get("/health")
async def health():
    return {"status": "ok"}