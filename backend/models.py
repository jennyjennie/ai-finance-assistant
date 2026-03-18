from pydantic import BaseModel
from typing import List, Literal, Optional


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    session_id: str
