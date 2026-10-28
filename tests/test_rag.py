import asyncio

from backend.app.services.rag import VetRAGService
from tests.fakes import FakeEmbedder, FakeReranker, FakeNER, FakeVectorStore, FakeGenerator

EMPTY_STATE = {"messages": [], "summary": ""}
PROFILE = {"role": "Ветеринар", "animal": "Крупный рогатый скот"}


def make_rag(search_results=None, ner=None):
    embedder = FakeEmbedder()
    generator = FakeGenerator()
    rag = VetRAGService(
        embedder=embedder,
        reranker=FakeReranker(),
        vector_store=FakeVectorStore(search_results),
        ner=ner or FakeNER(),
        generator=generator,
    )
    return rag, embedder, generator


def ask(rag, query):
    return asyncio.run(rag.answer(query, PROFILE, dict(EMPTY_STATE)))


def test_query_is_enriched_with_symptoms_and_animal():
    rag, embedder, _ = make_rag(ner=FakeNER(animals=["корова"], symptoms=["диарея"]))

    ask(rag, "У коровы диарея")

    assert embedder.queries == ["У коровы диарея симптомы: диарея животное: корова"]


def test_found_documents_are_passed_to_llm_as_context():
    chunks = [{"text": "Диарея у телят часто вызвана паразитами.", "score": 0.8}]
    rag, _, generator = make_rag(search_results=chunks)

    result = ask(rag, "У коровы диарея")

    assert "Диарея у телят часто вызвана паразитами." in generator.last_query
    assert result["sources"] == chunks
    assert result["answer"] == "Ответ ветеринара"


def test_fallback_to_knowledge_base_when_no_documents_found():
    rag, _, generator = make_rag(search_results=[])

    result = ask(rag, "У коровы диарея")

    assert "Возможные диагнозы: паразиты, смена корма, инфекция ЖКТ, отравление" in generator.last_query
    assert result["sources"] == []


def test_plain_question_when_nothing_is_known():
    rag, _, generator = make_rag(search_results=[])

    ask(rag, "Как часто кормить кур?")

    assert generator.last_query == "Как часто кормить кур?"
