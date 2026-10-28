import os
import re
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request

from backend.app.api.deps import get_vector_store
from backend.app.services.parser import parse_document
from backend.app.services.chunker import chunk_text
from backend.app.services.vector_store import VectorStore
from backend.app.services.summarizer import summarize_text
from backend.app.core.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, UPLOADS_DIRECTORY

router = APIRouter(prefix="/api/v1/ai-vet/documents", tags=["documents"])


def _safe_name(value: str) -> str:
    # Keep only the base name and harmless characters, so "../" cannot escape UPLOADS_DIRECTORY
    return re.sub(r"[^\w.\-]", "_", Path(value).name)


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = "0",
    vs: VectorStore = Depends(get_vector_store),
):
    filename = _safe_name(file.filename or "")
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Поддерживаются только: {ALLOWED_EXTENSIONS}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, f"Файл слишком большой (макс. {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB)")

    file_path = str(UPLOADS_DIRECTORY / f"{_safe_name(user_id)}_{filename}")
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    parsed = parse_document(file_path)
    chunks = chunk_text(parsed["text"], parsed["page_map"])
    if not chunks:
        raise HTTPException(400, "В документе не найден текст")

    embedder = request.app.state.embedder
    embeddings = embedder.embed_documents([c["text"] for c in chunks])

    await vs.ensure_collection(embedder.dimension)
    await vs.upsert_chunks(1, chunks, embeddings)

    summary = summarize_text(parsed["text"])

    return {
        "filename": filename,
        "language": parsed["language"],
        "chunk_count": len(chunks),
        "summary": summary,
    }


@router.get("/")
async def list_documents():
    return {"items": []}


@router.delete("/{document_id}")
async def delete_document(document_id: int, vs: VectorStore = Depends(get_vector_store)):
    await vs.delete_document(document_id)
    return {"status": "deleted", "id": document_id}
