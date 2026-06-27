# Phase 4 Plan: Production Scale & Ecosystem

Adaptive Study Planner — Adaptive Learning Operating System
Version: 4.0.0-PROD
Date: 2026-06-26

---

## Context

Phase 3 delivered what the original roadmap called "Phase 4 Scale":
- ✅ Multi-user authentication (Supabase Auth)
- ✅ PostgreSQL + pgvector (Supabase)
- ✅ Cloud deployment (Cloudflare Worker + Supabase Edge Functions)
- ✅ Row Level Security (RLS)
- ✅ API gateway at the edge
- ✅ Document processing pipeline
- ✅ Collaborative groups and topic sharing

Phase 4 now focuses on **what remains**: production-grade inference, advanced renderers, ecosystem integration, and commercialization.

---

## Phase 4 Scope

| # | Capability | Description | Est. Effort | Priority |
|---|-----------|-------------|-------------|----------|
| 1 | **Production Inference** | vLLM or SGLang for GPU-accelerated LLM inference | 2 weeks | P0 |
| 2 | **Video Rendering Pipeline** | Scene planner → SVG → animation → TTS narration → export | 3-4 weeks | P1 |
| 3 | **Graph Database** | Neo4j/ArangoDB for concept/prerequisite graphs | 2 weeks | P1 |
| 4 | **Mobile PWA** | Progressive Web App with offline support | 2 weeks | P1 |
| 5 | **Real-time Collaboration** | Supabase Realtime for live study sessions | 1 week | P2 |
| 6 | **LMS Integration** | Canvas, Blackboard LTI 1.3 plugins | 2-3 weeks | P2 |
| 7 | **SAML/LDAP (B2B)** | Enterprise SSO for university/institutional sales | 2 weeks | P3 |
| 8 | **API v2 Productization** | Rate-limited public API with developer portal | 2 weeks | P3 |
| 9 | **Monetization** | Stripe billing, freemium tiers, usage metering | 2 weeks | P3 |
| 10 | **Observability** | Sentry + CloudWatch APM + custom dashboards | 1 week | P2 |

**Total estimated effort: 8-12 weeks**

---

## 1. Production Inference (P0)

### Problem
Ollama is sufficient for local development but lacks throughput for 100+ concurrent users. vLLM/SGLang provide 10-100x higher throughput via GPU batching.

### Design
```
User Request
│
▼
Cloudflare Worker
│
▼
vLLM / SGLang (GPU instance, e.g. AWS g5.xlarge)
│
▼
LLMProvider.generate() → cached response
```

### Implementation
- Deploy vLLM on AWS EC2 g5.xlarge or Lambda Labs GPU instance
- Use OpenAI-compatible API format (drop-in replacement for Ollama)
- Configure `LLMProvider` to use `http://vllm-endpoint:8000/v1/chat/completions`
- Add circuit breaker: if vLLM is down, fallback to Ollama (local) or OpenAI (paid)
- Benchmark: target < 500ms for RAG Q&A, < 2s for summarization

### Infrastructure
- AWS EC2 g5.xlarge (4 vCPU, 16GB, 1x A10G GPU) ~ $0.75/hr = ~$550/month
- Or Lambda Labs / CoreWeave for cheaper GPU pricing
- Docker container with vLLM serving Llama 3.1 8B (4-bit quantized)
- Auto-scaling: 1-3 instances based on queue depth

---

## 2. Video Rendering Pipeline (P1)

### Philosophy
Video is a **rendering pipeline**, not generative AI. Interactive education > passive video.

### Pipeline
```
Knowledge Content
│
▼
Scene Planner (deterministic: what to show, in what order)
│
▼
SVG Generator (vector graphics per scene)
│
▼
Animation Engine (CSS/JS or SVG SMIL animations)
│
▼
Narration (TTS from SpeechProvider, cached)
│
▼
Video Composition (ffmpeg: concat scenes + audio)
│
▼
Export (MP4/WebM)
```

