from backend.app.core.config import CHUNK_SIZE
from backend.app.services import chunker

LONG_TEXT = " ".join(f"Предложение номер {i:02d} о здоровье животных." for i in range(60))


def test_empty_text_gives_no_chunks():
    assert chunker.chunk_text("", [(0, 0, 1)]) == []


def test_short_text_is_one_chunk():
    chunks = chunker.chunk_text("Корова не ест. Температура 40.", [(0, 30, 1)])

    assert len(chunks) == 1
    assert chunks[0]["text"] == "Корова не ест. Температура 40."
    assert chunks[0]["char_start"] == 0


def test_long_text_is_split_into_limited_chunks():
    chunks = chunker.chunk_text(LONG_TEXT, [(0, len(LONG_TEXT), 1)])

    assert len(chunks) > 1
    assert [c["chunk_index"] for c in chunks] == list(range(len(chunks)))
    assert all(len(c["text"]) <= CHUNK_SIZE for c in chunks)


def test_char_start_points_to_chunk_text():
    chunks = chunker.chunk_text(LONG_TEXT, [(0, len(LONG_TEXT), 1)])

    for chunk in chunks:
        start = chunk["char_start"]
        assert LONG_TEXT[start:start + 30] == chunk["text"][:30]


def test_page_number_comes_from_page_map():
    half = len(LONG_TEXT) // 2
    chunks = chunker.chunk_text(LONG_TEXT, [(0, half, 1), (half, len(LONG_TEXT), 2)])

    assert chunks[0]["page_num"] == 1
    assert chunks[-1]["page_num"] == 2


def test_zero_overlap_does_not_grow_chunks(monkeypatch):
    monkeypatch.setattr(chunker, "CHUNK_OVERLAP", 0)

    chunks = chunker.chunk_text(LONG_TEXT, [(0, len(LONG_TEXT), 1)])

    assert all(len(c["text"]) <= CHUNK_SIZE for c in chunks)
