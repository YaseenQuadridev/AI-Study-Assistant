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
├── tests/
│   └── test_core.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Infrastructure

| Phase | Target | Status |
|-------|--------|--------|
| Phase 1 | Local / JSON file | ✅ Built |
| Phase 2 | FAISS vector store (local) | ✅ Built |
| Phase 3 | Supabase PostgreSQL + pgvector | ✅ Schema created |
| Phase 3 | Cloudflare R2 | 🔄 Enable in dashboard |

**Environment variables:**
- `FLASK_DEBUG` — set `true` for local dev only
- `CORS_ORIGINS` — comma-separated allowed origins (default `*` for dev)
- `RATE_LIMIT_WINDOW` — seconds per window (default 60)
- `RATE_LIMIT_MAX` — requests per window (default 30)

**Supabase Project:** `blowpaeftobvczysekrr`
**Cloudflare Account:** `ff42f7b54f53ec415f8d196d19501f32`

---

## License

MIT
