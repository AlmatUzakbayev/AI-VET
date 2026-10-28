import pytest

from backend.app.api.deps import get_rag_service


class StubRag:
    def __init__(self):
        self.calls = []

    async def answer(self, query, user_config, conversation_state):
        self.calls.append((query, user_config))
        return {
            "answer": "Проверьте температуру",
            "sources": [{"text": "фрагмент", "score": 0.9}],
            "conversation_state": {"messages": ["saved"], "summary": ""},
        }


@pytest.fixture
def rag(app):
    stub = StubRag()
    app.dependency_overrides[get_rag_service] = lambda: stub
    return stub


def test_ask_returns_answer_and_sources(client, rag):
    response = client.post("/api/v1/ai-vet/ask", json={"user_id": "1", "user_text": "Корова не ест"})

    assert response.status_code == 200
    assert response.json() == {
        "response": "Проверьте температуру",
        "sources": [{"text": "фрагмент", "score": 0.9}],
    }


def test_ask_uses_user_profile_and_saves_conversation(client, app, rag):
    app.state.user_statuses["1"] = {"role": "Ветеринар", "animal": "Свиньи"}

    client.post("/api/v1/ai-vet/ask", json={"user_id": "1", "user_text": "Кашель"})

    assert rag.calls == [("Кашель", {"role": "Ветеринар", "animal": "Свиньи"})]
    assert app.state.conversations["1"] == {"messages": ["saved"], "summary": ""}


@pytest.mark.parametrize("payload", [{}, {"user_id": "1"}, {"user_text": "Кашель"}])
def test_ask_without_required_fields_returns_422(client, rag, payload):
    response = client.post("/api/v1/ai-vet/ask", json=payload)
    assert response.status_code == 422
    assert rag.calls == []
