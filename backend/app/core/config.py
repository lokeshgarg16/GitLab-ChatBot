from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "GitLab Handbook RAG Chatbot"
    environment: str = Field("development", env="ENVIRONMENT")
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
    chroma_persist_directory: str = Field("./data/chroma", env="CHROMA_PERSIST_DIRECTORY")
    chroma_collection_name: str = Field("gitlab_handbook", env="CHROMA_COLLECTION_NAME")
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-1.5-pro", env="GEMINI_MODEL")
    gemini_temperature: float = Field(0.0, env="GEMINI_TEMPERATURE")
    max_chunk_size: int = Field(500, env="MAX_CHUNK_SIZE")
    chunk_overlap: int = Field(100, env="CHUNK_OVERLAP")
    max_context_docs: int = Field(5, env="MAX_CONTEXT_DOCS")
    follow_up_suggestions_count: int = Field(3, env="FOLLOW_UP_SUGGESTIONS_COUNT")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()
