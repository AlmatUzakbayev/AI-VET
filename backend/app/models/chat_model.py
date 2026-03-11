from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    role: str
    content: str
    created_at: datetime = None


class ChatSession(BaseModel):
    user_id: str
    messages: list[ChatMessage] = []
    summary: str = ""
