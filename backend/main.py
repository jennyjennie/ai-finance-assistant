from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ChatRequest, ChatResponse
from claude_client import run_chat
from routers.portfolio import router as portfolio_router

app = FastAPI(title="AI Finance Assistant")

app.include_router(portfolio_router)

# FRONTEND_URL supports multiple origins (comma-separated) for production + local dev
_raw = os.getenv("FRONTEND_URL", "http://localhost:3000")
allowed_origins = [u.strip() for u in _raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")
    message = await run_chat(request.messages)
    return ChatResponse(message=message)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
