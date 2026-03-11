# AI Veterinary Assistant

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
Qdrant           Gemini/OpenAI
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
| LLM | Google Gemini / OpenAI GPT |
| History | JSON file storage |

## Installation

### Prerequisites
- Python 3.12+
- Docker and docker-compose (for containerized deployment)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-vet-dev
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables by creating a `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_telegram_token
GOOGLE_API_KEY=your_google_key
OPENAI_API_KEY=your_openai_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key
BACKEND_URL=http://localhost:8080
```

## Usage

### Running Locally

1. Start the backend API:
```bash
cd backend/app
uvicorn app:app --reload --port 8080
```

2. In a separate terminal, start the Telegram bot:
```bash
python -m bot.tg_app
```

3. Open the bot in Telegram, select your role and animal type, then start asking questions

### Running with Docker
```bash
docker-compose up --build
```

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
