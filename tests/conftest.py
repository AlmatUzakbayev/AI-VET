import pytest
from fastapi.testclient import TestClient

from backend.app import app as app_module
from backend.app.api import documents
from backend.app.api.deps import get_vector_store
from tests.fakes import FakeEmbedder, FakeReranker, FakeNER, FakeVectorStore


@pytest.fixture
def vector_store():
    return FakeVectorStore()


@pytest.fixture
def app(vector_store, tmp_path, monkeypatch):
    # The lifespan loads real models and JSON history, so the state is filled by hand instead
    application = app_module.create_app()
    application.state.user_statuses = {}
    application.state.conversations = {}
    application.state.embedder = FakeEmbedder()
    application.state.reranker = FakeReranker()
    application.state.ner = FakeNER()
    application.dependency_overrides[get_vector_store] = lambda: vector_store

    monkeypatch.setattr(documents, "UPLOADS_DIRECTORY", tmp_path)
    monkeypatch.setattr(documents, "summarize_text", lambda text: "краткое содержание")
    return application


@pytest.fixture
def client(app):
    return TestClient(app)