### Components
- `ScenePlanner`: Python module that structures content into scenes
- `SVGRenderer`: Generates SVG diagrams from structured content
- `AnimationEngine`: Applies transitions, highlights, morphs
- `AudioComposer`: Stitches cached TTS segments with scene timings
- `VideoCompositor`: ffmpeg-based composition

### Output Formats
- MP4 (h.264) for broad compatibility
- WebM (VP9) for web streaming
- GIF for short loops
- Interactive HTML5 (fallback, no video export needed)

---

## 3. Graph Database (P1)

### Problem
PostgreSQL relational tables are inefficient for traversing concept relationships and prerequisite chains.

### Solution
Add Neo4j or ArangoDB as a **secondary store** for knowledge graphs.

### Data Model
```
(Concept:Calculus)-[:PREREQUISITE]->(Concept:Algebra)
(Concept:Calculus)-[:RELATED_TO]->(Concept:Physics)
(Topic:Integration)-[:PART_OF]->(Concept:Calculus)
(Document:Chapter3)-[:COVERS]->(Concept:Calculus)
```

### Use Cases
- Prerequisite-aware planning: "You can't study Integration until you review Algebra"
- Concept gap analysis: "You're missing prerequisites for 3 topics"
- Study path optimization: shortest path to exam readiness

### Integration
- Sync graph from PostgreSQL chunks on document ingestion
- Read graph for planning; write to PostgreSQL for persistence
- ArangoDB preferred (multi-model: documents + graph + search)

---

## 4. Mobile PWA (P1)

### Problem
Frontend is desktop-only. Students study on phones.

### Solution
Progressive Web App with:
- Service Worker for offline caching
- IndexedDB for offline state (syncs when online)
- Push notifications for study reminders
- Responsive design (already partially done)
- Installable (add to home screen)
- Native app wrapper (Capacitor or Tauri) for app store distribution

### Features
- Offline study plan generation (deterministic core runs in browser via WASM or JS port)
- Offline session logging (queues for sync)
- Audio playback (cached TTS) offline
- Push notifications: "Time to study Calculus"

---

## 5. Real-time Collaboration (P2)

### Solution
Supabase Realtime for live group study sessions.

### Features
- Live cursor positions in shared whiteboard
- Real-time quiz competition (group study mode)
- Live annotation on documents
- Presence: who is studying what right now

---

## 6. LMS Integration (P2)

### Target Platforms
- Canvas (Instructure) — LTI 1.3 Advantage
- Blackboard — REST API + LTI
- Moodle — LTI + Web Services

### Integration Points
- Import course syllabus → auto-generate topics
- Export study plan → Canvas calendar events
- Import quiz results → auto-update U (user performance)
- SSO via LTI (no separate auth needed)

---

## 7. SAML/LDAP (P3)

### Target
University B2B sales. Centralized identity via existing university IdP.

### Solution
- SAML 2.0 via Supabase Auth (Enterprise SSO)
- LDAP for on-premise Active Directory
- Separate enterprise tier pricing

---

## 8. API v2 Productization (P3)

### Public API
- `/v2/plan` — generate study plan
- `/v2/topics` — CRUD topics
- `/v2/knowledge` — query knowledge layer
- `/v2/render` — render content to any format
- Rate limits: 100 req/min free, 1000 req/min pro, 10,000 req/min enterprise
- API keys with scopes (read/write/admin)

### Developer Portal
- API documentation (OpenAPI spec)
- SDKs: Python, JavaScript, TypeScript
- Webhooks: study plan generated, document processed

---

## 9. Monetization (P3)

### Freemium Tiers

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | 10 topics, local AI only, basic renderers |
| Pro | $9/mo | Unlimited topics, cloud AI, all renderers, groups |
| Team | $29/mo | 5 users, shared workspaces, LMS integration |
| Enterprise | Custom | SAML, SLA, dedicated support, custom inference |

### Billing
- Stripe subscriptions
- Usage metering: API calls, document pages, video minutes, AI tokens
- Team billing: admin dashboard for seat management

---

## 10. Observability (P2)

