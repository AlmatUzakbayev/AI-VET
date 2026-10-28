# AI Veterinary Assistant

[![tests](https://github.com/AlmatUzakbayev/AI-VET/actions/workflows/tests.yml/badge.svg)](https://github.com/AlmatUzakbayev/AI-VET/actions/workflows/tests.yml)

Backend service and Telegram bot for veterinary consultation powered by RAG.

You can find the bot at @MED_VET_BOT.

## Overview

This project provides an AI-powered veterinary assistant platform combining modern NLP technologies with a convenient Telegram interface. Users can describe symptoms, ask questions about animal health, and receive professional recommendations — the system searches through veterinary documents and generates accurate answers.

Key features include:
- Conversational AI with role selection (Veterinarian / Zootechnician)
- Document processing (PDF, DOCX) with automatic chunking and embedding
- Two-stage retrieval: bi-encoder (Qdrant) → cross-encoder reranker
- Fallback to direct LLM response when no documents found
- Multilingual support via `intfloat/multilingual-e5-large` (100+ languages)
- Built-in veterinary knowledge base for common symptoms and diagnoses
- Conversation history with automatic summarization
- Telegram bot interface with role and animal selection

## Architecture

The project consists of two main components:
- **Backend API** - FastAPI service handling RAG pipeline and conversation management
- **Telegram Bot** - User interface for interacting with the veterinary assistant

```
Telegram User
      ↓
Aiogram Bot (bot/)
      ↓
FastAPI Backend (backend/)
      ↓
  ┌───┴──────────────┐
Qdrant            Gemini       
(vectors)        (generation)
      ↓
Two-stage Retrieval:
1. multilingual-e5-large → query vector
2. Qdrant → top-10 candidates
3. cross-encoder/ms-marco-MiniLM → rerank → top-3
4. If found → answer with context
5. If not found → AiVeterinarian (direct LLM)
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + asyncio |
| Bot | Aiogram 3 |
| Vector DB | Qdrant Cloud |
| Embeddings | intfloat/multilingual-e5-large |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| LLM | Google Gemini (via LangChain) |
| History | JSON file storage |

## Installation

### Prerequisites
- Python 3.12+
- A Qdrant instance (Qdrant Cloud or a local container)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/AlmatUzakbayev/AI-VET.git
cd AI-VET
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables by copying `.env.example` to `.env`.
The backend needs only these; the rest of `.env.example` is optional:
```env
GOOGLE_API_KEY=your_google_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
```
The bot additionally needs:
```env
TELEGRAM_BOT_TOKEN=your_telegram_token
BACKEND_URL=http://localhost:8080
```

## Usage

### Running Locally

1. Start the backend API from the project root:
```bash
uvicorn backend.app.app:app --reload --port 8080
```

2. In a separate terminal, start the Telegram bot:
```bash
python -m bot.tg_app
```

3. Open the bot in Telegram, select your role and animal type, then start asking questions

## API Reference

### Users
- **POST** `/api/v1/ai-vet/users/create` — Create new user
- **GET** `/api/v1/ai-vet/users/{user_id}` — Get user profile
- **PATCH** `/api/v1/ai-vet/users/{user_id}` — Update role or animal

### Chat
- **POST** `/api/v1/ai-vet/ask` — Ask question (RAG pipeline)

### Documents
- **POST** `/api/v1/ai-vet/documents/upload` — Upload veterinary document
- **GET** `/api/v1/ai-vet/documents/` — List documents
- **DELETE** `/api/v1/ai-vet/documents/{id}` — Delete document

## Testing

The test suite covers the API, the RAG pipeline, document parsing, chunking and
entity extraction. The embedding models, Qdrant and the LLM are replaced with
fakes, so the tests need no API keys or network and run in a few seconds.

```bash
pip install -r requirements-test.txt
python -m nltk.downloader punkt_tab
pytest -v
```

| Area | What is checked |
|------|-----------------|
| API | Users, legacy bot endpoints, `/ask`, document upload and delete, validation errors (400 / 404 / 422) |
| Security | An upload filename like `../../evil.txt` cannot escape the uploads directory |
| RAG pipeline | Query enrichment with symptoms and animal, context from found documents, fallback to the built-in knowledge base |
| Chunking | Chunk size limit, `char_start` and page numbers, zero overlap |
| Parsing | TXT, DOCX and PDF (page map), language detection, unsupported formats |
| NER | Animals in any case form ("у коровы" → корова), symptoms, duration |

Tests run on every push via GitHub Actions.

## Known Limitations

- Every uploaded document is stored in Qdrant with `document_id = 1`, so search
  covers all documents together and `DELETE /documents/1` removes all of them.
- `GET /documents/` always returns an empty list.
- Conversation history is kept in memory and written to JSON files only on shutdown.

## Development Notes

- First startup downloads `multilingual-e5-large` (~2.2GB) — takes 10-30 min
- For faster testing use `sentence-transformers/all-MiniLM-L6-v2` (~90MB)
- Conversation history is saved to `database/saved_conversations/`
- User statuses are saved to `database/saved_user_statuses/`

## Security

- Never commit `.env` to version control
- Use secret managers for production deployments
- Regularly rotate API keys and tokens

## Roadmap

- [ ] Fine-tuning on veterinary datasets
- [ ] NLP classification of diseases by symptoms
- [ ] Integration with veterinary drug database
- [ ] Specialist referral system
- [ ] Web interface (React)
