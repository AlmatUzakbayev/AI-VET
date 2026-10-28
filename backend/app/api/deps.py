from fastapi import Depends, Request

from backend.app.services.rag import VetRAGService
from backend.app.services.vector_store import VectorStore


def get_vector_store() -> VectorStore:
    return VectorStore()


def get_rag_service(
    request: Request,
    vector_store: VectorStore = Depends(get_vector_store),
) -> VetRAGService:
    # Models are loaded once in the lifespan and shared between requests
    return VetRAGService(
        embedder=request.app.state.embedder,
        reranker=request.app.state.reranker,
        vector_store=vector_store,
        ner=request.app.state.ner,
    )
