from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


load_dotenv()  # reads .env at project root (when running from repo)


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL", "mistralai/mistral-7b-instruct-v0.1"
).strip()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


def _extract_reply(openrouter_json: Dict[str, Any]) -> str:
    """
    OpenRouter response is OpenAI-compatible:
      { "choices": [ { "message": { "role": "...", "content": "..." } } ] }
    """
    try:
        choices = openrouter_json.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("Missing choices")

        msg = choices[0].get("message")
        if not isinstance(msg, dict):
            raise ValueError("Missing message")

        content = msg.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Missing content")

        return content.strip()
    except Exception as exc:
        raise ValueError(f"Invalid OpenRouter response shape: {exc}") from exc


def call_openrouter(user_message: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Recommended by OpenRouter for app identification.
        "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost"),
        "X-Title": os.getenv("OPENROUTER_APP_TITLE", "ai-chatbot"),
    }

    payload: Dict[str, Any] = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
    except requests.RequestException as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

    if resp.status_code >= 400:
        # Try to surface useful error info without crashing on non-JSON bodies.
        detail: Optional[str] = None
        try:
            err = resp.json().get("error")
            if isinstance(err, dict):
                detail = str(err.get("message") or err.get("code") or err)
            elif err is not None:
                detail = str(err)
        except Exception:
            detail = resp.text[:500] if resp.text else None
        raise RuntimeError(f"OpenRouter returned {resp.status_code}: {detail or 'Unknown error'}")

    try:
        data = resp.json()
    except ValueError as exc:
        raise RuntimeError("OpenRouter returned non-JSON response") from exc

    return _extract_reply(data)


app = FastAPI(title="AI Chatbot API", version="1.0.0")

# Allow local frontend (file://, http://localhost, etc.) during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    message = (req.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        reply = call_openrouter(message)
        return ChatResponse(reply=reply)
    except RuntimeError as exc:
        # API/network/config issues
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        # Unexpected response parsing issues
        raise HTTPException(status_code=502, detail=str(exc)) from exc

