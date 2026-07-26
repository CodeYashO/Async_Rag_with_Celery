# Async RAG

A FastAPI service that runs retrieval-augmented generation (RAG) **asynchronously** using [Celery](https://docs.celeryq.dev/) and Redis. Clients submit a chat message, receive a task ID immediately, and poll for the answer once the worker finishes similarity search and LLM generation.

## How it works

1. **POST `/async_rag/v1/chat`** — Enqueues a Celery task with the user message and returns `{ "id", "status": "queued" }`.
2. **Celery worker** — Runs `rag_pipeline`: embeds the query, searches Qdrant, builds context, and calls OpenAI.
3. **GET `/async_rag/v1/chat_result?id=<task_id>`** — Returns task status (`PENDING`, `STARTED`, etc.) or, when complete, `{ "status": "Completed", "result": "..." }`.

```
Client          FastAPI              Redis           Celery worker
  |                |                    |                  |
  | POST /chat     |                    |                  |
  |--------------->| process_chat.delay |                  |
  |                |------------------->|                  |
  |<-- task id ----|                    |                  |
  |                |                    |---- pull task -->|
  |                |                    |                  | RAG + OpenAI
  | GET /chat_result                    |<-- store result -|
  |--------------->| AsyncResult        |                  |
  |<-- result -----|                    |                  |
```

## Prerequisites

| Dependency | Purpose |
|------------|---------|
| **Redis** | Celery broker and result backend (`redis://localhost:6379/0`) |
| **Qdrant** | Vector store at `http://localhost:6333` with collection **`learning_rag`** |
| **OpenAI API key** | Embeddings (`text-embedding-3-large`) and chat (`gpt-4.1-nano`) |

Ensure your Qdrant collection is populated (embeddings and metadata such as `page_label` and `source`) before querying.

## Setup

1. Clone the repository and create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root (see `.gitignore`):

   ```env
   OPENAI_API_KEY=your_key_here
   ```

3. Start Redis and Qdrant locally (examples with Docker):

   ```bash
   docker run -d -p 6379:6379 redis:7
   docker run -d -p 6333:6333 qdrant/qdrant
   ```

## Running the app

Run these in **separate terminals** from the project root:

**API server**

```bash
uvicorn main:app --reload
```

**Celery worker**

```bash
celery -A celery_app.celery worker --loglevel=info
```

**Health check**

```bash
curl http://127.0.0.1:8000/health
```

Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API

### `POST /async_rag/v1/chat`

**Body**

```json
{
  "message": "Your question here"
}
```

**Response**

```json
{
  "id": "celery-task-uuid",
  "status": "queued"
}
```

### `GET /async_rag/v1/chat_result?id=<task_id>`

**Response (in progress)**

```json
{
  "status": "PENDING"
}
```

**Response (complete)**

```json
{
  "status": "Completed",
  "result": "Answer text with page references from RAG context"
}
```

### `GET /health`

```json
{
  "message": "server is running."
}
```

## Project layout

| File | Role |
|------|------|
| `main.py` | FastAPI app and health route |
| `routes.py` | Chat enqueue and result polling |
| `model.py` | Pydantic request models |
| `tasks.py` | Celery task wrapping `rag_pipeline` |
| `celery_app.py` | Celery app (Redis broker/backend) |
| `rag.py` | Qdrant similarity search + OpenAI completion |

## Configuration notes

- **Qdrant**: URL and collection name are set in `rag.py` (`http://localhost:6333`, `learning_rag`). Change these if your deployment differs.
- **Redis**: Broker and backend are configured in `celery_app.py` (database `0` on localhost).

## License

Add a license file if you plan to distribute this project.
