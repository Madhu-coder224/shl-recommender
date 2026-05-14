# SHL Assessment Recommender API

A FastAPI backend service that acts as an AI-powered chatbot recommending SHL HR assessments based on job role queries.

## Run & Operate

- Workflow: `artifacts/api-server: API Server` — runs uvicorn on port 8080
- Required env: `GEMINI_API_KEY` — Google AI Studio API key

## Stack

- Python 3 + FastAPI + Uvicorn
- Google Gemini 2.5 Flash via `google-genai` SDK
- Pydantic for request/response validation

## Where things live

- `artifacts/api-server/main.py` — entire FastAPI app, system prompt, and Gemini wiring
- `artifacts/api-server/requirements.txt` — Python dependencies

## API Endpoints

- `GET /health` — returns `{"status": "ok"}`
- `POST /chat` — takes `{"messages": [{"role": "user"|"assistant", "content": "..."}]}`, returns `{"reply": "...", "recommendations": [{"name": "...", "description": "...", "url": "https://shl.com/..."}], "end_of_conversation": false}`

## Architecture decisions

- Routes are prefixed with `/api` to match the shared reverse proxy path routing
- Gemini is called with `response_mime_type: "application/json"` to enforce structured output; falls back gracefully if parsing fails
- System prompt embeds the full SHL assessment catalog with usage guidance per assessment
- `end_of_conversation` is set to `true` only when user signals they are done (e.g., "thanks", "goodbye")

## Product

HR professionals and hiring managers can send job role queries in a multi-turn chat and receive curated SHL assessment recommendations with justifications.

## User preferences

- Python FastAPI (not Node.js/Express)
- Uses own Gemini API key (`GEMINI_API_KEY`)

## Gotchas

- The Replit Gemini AI Integration proxy only works with the JS/TS SDK — the Python `google-genai` client must use a real API key directly
- Routes must include the `/api` prefix since the shared proxy does not strip path prefixes
