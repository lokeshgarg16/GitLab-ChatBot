from fastapi import APIRouter, UploadFile, File, HTTPException
from urllib.parse import unquote
from typing import List
from langchain_core.documents import Document
import io
import csv

from app.core.config import settings
from app.core.logging import logger
from app.db.chroma_client import build_vector_store
from app.utils.text import clean_html_text, chunk_text

try:
    import pdfplumber
except Exception:
    pdfplumber = None


router = APIRouter(prefix="/upload", tags=["upload"])


def _fetch_uploaded_sources(store):
    documents = []

    try:
        result = store.get(include=["metadatas"])
        metadatas = result.get("metadatas") or []
        ids = result.get("ids") or []

        for index, metadata in enumerate(metadatas):
            if not metadata:
                continue

            source = metadata.get("source")
            if not source:
                continue

            doc_id = ids[index] if index < len(ids) else None

            documents.append({
                "id": doc_id,
                "source": source,
            })

    except Exception as exc:
        logger.exception(
            "Failed to fetch uploaded document metadata from Chroma: %s",
            exc,
        )

    return documents


@router.get("/", summary="List uploaded documents")
async def list_uploaded_docs():
    store = build_vector_store()

    sources = {}

    for item in _fetch_uploaded_sources(store):
        source = item["source"]

        if source not in sources:
            sources[source] = {
                "source": source,
                "count": 0,
            }

        sources[source]["count"] += 1

    return {
        "sources": list(sources.values())
    }


@router.delete("/{source}", summary="Delete an uploaded document source from Chroma")
async def delete_uploaded_doc(source: str):
    source = unquote(source)
    store = build_vector_store()

    try:
        result = store.get(
            where={"source": {"$eq": source}},
            include=["metadatas"],
        )
    except Exception as exc:
        logger.exception(
            "Failed to query Chroma for source deletion: %s",
            exc,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to query vector store",
        )

    ids = result.get("ids") or []

    if not ids:
        raise HTTPException(
            status_code=404,
            detail="Uploaded document not found",
        )

    try:
        store.delete(ids=ids)
    except Exception as exc:
        logger.exception(
            "Failed to delete documents from Chroma: %s",
            exc,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to delete uploaded document",
        )

    return {
        "status": "deleted",
        "source": source,
        "deleted_count": len(ids),
    }


@router.post("/", summary="Upload a document and ingest into Chroma")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or "uploaded"

    try:
        content_bytes = await file.read()

        if not content_bytes:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        if file.content_type == "application/pdf" or filename.lower().endswith(".pdf"):
            if pdfplumber is None:
                raise HTTPException(
                    status_code=500,
                    detail="pdfplumber is not installed. Run: pip install pdfplumber",
                )

            try:
                with pdfplumber.open(io.BytesIO(content_bytes)) as pdf:
                    pages = [
                        page.extract_text() or ""
                        for page in pdf.pages
                    ]

                text = "\n\n".join(pages)

            except Exception as exc:
                logger.exception(
                    "Failed to extract PDF text: %s",
                    exc,
                )
                raise HTTPException(
                    status_code=400,
                    detail="Failed to extract text from PDF",
                )

        elif filename.lower().endswith(".csv"):
            try:
                try:
                    decoded = content_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    decoded = content_bytes.decode("latin-1")

                reader = csv.reader(io.StringIO(decoded))
                rows = [", ".join(row) for row in reader]
                text = "\n".join(rows)

            except Exception as exc:
                logger.exception(
                    "Failed to parse CSV: %s",
                    exc,
                )
                raise HTTPException(
                    status_code=400,
                    detail="Failed to parse CSV file",
                )

        else:
            try:
                text = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    text = content_bytes.decode("latin-1")
                except Exception:
                    raise HTTPException(
                        status_code=400,
                        detail="Unable to decode uploaded file",
                    )

            if file.content_type == "text/html" or filename.lower().endswith((".html", ".htm")):
                text = clean_html_text(text)

        text = text.strip()

        if not text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in uploaded file",
            )

        chunks = chunk_text(
            text,
            settings.max_chunk_size,
            settings.chunk_overlap,
        )

        documents: List[Document] = [
            Document(
                page_content=chunk,
                metadata={
                    "source": filename,
                    "chunk_index": idx,
                },
            )
            for idx, chunk in enumerate(chunks)
            if chunk.strip()
        ]

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No document chunks created",
            )

        store = build_vector_store()

        try:
            store.add_documents(documents)
        except Exception as exc:
            logger.exception(
                "Failed to add documents to vector store: %s",
                exc,
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add documents to vector store: {str(exc)}",
            )

        try:
            collection_count = store._collection.count()
        except Exception:
            collection_count = None

        return {
            "status": "ingested",
            "source": filename,
            "chunks": len(documents),
            "collection_count": collection_count,
        }

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception("Upload failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )