# AI Chatbot (FastAPI + OpenRouter + Vanilla JS)

## Setup

1) Create an OpenRouter key and set it in `.env`:

```bash
OPENROUTER_API_KEY=your_key_here
```

2) Install backend deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run backend (localhost:8000)

```bash
uvicorn backend.main:app --reload --port 8000
```

## Open frontend

Option A (recommended): serve the `frontend/` folder:

```bash
cd frontend
python -m http.server 5173
```

Then open `http://localhost:5173`.

Option B: open `frontend/index.html` directly (may be limited by browser security in some setups).

## API

- `POST /chat`
  - Request JSON: `{ "message": "string" }`
  - Response JSON: `{ "reply": "string" }`

