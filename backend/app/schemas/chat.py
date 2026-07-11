"""Pydantic schemas for AI chat."""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    profile_id: int
    message: str = Field(..., min_length=1, max_length=2000)
    page_context: str = "dashboard"  # Which page the user is on
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str  # Markdown-formatted response
