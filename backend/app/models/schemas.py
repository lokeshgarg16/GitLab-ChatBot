from typing import List, Optional
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    follow_up_suggestions: List[str]
    retrieved_chunks: List[str]

class HealthResponse(BaseModel):
    status: str
    details: Optional[str] = None
