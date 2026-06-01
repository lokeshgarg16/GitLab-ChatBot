from fastapi import APIRouter, HTTPException, status
from redis.asyncio import Redis
from app.core.config import settings
from app.core.logging import logger
from app.models.schemas import ChatRequest, ChatResponse
from app.services.memory import ConversationMemory
from app.services.rag import RAGService
from app.db.chroma_client import build_vector_store

router = APIRouter(prefix="/chat", tags=["chat"])


def get_redis_client():
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def get_rag_service() -> RAGService:
    redis_client = get_redis_client()
    memory = ConversationMemory(redis_client)
    vector_store = build_vector_store()
    return RAGService(vector_store=vector_store, memory=memory)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or "anonymous"
    rag_service = await get_rag_service()

    try:
        result = await rag_service.build_response(request.query, session_id)
        return result
    except Exception as exc:
        logger.exception("Error handling chat request")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
