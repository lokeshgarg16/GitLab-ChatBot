import json
from typing import List, Optional
from redis.asyncio import Redis
import redis as redis_lib

from app.core.logging import logger


class ConversationMemory:
    """Simple conversation memory that optionally uses Redis.

    If Redis is not provided or becomes unavailable, methods fail gracefully:
    - `get_history` returns an empty list on error
    - `append_message` logs a warning and continues
    - `clear_history` logs a warning and continues
    """

    def __init__(self, redis: Optional[Redis] = None):
        self.redis = redis

    async def get_history(self, session_id: str) -> List[dict]:
        if self.redis is None:
            return []
        try:
            raw = await self.redis.get(f"chat:history:{session_id}")
        except (redis_lib.exceptions.ConnectionError, Exception) as exc:
            logger.warning("Redis unavailable when getting history for %s: %s", session_id, exc)
            return []

        if not raw:
            return []

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to decode history JSON for session %s", session_id)
            return []

    async def append_message(self, session_id: str, role: str, text: str):
        try:
            history = await self.get_history(session_id)
            history.append({"role": role, "text": text})

            if self.redis is None:
                # No persistence available; keep in-memory only
                return

            try:
                await self.redis.set(
                    f"chat:history:{session_id}", json.dumps(history), ex=60 * 60 * 24
                )
            except (redis_lib.exceptions.ConnectionError, Exception) as exc:
                logger.warning("Failed to append message to Redis for %s: %s", session_id, exc)
        except Exception as exc:
            logger.warning("Unexpected error appending message for %s: %s", session_id, exc)

    async def clear_history(self, session_id: str):
        if self.redis is None:
            return
        try:
            await self.redis.delete(f"chat:history:{session_id}")
        except (redis_lib.exceptions.ConnectionError, Exception) as exc:
            logger.warning("Failed to clear history for %s: %s", session_id, exc)
