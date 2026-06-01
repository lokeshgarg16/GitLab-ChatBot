from langchain.embeddings import GoogleGeminiEmbeddings
from app.core.config import settings


def get_embeddings_client():
    return GoogleGeminiEmbeddings(api_key=settings.gemini_api_key)
