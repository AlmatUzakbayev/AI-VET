import os
import aiofiles
from fastapi import APIRouter, UploadFile, File, HTTPException, Request

from backend.app.services.parser import parse_document
from backend.app.services.chunker import chunk_text
from backend.app.services.vector_store import VectorStore
from backend.app.services.summarizer import summarize_text
from backend.app.core.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, UPLOADS_DIRECTORY

router = APIRouter(prefix="/api/v1/ai-vet/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = "0",
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Поддерживаются только: {ALLOWED_EXTENSIONS}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, "Файл слишком большой (макс. 20MB)")

    file_path = str(UPLOADS_DIRECTORY / f"{user_id}_{file.filename}")
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    parsed = parse_document(file_path)
    chunks = chunk_text(parsed["text"], parsed["page_map"])

    embedder = request.app.state.embedder
    embeddings = embedder.embed_documents([c["text"] for c in chunks])

    vs = VectorStore()
    await vs.ensure_collection(embedder.dimension)
    await vs.upsert_chunks(1, chunks, embeddings)

    summary = summarize_text(parsed["text"])

    return {
        "filename": file.filename,
        "language": parsed["language"],
        "chunk_count": len(chunks),
        "summary": summary,
    }


@router.get("/")
async def list_documents():
    return {"items": []}


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    vs = VectorStore()
    await vs.delete_document(int(document_id))
    return {"status": "deleted", "id": document_id}