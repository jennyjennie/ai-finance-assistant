import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from database import get_db
from db_models import Session as DBSession, DBMessage

router = APIRouter(prefix="/sessions", tags=["history"])


@router.post("")
async def create_session(db: AsyncSession = Depends(get_db)):
    session = DBSession()
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"id": str(session.id), "title": session.title, "created_at": session.created_at}


@router.get("")
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBSession).order_by(desc(DBSession.created_at)))
    sessions = result.scalars().all()
    return [{"id": str(s.id), "title": s.title, "created_at": s.created_at} for s in sessions]


@router.get("/{session_id}/messages")
async def get_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session_id")
    result = await db.execute(
        select(DBMessage)
        .where(DBMessage.session_id == sid)
        .order_by(DBMessage.created_at)
    )
    msgs = result.scalars().all()
    return [{"role": m.role, "content": m.content} for m in msgs]
