from backend.app.core.constants import EMBEDDINGS_MODEL

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


class EmbeddingService:
    def __init__(self):
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers is not installed or failed to import")
        self.model = SentenceTransformer(EMBEDDINGS_MODEL)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def embed_query(self, query: str) -> list[float]:
        return self.model.encode(query).tolist()

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        return self.model.encode(documents).tolist()
