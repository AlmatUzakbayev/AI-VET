import nltk
from backend.app.core.config import CHUNK_SIZE, CHUNK_OVERLAP


def _ensure_tokenizer() -> None:
    # sent_tokenize needs the punkt_tab data, which is not shipped with the nltk package
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)


def chunk_text(text: str, page_map: list) -> list[dict]:
    _ensure_tokenizer()
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    chunk_start = 0
    prev_end = 0

    for sentence in sentences:
        found = text.find(sentence, prev_end)
        sentence_start = found if found != -1 else prev_end

        if len(current_chunk) + len(sentence) > CHUNK_SIZE and current_chunk:
            _append_chunk(chunks, current_chunk, chunk_start, page_map)
            # current_chunk[-0:] would return the whole string, so overlap 0 needs its own branch
            overlap = current_chunk[-CHUNK_OVERLAP:] if CHUNK_OVERLAP > 0 else ""
            current_chunk = overlap + " " + sentence
            chunk_start = max(prev_end - len(overlap), 0) if overlap else sentence_start
        else:
            if not current_chunk:
                chunk_start = sentence_start
            current_chunk += " " + sentence

        prev_end = sentence_start + len(sentence)

    if current_chunk.strip():
        _append_chunk(chunks, current_chunk, chunk_start, page_map)

    return chunks


def _append_chunk(chunks: list[dict], chunk: str, char_start: int, page_map: list) -> None:
    chunks.append({
        "text": chunk.strip(),
        "chunk_index": len(chunks),
        "char_start": char_start,
        "page_num": _get_page(char_start, page_map),
    })


def _get_page(char_pos: int, page_map: list) -> int:
    for start, end, page_num in page_map:
        if start <= char_pos < end:
            return page_num
    return 1
