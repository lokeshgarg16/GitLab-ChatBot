import json
import os
import time
from typing import List
import requests
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import GoogleGeminiEmbeddings

from app.core.config import settings
from app.utils.text import clean_html_text, chunk_text


GITLAB_PAGES = [
    "https://about.gitlab.com/handbook/",
    "https://about.gitlab.com/direction/",
]


def fetch_page(url: str) -> str:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.text


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("article") or soup
    for selector in article.select("script, style, nav, footer, header, noscript"):
        selector.decompose()
    return clean_html_text(str(article))


def build_documents(url: str, content: str) -> List[Document]:
    chunks = chunk_text(content, settings.max_chunk_size, settings.chunk_overlap)
    return [
        Document(page_content=chunk, metadata={"source": url, "chunk_index": idx})
        for idx, chunk in enumerate(chunks)
    ]


def main():
    embeddings = GoogleGeminiEmbeddings(api_key=settings.gemini_api_key)
    store = Chroma(
        persist_directory=settings.chroma_persist_directory,
        collection_name=settings.chroma_collection_name,
        embedding_function=embeddings,
    )

    raw_documents = []
    for url in GITLAB_PAGES:
        print(f"Fetching {url}")
        html = fetch_page(url)
        text = extract_text(html)
        raw_documents.extend(build_documents(url, text))
        time.sleep(1)

    if raw_documents:
        print(f"Ingesting {len(raw_documents)} chunks into ChromaDB")
        store.add_documents(raw_documents)
        store.persist()
        print("Ingestion complete")
    else:
        print("No documents were created from scraper")


if __name__ == "__main__":
    main()
