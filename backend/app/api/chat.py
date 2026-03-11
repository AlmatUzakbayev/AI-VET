from fastapi import APIRouter, Request
from backend.app.data.data import UserInput
from backend.app.services.rag import VetRAGService
from backend.app.services.vector_store import VectorStore

router = APIRouter(prefix="/api/v1/ai-vet", tags=["chat"])


@router.post("/ask")
async def ask_endpoint(request: Request, payload: UserInput):
    user_id = payload.user_id
    user_text = payload.user_text

    user_config = request.app.state.user_statuses.get(user_id, {"role": "", "animal": ""})
    conversation_state = request.app.state.conversations.get(user_id, {"messages": [], "summary": ""})

    rag = VetRAGService(
        embedder=request.app.state.embedder,
        reranker=request.app.state.reranker,
        vector_store=VectorStore(),
    )

    result = await rag.answer(user_text, user_config, conversation_state)
    request.app.state.conversations[user_id] = result["conversation_state"]

    return {"response": result["answer"], "sources": result["sources"]}