import asyncio
from typing import AsyncGenerator, List

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings
from app.core.logging import logger
from app.services.memory import ConversationMemory
from app.utils.prompts import build_prompt, FOLLOW_UP_PROMPT


class RAGService:
    def __init__(self, vector_store: Chroma, memory: ConversationMemory):
        self.vector_store = vector_store
        self.memory = memory

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            temperature=settings.gemini_temperature,
            google_api_key=settings.gemini_api_key,
        )

    async def retrieve_documents(self, query: str) -> List[Document]:
        logger.info("Running semantic search for user query")

        return await asyncio.to_thread(
            self.vector_store.similarity_search,
            query,
            k=settings.max_context_docs,
        )

    async def generate_follow_up_suggestions(self, question: str) -> List[str]:
        prompt = FOLLOW_UP_PROMPT.format(
            count=settings.follow_up_suggestions_count
        )
        prompt += f"\nQuestion: {question}"

        logger.info("Generating follow-up suggestions")

        response = await asyncio.to_thread(
            lambda: self.llm.invoke(prompt).content
        )

        return [
            line.strip("- \n")
            for line in response.splitlines()
            if line.strip()
        ][: settings.follow_up_suggestions_count]

    async def build_response(
        self,
        query: str,
        session_id: str,
    ) -> dict:
        docs = await self.retrieve_documents(query)

        source_labels = [
            f"source:{doc.metadata.get('source', 'unknown')}"
            for doc in docs
        ]

        prompt = build_prompt(
            [doc.page_content for doc in docs],
            query,
        )

        logger.info("Building prompt and generating response")

        answer_text = ""

        try:
            async for token in self.stream_answer(prompt):
                answer_text += token

        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            raise

        suggestions = []

        await self.memory.append_message(
            session_id,
            "user",
            query,
        )

        await self.memory.append_message(
            session_id,
            "assistant",
            answer_text,
        )

        return {
            "answer": answer_text,
            "sources": source_labels,
            "confidence": 0.75,
            "follow_up_suggestions": suggestions,
            "retrieved_chunks": [
                doc.page_content for doc in docs
            ],
        }

    async def stream_answer(
        self,
        prompt: str,
    ) -> AsyncGenerator[str, None]:

        try:
            for chunk in self.llm.stream(prompt):
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content

        except Exception:
            response = await asyncio.to_thread(
                lambda: self.llm.invoke(prompt).content
            )

            yield response