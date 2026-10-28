from fastapi import APIRouter, Depends, Request
from backend.app.api.deps import get_rag_service
from backend.app.data.data import UserInput
from backend.app.services.rag import VetRAGService

router = APIRouter(prefix="/api/v1/ai-vet", tags=["chat"])


@router.post("/ask")
async def ask_endpoint(
    request: Request,
    payload: UserInput,
    rag: VetRAGService = Depends(get_rag_service),
):
    user_id = payload.user_id
    user_text = payload.user_text

    user_config = request.app.state.user_statuses.get(user_id, {"role": "", "animal": ""})
    conversation_state = request.app.state.conversations.get(user_id, {"messages": [], "summary": ""})

    result = await rag.answer(user_text, user_config, conversation_state)
    request.app.state.conversations[user_id] = result["conversation_state"]

    return {"response": result["answer"], "sources": result["sources"]}
