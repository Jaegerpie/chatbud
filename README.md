# AI Chatbot (FastAPI + OpenRouter + Vanilla JS)

## Prerequisites

- Git
- Python 3.10+
- An OpenRouter API key

## Setup

1) Clone and enter the project:

```bash
git clone https://github.com/Jaegerpie/chatbud.git
cd chatbud
```

2) Create your local env file from template:

```bash
cp .env.example .env
```

Then set your key in `.env`:

```bash
OPENROUTER_API_KEY=your_key_here
```

3) Create a virtual environment and install dependencies:

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
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

## Security note

- Never commit `.env`.
- If a key is exposed, revoke/rotate it immediately in OpenRouter.

## API

- `POST /chat`
  - Request JSON: `{ "message": "string" }`
  - Response JSON: `{ "reply": "string" }`

