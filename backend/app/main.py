import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.api.routers.chat import router as chat_router
from app.api.routers.health import router as health_router
from app.api.routers.upload import router as upload_router
from app.api.routers.debug import router as debug_router

# CORS configuration for development and production
allow_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://your-vercel-app.vercel.app",  # Update with your actual Vercel frontend URL
]

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(debug_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting GitLab Handbook RAG chatbot backend")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down backend")


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.environment == "development")