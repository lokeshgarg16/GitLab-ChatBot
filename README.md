# GitLab Handbook RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built for GitLab Handbook and Direction content.

## Project Overview

- **Backend:** FastAPI + Python
- **Frontend:** React + Tailwind CSS + Vite
- **Vector DB:** ChromaDB
- **LLM / Embeddings:** Google Gemini via LangChain
- **Memory:** Redis optional conversation memory
- **Features:** document upload, delete, list, chat history, source citations

## Folder Structure

- `backend/` — FastAPI backend, ingestion scripts, and API routers
- `frontend/` — React chat UI and upload UI
- `docker-compose.yml` — optional local services
- `vercel.json` — frontend deployment config
- `render.yaml` — deploy configuration

## Features

- Chat UI with saved sessions and dark mode
- RAG-powered answers with source citations
- Upload documents from the UI
- Supported upload formats: `.txt`, `.md`, `.html`, `.pdf`, `.csv`
- UI shows uploaded documents and chunk counts
- Delete uploaded documents mid-chat and flush them from ChromaDB
- Redis-backed memory is optional and fails gracefully if unavailable

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-org/gitlab-rag-chatbot.git
cd gitlab-rag-chatbot
```

### 2. Configure environment variables

Create `backend/.env` with your values, for example:

```env
GEMINI_API_KEY=your_gemini_api_key
REDIS_URL=redis://localhost:6379/0
CHROMA_PERSIST_DIRECTORY=./data/chroma
CHROMA_COLLECTION_NAME=gitlab_handbook
MAX_CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

### 3. Install dependencies

#### Backend

```bash
cd backend
python -m pip install -r requirements.txt
```

#### Frontend

```bash
cd ../frontend
npm install
```

### 4. Run the backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 5. Run the frontend

```bash
cd frontend
npm run dev
```

Then open the browser at `http://localhost:5173`.

## Upload and Document Management

### Upload documents

Use the frontend Upload button to add files directly into ChromaDB. Supported file types:

- `.txt`
- `.md` / `.markdown`
- `.html` / `.htm`
- `.pdf`
- `.csv`

### See uploaded documents

The UI includes an "Uploaded documents" panel showing current sources and chunk counts.

### Delete uploaded documents mid-chat

Use the Delete button next to any uploaded document to remove its vectors from ChromaDB.

## API Endpoints

### `GET /health/`

Health check endpoint.

### `POST /chat/`

Query the chatbot.

Example request:

```json
{
  "query": "How does GitLab handle product direction planning?",
  "session_id": "session-1"
}
```

### `POST /upload/`

Upload a file using multipart form data.

### `GET /upload/`

List uploaded document sources and their chunk counts.

### `DELETE /upload/{source}`

Delete documents from ChromaDB by source name.

## Notes

- Chroma persistence is used for uploaded document vectors.
- The frontend automatically refreshes uploaded document state after upload and deletion.
- If Redis is unavailable, chat memory will still work without failing.

## Troubleshooting

- If upload fails, make sure `python-multipart` and `pdfplumber` are installed in `backend/requirements.txt`.
- If the frontend cannot reach the backend, verify `VITE_API_URL` or the default backend URL `http://localhost:8000`.
- If Chroma storage is not persisted, ensure `CHROMA_PERSIST_DIRECTORY` is writable.

## Recommended Deployment (Render)

This project is ready to deploy on Render for a simple, managed experience (both backend and frontend). The repo includes `render.yaml` which configures a Docker backend service and a static frontend site.

Quick steps:

1. Sign in to Render and connect your GitHub repository.
2. Choose to create services from `render.yaml` (Render will detect and use the manifest).
3. Add a secret `GEMINI_API_KEY` in Render for the backend service.
4. Provision Redis on Render or set `REDIS_URL` to an external Redis provider (e.g., Upstash).
5. Deploy — Render will build backend from `backend/Dockerfile` and frontend from `frontend` config.

Alternatives:
- Frontend on Vercel + Backend on Render (set `VITE_API_URL` accordingly).
- Deploy with Docker Compose / Kubernetes on your own cloud provider if you need full control.

