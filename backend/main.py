from dotenv import load_dotenv
load_dotenv()

import os
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from models import ChatRequest, ChatResponse
from claude_client import run_chat
from routers.portfolio import router as portfolio_router
from routers.history import router as history_router
from database import get_db
from db_models import Session as DBSession, DBMessage

app = FastAPI(title="AI Finance Assistant")

app.include_router(portfolio_router)
app.include_router(history_router)

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
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    # Get or create session
    if request.session_id:
        try:
            sid = uuid.UUID(request.session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session_id")
        db_session = await db.get(DBSession, sid)
        if not db_session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        first_user = next((m for m in request.messages if m.role == "user"), None)
        title = first_user.content[:80] if first_user else None
        db_session = DBSession(title=title)
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        sid = db_session.id

    # Save the new user message (last item in the list)
    new_user_msg = request.messages[-1]
    db.add(DBMessage(session_id=sid, role=new_user_msg.role, content=new_user_msg.content))
    await db.commit()

    message = await run_chat(request.messages)

    db.add(DBMessage(session_id=sid, role="assistant", content=message))
    await db.commit()

    return ChatResponse(message=message, session_id=str(sid))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
