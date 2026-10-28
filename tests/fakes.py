"""Test doubles for the ML models and external services used by the RAG pipeline."""
from langchain_core.messages import AIMessage


class FakeEmbedder:
    dimension = 3

    def __init__(self):
        self.queries = []

    def embed_query(self, query: str) -> list[float]:
        self.queries.append(query)
        return [0.1, 0.2, 0.3]

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        return [[0.1, 0.2, 0.3] for _ in documents]


class FakeReranker:
    def rerank(self, query: str, candidates: list[dict]) -> list[dict]:
        return candidates[:3]


class FakeVectorStore:
    def __init__(self, search_results: list[dict] | None = None):
        self.search_results = search_results or []
        self.upserted = []
        self.deleted = []

    async def ensure_collection(self, vector_size: int):
        pass

    async def upsert_chunks(self, document_id: int, chunks: list[dict], embeddings: list[list[float]]):
        self.upserted.append((document_id, chunks))

    async def search(self, query_vector: list[float], document_id: int, top_k: int = 10) -> list[dict]:
        return self.search_results

    async def delete_document(self, document_id: int):
        self.deleted.append(document_id)


class FakeNER:
    def __init__(self, animals: list[str] | None = None, symptoms: list[str] | None = None):
        self.animals = animals or []
        self.symptoms = symptoms or []

    def extract(self, text: str) -> dict:
        return {"animals": self.animals, "symptoms": self.symptoms, "duration": None, "named_entities": []}


class FakeGenerator:
    def __init__(self, reply: str = "Ответ ветеринара"):
        self.reply = reply
        self.last_query = None

    def ask(self, user_input: str, user_config: dict, conversation_state: dict) -> dict:
        self.last_query = user_input
        messages = list(conversation_state.get("messages", []))
        messages.append(AIMessage(content=self.reply))
        return {"messages": messages, "summary": conversation_state.get("summary", "")}
