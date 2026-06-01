from app.core.config import settings


def build_vector_store(persist_directory: str = None):
    """Create and return a Chroma vector store instance.

    Import heavy/optional dependencies lazily and support multiple
    import paths (langchain_community.vectorstores or langchain_chroma)
    so the module can be imported even if the optional adapter isn't
    installed yet. Raise a clear error if neither is available.
    """
    persist_directory = persist_directory or settings.chroma_persist_directory

    # Lazy import embeddings and Chroma implementation
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
    except Exception as e:
        raise RuntimeError("GoogleGenerativeAIEmbeddings import failed: %s" % e)

    # Try langchain_community.vectorstores.Chroma first, then langchain_chroma
    ChromaImpl = None
    try:
        from langchain_community.vectorstores import Chroma as ChromaImpl
    except Exception:
        try:
            from langchain_chroma import Chroma as ChromaImpl
        except Exception:
            ChromaImpl = None

    if ChromaImpl is None:
        raise RuntimeError(
            "No Chroma vectorstore implementation available. Install 'langchain_community' or 'langchain-chroma'."
        )

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        google_api_key=settings.gemini_api_key,
    )

    return ChromaImpl(
        persist_directory=persist_directory,
        collection_name=settings.chroma_collection_name,
        embedding_function=embeddings,
    )