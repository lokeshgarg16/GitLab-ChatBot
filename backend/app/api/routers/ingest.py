from typing import List

import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, HTTPException
from langchain_core.documents import Document

from app.core.config import settings
from app.core.logging import logger
from app.db.chroma_client import build_vector_store
from app.utils.text import clean_html_text, chunk_text

router = APIRouter(prefix="/ingest", tags=["ingest"])

GITLAB_PAGES = [
    "https://handbook.gitlab.com/",
    "https://about.gitlab.com/direction/",
]


def fetch_page(url: str) -> str:
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "GitLab Handbook RAG Bot/1.0"},
    )
    response.raise_for_status()
    return response.text


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup.find_all(["script", "style", "nav", "footer"]):
        element.decompose()

    return clean_html_text(str(soup))


@router.post("/gitlab", summary="Import GitLab Handbook pages into Chroma")
async def ingest_gitlab_pages():
    documents: List[Document] = []

    for url in GITLAB_PAGES:
        try:
            html = fetch_page(url)
        except Exception as exc:
            logger.exception("Failed to fetch GitLab page %s: %s", url, exc)
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch GitLab page: {url}",
            )

        text = extract_text(html).strip()

        if not text:
            logger.warning("No text extracted from GitLab page: %s", url)
            continue

        chunks = chunk_text(
            text,
            settings.max_chunk_size,
            settings.chunk_overlap,
        )

        documents.extend(
            Document(
                page_content=chunk,
                metadata={
                    "source": url,
                    "type": "gitlab_page",
                    "chunk_index": idx,
                },
            )
            for idx, chunk in enumerate(chunks)
            if chunk.strip()
        )

    if not documents:
        raise HTTPException(
            status_code=500,
            detail="No chunks were created from GitLab pages",
        )

    store = build_vector_store()

    try:
        store.add_documents(documents)
    except Exception as exc:
        logger.exception("Failed to add GitLab documents to Chroma: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to add GitLab pages to vector store",
        )

    return {
        "pages": len(GITLAB_PAGES),
        "chunks": len(documents),
    }
