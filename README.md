# Adaptive Study Planner

Adaptive Learning Operating System — deterministic study planning with provider-agnostic AI.

> **Knowledge First. Rendering Second. AI Third.**

---

## Quick Start

```bash
cd adaptive-study-planner
pip install -r requirements.txt

# Phase 1: CLI
python scoring_test/cli.py plan
python scoring_test/cli.py dashboard

# Phase 1: Flask UI
python scoring_test/flask_app.py
# Open http://localhost:5000

# Phase 1: Streamlit Dashboard
streamlit run scoring_test/dashboard.py

# Phase 3: Frontend (Supabase-backed)
# Open frontend/index.html in browser or serve with any static server
python -m http.server 8080 --directory frontend
```

---

## Architecture

```
User
│
▼
Planner (Deterministic Core)  → scorer.py + services.py + predictor.py
│
▼
Knowledge Layer  → Docling → Semantic Chunker → FAISS / pgvector
│
▼
Reasoning Layer  → RAG Engine → LLMProvider (Ollama / OpenAI)
│
▼
Rendering Layer  → Text / Markdown / HTML / Slides / Quiz / Audio
│
▼
Output
```

| Layer | Deterministic? | Key File |
|-------|---------------|----------|
| Planner | **Yes** | `scoring_test/services.py` |
| Knowledge | **Yes** | `backend/knowledge/` |
| Reasoning | No | `backend/reasoning/rag_engine.py` |
| Rendering | **Yes** | `backend/rendering/` |

---

## Provider Interfaces

| Capability | Default | Optional Paid |
|-----------|---------|---------------|
| LLM | Ollama (local) | OpenAI, Gemini, Anthropic |
| Embeddings | BAAI/BGE (local) | OpenAI, Jina, Nomic |
| TTS | Kokoro (local) | ElevenLabs, Piper, Coqui |

Swap providers with zero code changes. Config only.

---

## Project Layout

```
adaptive-study-planner/
├── scoring_test/          # Phase 1 MVP
│   ├── scorer.py
│   ├── services.py
│   ├── predictor.py
│   ├── cli.py
│   ├── flask_app.py
│   ├── dashboard.py
│   ├── templates/
│   └── static/
├── backend/               # Phase 2+ layers
│   ├── providers/         # LLM, Embedding, Speech abstractions
│   ├── knowledge/         # Docling, chunking, FAISS
│   ├── reasoning/         # RAG engine
│   └── rendering/         # Text, HTML, slides, quiz, audio
├── frontend/              # Phase 3 standalone SPA (Supabase auth)
│   ├── index.html
│   └── phase3-app.js
├── cloudflare-worker/     # Phase 3 API gateway
│   ├── worker.js
│   └── wrangler.toml
├── tests/
│   └── test_core.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── SECURITY.md
├── ENGINEERING_REVIEW.md
└── INDEPENDENT_REVIEW.md
```

---

## Phase 3 Infrastructure

| Component | Provider | Status | URL |
|-----------|----------|--------|-----|
| Database | Supabase PostgreSQL + pgvector | ✅ Ready | `blowpaeftobvczysekrr.supabase.co` |
| Edge Function | Supabase Edge Functions | ✅ Deployed | `/functions/v1/process-document` |
| API Gateway | Cloudflare Worker | 📝 Code ready | Deploy with `wrangler deploy` |
| Object Storage | Cloudflare R2 | 🔄 Enable in dashboard | `ff42f7b54f53ec415f8d196d19501f32` |
| Auth | Supabase Auth | ✅ Built-in | Email/Password + OAuth |
| Frontend | Static HTML/JS | ✅ Built | `frontend/index.html` |

---

## Environment Variables

```bash
# Phase 1 / 2
FLASK_DEBUG=false              # true for local dev only
FLASK_PORT=5000
CORS_ORIGINS=*                 # comma-separated for production
RATE_LIMIT_WINDOW=60
RATE_LIMIT_MAX=30

# Phase 3 (Supabase)
SUPABASE_URL=https://blowpaeftobvczysekrr.supabase.co
SUPABASE_KEY=sb_publishable_ZhJf8u6YjuDewlJp1tTfJw_p7eu8NpH

# AI Providers (optional — local defaults require no keys)
# OPENAI_API_KEY=sk-...
# ELEVENLABS_API_KEY=...

# Ollama (local default)
OLLAMA_BASE_URL=http://localhost:11434
```

---

## License

MIT