### Stack
- Sentry: error tracking + performance monitoring (APM)
- CloudWatch: infrastructure metrics (ECS, RDS, ALB)
- Custom dashboard: provider usage, renderer usage, cache hit rates, knowledge layer size
- Alerting: PagerDuty or Slack for critical errors

---

## Infrastructure Evolution (Phase 4)

```
Phase 3 (Current)
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Browser   │────▶│  Cloudflare Edge  │────▶│  Supabase Edge   │
│  (frontend) │     │  (Worker / CDN)   │     │  (Auth / DB)     │
└─────────────┘     └──────────────────┘     └──────────────────┘

Phase 4 (Production)
┌─────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   PWA /     │────▶│  Cloudflare CDN  │────▶│  Cloudflare      │
│   Mobile    │     │  + Workers       │     │  Worker (API)    │
└─────────────┘     └──────────────────┘     └──────────────────┘
                                                      │
                       ┌──────────────────┐    ┌────┴────┐
                       │  vLLM / SGLang   │◄───│  RAG    │
                       │  (GPU Inference) │    │  Engine │
                       └──────────────────┘    └─────────┘
                              │
                       ┌──────┴──────┐
                       │  ArangoDB   │ (Graph)
                       │  (Neo4j)    │
                       └─────────────┘
                              │
                       ┌──────┴──────┐
                       │  Supabase   │
                       │  PostgreSQL │ (Primary DB)
                       │  + pgvector │
                       └─────────────┘
```

---

## Migration Path from Phase 3

1. **Production Inference**: Add vLLM endpoint, update `LLMProvider` config. No code changes to business logic.
2. **Video Pipeline**: New renderer in `backend/rendering/`. Add `VideoRenderer` to registry.
3. **Graph DB**: Add `GraphStore` abstraction alongside `VectorStore`. Sync on document ingestion.
4. **PWA**: Add service worker + manifest to `frontend/`. Port deterministic core to JS or WASM.
5. **Realtime**: Enable Supabase Realtime on tables. Add `supabase.channel()` to frontend.
6. **LMS**: New `lms/` module with LTI adapters. No changes to core.
7. **SAML**: Supabase Auth enterprise config. No code changes.
8. **API v2**: New route handlers in Cloudflare Worker. Version existing routes.
9. **Monetization**: Stripe webhook handler. Add `subscriptions` table.
10. **Observability**: Sentry SDK integration. CloudWatch agent on inference servers.

---

## Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| LLM inference latency | < 500ms p95 | vLLM benchmarks |
| Video generation time | < 2 min per minute of content | Pipeline benchmarks |
| Graph query latency | < 100ms | ArangoDB profiler |
| PWA offline functionality | 100% of core features | Manual testing |
| API uptime | 99.9% | CloudWatch / Sentry |
| Concurrent users | 1,000+ | Load testing with k6 |
| Revenue | $1,000 MRR | Stripe dashboard |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| vLLM GPU costs exceed budget | Medium | High | Start with Lambda Labs; monitor costs daily; fallback to OpenAI |
| Video pipeline too complex for 3-4 weeks | Medium | Medium | De-scope to "interactive HTML5" first; MP4 export later |
| Graph DB adds ops burden | Medium | Medium | ArangoDB managed (Oasis); or defer to Phase 4.5 |
| Mobile PWA adoption low | Low | Medium | Analytics on install rate; pivot to native app if < 10% |
| LMS integration blocked by IT | High | Medium | Start with Canvas (most open API); offer manual CSV import fallback |

---

## Decision: Proceed with Phase 4?

Phase 4 is **well-defined** and **technically feasible**. The architecture from Phase 3 supports all Phase 4 capabilities without redesign.

**Recommendation:** Start with P0 (Production Inference) and P1 (Video + Graph + PWA) in parallel. These are the highest-value differentiators.

**Dependencies:**
- vLLM GPU instance budget approved
- Video pipeline designer/animator resource identified
- Mobile PWA developer capacity available

---

*This plan replaces all prior Phase 4 references in the documentation. The original Phase 4 scope (multi-user, PostgreSQL, auth) has been completed in Phase 3 and is no longer part of Phase 4.*
