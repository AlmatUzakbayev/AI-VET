from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from backend.app.services.ner import VetNERService
from backend.app.core.constants import UPLOADS_DIRECTORY
from backend.app.database.database import HistoryWriter
from backend.app.services.embeddings import EmbeddingService
from backend.app.services.reranker import RerankerService
from backend.app.api.chat import router as chat_router
from backend.app.api.documents import router as documents_router
from backend.app.api.users import router as users_router, compat_router

HISTORY_WRITER = HistoryWriter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    UPLOADS_DIRECTORY.mkdir(parents=True, exist_ok=True)
    app.state.user_statuses = HISTORY_WRITER.load_user_statuses()
    app.state.conversations = HISTORY_WRITER.load_user_conversations()
    app.state.embedder = EmbeddingService()
    app.state.reranker = RerankerService()
    app.state.ner = VetNERService()

    logger.info("Application started. User data loaded.")
    yield
    HISTORY_WRITER.save_user_statuses(app.state.user_statuses)
    HISTORY_WRITER.save_user_conversations(app.state.conversations)
    logger.info("User data saved. Application shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Veterinary Assistant API",
        description="AI-ветеринарный ассистент с RAG pipeline",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(users_router)
    app.include_router(chat_router)
    app.include_router(documents_router)
    app.include_router(compat_router)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)