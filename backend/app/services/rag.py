from backend.app.services.ner import VetNERService
from backend.app.services.embeddings import EmbeddingService
from backend.app.services.vector_store import VectorStore
from backend.app.services.reranker import RerankerService
from backend.app.services.generator import AiVeterinarian


class VetRAGService:
    def __init__(
        self,
        embedder: EmbeddingService,
        reranker: RerankerService,
        vector_store: VectorStore,
        ner: VetNERService | None = None,
        generator: AiVeterinarian | None = None,
    ):
        self.embedder = embedder
        self.reranker = reranker
        self.vector_store = vector_store
        self.generator = generator or AiVeterinarian()
        self.ner = ner or VetNERService()

    async def answer(self, query: str, user_config: dict, conversation_state: dict) -> dict:
        entities = self.ner.extract(query)

        enriched_query = query
        if entities["symptoms"]:
            enriched_query += f" симптомы: {', '.join(entities['symptoms'])}"
        if entities["animals"]:
            enriched_query += f" животное: {', '.join(entities['animals'])}"

        query_vector = self.embedder.embed_query(enriched_query)
        candidates = await self.vector_store.search(query_vector, document_id=1)
        reranked = self.reranker.rerank(enriched_query, candidates)

        if not reranked:
            from backend.app.services.vet_knowledge import VetKnowledge
            vet = VetKnowledge()
            diagnoses = vet.get_possible_diagnoses(query)
            context = f"Возможные диагнозы: {', '.join(diagnoses)}" if diagnoses else ""
        else:
            context = "\n\n".join(c["text"] for c in reranked)

        final_query = f"{query}\n\n[Контекст из базы знаний]:\n{context}" if context else query

        updated_state = self.generator.ask(final_query, user_config, conversation_state)
        answer = updated_state["messages"][-1].content

        return {
            "answer": answer,
            "sources": reranked,
            "conversation_state": updated_state,
        }