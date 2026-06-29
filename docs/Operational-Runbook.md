# Operational Runbook (ORB)

## AI Study Assistant — Phase 4.1.0 ENTERPRISE

**Version:** 1.0.0
**Date:** 2026-06-28
**Status:** Approved — Production Ready
**Owner:** Platform Engineering & SRE Team
**Authors:** Principal SRE, Principal Platform Engineer, Principal Cloud Architect, Principal Security Engineer, Principal AI Infrastructure Engineer, DevSecOps Lead, Compliance Architect
**Reviewers:** CTO, Engineering Lead, Security Lead, AI Infrastructure Lead
**Approval Date:** 2026-06-28
**Next Review:** 2026-09-28 (Quarterly)
**Classification:** Internal — Operational Use Only

---

## Document Control

| Version | Date | Author | Changes | Approved By |
|---------|------|--------|---------|-------------|
| 1.0.0 | 2026-06-28 | Platform Engineering & SRE Team | Initial enterprise release | CTO |

---

## Table of Contents

1. Executive Summary
2. Production Architecture
3. Infrastructure Inventory
4. Deployment Strategy
5. Monitoring
6. Incident Response
7. Disaster Recovery
8. Operational Procedures
9. Security Operations
10. AI Operations (AIOps)
11. Capacity Planning
12. Performance Operations
13. Support Operations
14. Operational Checklists
15. Production Readiness Checklist
16. Appendices

---

## 1. Executive Summary

### 1.1 Production Environment

The Adaptive Study Planner (ASP) operates as a **multi-tenant SaaS platform** serving students, educators, and institutional clients globally. The platform ingests educational documents (PDFs, images, DOCX, PPTX, EPUB), processes them through a 14-stage AI pipeline, and constructs a personalized, structured knowledge base for each user. AI-powered study assistance — including Q&A, flashcards, quizzes, study plans, and knowledge graph visualization — is strictly grounded in the user's own uploaded materials or automatically discovered official sources.

The platform is architected as a **serverless-first, edge-deployed, AI-native application** with the following production characteristics:

| Attribute | Value | Rationale |
|-----------|-------|-----------|
| Deployment Model | Multi-cloud (Cloudflare + Supabase) | Edge latency, global reach, managed services |
| Tenant Isolation | Database-level RLS | Strict data segregation per user |
| AI Inference | Local-first (Ollama/vLLM) with cloud fallback (OpenAI) | Cost control, privacy, zero egress |
| Storage | Object storage (R2) with cross-region replication | Zero egress fees, disaster recovery |
| Backup | Automated daily + Telegram cold backup | Multi-layer resilience |
| Compliance | GDPR, CCPA, DPDP (India) ready; SOC 2 Type II roadmap | Global student privacy requirements |

### 1.2 Deployment Model

| Layer | Technology | Deployment Model | Region |
|-------|------------|-----------------|--------|
| API Gateway | Cloudflare Workers | Serverless edge | Global (250+ PoPs) |
| Frontend | Cloudflare Pages | Static CDN | Global |
| AI Pipeline | Supabase Edge Functions | Serverless (region-bound) | User-selected |
| Database | Supabase PostgreSQL + pgvector | Managed (primary + read replicas) | User-selected |
| Object Storage | Cloudflare R2 | S3-compatible, cross-region | Multi-region |
| Cache | Upstash Redis | Serverless, auto-scaling | Multi-region |
| AI Inference | Ollama / vLLM | Self-hosted GPU / CPU | User-selected or dedicated |
| Monitoring | Grafana + Sentry + PagerDuty | Managed SaaS | Multi-region |
| CI/CD | GitHub Actions | Cloud-native | Global |
| Feature Flags | LaunchDarkly | Managed SaaS | Global |

### 1.3 Operational Philosophy

| Principle | Description | Implementation |
|-----------|-------------|---------------|
| **You Build It, You Run It** | Every engineering team owns their services in production | Team-based on-call, team-owned SLOs |
| **SRE First** | Error budgets, SLO-driven prioritization, blameless postmortems | Monthly error budget reviews, mandatory postmortems |
| **Automation by Default** | All repeatable operational procedures must be automated | GitOps, IaC, automated runbooks |
| **Observability by Design** | Every service emits metrics, logs, and traces by default | OpenTelemetry, structured JSON logging, golden signals |
| **Security by Default** | Zero trust architecture, least privilege, defense in depth | RBAC, RLS, MFA, encryption everywhere |
| **Local-First AI** | Default to free, local AI models; cloud only as fallback | Ollama default, OpenAI opt-in |
| **Graceful Degradation** | Every service has a fallback chain | Circuit breakers, fallback LLMs, cached responses |

### 1.4 Reliability Goals

| Metric | Target (SLO) | SLA (Customer-facing) | Measurement |
|--------|-------------|----------------------|-------------|
| Platform Uptime | 99.95% | 99.9% | Synthetic probe every 30s |
| API p95 Latency | < 300ms | < 500ms | APM (Sentry) |
| Retrieval p95 Latency | < 150ms | < 200ms | APM |
| AI Response p95 Latency | < 1.5s | < 2s | APM |
| Document Processing Success Rate | 99.8% | 99.5% | Log analysis |
| OCR Accuracy (printed text) | > 90% | > 85% | Weekly sample |
| OCR Accuracy (handwritten) | > 75% | > 70% | Weekly sample |
| Citation Verification Accuracy | 100% | 100% | Per-response verification |
| Hallucination Rate | 0% | 0% | Weekly AI evaluation |
| Embedding Generation Success Rate | 99.9% | 99.5% | Log analysis |
| Knowledge Graph Query Latency (≤3 hops) | < 100ms | < 150ms | APM |
| Cache Hit Rate | > 80% | > 70% | Redis metrics |

### 1.5 Service Ownership

| Service | Primary Owner | On-Call Rotation | Escalation Path | Documentation |
|---------|-------------|-----------------|-----------------|---------------|
| Cloudflare Workers (API Gateway) | Platform Engineering | P1: 15 min | SRE Lead → CTO | Section 3.2, 3.3 |
| Cloudflare Pages (Frontend) | Frontend Engineering | P2: 1 hour | Frontend Lead → SRE Lead | Section 3.1 |
| Supabase PostgreSQL (Primary DB) | Database Engineering | P1: 15 min | DBA Lead → SRE Lead | Section 3.5 |
| Supabase Edge Functions (AI Pipeline) | AI Infrastructure | P1: 15 min | AI Infra Lead → SRE Lead | Section 3.11 |
| pgvector (Vector Search) | Database Engineering | P1: 15 min | DBA Lead → AI Infra Lead | Section 3.5 |
| Cloudflare R2 (Object Storage) | Platform Engineering | P2: 1 hour | SRE Lead → CTO | Section 3.4 |
| Upstash Redis (Cache & Queues) | Platform Engineering | P2: 1 hour | SRE Lead → CTO | Section 3.12 |
| Ollama / vLLM (AI Inference) | AI Infrastructure | P1: 15 min | AI Infra Lead → CTO | Section 3.11 |
| OpenAI Fallback | AI Infrastructure | P2: 1 hour | AI Infra Lead → CTO | Section 3.11 |
| OCR Pipeline (Tesseract / Google Vision / MathPix) | AI Infrastructure | P2: 1 hour | AI Infra Lead → CTO | Section 3.11 |
| Embedding Pipeline (BAAI/BGE / OpenAI) | AI Infrastructure | P2: 1 hour | AI Infra Lead → CTO | Section 3.11 |
| Hybrid Retrieval Engine | AI Infrastructure | P1: 15 min | AI Infra Lead → CTO | Section 3.11 |
| Citation Engine | AI Infrastructure | P2: 1 hour | AI Infra Lead → CTO | Section 3.11 |
| Knowledge Graph Service | Database Engineering | P2: 1 hour | DBA Lead → AI Infra Lead | Section 3.6 |
| Monitoring & Alerting Stack | SRE | P0: 5 min | SRE Lead → CTO | Section 3.7 |
| Security Operations (WAF, SIEM, IAM) | Security Engineering | P1: 15 min | Security Lead → CTO | Section 3.9, 9 |
| CI/CD Pipeline | DevOps | P2: 1 hour | DevOps Lead → SRE Lead | Section 3.10 |
| Feature Flag Management | Platform Engineering | P3: 4 hours | SRE Lead → CTO | Section 4.4 |

### 1.6 Support Responsibilities

| Tier | Hours | Response Time | Scope | Escalation Path |
|------|-------|--------------|-------|-----------------|
| L1 — Support Engineering | 24/7 | 15 minutes | User issues, password resets, basic troubleshooting, FAQ | Escalate to L2 after 30 min |
| L2 — Platform Engineering | 24/7 | 1 hour | API issues, performance degradation, deployment failures, non-critical infrastructure | Escalate to L3 after 2 hours |
| L3 — SRE / AI Infrastructure | 24/7 | 15 minutes | Infrastructure outages, AI pipeline failures, data corruption, security incidents, critical performance | Escalate to L4 after 1 hour |
| L4 — Engineering Leadership | Business hours (09:00–18:00 UTC) | 4 hours | Architectural decisions, major security incidents, vendor escalations, budget approvals | CTO involvement for SEV-0 |
| L5 — Executive / CTO | On-demand | As needed | Data breaches, regulatory incidents, complete platform outages, vendor contract disputes | Board notification for legal/regulatory |

---

## 2. Production Architecture

### 2.1 Production Topology (ASCII Diagram)

```
                              Internet
                                 |
                    +------------+------------+
                    |      Cloudflare CDN     |
                    |   (WAF + DDoS + Cache)  |
                    +------------+------------+
                                 |
              +------------------+------------------+
              |                                      |
     +--------v--------+                    +--------v--------+
     |  Cloudflare     |                    |  Cloudflare     |
     |  Workers        |                    |  Pages          |
     |  (API Gateway)  |                    |  (Static PWA)   |
     |  • Rate Limit   |                    |  • Service Worker|
     |  • JWT Validate |                    |  • Offline Cache |
     |  • CORS Handle  |                    |  • PWA Manifest |
     +--------+--------+                    +-----------------+
              |
     +--------v--------+
     |  Supabase Edge  |
     |  Functions      |
     |  (AI Pipeline)  |
     |  • Document     |
     |    Processing   |
     |  • Embedding    |
     |  • Citation     |
     |  • Graph Build  |
     +--------+--------+
              |
     +--------v--------+
     |  Supabase       |
     |  PostgreSQL     |
     |  + pgvector     |
     |  + RLS          |
     |  + Read Replica |
     +--------+--------+
              |
     +--------v--------+
     |  Upstash Redis  |
     |  • Cache        |
     |  • Queues       |
     |  • Rate Limit   |
     |  • Session Store|
     +--------+--------+
              |
     +--------v--------+
     |  Cloudflare R2  |
     |  (Object Store) |
     |  • Documents    |
     |  • Thumbnails   |
     |  • Audio Cache  |
     |  • Exports      |
     |  • Backups      |
     +-----------------+
              |
     +--------v--------+
     |  AI Inference   |
     |  • Ollama (CPU) |
     |  • vLLM (GPU)   |
     |  • OpenAI       |
     |    (Fallback)   |
     +-----------------+
```

### 2.2 Environment Definitions

#### 2.2.1 Development

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Local development, feature experimentation, unit testing |
| **URL** | `http://localhost:8787` (Wrangler dev), `http://localhost:3000` (frontend) |
| **Database** | Local PostgreSQL 15 + pgvector (Docker Compose) |
| **AI** | Local Ollama (llama3.2:latest, CPU) |
| **Storage** | Local MinIO (S3-compatible) |
| **Cache** | Local Redis (Docker) |
| **Access** | Individual developers only |
| **Data** | Synthetic test data only; no production data |
| **Deployment** | Manual (`wrangler dev`, `docker-compose up`) |
| **Monitoring** | Console logs only |
| **Security** | No TLS, no WAF, relaxed CORS |
| **SLA** | None — best effort |

#### 2.2.2 Testing (CI)

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Automated test execution on every PR/commit |
| **URL** | Ephemeral (GitHub Actions runners, GitHub Codespaces) |
| **Database** | Supabase dev project (isolated schema, reset per run) |
| **AI** | Ollama (CI runner, CPU-only, llama3.2) |
| **Storage** | R2 dev bucket (`adaptive-study-planner-dev`) |
| **Cache** | Upstash Redis (dev instance) |
| **Access** | CI/CD pipeline only (GitHub Actions service accounts) |
| **Data** | Synthetic fixtures + anonymized production snapshots (no PII) |
| **Deployment** | Fully automated on every PR push |
| **Monitoring** | Test result artifacts in GitHub Actions |
| **Security** | Ephemeral credentials, no long-lived secrets |
| **SLA** | None — test failures block merge |

#### 2.2.3 Staging

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Pre-production validation, integration testing, load testing, security review |
| **URL** | `https://staging.adaptive-study-planner.com` |
| **Database** | Supabase staging project (migrated nightly from production snapshot, anonymized) |
| **AI** | vLLM (GPU, staging cluster, single node) |
| **Storage** | R2 staging bucket (`adaptive-study-planner-staging`) |
| **Cache** | Upstash Redis (staging instance) |
| **Access** | Engineering team, QA team, security team, approved beta users |
| **Data** | Anonymized production snapshot (7 days old), no PII, no real credentials |
| **Deployment** | Automated on merge to `develop` branch; manual gate for database migrations |
| **Monitoring** | Full observability stack (Grafana, Sentry, Jaeger) |
| **Security** | TLS 1.3, WAF in log-only mode, RBAC enforced, RLS enabled |
| **SLA** | 99.0% — staging is not production |
| **Feature Flags** | All flags enabled for testing; canary at 100% |

#### 2.2.4 Production

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Live customer-facing service |
| **URL** | `https://adaptive-study-planner.com` |
| **Database** | Supabase production project (primary + 2 read replicas, PgBouncer) |
| **AI** | vLLM (GPU, production cluster, 2+ nodes) + OpenAI fallback (if enabled) |
| **Storage** | R2 production bucket (`adaptive-study-planner-prod`) with cross-region replication |
| **Cache** | Upstash Redis (production cluster, 2+ shards) |
| **Access** | Customers, SRE on-call, emergency admin access (JIT only) |
| **Data** | All customer data, encrypted at rest, RLS-enforced |
| **Deployment** | Manual approval after staging validation + security sign-off |
| **Monitoring** | Full observability stack + synthetic monitoring (Pingdom/UptimeRobot) |
| **Security** | TLS 1.3, WAF active, DDoS protection, RBAC + RLS + MFA, field-level encryption |
| **SLA** | 99.9% uptime, 99.5% processing success, < 500ms API p95 |
| **Feature Flags** | Canary releases (5% → 25% → 50% → 100%) |

#### 2.2.5 Disaster Recovery (DR)

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Recovery from catastrophic failure (region loss, primary database destruction) |
| **URL** | Activated on DR declaration only; no live URL until activated |
| **Database** | Point-in-time recovery from cross-region backups (7-day WAL retention) |
| **AI** | Ollama (CPU only, no GPU dependency — degraded but functional) |
| **Storage** | R2 cross-region replica + Telegram cold backup |
| **Cache** | Cold start (no cache — rebuild from database) |
| **Access** | SRE Lead, CTO only (DR activation requires two-party approval) |
| **Data** | Last successful backup (RPO < 1 hour) |
| **Deployment** | Runbook-driven recovery procedure (manual, not automated) |
| **Monitoring** | Basic health checks only (monitoring stack may also be in DR) |
| **Security** | Emergency access procedures; all normal access controls apply post-recovery |
| **RTO Target** | < 4 hours from DR declaration to basic service availability |
| **RPO Target** | < 1 hour maximum data loss |

#### 2.2.6 Sandbox

| Attribute | Specification |
|-----------|--------------|
| **Purpose** | Customer PoC, security testing, penetration testing, sales demos |
| **URL** | `https://sandbox.adaptive-study-planner.com` |
| **Database** | Isolated Supabase project (reset weekly every Sunday 00:00 UTC) |
| **AI** | Ollama (CPU only, no GPU) |
| **Storage** | Dedicated R2 sandbox bucket |
| **Cache** | Dedicated Redis sandbox instance |
| **Access** | Approved external parties (PoC customers), security team, sales team |
| **Data** | Dummy data only; no real PII, no production credentials, no production secrets |
| **Deployment** | Automated from `sandbox` branch; refreshed weekly |
| **Monitoring** | Basic logs only (no customer data to monitor) |
| **Security** | TLS 1.3, WAF active, no production secrets, isolated network |
| **SLA** | None — best effort, may be taken down without notice |
| **Reset Schedule** | Every Sunday 00:00 UTC (all data wiped, re-seeded with fixtures) |

---

## 3. Infrastructure Inventory

### 3.1 Frontend

| Component | Technology | Purpose | Owner | SLA | Cost |
|-----------|------------|---------|-------|-----|------|
| PWA (UI) | Vanilla JavaScript + Tailwind CSS v3 | User interface, responsive design, offline capability | Frontend Engineering | 99.9% | N/A (static) |
| Static Hosting | Cloudflare Pages | CDN-delivered frontend, global edge cache | Platform Engineering | 99.9% | $0 (free tier) |
| Service Worker | Workbox v7 | Offline caching, background sync, PWA install | Frontend Engineering | N/A | N/A |
| Asset Pipeline | Vite | Build, bundle, minification | Frontend Engineering | N/A | N/A |
| Icons & Fonts | Phosphor Icons + Inter font | UI iconography and typography | Frontend Engineering | N/A | N/A |

### 3.2 Backend — API Gateway

| Component | Technology | Purpose | Owner | SLA | Cost |
|-----------|------------|---------|-------|-----|------|
| API Gateway | Cloudflare Workers (Workers Runtime) | Route, validate, rate limit, cors | Platform Engineering | 99.9% | $5/10M requests |
| Edge Routing | Cloudflare Workers Routes | Path-based routing, API versioning | Platform Engineering | 99.9% | Included |
| Rate Limiting | Cloudflare Workers + Upstash Redis | Token bucket per user/IP | Platform Engineering | 99.9% | Upstash usage |
| JWT Validation | Cloudflare Workers (jose library) | RS256 signature verification | Security Engineering | 99.9% | N/A |
| CORS Handling | Cloudflare Workers | Preflight, origin whitelist | Platform Engineering | 99.9% | N/A |
| DDoS Protection | Cloudflare WAF (Pro Plan) | L3/L4/L7 DDoS mitigation | Security Engineering | 99.9% | $20/month |
| Bot Management | Cloudflare WAF | Bot detection, challenge pages | Security Engineering | 99.9% | Included |
| Web Application Firewall | Cloudflare WAF Custom Rules | OWASP Top 10 protection, custom rules | Security Engineering | 99.9% | Included |

### 3.3 Backend — AI Orchestration

| Component | Technology | Purpose | Owner | SLA | Cost |
|-----------|------------|---------|-------|-----|------|
| Edge Functions | Supabase Edge Functions (Deno runtime) | AI pipeline, document processing, embedding | AI Infrastructure | 99.9% | $0.40/GB-hr |
| Webhooks | Cloudflare Workers | Async processing triggers, event routing | Platform Engineering | 99.9% | Workers usage |
| Background Jobs | Supabase pg_cron + Edge Functions | Scheduled tasks, maintenance, cleanup | AI Infrastructure | 99.5% | Included |
| Event Bus | Supabase Realtime (WebSockets) | Processing status updates, live notifications | Platform Engineering | 99.5% | Included |

### 3.4 Authentication & Authorization

| Component | Technology | Purpose | Owner | SLA | Cost |
|-----------|------------|---------|-------|-----|------|
| Auth Provider | Supabase Auth (GoTrue) | JWT issuance, OAuth, SAML, password reset | Security Engineering | 99.9% | Included |
| MFA | TOTP (RFC 6238) via authenticator apps | Enterprise 2FA | Security Engineering | 99.9% | N/A |
| API Keys | Scoped JWT (RS256, custom claims) | Programmatic access, service-to-service | Security Engineering | 99.9% | N/A |
| OAuth 2.0 | Supabase Auth (Google, GitHub) | Social login | Security Engineering | 99.9% | N/A |
| SAML 2.0 | Supabase Auth (Enterprise) | SSO for institutional clients | Security Engineering | 99.9% | Enterprise tier |
| Row-Level Security | PostgreSQL RLS policies | Tenant isolation at database level | Database Engineering | 99.9% | N/A |
| RBAC | PostgreSQL roles + application logic | Role-based access control | Security Engineering | 99.9% | N/A |

### 3.5 Storage — Object Storage

| Component | Technology | Purpose | Owner | SLA | Cost |
|-----------|------------|---------|-------|-----|------|
| Object Storage (Primary) | Cloudflare R2 | Raw documents, audio, exports, thumbnails | Platform Engineering | 99.9% | $0.015/GB |
| Object Storage (Fallback) | AWS S3 (optional) | Enterprise multi-cloud fallback | Platform Engineering | 99.99% | $0.023/GB |
| Cold Backup | Telegram Bot API | Optional off-site backup for raw documents | SRE | Best effort | Free |
| Presigned URLs | Cloudflare R2 | Secure temporary access to private objects | Platform Engineering | 99.9% | Included |
| Lifecycle Policies | R2 + S3 | Automatic archival, deletion after account closure | Platform Engineering | 99.9% | N/A |
| Cross-Region Replication | R2 (automatic) | Real-time replication to secondary region | Platform Engineering | 99.9% | Egress fees |

### 3.6 Database

| Component | Technology | Purpose | Owner | SLA | Cost |
|-----------|------------|---------|-------|-----|------|
| Primary Database | Supabase PostgreSQL 15 | Metadata, users, documents, chunks, audit logs | Database Engineering | 99.9% | $25/month base |
| Vector Extension | pgvector 0.5.1+ | Semantic search, 1024-dim embeddings | Database Engineering | 99.9% | Included |
| Full-Text Index | PostgreSQL GIN tsvector | BM25 keyword search | Database Engineering | 99.9% | Included |
| Read Replicas | PostgreSQL Streaming Replication | Read-heavy query offloading | Database Engineering | 99.9% | $15/month/replica |
| Connection Pool | PgBouncer | Connection management, prevent exhaustion | Database Engineering | 99.9% | Included |
| WAL Archiving | PostgreSQL WAL-G | Continuous backup, point-in-time recovery | Database Engineering | 99.9% | Storage cost |
| Database Migrations | Supabase CLI + sqitch | Schema versioning, reversible migrations | Database Engineering | N/A | N/A |

### 3.7 Knowledge Graph

| Component | Technology | Purpose | Owner | SLA | Cost |
|-----------|------------|---------|-------|-----|------|
| Graph Store (Phase 3) | PostgreSQL + Recursive CTEs | Concept relationships, prerequisites | Database Engineering | 99.9% | Included |
| Graph Store (Phase 4 Eval) | ArangoDB (if migrated) | Multi-model graph for >10K edges/user | Database Engineering | 99.9% | Self-hosted |
| Graph Visualization | D3.js v7 + Cytoscape.js | Frontend interactive graph rendering | Frontend Engineering | 99.5% | N/A |
| Graph Analytics | PostgreSQL CTE + application logic | Learning path optimization, gap detection | AI Infrastructure | 99.5% | N/A |

### 3.8 Monitoring & Observability

| Component | Technology | Purpose | Owner | SLA | Cost |
|-----------|------------|---------|-------|-----|------|
| Metrics | Grafana Cloud + Prometheus | Dashboards, SLI/SLO tracking, trend analysis | SRE | 99.9% | $0 (free tier) |
| Log Aggregation | Loki (Grafana Cloud) | Centralized log search, structured JSON | SRE | 99.9% | Grafana Cloud |
| Error Tracking | Sentry (SaaS) | Error grouping, performance monitoring, release health | SRE | 99.9% | $26/month |
| Distributed Tracing | OpenTelemetry + Jaeger (self-hosted) | End-to-end request flow, latency analysis | SRE | 99.5% | Self-hosted |
| Synthetic Monitoring | UptimeRobot (Pro) | External health checks from 5+ locations | SRE | 99.9% | $15/month |
| Alerting | PagerDuty (Business) | P0/P1 alert routing, on-call scheduling | SRE | 99.9% | $29/user/month |
| Notification | Slack (Paid workspace) | Alert channels, incident coordination | SRE | 99.9% | $8/user/month |
| Status Page | Statuspage.io (or Cloudflare) | Public-facing status and incidents | SRE | 99.9% | $29/month |
| APM | Sentry Performance | API latency, database query performance | SRE | 99.9% | Included in Sentry |

### 3.9 Logging & Tracing

| Component | Technology | Purpose | Retention | Owner |
|-----------|------------|---------|-----------|-------|
| Application Logs | Structured JSON (stdout → Loki) | Correlation ID, request details, processing stages | 30 days hot, 1 year cold (S3 Glacier) | SRE |
| Audit Logs | PostgreSQL WORM table | Immutable user/system/admin actions | 7 years (immutable) | Compliance |
| Security Logs | Sentry + SIEM (future) | Auth events, access anomalies, intrusion detection | 2 years | Security Engineering |
| AI Logs | PostgreSQL (ai_queries table) | Grounding audit, citation verification, model drift | 2 years | AI Infrastructure |
| Access Logs | Cloudflare Logs + Loki | HTTP requests, IPs, user agents, WAF decisions | 30 days | SRE |
| System Logs | journald / Cloudflare | Service restarts, resource exhaustion, kernel events | 30 days | SRE |

### 3.10 Tracing

| Component | Technology | Purpose | Sampling Rate | Owner |
|-----------|------------|---------|---------------|-------|
| Distributed Traces | OpenTelemetry SDK (JS + Python) | End-to-end request flow across all services | 10% (production), 100% (staging) | SRE |
| Trace Context | W3C Trace Context (traceparent/tracestate) | Propagation across service boundaries | All requests | SRE |
| Span Storage | Jaeger (self-hosted) | Trace visualization, latency analysis | 7 days | SRE |
| Span Enrichment | OpenTelemetry Resource Detectors | Service name, version, environment, host | All spans | SRE |

### 3.11 CI/CD

| Component | Technology | Purpose | Owner | SLA |
|-----------|------------|---------|-------|-----|
| Source Control | GitHub | Git repository, code review, branch protection | DevOps | 99.9% |
| CI Pipeline | GitHub Actions | Lint, test, security scan, build, deploy | DevOps | 99.9% |
| IaC | Terraform + Cloudflare Wrangler | Infrastructure as code, state management | Platform Engineering | N/A |
| Artifact Registry | GitHub Packages + R2 | Build artifacts, container images, model weights | DevOps | 99.9% |
| Feature Flags | LaunchDarkly | Gradual rollout, A/B testing, kill switches | Platform Engineering | 99.9% |
| Secret Management (CI) | GitHub Secrets + HashiCorp Vault | CI/CD secrets, API keys, deployment tokens | Security Engineering | 99.9% |
| Deployment Orchestration | GitHub Actions + Wrangler CLI | Automated deployment to Workers, Edge Functions | DevOps | 99.9% |
| Database Migrations | Supabase CLI + sqitch | Reversible schema migrations, rollback | Database Engineering | N/A |

### 3.12 Background Workers

| Worker Type | Technology | Purpose | Concurrency | Owner | SLA |
|-------------|------------|---------|-------------|-------|-----|
| OCR Workers | Supabase Edge Functions | Image → text extraction (Tesseract / Google Vision / MathPix) | 10 parallel per tenant | AI Infrastructure | 99.5% |
| Embedding Workers | Supabase Edge Functions | Chunk → vector embedding (BAAI/BGE / OpenAI) | 20 parallel per tenant | AI Infrastructure | 99.5% |
| Retrieval Workers | Cloudflare Workers | Query → hybrid search (dense + sparse + graph) | 200 concurrent | AI Infrastructure | 99.9% |
| AI Workers | vLLM / Ollama / OpenAI | LLM inference, grounding, response generation | 50 concurrent | AI Infrastructure | 99.5% |
| Citation Workers | Supabase Edge Functions | Citation verification, evidence trace generation | 20 concurrent | AI Infrastructure | 99.5% |
| Graph Workers | PostgreSQL CTE (async) | Graph traversal, prerequisite chain analysis | 10 concurrent | Database Engineering | 99.5% |
| Extraction Workers | Supabase Edge Functions | Concept, formula, question extraction from parsed text | 15 parallel | AI Infrastructure | 99.5% |
| Auto-Setup Workers | Supabase Edge Functions | Web scraping, resource discovery, download | 5 parallel | AI Infrastructure | 99.5% |
| Export Workers | Supabase Edge Functions | JSON, Markdown, Anki deck generation | 5 parallel | Platform Engineering | 99.5% |
| Cleanup Workers | Supabase Edge Functions | Account deletion, expired cache purge, orphan removal | 3 parallel | Platform Engineering | 99.5% |

### 3.13 Queues

| Queue | Technology | Purpose | TTL | Max Depth | Owner |
|-------|------------|---------|-----|-----------|-------|
| Document Processing | Redis (Upstash) | Upload → validation → OCR → parsing → extraction → chunking → embedding → indexing | 24 hours | 1,000 | AI Infrastructure |
| OCR Queue | Redis (Upstash) | Pending OCR jobs (per-page, multi-engine) | 12 hours | 500 | AI Infrastructure |
| Embedding Queue | Redis (Upstash) | Pending embedding jobs (batch-optimized) | 12 hours | 500 | AI Infrastructure |
| Retrieval Queue | Redis (Upstash) | Query caching, result pre-computation | 1 hour | 10,000 | AI Infrastructure |
| AI Inference Queue | Redis (Upstash) | LLM requests (prioritized by user tier) | 5 minutes | 500 | AI Infrastructure |
| Export Queue | Redis (Upstash) | Data export generation (JSON, Anki, Markdown) | 24 hours | 100 | Platform Engineering |
| Dead Letter Queue | Redis (Upstash) | Failed jobs for manual review and reprocessing | 7 days | 500 | SRE |
| Scheduled Jobs | pg_cron (PostgreSQL) | Daily maintenance, retention enforcement, backup triggers | N/A | N/A | SRE |

### 3.14 Cache

| Cache Layer | Technology | Purpose | TTL | Size | Owner |
|-------------|------------|---------|-----|------|-------|
| Query Results | Upstash Redis | Frequently asked questions, repeated searches | 1 hour | 1 GB | AI Infrastructure |
| Embeddings | Upstash Redis | SHA-256 keyed embedding cache | 24 hours | 5 GB | AI Infrastructure |
| Document Metadata | Upstash Redis | Document properties, status, counts | 1 hour | 500 MB | Platform Engineering |
| AI Responses | Upstash Redis | Generated answers, summaries, explanations | 30 minutes | 2 GB | AI Infrastructure |
| Static Assets | Cloudflare CDN | JS bundles, CSS, images, fonts, PWA assets | 30 days | Unlimited | Frontend Engineering |
| API Responses | Cloudflare Workers Cache | Health checks, configuration, feature flags | 5 minutes | 500 MB | Platform Engineering |
| Session Data | Upstash Redis | JWT blacklists, active sessions, CSRF tokens | 1 hour | 200 MB | Security Engineering |
| Rate Limit Counters | Upstash Redis | Per-user, per-IP request counters | 1 minute | 100 MB | Platform Engineering |

### 3.15 CDN

| Component | Technology | Purpose | TTL | Owner |
|-----------|------------|---------|-----|-------|
| Static Assets | Cloudflare CDN | Frontend JS, CSS, images, fonts, PWA manifest | 30 days | Frontend Engineering |
| Document Thumbnails | Cloudflare CDN | Page previews, generated images | 7 days | Platform Engineering |
| Exported Files | Cloudflare CDN | User exports (temporary presigned URLs) | 7 days | Platform Engineering |
| API Edge Cache | Cloudflare Workers Cache | Health endpoints, public configuration | 5 minutes | Platform Engineering |

### 3.16 Secrets Management

| Component | Technology | Purpose | Rotation Frequency | Owner |
|-----------|------------|---------|-------------------|-------|
| API Keys (Cloud Services) | HashiCorp Vault | Cloudflare, Supabase, OpenAI, Google Vision credentials | 90 days | Security Engineering |
| DB Credentials | Supabase Vault | PostgreSQL passwords, connection strings | 90 days | Database Engineering |
| JWT Signing Keys | Supabase Auth + Vault | RS256 private keys for session tokens | 180 days | Security Engineering |
| OAuth Secrets | HashiCorp Vault | Google, GitHub OAuth client secrets | 90 days | Security Engineering |
| LLM API Keys | HashiCorp Vault | OpenAI API keys, Google Vision keys | 90 days | AI Infrastructure |
| TLS Certificates | Let's Encrypt + Cloudflare | HTTPS termination, domain validation | 90 days | Platform Engineering |
| User Content Encryption Keys | Supabase Vault (envelope encryption) | Per-user document encryption keys | 90 days (on request) | Security Engineering |
| Telegram Bot Token | HashiCorp Vault | Bot API authentication | 180 days | SRE |
| Backup Encryption Keys | HSM (air-gapped, Shamir's Secret Sharing 3 of 5) | Backup encryption, WORM audit logs | 180 days | Security Engineering |

---

## 4. Deployment Strategy

### 4.1 Blue-Green Deployment

| Attribute | Specification |
|-----------|--------------|
| **Use Case** | Major version releases (v4.x → v5.x), database schema changes, infrastructure migrations |
| **Process** | 1. Deploy new version to green environment (staging with production data snapshot)<br>2. Run full validation suite against green (unit, integration, AI eval, E2E, load)<br>3. Run database migration on green (if reversible)<br>4. Switch traffic from blue to green via Cloudflare DNS/Worker routes<br>5. Monitor green for 1 hour with enhanced observability<br>6. If issues detected, rollback to blue (DNS switchback, < 30 seconds)<br>7. If stable, decommission blue after 24 hours |
| **Downtime** | < 30 seconds (DNS TTL + Worker propagation) |
| **Rollback Time** | < 30 seconds (instant DNS/Worker route switch) |
| **Risk** | Low (instant rollback, zero data loss) |
| **Data Loss** | None (no in-place mutation) |
| **Cost** | 2x infrastructure for duration of overlap (typically 25 hours) |
| **Approval Required** | Engineering Lead + SRE Lead + Product Owner |
| **Runbook** | `runbooks/deployment-blue-green.md` |

### 4.2 Rolling Deployment

| Attribute | Specification |
|-----------|--------------|
| **Use Case** | Minor patches (v4.1.x → v4.1.y), bug fixes, non-breaking changes, configuration updates |
| **Process** | 1. Deploy new version to 10% of Cloudflare Workers (canary region)<br>2. Monitor error rate and latency for 10 minutes<br>3. If error rate < 0.1% and latency < SLO, deploy to 50%<br>4. If healthy, deploy to 100%<br>5. If any stage fails, automatic rollback to previous version |
| **Downtime** | Zero (gradual rollout, no traffic interruption) |
| **Rollback Time** | < 5 minutes (re-deploy previous version) |
| **Risk** | Medium (partial exposure to issues) |
| **Data Loss** | None |
| **Cost** | No additional infrastructure |
| **Approval Required** | SRE Lead (for production) |
| **Runbook** | `runbooks/deployment-rolling.md` |

### 4.3 Canary Releases

| Attribute | Specification |
|-----------|--------------|
| **Use Case** | New features, UI changes, AI model updates, pricing changes, experimental features |
| **Process** | 1. Enable feature flag for 5% of users (free tier, diverse geography)<br>2. Monitor feature-specific metrics for 24 hours (adoption, errors, latency, user satisfaction)<br>3. If metrics healthy, increase to 25%<br>4. If metrics healthy, increase to 50%<br>5. If metrics healthy, increase to 100%<br>6. At each stage, require approval from Product Owner |
| **Rollback** | Disable feature flag (instant, < 10 seconds) |
| **Duration** | 1–7 days per stage (minimum 4 days total) |
| **Risk** | Low (instant rollback via feature flag) |
| **Data Loss** | None |
| **Cost** | No additional infrastructure |
| **Approval Required** | Product Owner at each stage |
| **Runbook** | `runbooks/deployment-canary.md` |

### 4.4 Feature Flags

| Flag | System | Default | Rollout Strategy | Owner | Description |
|------|--------|---------|-----------------|-------|-------------|
| `hybrid_retrieval` | LaunchDarkly | ON | 100% (core feature) | AI Infrastructure | Dense + sparse + graph + metadata retrieval |
| `google_vision_ocr` | LaunchDarkly | OFF | Pro tier only | AI Infrastructure | Google Vision Handwriting OCR for pro users |
| `mathpix_formula` | LaunchDarkly | OFF | Pro tier only | AI Infrastructure | MathPix formula OCR for pro users |
| `openai_fallback` | LaunchDarkly | ON | 100% (fallback) | AI Infrastructure | OpenAI cloud fallback when local AI fails |
| `graph_visualization` | LaunchDarkly | ON | 100% (core feature) | Frontend Engineering | Interactive D3.js knowledge graph |
| `knowledge_sharing` | LaunchDarkly | OFF | Gradual (beta) | Platform Engineering | Study group collaboration and sharing |
| `auto_resource_setup` | LaunchDarkly | ON | 100% (core feature) | AI Infrastructure | Zero-upload exam auto-discovery |
| `chunked_upload` | LaunchDarkly | ON | 100% (core feature) | Platform Engineering | Resumable chunked file upload |
| `citation_verification` | LaunchDarkly | ON | 100% (core feature) | AI Infrastructure | Automated citation verification per response |
| `enterprise_sso` | LaunchDarkly | OFF | Enterprise tier only | Security Engineering | SAML 2.0 / LDAP SSO integration |
| `field_level_encryption` | LaunchDarkly | OFF | Gradual (Phase 4.2) | Security Engineering | Per-user field-level encryption for PII |
| `hnsw_index` | LaunchDarkly | OFF | 10% → 50% → 100% | Database Engineering | HNSW vector index (replaces IVFFlat) |
| `arangodb_graph` | LaunchDarkly | OFF | Sandbox only | Database Engineering | ArangoDB graph evaluation (Phase 4.2) |
| `differential_privacy` | LaunchDarkly | OFF | Roadmap (Phase 4.3) | AI Infrastructure | Differential privacy for analytics queries |
| `federated_learning` | LaunchDarkly | OFF | Roadmap (Phase 4.4) | AI Infrastructure | Federated model improvement (no raw data sharing) |

### 4.5 Rollback Strategy Matrix

| Deployment Type | Rollback Method | Time to Rollback | Data Loss | Automation Level | Runbook |
|-----------------|-----------------|-----------------|-----------|-----------------|---------|
| Blue-Green | DNS / Worker route switch | < 30 seconds | None | Semi-automated | `runbooks/rollback-blue-green.md` |
| Rolling | Re-deploy previous version | < 5 minutes | None | Automated (CI pipeline) | `runbooks/rollback-rolling.md` |
| Canary | Disable feature flag | < 10 seconds | None | Automated (LaunchDarkly API) | `runbooks/rollback-canary.md` |
| Database Migration | Reverse migration script | < 10 minutes | None (if reversible) | Manual (requires DBA) | `runbooks/rollback-database.md` |
| Hotfix | Direct commit + deploy | < 15 minutes | None | Manual (expedited) | `runbooks/rollback-hotfix.md` |
| Infrastructure (Terraform) | `terraform apply` previous state | < 5 minutes | None | Semi-automated | `runbooks/rollback-terraform.md` |
| AI Model | Switch model version in config | < 30 seconds | None | Automated (config push) | `runbooks/rollback-model.md` |
| Secrets | Vault revert + redeploy | < 2 minutes | None | Semi-automated | `runbooks/rollback-secrets.md` |

### 4.6 Emergency Rollback Procedure

```bash
#!/bin/bash
# Emergency Rollback Procedure
# WARNING: Use only for SEV-0 or SEV-1 incidents
# AUTHORIZATION: SRE Lead or CTO approval required

set -euo pipefail

# Step 1: Identify last known good version
LAST_GOOD=$(git log --oneline --grep="stable\|hotfix\|release" -10 | head -1 | awk '{print $1}')
echo "Last known good version: $LAST_GOOD"

# Step 2: Confirm authorization
read -p "Enter SRE Lead authorization code: " AUTH_CODE
if [[ "$AUTH_CODE" != "$(vault kv get -field=emergency_code secret/rollback)" ]]; then
    echo "Authorization failed. Aborting."
    exit 1
fi

# Step 3: Log emergency rollback
slack send --channel="#sre-alerts" \
    --message "🚨 EMERGENCY ROLLBACK initiated by $(whoami) to $LAST_GOOD"

# Step 4: Re-deploy previous version
wrangler deploy --tag $LAST_GOOD --env production
supabase functions deploy --project-ref "$SUPABASE_PROD_REF" --version $LAST_GOOD

# Step 5: Disable problematic feature flags
launchdarkly flag disable new_feature --env production
launchdarkly flag disable experimental_model --env production

# Step 6: Verify health
for i in {1..30}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://adaptive-study-planner.com/api/v3/health)
    if [[ "$STATUS" == "200" ]]; then
        echo "Health check PASSED (attempt $i)"
        break
    fi
    sleep 5
done

if [[ "$STATUS" != "200" ]]; then
    echo "Health check FAILED after rollback. Escalate to CTO immediately."
    pagerduty trigger --escalation-policy="CTO"
    exit 1
fi

# Step 7: Notify stakeholders
slack send --channel="#sre-alerts" \
    --message "✅ Emergency rollback to $LAST_GOOD completed. Health checks passing."

# Step 8: Create incident ticket
jira create --project="OPS" --issue-type="Incident" \
    --summary="Emergency Rollback to $LAST_GOOD" \
    --description="SEV-0/SEV-1 incident required emergency rollback. See incident channel."
```

### 4.7 Hotfix Process

| Step | Action | Owner | SLA | Verification |
|------|--------|-------|-----|-------------|
| 1. Declare | Create `hotfix/` branch from `main` | On-call Engineer | Immediate | Branch created, Jira ticket opened |
| 2. Fix | Apply minimal fix (no feature additions, no refactoring) | On-call Engineer | 30 min | Change reviewed by second engineer |
| 3. Test | Run targeted unit tests + smoke tests + security scan | CI Pipeline | 15 min | All tests passing, 0 critical vulnerabilities |
| 4. Review | Expedited review (1 approver, 15 min SLA) | On-call Senior Engineer | 15 min | PR approved with comment on root cause |
| 5. Deploy | Direct deploy to production (skip staging) | CI Pipeline | 10 min | Deployment successful, health checks passing |
| 6. Monitor | 1-hour enhanced monitoring (all golden signals, all alerts) | SRE | 1 hour | No anomalies detected |
| 7. Merge | Back-merge to `develop` and `main` | DevOps | 30 min | Both branches updated, no conflicts |
| 8. Postmortem | Document root cause and permanent fix | Engineering Team | 24 hours | Postmortem published, action items assigned |

### 4.8 Version Promotion Matrix

| From → To | Method | Validation Required | Approval Required | Duration |
|-----------|--------|---------------------|-------------------|----------|
| Develop → Staging | Automated CI/CD | Unit tests, lint, security scan | None | 10 minutes |
| Staging → Production | Manual gate | Full test suite + AI eval + E2E + load test + security review | Engineering Lead + SRE Lead + Product Owner | 30 minutes |
| Hotfix → Production | Expedited | Targeted tests + smoke test + security scan | SRE Lead | 30 minutes |
| Production → DR | Restore from backup | Backup integrity verification | SRE Lead + CTO | 2–4 hours |
| DR → Production | Gradual promotion | Full validation + data integrity check | CTO + Engineering Lead | 4–8 hours |

### 4.9 Release Approval Process

| Gate | Criteria | Approver | Evidence |
|------|----------|----------|----------|
| **Code Review** | All PRs approved, no unresolved comments | Senior Engineer | GitHub PR approvals |
| **Test Pass** | Unit ≥ 80%, Integration 100%, AI eval MRR@10 > 0.6 | QA Lead | CI test reports |
| **Security Scan** | 0 critical/high vulnerabilities, all secrets checked | Security Engineer | Snyk/Dependabot/Trivy reports |
| **Performance** | Load test passed (200 concurrent users, < 1% error), p95 latency < SLO | SRE Lead | k6/load test report |
| **Database Migration** | Migration tested on staging, reversible, < 1 min downtime | DBA Lead | Migration test log |
| **Feature Flags** | All flags configured, default states verified, rollback plan documented | Platform Engineering | LaunchDarkly config review |
| **Monitoring** | Dashboards updated, alerts tested, synthetic monitoring enabled | SRE | Grafana alert test results |
| **Documentation** | API docs updated, runbook updated, known issues list updated | Technical Writer | Documentation diff |
| **Customer Comms** | Changelog prepared, in-app banner ready (if user-facing) | Product Owner | Marketing/CS sign-off |
| **Compliance** | Privacy impact assessment complete (if data handling changes), accessibility verified | Compliance Officer | Compliance checklist |

### 4.10 Deployment Checklist

- [ ] All tests passing (unit, integration, AI eval, E2E, load, security)
- [ ] Security scan: 0 critical/high vulnerabilities, no secrets in code
- [ ] Database migration tested on staging (reversible, < 1 min downtime)
- [ ] Feature flags configured (default states, gradual rollout plan)
- [ ] Monitoring dashboards updated (new metrics, new alerts)
- [ ] Alerts verified (PagerDuty, Slack — test firing)
- [ ] Rollback plan documented and tested (rollback procedure executed on staging)
- [ ] On-call engineer briefed on changes (runbook review, escalation path)
- [ ] Customer communication prepared (changelog, in-app banner, status page)
- [ ] Production readiness checklist complete (Section 15)
- [ ] Legal/compliance sign-off (if data handling, privacy, or terms changes)
- [ ] Database backup completed before migration
- [ ] Previous version artifacts available (container images, build artifacts)
- [ ] CDN cache purge planned (if static assets changed)
- [ ] Rate limits reviewed (if new endpoints or changed quotas)

### 4.11 Deployment Validation

| Check | Method | Frequency | Owner | Action on Failure |
|-------|--------|-----------|-------|-------------------|
| Health endpoint | `GET /api/v3/health` | Every 30s (synthetic) | SRE | Alert P0 if > 1 min down |
| API latency | Sentry APM | Every request | SRE | Alert P1 if p95 > SLO |
| Error rate | Sentry + Grafana | Every request | SRE | Alert P1 if > 0.1% |
| Database connectivity | Connection pool metrics | Every 30s | SRE | Alert P0 if failures |
| Cache hit rate | Redis metrics | Every 5 min | SRE | Alert P2 if < 60% |
| AI response quality | Citation verification | Every response | AI Infrastructure | Alert P1 if < 100% |
| Feature flag state | LaunchDarkly API | Every 5 min | Platform Engineering | Alert P2 if misconfigured |
| Security headers | Security scan | Post-deployment | Security Engineering | Alert P1 if missing |
| SSL certificate | SSL Labs / OpenSSL | Every 6 hours | Platform Engineering | Alert P2 if expiry < 30 days |
| Backup completion | R2 backup logs | Daily | SRE | Alert P1 if backup missing |

---

## 5. Monitoring

### 5.1 Golden Signals (Per Service)

The four golden signals are monitored for every service in the platform:

| Signal | Metric | Instrumentation | Alert Threshold | Dashboard |
|--------|--------|----------------|-----------------|-----------|
| **Latency** | p95, p99 request duration | OpenTelemetry + Sentry APM | p95 > 500ms for 5 min | Grafana |
| **Traffic** | Requests per second (RPS), unique users | Cloudflare Analytics + Grafana | RPS > 10,000 sustained | Grafana |
| **Errors** | HTTP 5xx rate, error rate by endpoint | Sentry + Grafana | > 0.1% for 2 min | Grafana |
| **Saturation** | CPU, GPU, RAM, disk, connection pool | Node exporter + Supabase metrics | > 80% for 5 min | Grafana |

**Additional Service-Specific Signals:**

| Service | Additional Signal | Metric | Threshold |
|---------|-------------------|--------|-----------|
| AI Inference | Token throughput | Tokens/sec | < 50% baseline |
| AI Inference | Queue wait time | Avg wait in inference queue | > 30 seconds |
| Embedding | Batch throughput | Chunks/sec | < 80% baseline |
| OCR | Page throughput | Pages/min | < 50% baseline |
| Retrieval | Query latency | p95 hybrid search | > 200ms |
| Database | Connection pool utilization | Active / max | > 80% |
| Database | Replication lag | Seconds behind primary | > 5 seconds |
| Cache | Eviction rate | Keys evicted/sec | > 100/sec |
| Storage | R2 request rate | Ops/sec | > 1,000/sec |

### 5.2 Metrics Dashboard Hierarchy

| Dashboard | Tool | Audience | Refresh | Contents |
|-----------|------|----------|---------|----------|
| Platform Overview | Grafana | All Engineering | 30s | Golden signals, SLO compliance, error budget |
| API Performance | Grafana + Sentry | Backend Engineers | 10s | Endpoint latency, error rates, throughput by endpoint |
| AI Pipeline | Grafana | AI Infrastructure | 10s | Processing queue depth, OCR accuracy, embedding success, model drift |
| Database Health | Grafana + Supabase | Database Engineers | 30s | Connection pool, replication lag, query performance, index bloat |
| User Experience | Sentry + Grafana | Frontend + Product | 1m | Page load times, Core Web Vitals, PWA metrics, user flows |
| Security | Sentry + WAF Logs | Security Engineering | 5m | Auth failures, WAF blocks, anomaly detection, access patterns |
| Cost | Cloudflare + Supabase + Grafana | Finance + SRE | 1h | Compute, storage, egress, AI inference costs by service |
| Capacity | Grafana | SRE + Platform | 1h | Resource utilization, growth trends, scaling triggers |
| Compliance | Custom (PostgreSQL) | Compliance | 1d | Audit log completeness, retention enforcement, deletion SLA |

### 5.3 Logs

| Log Type | Format | Collection | Retention | Search | Owner |
|----------|--------|------------|-----------|--------|-------|
| Application Logs | Structured JSON (ECS schema) | stdout → Loki | 30d hot, 1y cold | Loki + Grafana | SRE |
| Access Logs | Cloudflare Logs (JSON) | Cloudflare → R2 → Loki | 30d | Loki + Grafana | SRE |
| Error Logs | Sentry (enriched stack traces) | Sentry SDK | 90d | Sentry UI | SRE |
| Audit Logs | PostgreSQL WORM table | Application → PostgreSQL | 7y (immutable) | SQL query (restricted) | Compliance |
| Security Logs | JSON (CEF format) | WAF + Application → SIEM | 2y | SIEM + Loki | Security Engineering |
| AI Logs | PostgreSQL (ai_queries table) | Application → PostgreSQL | 2y | SQL query | AI Infrastructure |
| System Logs | journald / syslog | systemd → Loki | 30d | Loki + Grafana | SRE |

**Required Log Fields (Application Logs):**

| Field | Type | Required | Example |
|-------|------|----------|---------|
| `timestamp` | ISO 8601 | Yes | `2026-06-28T10:00:00Z` |
| `level` | enum | Yes | `INFO`, `WARN`, `ERROR`, `FATAL` |
| `service` | string | Yes | `api-gateway`, `ai-pipeline`, `embedding-worker` |
| `correlation_id` | UUID | Yes | `550e8400-e29b-41d4-a716-446655440000` |
| `user_id` | UUID | If applicable | `user_123` |
| `request_id` | UUID | Yes | `req_abc123` |
| `method` | string | For HTTP | `GET`, `POST` |
| `path` | string | For HTTP | `/api/v3/ask` |
| `status_code` | integer | For HTTP | `200`, `500` |
| `latency_ms` | integer | For HTTP | `150` |
| `message` | string | Yes | `Document processing completed` |
| `error` | JSON | If error | `{"type": "OCRFailure", "detail": "..."}` |
| `metadata` | JSON | Optional | `{"document_id": "...", "engine": "tesseract"}` |

### 5.4 Distributed Tracing

| Aspect | Specification |
|--------|--------------|
| **Standard** | OpenTelemetry (OTel) v1.20+ |
| **Propagation** | W3C Trace Context (`traceparent`, `tracestate`) |
| **Instrumentation** | Cloudflare Workers (OTel JS), Supabase Edge Functions (OTel Deno), PostgreSQL (auto-instrumentation), Redis (OTel wrapper) |
| **Sampling** | 10% in production (head-based), 100% in staging, 1% in development |
| **Span Limits** | Max 1,000 spans per trace, max 256 attributes per span, max 128 events per span |
| **Trace Storage** | Jaeger (self-hosted) with 7-day retention |
| **Trace Visualization** | Jaeger UI + Grafana Trace View |
| **Critical Traces** | AI pipeline end-to-end, document processing, retrieval + generation, upload + validation |

### 5.5 Health Checks

| Endpoint | Method | Frequency | Expected Response | Timeout | Action on Failure | Owner |
|----------|--------|-----------|-------------------|---------|-------------------|-------|
| `/api/v3/health` | GET | Every 30s (synthetic) | `{"status": "ok", "version": "4.1.0", "timestamp": "..."}` | 5s | Alert P0, page on-call | SRE |
| `/api/v3/health/deep` | GET | Every 5 min | `{"status": "ok", "database": "ok", "cache": "ok", "storage": "ok", "ai": "ok"}` | 10s | Alert P1 | SRE |
| Database ping | `SELECT 1` | Every 30s | `1` | 2s | Alert P0, failover to replica | SRE |
| Redis ping | `PING` | Every 30s | `PONG` | 2s | Alert P1, cache bypass | SRE |
| R2 bucket list | `ListObjectsV2` | Every 5 min | Success (non-empty) | 10s | Alert P1, check replication | SRE |
| vLLM health | GET `/health` | Every 30s | `{"status": "ok"}` | 5s | Alert P0, fallback to OpenAI → Ollama | AI Infrastructure |
| Ollama health | GET `/api/tags` | Every 5 min | `{"models": [...]}` | 10s | Alert P2 | AI Infrastructure |
| OCR engine health | `tesseract --version` | Every 5 min | Version string | 5s | Alert P2, queue for Google Vision | AI Infrastructure |
| Embedding health | `GET /api/v3/health` (deep) | Every 5 min | pgvector connectivity + model availability | 10s | Alert P1 | AI Infrastructure |
| Sentry ingestion | `POST /api/2/store/` | Every 5 min | `200 OK` | 5s | Alert P2 (monitoring blind spot) | SRE |
| PagerDuty API | `GET /incidents` | Every 5 min | `200 OK` | 5s | Alert P2 (alerting blind spot) | SRE |

### 5.6 Synthetic Monitoring

| Monitor | Tool | Frequency | Locations | Test | Alert |
|---------|------|-----------|-----------|------|-------|
| Homepage load | UptimeRobot | Every 60s | US-East, US-West, EU-West, AP-South, SA-East | HTTP GET, expect 200, < 2s | P1 if > 1 location fails |
| API health | UptimeRobot | Every 30s | Same 5 locations | `GET /api/v3/health`, expect 200, JSON `status: ok` | P0 if any location fails |
| Document upload | Custom (Selenium) | Every 15 min | US-East | Upload 1MB PDF, verify processing completes < 5 min | P1 if fails or times out |
| AI Q&A | Custom (API) | Every 5 min | US-East | `POST /api/v3/ask`, verify citation present, < 2s | P1 if fails or no citation |
| Search | Custom (API) | Every 5 min | US-East | `POST /api/v3/search`, verify results > 0, < 500ms | P1 if fails or no results |
| SSL expiry | UptimeRobot | Every 6 hours | Global | Certificate validity > 30 days | P2 if < 30 days |
| DNS resolution | UptimeRobot | Every 5 min | Global | Resolve A/AAAA records | P1 if fails |
| CDN cache hit | Cloudflare Analytics | Every 15 min | Global | Cache hit rate > 80% | P2 if < 60% |

### 5.7 Service Dashboards

| Dashboard | Key Panels | Alert Panels |
|-----------|-----------|-------------|
| **API Gateway** | RPS, latency p50/p95/p99, error rate by status, top endpoints, rate limit hits | Error rate > 0.1%, p95 > 500ms, 5xx spike |
| **AI Pipeline** | Documents in queue, processing rate, OCR accuracy, embedding success, model drift, hallucination rate | Queue depth > 100, OCR < 80%, hallucination > 0% |
| **Database** | Connections, query duration, replication lag, table bloat, index usage, vacuum status | Connections > 80%, lag > 5s, bloat > 30% |
| **Cache** | Hit rate, eviction rate, memory usage, key count, slow commands | Hit rate < 60%, evictions > 100/sec |
| **AI Inference** | GPU utilization, token throughput, queue depth, model load time, fallback rate | GPU > 80%, queue wait > 30s, fallback rate > 5% |
| **Storage** | R2 requests, storage growth, egress, replication lag, presigned URL expiry | Replication lag > 1 hour, storage growth > 50% QoQ |
| **Security** | WAF blocks, auth failures, anomaly score, rate limit hits, geo-distribution | WAF blocks > 1,000/min, auth failures > 10% |
| **Cost** | Daily spend by service, cost per user, AI inference cost, storage cost, forecast vs budget | Any service > 80% of monthly budget |

### 5.8 Alert Thresholds

| Priority | Metric | Threshold | Duration | Channel | Response Time | Escalation | Runbook |
|----------|--------|-----------|----------|---------|---------------|------------|---------|
| **P0** | API down (0% success) | 0% success rate | 1 minute | PagerDuty + Phone + SMS + Slack #sre-alerts | 5 minutes | Auto-escalate to SRE Lead after 10 min, CTO after 15 min | `runbooks/api-down.md` |
| **P0** | Database unreachable | Connection failure | 1 minute | PagerDuty + Phone + SMS + Slack #sre-alerts | 5 minutes | Auto-escalate to DBA Lead after 10 min, CTO after 15 min | `runbooks/db-failover.md` |
| **P0** | AI inference completely down | All LLM endpoints failing | 1 minute | PagerDuty + Phone + SMS + Slack #sre-alerts | 5 minutes | Auto-escalate to AI Infra Lead after 10 min, CTO after 15 min | `runbooks/llm-failover.md` |
| **P0** | Security breach detected | Anomaly score > 95th percentile | Immediate | PagerDuty + Phone + SMS + Slack #security | 5 minutes | Auto-escalate to Security Lead + CTO immediately | `runbooks/security-incident.md` |
| **P1** | API p95 latency > 500ms | p95 > 500ms | 5 minutes | Slack #sre-alerts + PagerDuty (non-phone) | 15 minutes | Escalate to SRE Lead after 30 min | `runbooks/latency-degradation.md` |
| **P1** | Processing failure rate > 1% | > 1% failures | 5 minutes | Slack #ai-alerts + PagerDuty | 15 minutes | Escalate to AI Infra Lead after 30 min | `runbooks/pipeline-failure.md` |
| **P1** | OCR accuracy < 80% | < 80% (printed) | 1 hour | Slack #ai-alerts | 1 hour | Escalate to AI Infra Lead after 2 hours | `runbooks/ocr-degradation.md` |
| **P1** | Citation accuracy < 100% | < 100% verified | 15 minutes | Slack #ai-alerts + PagerDuty | 15 minutes | Escalate to AI Infra Lead after 30 min | `runbooks/citation-failure.md` |
| **P1** | Hallucination detected | > 0 hallucinations | Immediate | Slack #ai-alerts + PagerDuty | 15 minutes | Escalate to AI Infra Lead + CTO after 30 min | `runbooks/hallucination-detected.md` |
| **P1** | Database replication lag > 5s | > 5 seconds | 5 minutes | Slack #sre-alerts | 15 minutes | Escalate to DBA Lead after 30 min | `runbooks/replication-lag.md` |
| **P2** | Cache hit rate < 60% | < 60% | 1 hour | Slack #warnings | 4 hours | Escalate to SRE Lead after 8 hours | `runbooks/cache-degradation.md` |
| **P2** | Embedding queue depth > 100 | > 100 pending | 30 minutes | Slack #warnings | 4 hours | Escalate to AI Infra Lead after 8 hours | `runbooks/queue-backlog.md` |
| **P2** | GPU utilization > 80% | > 80% | 15 minutes | Slack #warnings | 4 hours | Escalate to AI Infra Lead after 8 hours | `runbooks/gpu-saturation.md` |
| **P2** | AI fallback rate > 5% | > 5% of requests using fallback | 1 hour | Slack #warnings | 4 hours | Escalate to AI Infra Lead after 8 hours | `runbooks/fallback-elevated.md` |
| **P3** | Disk usage > 80% | > 80% | 1 day | Email digest | 24 hours | None | `runbooks/capacity-planning.md` |
| **P3** | SSL certificate expiry < 30 days | < 30 days | 6 hours | Email digest | 24 hours | None | `runbooks/certificate-renewal.md` |
| **P3** | Backup not completed | Missing daily backup | 1 day | Email digest + Slack #warnings | 24 hours | Escalate to SRE Lead after 48 hours | `runbooks/backup-failure.md` |
| **P3** | Cost > 80% of budget | Any service | Daily | Email digest | 24 hours | None | `runbooks/cost-optimization.md` |

### 5.9 SLIs, SLOs, and SLAs

| SLI | SLO (Internal Target) | SLA (Customer Contract) | Measurement Window | Measurement Method |
|-----|----------------------|------------------------|-------------------|-------------------|
| API availability | 99.95% | 99.9% | 30-day rolling | Synthetic probe every 30s |
| API latency (p95) | < 300ms | < 500ms | 30-day rolling | APM (Sentry) |
| Retrieval latency (p95) | < 150ms | < 200ms | 30-day rolling | APM |
| AI response latency (p95) | < 1.5s | < 2s | 30-day rolling | APM |
| Document processing success rate | 99.8% | 99.5% | 30-day rolling | Log analysis |
| OCR accuracy (printed) | > 90% | > 85% | Weekly sample | Manual sampling + automated test |
| OCR accuracy (handwritten) | > 75% | > 70% | Weekly sample | Manual sampling + automated test |
| Citation verification accuracy | 100% | 100% | Per response | Automated verification |
| Hallucination rate | 0% | 0% | Weekly evaluation | AI evaluation suite |
| Embedding generation success rate | 99.9% | 99.5% | 30-day rolling | Log analysis |
| Knowledge graph query latency (≤3 hops) | < 100ms | < 150ms | 30-day rolling | APM |
| Cache hit rate | > 80% | > 70% | 30-day rolling | Redis metrics |
| Platform uptime | 99.95% | 99.9% | 30-day rolling | Synthetic monitoring |
| Data export SLA | < 30 days | < 30 days | Per request | Ticket tracking |
| Account deletion SLA | < 30 days | < 30 days | Per request | Ticket tracking |
| Support response (L1) | < 15 min | < 1 hour | Per ticket | Ticketing system |
| Support response (L2) | < 1 hour | < 4 hours | Per ticket | Ticketing system |
| Support response (L3) | < 15 min | < 2 hours | Per ticket | Ticketing system |

### 5.10 Error Budgets

| Budget | Allowance | Period | Calculation | Action on Exhaustion |
|--------|-----------|--------|------------|---------------------|
| API availability | 0.05% downtime | Monthly | 21.6 minutes | Freeze all non-critical releases until next period |
| API latency | 0.1% of requests > 500ms | Monthly | — | Freeze feature releases; performance optimization only |
| Processing success | 0.2% failure rate | Monthly | — | Freeze AI model updates; fix pipeline issues |
| AI hallucination | 0 hallucinations | Monthly | — | Halt all AI responses; emergency investigation |
| Citation accuracy | 0 unverified citations | Monthly | — | Disable AI Q&A until root cause fixed |
| **Tracking** | Grafana dashboard + monthly SRE review | — | — | Error budget status reported in monthly SRE review |
| **Notification** | Slack #sre-alerts when budget > 50% consumed | — | — | PagerDuty when budget > 75% consumed |
| **Consequence** | If any budget exceeded: mandatory engineering review, no releases for 1 week minimum, postmortem required | — | — | Engineering Lead approval required to resume releases |

---

## 6. Incident Response

### 6.1 Severity Level Definitions

#### SEV-0 — Critical (All-Hands / War Room)

| Attribute | Specification |
|-----------|--------------|
| **Definition** | Complete platform outage, data breach, or catastrophic data loss affecting all users |
| **Examples** | All Cloudflare Workers down globally; primary database corruption with replica failure; security breach with confirmed data exfiltration; R2 total loss with backup failure; complete AI inference failure with no fallback; active DDoS attack overwhelming all defenses |
| **Response Time** | 5 minutes (24/7, including weekends and holidays) |
| **Escalation** | Auto-page all on-call engineers (SRE, AI Infra, Platform, Security, DBA), SRE Lead, CTO, and CISO |
| **Communication** | War room (Zoom, auto-created), public status page updated every 15 minutes, Slack #incidents-war-room, customer email if > 1 hour |
| **Postmortem** | Required within 4 hours of resolution; mandatory attendance for all on-call engineers and leads; executive summary to CTO within 8 hours |
| **Error Budget Impact** | Deducts full monthly error budget |
| **Legal/Compliance** | Legal and Compliance teams notified immediately; regulatory breach assessment within 24 hours |

#### SEV-1 — Major

| Attribute | Specification |
|-----------|--------------|
| **Definition** | Major feature unavailable or severe degradation affecting > 25% of users |
| **Examples** | AI pipeline down (no document processing); upload service failing (all uploads rejected); retrieval returning empty results for all users; > 50% error rate on API; database primary failure with successful replica promotion (degraded performance); major security vulnerability actively exploited (contained); R2 primary region failure with cross-region fallback active |
| **Response Time** | 15 minutes (24/7) |
| **Escalation** | Page SRE Lead + AI Infrastructure Lead + Platform Lead; notify CTO if not resolved within 1 hour |
| **Communication** | Slack #incidents, status page updated every 30 minutes; customer email if > 2 hours |
| **Postmortem** | Required within 24 hours of resolution; attended by owning team and SRE Lead |
| **Error Budget Impact** | Deducts 50% of monthly error budget |
| **Legal/Compliance** | Compliance team notified if data handling affected |

#### SEV-2 — Significant

| Attribute | Specification |
|-----------|--------------|
| **Definition** | Degraded performance or partial feature failure affecting some users (5–25%) |
| **Examples** | Slow AI responses (> 5s p95); OCR accuracy drop below 80%; partial feature failure (e.g., graph visualization not loading); > 10% error rate on specific endpoints; cache failure causing elevated latency; single read replica failure; single AI inference node failure with remaining nodes handling load |
| **Response Time** | 1 hour (business hours, 09:00–18:00 UTC); next business day if outside hours |
| **Escalation** | Slack #incidents, assign to owning team lead; page on-call if during business hours |
| **Communication** | Slack #incidents; no status page unless > 1 hour duration |
| **Postmortem** | Required within 48 hours of resolution; team lead discretion for attendance |
| **Error Budget Impact** | Deducts 25% of monthly error budget |
| **Legal/Compliance** | None unless data handling affected |

#### SEV-3 — Minor

| Attribute | Specification |
|-----------|--------------|
| **Definition** | Isolated issue affecting < 5% of users, workaround available, no data loss |
| **Examples** | Single user upload failure; intermittent 500s on non-critical endpoint; non-critical feature bug (e.g., export format issue); slow response for specific document type; UI glitch in knowledge graph visualization |
| **Response Time** | 4 hours (business hours) |
| **Escalation** | Support ticket, assigned to engineering team; no paging unless escalated by support |
| **Communication** | Internal ticket tracking; user communication via support ticket |
| **Postmortem** | Optional; at team lead discretion if pattern detected |
| **Error Budget Impact** | None |
| **Legal/Compliance** | None |

#### SEV-4 — Informational

| Attribute | Specification |
|-----------|--------------|
| **Definition** | No user impact; proactive issue or observation |
| **Examples** | Latency approaching threshold (but still within SLO); non-critical alert (e.g., disk usage > 70%); capacity warning (e.g., queue depth approaching limit); security scan finding (low severity); dependency deprecation notice |
| **Response Time** | Next business day |
| **Escalation** | Ticket backlog; no paging |
| **Communication** | Weekly ops review; no immediate communication |
| **Postmortem** | Not required |
| **Error Budget Impact** | None |
| **Legal/Compliance** | None |

### 6.2 Incident Response Flow

```
Alert Fires (PagerDuty / Slack / Synthetic Monitor)
  |
  +---> P0: Auto-page on-call + SRE Lead + CTO + CISO (5 min SLA)
  +---> P1: Page on-call + team lead (15 min SLA)
  +---> P2: Slack alert + auto-create ticket (1 hour SLA)
  +---> P3: Email digest + ticket backlog (24 hour SLA)
  |
  +---> Acknowledge (mark as "acknowledged" in PagerDuty within SLA)
  |     | Failure to acknowledge: auto-escalate to next level
  |
  +---> Triage (determine severity, scope, impact, affected users)
  |     | Questions: What broke? Who is affected? How bad? Any data loss?
  |     | Update status page (if SEV-0 or SEV-1)
  |
  +---> Mitigate (apply workaround, enable fallback, scale up, disable feature)
  |     | Goal: Restore service, not necessarily fix root cause
  |     | Document all mitigation steps in incident channel
  |     | Notify stakeholders of mitigation status
  |
  +---> Communicate (status page, Slack, customer comms if needed)
  |     | SEV-0: Update every 15 min
  |     | SEV-1: Update every 30 min
  |     | SEV-2: Update every 1 hour (if > 1 hour)
  |     | SEV-3: Support ticket updates only
  |
  +---> Resolve (verify fix, monitor for 30 min, confirm stable)
  |     | Run full health check suite
  |     | Confirm all golden signals within SLO
  |     | Mark incident resolved in PagerDuty
  |     | Final status page update: "Resolved"
  |
  +---> Postmortem (within SLA deadline)
  |     | SEV-0: 4 hours after resolution
  |     | SEV-1: 24 hours after resolution
  |     | SEV-2: 48 hours after resolution
  |     | Publish to incident wiki, assign action items
```

### 6.3 Postmortem Template

```markdown
# Postmortem: [Incident Title] — [Date] — SEV-[X]

## Metadata
| Field | Value |
|-------|-------|
| Incident ID | INC-YYYY-MM-DD-NNN |
| Severity | SEV-X |
| Date | YYYY-MM-DD |
| Start Time | HH:MM UTC |
| End Time | HH:MM UTC |
| Duration | N minutes |
| Detected By | [Monitoring / User Report / Manual] |
| Responders | [Name, Name, Name] |
| Lead Responder | [Name] |

## Summary
One-paragraph description of what happened, the impact, and the resolution.

## Impact Assessment
| Metric | Value |
|--------|-------|
| Users Affected | [number or percentage] |
| Requests Failed | [number] |
| Data Loss | [Yes/No — if yes, amount and recovery] |
| Revenue Impact | [if applicable] |
| Reputational Impact | [if applicable] |
| Compliance Impact | [if applicable] |

## Timeline (UTC)
| Time | Event | Actor |
|------|-------|-------|
| HH:MM | Alert fired | [Monitoring system] |
| HH:MM | On-call acknowledged | [Engineer name] |
| HH:MM | Root cause identified | [Engineer name] |
| HH:MM | Mitigation applied | [Engineer name] |
| HH:MM | Service restored | [System] |
| HH:MM | Monitoring confirmed stable | [Engineer name] |

## Root Cause Analysis
### 5 Whys:
1. Why did the incident occur? [Answer]
2. Why did [Answer]? [Answer]
3. Why did [Answer]? [Answer]
4. Why did [Answer]? [Answer]
5. Why did [Answer]? [Root cause]

### Technical Details:
[Detailed technical explanation]

## What Went Well
- [Bullet points of effective responses, good decisions, helpful tools]

## What Went Wrong
- [Bullet points of missed signals, slow responses, inadequate tools, communication gaps]

## Action Items
| Action | Owner | Due Date | Priority | Status |
|--------|-------|----------|----------|--------|
| [Fix root cause] | [Name] | [Date] | P0 | Open |
| [Improve monitoring] | [Name] | [Date] | P1 | Open |
| [Update runbook] | [Name] | [Date] | P2 | Open |
| [Training / process improvement] | [Name] | [Date] | P2 | Open |

## Lessons Learned
[Free-form reflection on process, tools, and team response]

## Follow-up Review
| Date | Attendees | Outcome |
|------|-----------|---------|
| [Date] | [Names] | [All action items verified complete] |
```

### 6.4 Communication Plans

| Severity | Internal | External | Frequency | Channels |
|----------|----------|----------|-----------|----------|
| SEV-0 | All engineering, leadership, legal, compliance | All customers (email), status page, Twitter/X | Every 15 min | Slack #incidents-war-room, Zoom war room, status page, email |
| SEV-1 | Engineering teams, SRE Lead, CTO | Affected customers (email if > 25%), status page | Every 30 min | Slack #incidents, status page, email |
| SEV-2 | Owning team, SRE | No external unless > 1 hour | Every 1 hour (if > 1 hour) | Slack #incidents |
| SEV-3 | Owning team | Support ticket only | Per ticket | Support system |
| SEV-4 | Weekly ops review | None | Weekly | Slack #ops-review |

---

## 7. Disaster Recovery

### 7.1 Backup Policy

| Component | Type | Frequency | Retention | Location | Encryption | Method | Validation |
|-----------|------|-----------|-----------|----------|------------|--------|------------|
| PostgreSQL (Full) | Base backup | Daily at 02:00 UTC | 7 days | Cross-region R2 (`backups/db/`) | AES-256-GCM | `pg_dump` custom format + `wal-g` | Monthly restore test on staging |
| PostgreSQL (WAL) | Incremental | Continuous (archived every 5 min) | 7 days | Same region R2 (`backups/wal/`) | AES-256-GCM | WAL-G archiving | Automated integrity check |
| PostgreSQL (PITR) | Point-in-time | On demand | 7 days | WAL + base backup | AES-256-GCM | WAL-G restore | Quarterly DR drill |
| R2 Documents | Real-time replication | Continuous | 30 days | Cross-region R2 (`backups/r2/`) | AES-256 (server-side) | R2 native replication | Quarterly integrity check |
| R2 Versioning | Object versions | Per write | 3 versions | Same bucket | AES-256 | R2 native versioning | N/A |
| Redis | RDB snapshot | Daily at 03:00 UTC | 7 days | R2 (`backups/redis/`) | AES-256-GCM | `BGSAVE` + upload | Monthly restore test |
| Configuration | Git snapshot | On every commit | 1 year (Git history) | GitHub | N/A (Git) | Git push | N/A |
| Audit Logs | WORM append | Real-time | 7 years | Separate PostgreSQL instance + HSM | AES-256-GCM + HSM | Application INSERT | Annual integrity audit |
| Telegram Cold Backup | Document upload | On every upload (optional) | Unlimited (Telegram policy) | Telegram Cloud | AES-256 (pre-encrypted) | Bot API upload | Manual verification (quarterly) |
| SSL Certificates | Certificate + key | On renewal | 1 year | HashiCorp Vault + R2 | AES-256-GCM | certbot + vault | Automated expiry check |

### 7.2 Restore Procedures

#### PostgreSQL Point-in-Time Recovery (PITR)

```bash
#!/bin/bash
# PostgreSQL PITR Procedure
# AUTHORIZATION: SRE Lead + DBA Lead (two-party approval)
# USE CASE: Database corruption, accidental deletion, ransomware recovery

set -euo pipefail

TARGET_TIME="${1:-$(date -u '+%Y-%m-%d %H:%M:%S UTC')}"  # Default: now
BACKUP_BUCKET="r2://backups/db/"
WAL_BUCKET="r2://backups/wal/"
RESTORE_DIR="/var/lib/postgresql/restore_$(date +%s)"

echo "=== PostgreSQL PITR to $TARGET_TIME ==="

# Step 1: Identify latest base backup before target time
LATEST_BASE=$(rclone ls $BACKUP_BUCKET | sort -k2 | tail -1 | awk '{print $2}')
echo "Latest base backup: $LATEST_BASE"

# Step 2: Download base backup
mkdir -p $RESTORE_DIR
rclone copy "${BACKUP_BUCKET}${LATEST_BASE}" $RESTORE_DIR/
echo "Base backup downloaded"

# Step 3: Extract
tar -xzf "${RESTORE_DIR}/${LATEST_BASE}" -C $RESTORE_DIR/
echo "Base backup extracted"

# Step 4: Configure recovery
mkdir -p $RESTORE_DIR/pg_wal
cat > $RESTORE_DIR/recovery.signal <<EOF
# Recovery signal file
EOF

cat > $RESTORE_DIR/postgresql.conf.d/recovery.conf <<EOF
restore_command = 'wal-g wal-fetch %f %p'
recovery_target_time = '$TARGET_TIME'
recovery_target_action = 'promote'
EOF

# Step 5: Start PostgreSQL in recovery mode
pg_ctl start -D $RESTORE_DIR -l $RESTORE_DIR/logfile
echo "PostgreSQL started in recovery mode"

# Step 6: Monitor recovery progress
until psql -h localhost -c "SELECT pg_is_in_recovery();" | grep -q "f"; do
    echo "Recovery in progress... $(date)"
    sleep 30
done

# Step 7: Verify
echo "Recovery complete!"
psql -h localhost -c "SELECT NOW() as recovery_time, pg_last_xact_replay_timestamp() as last_replay;"
psql -h localhost -c "SELECT COUNT(*) as document_count FROM documents;"
psql -h localhost -c "SELECT COUNT(*) as chunk_count FROM chunks;"

# Step 8: Promote to primary (if this is the new primary)
# psql -h localhost -c "SELECT pg_promote();"

echo "=== PITR Complete ==="
```

#### R2 Document Recovery

```bash
#!/bin/bash
# R2 Document Recovery Procedure
# USE CASE: R2 primary region failure, bucket deletion, object corruption

set -euo pipefail

SOURCE_BUCKET="r2://backups/r2/"
DEST_BUCKET="r2://adaptive-study-planner-prod/"
RESTORE_LOG="/var/log/r2_restore_$(date +%s).log"

echo "=== R2 Document Recovery ==="

# Step 1: List objects in cross-region backup bucket
echo "Listing backup objects..."
rclone ls $SOURCE_BUCKET --recursive > /tmp/backup_objects.txt
TOTAL=$(wc -l < /tmp/backup_objects.txt)
echo "Total objects to verify: $TOTAL"

# Step 2: Sync to primary bucket (with checksum verification)
echo "Starting sync..."
rclone sync $SOURCE_BUCKET $DEST_BUCKET \
    --checksum \
    --transfers 32 \
    --checkers 64 \
    --log-file $RESTORE_LOG \
    --stats 10s

# Step 3: Verify integrity (sample 10% of objects)
echo "Verifying integrity..."
SAMPLE_SIZE=$((TOTAL / 10))
shuf -n $SAMPLE_SIZE /tmp/backup_objects.txt | while read line; do
    OBJ=$(echo $line | awk '{print $2}')
    SOURCE_CHECKSUM=$(rclone md5sum "${SOURCE_BUCKET}${OBJ}")
    DEST_CHECKSUM=$(rclone md5sum "${DEST_BUCKET}${OBJ}")
    if [[ "$SOURCE_CHECKSUM" != "$DEST_CHECKSUM" ]]; then
        echo "MISMATCH: $OBJ" >> /tmp/integrity_errors.txt
    fi
done

if [[ -f /tmp/integrity_errors.txt ]]; then
    echo "WARNING: Integrity errors found:"
    cat /tmp/integrity_errors.txt
else
    echo "Integrity verification PASSED (sampled $SAMPLE_SIZE objects)"
fi

# Step 4: Verify database-document consistency
echo "Checking database consistency..."
psql -c "SELECT id, r2_path FROM documents WHERE r2_path NOT IN (SELECT r2_path FROM restored_objects);"

echo "=== R2 Recovery Complete ==="
```

#### Telegram Cold Backup Recovery

```bash
#!/bin/bash
# Telegram Cold Backup Recovery
# USE CASE: Primary and cross-region R2 both unavailable
# NOTE: This is a last-resort procedure. Recovery is manual and slow.
# AUTHORIZATION: SRE Lead + CTO (two-party approval)

set -euo pipefail

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHANNEL_ID="${TELEGRAM_CHANNEL_ID:-}"
USER_ID="${1:-}"
DOCUMENT_ID="${2:-}"

if [[ -z "$TELEGRAM_BOT_TOKEN" || -z "$TELEGRAM_CHANNEL_ID" ]]; then
    echo "ERROR: Telegram credentials not configured"
    exit 1
fi

echo "=== Telegram Cold Backup Recovery ==="
echo "User: $USER_ID, Document: $DOCUMENT_ID"

# Step 1: Search Telegram channel for document
# Caption format: "BACKUP:user_id:{user_id}:doc_id:{document_id}:sha256:{hash}"
SEARCH_QUERY="BACKUP:user_id:${USER_ID}:doc_id:${DOCUMENT_ID}"

echo "Searching Telegram for: $SEARCH_QUERY"
# Use Telegram Bot API to search messages
# Note: Bot API does not support message search; this requires manual admin review
# Alternative: Maintain a local index of Telegram backup captions

# Step 2: If found, download file
# Step 3: Validate checksum (SHA-256)
# Step 4: Restore to R2
# Step 5: Re-index in database
# Step 6: Verify accessibility

echo "WARNING: Telegram recovery is manual. See runbook: docs/runbooks/telegram-recovery.md"
echo "=== Telegram Recovery Initiated (manual steps required) ==="
```

### 7.3 RPO and RTO Matrix

| Scenario | RPO (Data Loss) | RTO (Downtime) | Recovery Method | Validation |
|----------|----------------|----------------|-----------------|------------|
| Database corruption (single table) | < 5 minutes | < 30 minutes | Point-in-time recovery from WAL | Row count verification, sample query |
| Database primary failure (replicas OK) | 0 | < 5 minutes | Promote read replica to primary | Connection test, replication check |
| Complete database loss (primary + replicas) | < 1 hour | < 2 hours | PITR from cross-region backup + WAL | Full restore test, data integrity check |
| R2 bucket deletion | < 1 hour | < 1 hour | Cross-region sync to new bucket | Object count, checksum sample |
| R2 region failure | 0 | < 30 minutes | DNS switch to cross-region replica | Access test, download verification |
| Complete region failure (all services) | < 1 hour | < 4 hours | Activate DR region, restore from backups | Full platform health check, E2E test |
| Telegram-only recovery (all R2 lost) | N/A (last Telegram backup) | < 24 hours | Manual download from Telegram, validate, re-index | Checksum validation, accessibility test |
| Redis failure | 0 (cache only) | < 5 minutes | Restart Redis, warm cache from database | Cache hit rate recovery |
| AI inference cluster failure | 0 | < 2 minutes | Fallback to OpenAI → Ollama | Inference health check, quality sample |
| Configuration loss | 0 | < 10 minutes | Restore from Git + Terraform state | Config diff, service restart |

### 7.4 Recovery Validation

| Validation Type | Frequency | Method | Owner | Criteria |
|-----------------|-----------|--------|-------|----------|
| Automated restore test | Monthly | Automated CI job restores latest backup to staging, runs smoke tests | SRE | All smoke tests pass, row counts match, no corruption |
| Full DR drill | Quarterly | Manual execution of DR runbook, restore to DR environment, run E2E suite | SRE Lead + CTO | RTO < 4 hours, RPO < 1 hour, all E2E tests pass |
| R2 integrity check | Quarterly | `rclone check` between primary and cross-region buckets, sample 10% | SRE | 0 mismatches, all objects accessible |
| Telegram backup verification | Quarterly | Manual download of 5 random documents, validate checksums | SRE | All checksums match, files uncorrupted |
| Backup completeness audit | Weekly | Verify all expected backups exist (daily DB, daily Redis, continuous WAL) | SRE | 0 missing backups |
| Recovery documentation review | Quarterly | Review and update all DR runbooks, test procedures | SRE Lead | All runbooks updated, no stale references |

**Validation Criteria (Full DR Drill):**

- [ ] All user documents accessible and uncorrupted (SHA-256 verified)
- [ ] All embeddings searchable with correct similarity scores (sample 100 queries)
- [ ] All knowledge graph edges intact (cycle detection passes, edge count matches)
- [ ] AI responses correctly grounded (100% citation verification on 50 test queries)
- [ ] Citation verification passes (0 invented citations in 50 test queries)
- [ ] User authentication functional (login, logout, token refresh)
- [ ] Document upload and processing end-to-end (1 test document, < 5 min)
- [ ] Search and Q&A functional (10 test queries, all answered with citations)
- [ ] Study plan generation functional (1 test plan, includes KB topics)
- [ ] Export functional (JSON, Markdown, Anki formats)
- [ ] Performance within SLO (p95 latency < 500ms for API, < 2s for AI)
- [ ] Monitoring and alerting functional (all golden signals reported)

### 7.5 DR Runbook Index

| Scenario | Runbook | Last Tested | Next Test | Owner |
|----------|---------|-------------|-----------|-------|
| Database primary failure | `runbooks/db-failover.md` | [Date] | [Date + 3 months] | DBA Lead |
| Complete database loss | `runbooks/db-restore-pitr.md` | [Date] | [Date + 3 months] | DBA Lead |
| R2 region failure | `runbooks/r2-failover.md` | [Date] | [Date + 3 months] | SRE Lead |
| R2 bucket deletion | `runbooks/r2-restore.md` | [Date] | [Date + 3 months] | SRE Lead |
| AI inference cluster failure | `runbooks/llm-failover.md` | [Date] | [Date + 3 months] | AI Infra Lead |
| Complete region failure | `runbooks/dr-activation.md` | [Date] | [Date + 3 months] | SRE Lead |
| DDoS attack | `runbooks/ddos-response.md` | [Date] | [Date + 6 months] | Security Lead |
| Security breach | `runbooks/security-incident.md` | [Date] | [Date + 3 months] | Security Lead |
| Telegram recovery | `runbooks/telegram-recovery.md` | [Date] | [Date + 3 months] | SRE Lead |
| OCR pipeline failure | `runbooks/ocr-recovery.md` | [Date] | [Date + 3 months] | AI Infra Lead |
| Embedding rebuild | `runbooks/embedding-rebuild.md` | [Date] | [Date + 3 months] | AI Infra Lead |
| Knowledge graph rebuild | `runbooks/graph-rebuild.md` | [Date] | [Date + 3 months] | DBA Lead |

---

## 8. Operational Procedures

### 8.1 Starting Services

```bash
#!/bin/bash
# Service Startup Procedure
# ENVIRONMENT: Production
# AUTHORIZATION: SRE Lead or on-call engineer

set -euo pipefail

echo "=== Production Service Startup ==="

# 1. Cloudflare Workers (API Gateway)
echo "[1/10] Starting Cloudflare Workers..."
wrangler deploy --env production
echo "Workers deployed"

# 2. Supabase Edge Functions
echo "[2/10] Starting Supabase Edge Functions..."
supabase functions deploy --project-ref "$SUPABASE_PROD_REF" --all
echo "Edge Functions deployed"

# 3. vLLM (GPU Inference)
echo "[3/10] Starting vLLM..."
docker-compose -f docker-compose.prod.yml up -d vllm
sleep 30  # Wait for model load
curl -s http://vllm:8000/health | grep -q "ok" && echo "vLLM healthy" || echo "WARNING: vLLM health check failed"

# 4. Ollama (CPU Fallback)
echo "[4/10] Starting Ollama..."
ollama serve &
sleep 10
ollama pull llama3.2
echo "Ollama ready"

# 5. PostgreSQL (if self-managed)
echo "[5/10] Starting PostgreSQL..."
pg_ctl start -D /var/lib/postgresql/data
echo "PostgreSQL started"

# 6. Redis
echo "[6/10] Starting Redis..."
redis-server /etc/redis/redis.conf
echo "Redis started"

# 7. Monitoring Stack
echo "[7/10] Starting monitoring..."
docker-compose -f monitoring/docker-compose.yml up -d
echo "Monitoring started"

# 8. Verify all services
echo "[8/10] Running health checks..."
./scripts/health-check-all.sh
echo "All health checks passed"

# 9. Enable traffic
echo "[9/10] Enabling traffic..."
wrangler kv put MAINTENANCE_MODE "false" --env production
echo "Traffic enabled"

# 10. Notify
echo "[10/10] Notifying team..."
slack send --channel="#sre-alerts" --message "✅ All production services started successfully"

echo "=== Startup Complete ==="
```

### 8.2 Stopping Services (Graceful Shutdown)

```bash
#!/bin/bash
# Service Shutdown Procedure
# ENVIRONMENT: Production
# AUTHORIZATION: SRE Lead or on-call engineer
# WARNING: This will make the platform unavailable

set -euo pipefail

echo "=== Production Service Shutdown ==="

# 1. Enable maintenance mode
echo "[1/8] Enabling maintenance mode..."
wrangler kv put MAINTENANCE_MODE "true" --env production
curl -X POST https://status.adaptive-study-planner.com/incidents \
    -d '{"status": "maintenance", "message": "Scheduled maintenance in progress"}'
echo "Maintenance mode enabled"

# 2. Wait for in-flight requests (drain)
echo "[2/8] Draining in-flight requests..."
sleep 60
echo "Drain complete (assumed)"

# 3. Stop Cloudflare Workers (no-dispatch)
echo "[3/8] Stopping Cloudflare Workers..."
wrangler deploy --env production --no-dispatch
echo "Workers stopped"

# 4. Stop Supabase Edge Functions
echo "[4/8] Stopping Supabase Edge Functions..."
supabase functions stop --project-ref "$SUPABASE_PROD_REF"
echo "Edge Functions stopped"

# 5. Stop vLLM
echo "[5/8] Stopping vLLM..."
docker-compose -f docker-compose.prod.yml down --timeout 60 vllm
echo "vLLM stopped"

# 6. Stop PostgreSQL (smart shutdown)
echo "[6/8] Stopping PostgreSQL..."
pg_ctl stop -D /var/lib/postgresql/data -m smart
echo "PostgreSQL stopped"

# 7. Stop Redis (save and shutdown)
echo "[7/8] Stopping Redis..."
redis-cli shutdown save
echo "Redis stopped"

# 8. Verify all stopped
echo "[8/8] Verification..."
./scripts/health-check-all.sh --expect-down
echo "All services confirmed stopped"

echo "=== Shutdown Complete ==="
```

### 8.3 Restarting Services

```bash
#!/bin/bash
# Service Restart Procedure
# USE CASE: Memory leak, configuration update, dependency refresh
# AUTHORIZATION: SRE Lead or on-call engineer

set -euo pipefail

SERVICE="${1:-}"
if [[ -z "$SERVICE" ]]; then
    echo "Usage: $0 <service_name>"
    echo "Services: workers, edge-functions, vllm, ollama, postgres, redis, monitoring"
    exit 1
fi

echo "=== Restarting $SERVICE ==="

case $SERVICE in
    workers)
        wrangler deploy --env production
        ;;
    edge-functions)
        supabase functions deploy --project-ref "$SUPABASE_PROD_REF" --all
        ;;
    vllm)
        docker-compose -f docker-compose.prod.yml restart --timeout 60 vllm
        sleep 30
        curl -s http://vllm:8000/health | grep -q "ok"
        ;;
    ollama)
        pkill ollama || true
        ollama serve &
        sleep 10
        ;;
    postgres)
        pg_ctl restart -D /var/lib/postgresql/data -m smart
        ;;
    redis)
        redis-cli shutdown save
        redis-server /etc/redis/redis.conf
        ;;
    monitoring)
        docker-compose -f monitoring/docker-compose.yml restart
        ;;
    *)
        echo "Unknown service: $SERVICE"
        exit 1
        ;;
esac

echo "=== $SERVICE Restarted ==="
```

### 8.4 Scaling Services

| Service | Scale Trigger | Scale Action | Max Scale | Owner | Automation |
|---------|--------------|--------------|-----------|-------|------------|
| Cloudflare Workers | RPS > 5,000 | Auto (serverless, no action needed) | Unlimited | Platform Engineering | Fully automated |
| Supabase Edge Functions | Queue depth > 100 | Auto (serverless, no action needed) | Unlimited | AI Infrastructure | Fully automated |
| vLLM GPU | GPU util > 80% for 10 min | Add GPU node (Kubernetes HPA) | 10 nodes | AI Infrastructure | Semi-automated (approval for > 3 nodes) |
| PostgreSQL | Connection count > 100 for 5 min | Add read replica | 5 replicas | Database Engineering | Manual (Terraform apply) |
| PgBouncer | Connection pool > 80% for 5 min | Add PgBouncer instance | 3 instances | Database Engineering | Manual |
| Redis | Memory > 80% for 10 min | Upgrade Upstash plan | 10 GB | Platform Engineering | Manual (Upstash console) |
| R2 | Storage growth | No action (unlimited) | Unlimited | Platform Engineering | N/A |
| Monitoring | Metric volume growth | Upgrade Grafana/Loki plan | Enterprise tier | SRE | Manual |
| CDN | Cache hit rate < 60% | Review cache rules, increase edge cache | N/A | Platform Engineering | Manual |

### 8.5 Rotating Secrets

```bash
#!/bin/bash
# Secret Rotation Procedure
# FREQUENCY: Per schedule in Section 3.16
# AUTHORIZATION: Security Engineer or SRE Lead
# WARNING: Incorrect rotation can cause service outage

set -euo pipefail

SECRET_TYPE="${1:-}"
if [[ -z "$SECRET_TYPE" ]]; then
    echo "Usage: $0 <secret_type>"
    echo "Types: api-key, db-password, jwt-key, oauth, llm-key, tls-cert"
    exit 1
fi

echo "=== Rotating $SECRET_TYPE ==="

# Step 1: Generate new secret
case $SECRET_TYPE in
    api-key)
        NEW_SECRET=$(openssl rand -hex 32)
        ;;
    db-password)
        NEW_SECRET=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
        ;;
    jwt-key)
        openssl genrsa -out /tmp/new_jwt_key.pem 2048
        NEW_SECRET=$(cat /tmp/new_jwt_key.pem)
        ;;
    oauth)
        echo "OAuth secrets must be rotated in provider console (Google, GitHub)"
        exit 1
        ;;
    llm-key)
        echo "LLM API keys must be rotated in provider dashboard (OpenAI, Google)"
        exit 1
        ;;
    tls-cert)
        certbot renew --force-renewal
        NEW_SECRET=$(cat /etc/letsencrypt/live/adaptive-study-planner.com/fullchain.pem)
        ;;
    *)
        echo "Unknown secret type: $SECRET_TYPE"
        exit 1
        ;;
esac

# Step 2: Update in HashiCorp Vault
vault kv put "secret/adaptive-study-planner/${SECRET_TYPE}" value="$NEW_SECRET"
echo "Updated in Vault"

# Step 3: Update in Supabase Vault (for DB credentials)
if [[ "$SECRET_TYPE" == "db-password" ]]; then
    supabase vault set-secret db-password "$NEW_SECRET"
    echo "Updated in Supabase Vault"
fi

# Step 4: Deploy with new secret (zero-downtime)
wrangler secret put "${SECRET_TYPE^^}" --env production <<< "$NEW_SECRET"
echo "Deployed to Cloudflare Workers"

# Step 5: Verify
wrangler tail --env production | grep -i "${SECRET_TYPE}" | head -5
echo "Verification complete (tail logs for 30 seconds)"

# Step 6: Revoke old secret (24 hours later — allows for cache expiration)
echo "Old secret will be revoked in 24 hours. Schedule: at now + 24 hours"
# at now + 24 hours <<EOF
# vault kv delete "secret/adaptive-study-planner/${SECRET_TYPE}-old"
# EOF

echo "=== Rotation Complete ==="
```

### 8.6 Database Migrations

```bash
#!/bin/bash
# Database Migration Procedure
# REQUIREMENT: All migrations must be reversible (up.sql + down.sql)
# AUTHORIZATION: DBA Lead or SRE Lead
# MAINTENANCE WINDOW: Required if migration > 1 minute downtime

set -euo pipefail

MIGRATION_NAME="${1:-}"
if [[ -z "$MIGRATION_NAME" ]]; then
    echo "Usage: $0 <migration_name>"
    exit 1
fi

echo "=== Database Migration: $MIGRATION_NAME ==="

# Step 1: Create migration files (reversible)
supabase migration new "$MIGRATION_NAME"
echo "Migration files created:"
echo "  - supabase/migrations/..._${MIGRATION_NAME}/up.sql"
echo "  - supabase/migrations/..._${MIGRATION_NAME}/down.sql"

# Step 2: Write migration (manual step — engineer edits files)
echo "[MANUAL] Edit up.sql and down.sql"
read -p "Press Enter when migration files are complete..."

# Step 3: Test on staging
echo "[3/5] Testing on staging..."
supabase db reset --linked
supabase migration up --linked

# Run smoke tests
./scripts/smoke-tests.sh staging
if [[ $? -ne 0 ]]; then
    echo "ERROR: Smoke tests failed on staging. Aborting."
    exit 1
fi

# Step 4: Estimate downtime
DOWNTIME=$(psql -c "EXPLAIN (ANALYZE, TIMING) $(cat supabase/migrations/*/up.sql)" 2>&1 | grep "Execution Time" | awk '{print $3}')
echo "Estimated downtime: ${DOWNTIME}ms"

# Step 5: Deploy to production
if [[ $(echo "$DOWNTIME > 60000" | bc) -eq 1 ]]; then
    echo "WARNING: Migration estimated downtime > 1 minute. Maintenance window required."
    read -p "Enter maintenance window authorization code: " AUTH
    if [[ "$AUTH" != "$(vault kv get -field=maintenance_code secret/adaptive-study-planner)" ]]; then
        echo "Authorization failed. Aborting."
        exit 1
    fi
    # Enable maintenance mode
    wrangler kv put MAINTENANCE_MODE "true" --env production
fi

echo "[4/5] Deploying to production..."
supabase migration up --linked

# Step 6: Verify
psql -c "\d" | grep -q "$MIGRATION_NAME" && echo "Migration verified" || echo "WARNING: Migration not found"

# Step 7: If failure, rollback
if [[ $? -ne 0 ]]; then
    echo "ERROR: Migration verification failed. Rolling back..."
    supabase migration down --linked
    exit 1
fi

# Step 8: Disable maintenance mode (if enabled)
wrangler kv put MAINTENANCE_MODE "false" --env production

echo "=== Migration Complete ==="
```

### 8.7 Reindexing Vectors (Zero-Downtime)

```sql
-- Zero-Downtime Vector Reindexing Procedure
-- USE CASE: Index corruption, model upgrade, performance degradation
-- AUTHORIZATION: DBA Lead

-- Step 1: Create new index concurrently (no table lock)
CREATE INDEX CONCURRENTLY idx_chunks_embedding_new
ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 200);

-- Step 2: Wait for index build to complete (monitor pg_stat_progress_create_index)
SELECT phase, blocks_total, blocks_done,
       ROUND(blocks_done::numeric / NULLIF(blocks_total, 0) * 100, 2) AS pct_complete
FROM pg_stat_progress_create_index
WHERE relid = 'chunks'::regclass;

-- Step 3: Verify index is valid (not marked as invalid)
SELECT indexrelid::regclass AS index_name,
       indisvalid AS is_valid
FROM pg_index
WHERE indrelid = 'chunks'::regclass
  AND indexrelid = 'idx_chunks_embedding_new'::regclass;

-- Step 4: Drop old index concurrently
DROP INDEX CONCURRENTLY idx_chunks_embedding;

-- Step 5: Rename new index to standard name
ALTER INDEX idx_chunks_embedding_new RENAME TO idx_chunks_embedding;

-- Step 6: Verify query plan uses new index
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM chunks
ORDER BY embedding <-> $1
LIMIT 5;
-- Expect: Index Scan using idx_chunks_embedding
```

### 8.8 Rebuilding Knowledge Graph

```bash
#!/bin/bash
# Knowledge Graph Rebuild Procedure
-- USE CASE: Graph corruption, model upgrade, prerequisite relationship update
-- AUTHORIZATION: DBA Lead + AI Infrastructure Lead
-- WARNING: This is computationally expensive. Run during off-peak hours.

set -euo pipefail

echo "=== Knowledge Graph Rebuild ==="

# Step 1: Create backup of existing edges
psql -c "CREATE TABLE knowledge_edges_backup_$(date +%Y%m%d) AS SELECT * FROM knowledge_edges;"
echo "Backup created"

# Step 2: Truncate existing edges (preserve nodes/concepts)
psql -c "TRUNCATE knowledge_edges;"
echo "Edges truncated"

# Step 3: Re-run extraction for all documents (batch processing)
python -m backend.extraction.batch_rebuild --all-documents --batch-size 10 --parallel 5
echo "Extraction complete"

# Step 4: Verify edge count
EDGE_COUNT=$(psql -t -c "SELECT COUNT(*) FROM knowledge_edges;")
echo "Total edges: $EDGE_COUNT"

# Step 5: Check for cycles (should be none)
CYCLES=$(psql -t -c "SELECT COUNT(*) FROM detect_cycles();")
if [[ "$CYCLES" -gt 0 ]]; then
    echo "WARNING: $CYCLES cycles detected in knowledge graph"
    psql -c "SELECT * FROM detect_cycles();"
else
    echo "No cycles detected"
fi

# Step 6: Verify prerequisite chain integrity
psql -c "SELECT COUNT(*) as orphaned_edges FROM knowledge_edges WHERE source_node NOT IN (SELECT name FROM concepts) OR target_node NOT IN (SELECT name FROM concepts);"

# Step 7: Sample verification (10 random users)
psql -c "SELECT user_id, COUNT(*) as edge_count FROM knowledge_edges GROUP BY user_id ORDER BY RANDOM() LIMIT 10;"

echo "=== Rebuild Complete ==="
```

### 8.9 Clearing Queues

```bash
#!/bin/bash
# Queue Clearing Procedure
# USE CASE: Poison message, queue corruption, emergency maintenance
# AUTHORIZATION: SRE Lead

set -euo pipefail

QUEUE_NAME="${1:-}"
if [[ -z "$QUEUE_NAME" ]]; then
    echo "Usage: $0 <queue_name>"
    echo "Queues: document_processing, ocr, embedding, retrieval, ai_inference, export, dead_letter"
    exit 1
fi

echo "=== Clearing Queue: $QUEUE_NAME ==="

# Step 1: Check current depth
DEPTH=$(redis-cli LLEN "${QUEUE_NAME}_queue")
echo "Current depth: $DEPTH"

# Step 2: Confirm (destructive action)
read -p "This will delete all $DEPTH items from $QUEUE_NAME. Type 'DELETE' to confirm: " CONFIRM
if [[ "$CONFIRM" != "DELETE" ]]; then
    echo "Aborted."
    exit 1
fi

# Step 3: Archive to dead letter (if not already dead letter)
if [[ "$QUEUE_NAME" != "dead_letter" ]]; then
    redis-cli EVAL "
        local items = redis.call('lrange', KEYS[1], 0, -1)
        for _, item in ipairs(items) do
            redis.call('rpush', 'dead_letter_queue', item)
        end
        return #items
    " 1 "${QUEUE_NAME}_queue"
    echo "Items archived to dead_letter_queue"
fi

# Step 4: Clear queue
redis-cli DEL "${QUEUE_NAME}_queue"
echo "Queue cleared"

# Step 5: Log
slack send --channel="#sre-alerts" \
    --message "⚠️ Queue $QUEUE_NAME cleared by $(whoami). $DEPTH items affected."

echo "=== Queue Cleared ==="
```

### 8.10 Recovering Failed OCR Jobs

```bash
#!/bin/bash
# Failed OCR Recovery Procedure
# USE CASE: OCR engine failure, batch of jobs stuck in queue
# AUTHORIZATION: AI Infrastructure Lead or SRE Lead

set -euo pipefail

echo "=== Failed OCR Recovery ==="

# Step 1: Identify failed OCR jobs
FAILED=$(psql -t -c "SELECT id FROM documents WHERE status = 'error' AND ocr_confidence IS NULL;")
FAILED_COUNT=$(echo "$FAILED" | wc -l)
echo "Failed OCR jobs: $FAILED_COUNT"

# Step 2: For each failed job, retry with alternative engine
for DOC_ID in $FAILED; do
    echo "Retrying document: $DOC_ID"
    
    # Get original engine
    ORIG_ENGINE=$(psql -t -c "SELECT ocr_engine FROM documents WHERE id = '$DOC_ID';")
    
    # Try alternative engine
    if [[ "$ORIG_ENGINE" == "tesseract" ]]; then
        NEW_ENGINE="google_vision"
    else
        NEW_ENGINE="tesseract"
    fi
    
    # Retry
    python -m backend.ocr.retry --document-id "$DOC_ID" --engine "$NEW_ENGINE"
    
    # Check result
    NEW_STATUS=$(psql -t -c "SELECT status FROM documents WHERE id = '$DOC_ID';")
    if [[ "$NEW_STATUS" == "ready" ]]; then
        echo "  → Success with $NEW_ENGINE"
    else
        echo "  → Failed again. Flagging for manual review."
        psql -c "UPDATE documents SET status = 'manual_review_needed' WHERE id = '$DOC_ID';"
    fi
done

echo "=== Recovery Complete ==="
```

### 8.11 Recovering Failed Ingestion Jobs

```bash
#!/bin/bash
# Failed Ingestion Recovery Procedure
# USE CASE: Pipeline stage failure, document stuck in processing
# AUTHORIZATION: AI Infrastructure Lead

set -euo pipefail

echo "=== Failed Ingestion Recovery ==="

# Step 1: Identify stuck documents
STUCK=$(psql -t -c "SELECT id FROM documents WHERE status IN ('uploaded', 'validating', 'scanning', 'extracting', 'chunking', 'embedding', 'indexing') AND updated_at < NOW() - INTERVAL '1 hour';")
STUCK_COUNT=$(echo "$STUCK" | wc -l)
echo "Stuck documents: $STUCK_COUNT"

# Step 2: Reset status and re-queue
for DOC_ID in $STUCK; do
    echo "Re-queueing document: $DOC_ID"
    psql -c "UPDATE documents SET status = 'uploaded', error_message = NULL, updated_at = NOW() WHERE id = '$DOC_ID';"
    
    # Trigger reprocessing
    curl -X POST "https://adaptive-study-planner.com/api/v3/documents/$DOC_ID/reprocess" \
        -H "Authorization: Bearer $SERVICE_TOKEN"
done

# Step 3: Monitor
sleep 60
STILL_STUCK=$(psql -t -c "SELECT COUNT(*) FROM documents WHERE status IN ('uploaded', 'validating', 'scanning', 'extracting', 'chunking', 'embedding', 'indexing') AND updated_at < NOW() - INTERVAL '1 hour';")
echo "Still stuck after retry: $STILL_STUCK"

if [[ "$STILL_STUCK" -gt 0 ]]; then
    echo "WARNING: Some documents still stuck. Investigate pipeline."
    slack send --channel="#ai-alerts" --message "⚠️ $STILL_STUCK documents still stuck after ingestion retry"
fi

echo "=== Recovery Complete ==="
```

### 8.12 Recovering Failed Retrieval Jobs

```bash
#!/bin/bash
# Failed Retrieval Recovery Procedure
# USE CASE: Search returning empty, retrieval latency spike
# AUTHORIZATION: AI Infrastructure Lead or SRE Lead

set -euo pipefail

echo "=== Failed Retrieval Recovery ==="

# Step 1: Check vector index health
psql -c "SELECT indexrelid::regclass, indexdef FROM pg_index WHERE indrelid = 'chunks'::regclass;"

# Step 2: Check for corrupted embeddings
CORRUPTED=$(psql -t -c "SELECT COUNT(*) FROM chunks WHERE embedding IS NULL;")
echo "Chunks with NULL embeddings: $CORRUPTED"

if [[ "$CORRUPTED" -gt 0 ]]; then
    echo "Re-embedding corrupted chunks..."
    python -m backend.embedding.retry --null-only
fi

# Step 3: Check index validity
INVALID=$(psql -t -c "SELECT COUNT(*) FROM pg_index WHERE indrelid = 'chunks'::regclass AND NOT indisvalid;")
if [[ "$INVALID" -gt 0 ]]; then
    echo "WARNING: $INVALID invalid indexes found. Reindexing..."
    psql -c "REINDEX INDEX CONCURRENTLY idx_chunks_embedding;"
fi

# Step 4: Clear query cache (may contain stale results)
redis-cli DEL "search:*"
redis-cli DEL "query:*"
echo "Query cache cleared"

# Step 5: Verify retrieval
TEST_QUERY="What is the ideal gas law?"
RESULT=$(curl -s -X POST "https://adaptive-study-planner.com/api/v3/retrieve" \
    -H "Authorization: Bearer $TEST_TOKEN" \
    -d "{\"query\": \"$TEST_QUERY\"}" | jq '.results | length')

if [[ "$RESULT" -gt 0 ]]; then
    echo "Retrieval verification PASSED ($RESULT results)"
else
    echo "WARNING: Retrieval still failing. Escalate to AI Infra Lead."
fi

echo "=== Recovery Complete ==="
```

### 8.13 Emergency Maintenance

```bash
#!/bin/bash
# Emergency Maintenance Procedure
# USE CASE: Critical security patch, data corruption fix, infrastructure emergency
# AUTHORIZATION: SRE Lead + CTO (two-party approval required)

set -euo pipefail

echo "=== Emergency Maintenance ==="

# Step 1: Two-party authorization
read -p "SRE Lead authorization code: " SRE_AUTH
read -p "CTO authorization code: " CTO_AUTH

if [[ "$SRE_AUTH" != "$(vault kv get -field=emergency_maintenance_sre secret/adaptive-study-planner)" || \
      "$CTO_AUTH" != "$(vault kv get -field=emergency_maintenance_cto secret/adaptive-study-planner)" ]]; then
    echo "Authorization failed. Both parties must approve."
    exit 1
fi

# Step 2: Enable maintenance mode
wrangler kv put MAINTENANCE_MODE "true" --env production

# Step 3: Notify users
curl -X POST https://status.adaptive-study-planner.com/incidents \
    -d '{"status": "maintenance", "message": "Emergency maintenance in progress. ETA: 30 minutes."}'

slack send --channel="#sre-alerts" \
    --message "🚨 Emergency maintenance started by $(whoami). Authorization: SRE Lead + CTO."

# Step 4: Drain in-flight requests
sleep 60

# Step 5: Perform maintenance (specific steps depend on the emergency)
echo "[MANUAL] Perform maintenance steps here."
read -p "Press Enter when maintenance is complete..."

# Step 6: Verify health
for i in {1..10}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://adaptive-study-planner.com/api/v3/health)
    if [[ "$STATUS" == "200" ]]; then
        echo "Health check PASSED (attempt $i)"
        break
    fi
    sleep 5
done

if [[ "$STATUS" != "200" ]]; then
    echo "CRITICAL: Health check FAILED after maintenance."
    pagerduty trigger --escalation-policy="CTO"
    exit 1
fi

# Step 7: Disable maintenance mode
wrangler kv put MAINTENANCE_MODE "false" --env production

# Step 8: Notify
curl -X POST https://status.adaptive-study-planner.com/incidents \
    -d '{"status": "resolved", "message": "Emergency maintenance complete. All systems operational."}'

slack send --channel="#sre-alerts" \
    --message "✅ Emergency maintenance complete. All health checks passing."

echo "=== Emergency Maintenance Complete ==="
```

---

## 9. Security Operations

### 9.1 Identity and Access Management (IAM)

| Identity Type | Authentication | Authorization | Lifecycle | Owner |
|---------------|---------------|---------------|-----------|-------|
| End Users | Supabase Auth (OAuth 2.0, SAML 2.0, password) | RBAC + RLS | Self-service registration, admin-managed deletion | Security Engineering |
| Service Accounts | Scoped JWT (RS256) | RBAC (system role) | Created by Terraform, rotated every 90 days | Security Engineering |
| CI/CD Pipeline | GitHub Actions OIDC + Vault | Role-based (deploy, read) | Tied to repository, no long-lived credentials | DevOps |
| On-Call Engineers | Personal accounts + MFA | RBAC + JIT admin access | HR-managed, deactivated within 24 hours of departure | Security Engineering |
| Emergency Access | Break-glass accounts (HSM-secured) | Full admin (audit logged) | Pre-created, 2-party approval to activate | Security Engineering + CTO |
| Third-Party Integrations | OAuth 2.0 + scoped API keys | Minimal permissions (principle of least privilege) | Contract-defined, reviewed quarterly | Security Engineering |

### 9.2 Role-Based Access Control (RBAC)

| Role | Permissions | Scope | MFA Required | Data Access |
|------|-------------|-------|--------------|-------------|
| `user` | CRUD own documents, search own KB, generate flashcards/quizzes, view own analytics | Own data only | Optional (recommended) | Own documents, chunks, embeddings, concepts |
| `editor` | `user` + edit shared topics, add comments, manage group content | Group-shared data + own data | Optional | Own data + shared group data |
| `admin` | `editor` + manage group members, view group analytics, moderate content | Group data + own data | Required | Group data + aggregated analytics (no raw PII) |
| `system` | Read all data for processing, write logs/metrics, manage queues | Internal infrastructure | N/A (service account) | All data (for processing only, no human access) |
| `enterprise` | `admin` + SAML SSO, API access, custom branding, dedicated support | Tenant data (institutional) | Required (SAML-enforced) | Tenant data + institutional analytics |
| `sre` | Read metrics, restart services, trigger DR, view logs | Infrastructure | Required | Metrics, logs, no user PII without JIT |
| `security_admin` | Read audit logs, rotate secrets, manage RLS, review access | Security | Required + hardware token | Audit logs, security events, no user content |
| `compliance_officer` | Read audit logs, verify retention, export compliance reports | Compliance | Required | Audit logs, retention reports, no user content |
| `data_architect` | Read all schemas, recommend indexing, review query plans | Database | Required | Schema metadata, query plans, no user content |

### 9.3 Secrets Rotation Schedule

| Secret Type | Rotation Frequency | Method | Owner | Notification | Automation |
|-------------|-------------------|--------|-------|------------|------------|
| JWT signing keys | 180 days | Key rotation API (graceful, dual-key period) | Security Engineering | 30 days before expiry | Semi-automated |
| Database passwords | 90 days | Supabase Vault rotation + application redeploy | Database Engineering | 14 days before expiry | Manual |
| API keys (OpenAI) | 90 days | OpenAI dashboard + Vault update | AI Infrastructure | 14 days before expiry | Manual |
| API keys (Google Vision) | 90 days | Google Cloud Console + Vault update | AI Infrastructure | 14 days before expiry | Manual |
| API keys (MathPix) | 90 days | MathPix dashboard + Vault update | AI Infrastructure | 14 days before expiry | Manual |
| OAuth client secrets | 90 days | Provider dashboard + Vault update | Security Engineering | 14 days before expiry | Manual |
| TLS certificates | 90 days | certbot auto-renew + Cloudflare | Platform Engineering | 30 days before expiry | Fully automated |
| Telegram bot token | 180 days | BotFather + Vault update | SRE | 30 days before expiry | Manual |
| User content encryption keys | 90 days (on request) | Supabase Vault envelope rotation | Security Engineering | User-initiated | Manual |
| Backup encryption keys | 180 days | HSM ceremony (Shamir's 3 of 5) | Security Engineering + SRE Lead | 60 days before expiry | Manual ceremony |
| CI/CD secrets | 90 days | GitHub Secrets + Vault rotation | DevOps | 14 days before expiry | Semi-automated |
| Feature flag API keys | 180 days | LaunchDarkly dashboard + Vault update | Platform Engineering | 30 days before expiry | Manual |

### 9.4 Certificate Rotation

```bash
#!/bin/bash
# TLS Certificate Rotation Procedure
# FREQUENCY: Every 90 days (automated)
# MONITORING: Alert if expiry < 30 days

# Check current certificate expiry
echo | openssl s_client -servername adaptive-study-planner.com \
    -connect adaptive-study-planner.com:443 2>/dev/null | \
    openssl x509 -noout -dates

# Cloudflare certificates auto-renew
cloudflare cert show --zone adaptive-study-planner.com

# If manual (Let's Encrypt for self-managed):
# certbot renew --force-renewal
# wrangler secret put TLS_CERT --env production < /etc/letsencrypt/live/adaptive-study-planner.com/fullchain.pem
# wrangler secret put TLS_KEY --env production < /etc/letsencrypt/live/adaptive-study-planner.com/privkey.pem
```

### 9.5 Encryption Standards

| Layer | Algorithm | Key Size | Mode | Key Management | Rotation | Owner |
|-------|-----------|----------|------|---------------|----------|-------|
| Transport | TLS | 2048-bit RSA / 256-bit ECDSA | TLS 1.3 | Let's Encrypt / Cloudflare | 90 days | Platform Engineering |
| Data at Rest (R2) | AES | 256-bit | GCM | Cloudflare-managed | Automatic | Cloudflare |
| Data at Rest (PostgreSQL) | AES | 256-bit | GCM | Supabase-managed | Automatic | Supabase |
| Data at Rest (Redis) | AES | 256-bit | GCM | Upstash-managed | Automatic | Upstash |
| Field-Level (PII) | AES | 256-bit | GCM | User-specific keys (envelope encryption) | 90 days | Security Engineering |
| Document Content | AES | 256-bit | GCM | User-specific keys (zero-knowledge) | 90 days (on request) | User (key holder) |
| Backups | AES | 256-bit | GCM | Separate backup key (HSM) | 180 days | Security Engineering |
| WORM Audit Logs | AES | 256-bit | GCM | HSM-backed key | 180 days | Security Engineering |
| Secrets in Vault | AES | 256-bit | GCM | HashiCorp Vault auto-unseal | Automatic | Security Engineering |

### 9.6 Key Management

| Key Type | Storage | Access Control | Rotation | Recovery | Audit |
|----------|---------|---------------|----------|----------|-------|
| Database encryption key | Cloud KMS (Supabase) | Database Engineering (JIT) | Automatic (90 days) | Cloud KMS backup | KMS audit logs |
| User content keys | Supabase Vault | User (via auth), Platform (envelope) | 90 days (on request) | Account recovery flow | Vault audit logs |
| API keys | HashiCorp Vault | Security Engineering (JIT) | 90 days | Vault backup (encrypted) | Vault audit logs |
| JWT signing keys | Supabase Auth + Vault | Security Engineering (JIT) | 180 days | Auth system backup | Auth audit logs |
| Backup keys | HSM (air-gapped, Shamir 3 of 5) | SRE Lead + Security Lead (joint) | 180 days | Shamir's Secret Sharing | Physical custody log |
| TLS private keys | Cloudflare + Let's Encrypt | Platform Engineering (read-only) | 90 days | certbot regenerate | Certificate transparency logs |
| CI/CD secrets | GitHub Secrets + Vault | DevOps (JIT) | 90 days | Vault backup | GitHub audit logs |

### 9.7 Security Monitoring

| Monitoring Layer | Tool | Coverage | Alert Threshold | Owner |
|------------------|------|----------|----------------|-------|
| WAF | Cloudflare WAF | All HTTP traffic | Block rate > 1% of traffic | Security Engineering |
| DDoS | Cloudflare DDoS Protection | L3/L4/L7 | Attack detected | Security Engineering |
| Bot Detection | Cloudflare Bot Management | All HTTP traffic | Bot score < 30 for > 5% of traffic | Security Engineering |
| Auth Anomalies | Sentry + Custom | Login patterns | Failed login rate > 10% for user | Security Engineering |
| Rate Limit Abuse | Cloudflare + Redis | Per-IP, per-user | Rate limit hits > 1,000/min | Security Engineering |
| Data Exfiltration | Custom (query logs) | Database queries | Bulk SELECT > 10,000 rows by non-system | Security Engineering |
| Secret Leakage | GitHub Secret Scanning | Repository commits | Secret detected in commit | Security Engineering |
| Runtime Protection | Sentry + Cloudflare | Application runtime | Suspicious process, unexpected outbound | Security Engineering |
| Vulnerability Scan | Snyk + Trivy + Dependabot | Dependencies, containers | Critical or High CVE | Security Engineering |
| Penetration Testing | External vendor | Full platform | Annual assessment | Security Engineering |

### 9.8 Threat Detection

| Threat Category | Detection Method | Alert | Response | Owner |
|-----------------|-----------------|-------|----------|-------|
| Brute force login | Failed login rate per IP/user | P1 if > 10 failures/min | Block IP, require CAPTCHA, notify user | Security Engineering |
| Credential stuffing | Cross-reference with breach databases | P1 if known breached password used | Force password reset, notify user | Security Engineering |
| Session hijacking | Geo-velocity anomaly, device fingerprint change | P2 if impossible travel detected | Invalidate session, force re-auth | Security Engineering |
| API key abuse | Usage pattern deviation, off-hours access | P2 if > 10x normal usage | Revoke key, notify owner, investigate | Security Engineering |
| Data exfiltration | Bulk query detection, unusual export patterns | P1 if > 10,000 rows selected by non-system | Block query, investigate, notify compliance | Security Engineering |
| Insider threat | Access pattern anomaly, off-hours admin access | P2 if admin access outside business hours | JIT access review, audit log analysis | Security Engineering |
| Supply chain attack | Dependency hash mismatch, unexpected package update | P0 if critical dependency compromised | Isolate, rollback, forensic analysis | Security Engineering |
| AI prompt injection | Input validation failure, unexpected output patterns | P2 if injection pattern detected | Block input, log for analysis, update filters | AI Infrastructure |
| Model extraction | High-volume embedding queries, systematic probing | P2 if probing pattern detected | Rate limit, block, investigate | AI Infrastructure |

### 9.9 Vulnerability Management

| Scan Type | Tool | Frequency | Scope | SLA | Owner |
|-----------|------|-----------|-------|-----|-------|
| Dependency scanning | Dependabot + Snyk | Daily (Dependabot), Weekly (Snyk) | All npm, pip, cargo dependencies | Critical: 24h, High: 7d | Security Engineering |
| Container scanning | Trivy | Weekly | All Docker images | Critical: 24h, High: 7d | Security Engineering |
| Static analysis | Semgrep + Bandit | Every PR | Source code | Critical: 24h, High: 7d | Security Engineering |
| Dynamic analysis | OWASP ZAP | Weekly | Staging environment | Critical: 24h, High: 7d | Security Engineering |
| Secrets scanning | GitHub Secret Scanning + TruffleHog | Every commit | Git repository | Immediate (revoke + rotate) | Security Engineering |
| Infrastructure scanning | Terraform Compliance (tfsec) | Every IaC change | Terraform configurations | Critical: 24h, High: 7d | Security Engineering |
| Penetration testing | External vendor | Annually | Full production platform | All findings: 30d | Security Engineering |

**Patch SLA:**

| Severity (CVSS) | SLA | Approval Required | Communication |
|-----------------|-----|-------------------|---------------|
| Critical (9.0–10.0) | 24 hours | Engineering Lead + SRE Lead | Emergency release, customer notification if applicable |
| High (7.0–8.9) | 7 days | Team Lead | Standard release, changelog note |
| Medium (4.0–6.9) | 30 days | Team Lead | Standard release, no external communication |
| Low (< 4.0) | 90 days | Team Lead | Next scheduled release |

### 9.10 Runtime Protection

| Protection Layer | Implementation | Coverage | Owner |
|------------------|---------------|----------|-------|
| WAF Rules | Cloudflare WAF (OWASP CRS, custom rules) | All HTTP traffic | Security Engineering |
| Rate Limiting | Token bucket (Redis) per user, per IP, per endpoint | All API endpoints | Platform Engineering |
| Input Validation | JSON Schema (AJV) + runtime validators | All API inputs | Backend Engineering |
| SQL Injection Prevention | Parameterized queries (pg-promise) | All database queries | Database Engineering |
| XSS Prevention | Content Security Policy (CSP), textContent only | All frontend rendering | Frontend Engineering |
| CSRF Protection | Double-submit cookie pattern | All state-changing requests | Security Engineering |
| Clickjacking Protection | X-Frame-Options: DENY, CSP frame-ancestors | All pages | Security Engineering |
| File Upload Security | Magic numbers, virus scan, size limits, extension whitelist | All upload endpoints | Security Engineering |
| AI Input Sanitization | Prompt injection detection, output filtering | All AI endpoints | AI Infrastructure |

### 9.11 Audit Logging

| Event Category | Events Logged | Retention | Immutability | Access |
|---------------|-------------|-----------|--------------|--------|
| Authentication | Login, logout, MFA success/failure, password reset, session create/destroy | 7 years | WORM | Security + Compliance |
| Authorization | Permission changes, role assignments, RLS policy changes | 7 years | WORM | Security + Compliance |
| Data Access | Document upload, view, delete, download, export, share | 7 years | WORM | Security + Compliance |
| AI Operations | Query, response, citation verification, model used, grounding score | 2 years | WORM | Security + AI Infra |
| Admin Actions | Secret rotation, user deletion, config changes, maintenance mode | 7 years | WORM | Security + Compliance |
| System Actions | Service restarts, scaling events, deployments, backups | 2 years | Append-only | SRE |
| Security Events | WAF blocks, rate limit hits, anomaly detections, breach attempts | 2 years | WORM | Security Engineering |
| Compliance | Data export, deletion request, retention enforcement, audit review | 7 years | WORM | Compliance Officer |

**Audit Log Schema (WORM Table):**

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL CHECK (event_type IN (
        'login', 'logout', 'mfa', 'password_reset',
        'document_upload', 'document_view', 'document_delete', 'document_download',
        'document_share', 'document_export', 'document_reprocess',
        'ai_query', 'ai_response', 'citation_verified', 'citation_failed',
        'admin_action', 'secret_rotation', 'rls_change', 'user_delete',
        'backup_complete', 'backup_fail', 'restore_complete',
        'security_event', 'compliance_export', 'data_deletion'
    )),
    actor_id UUID,                    -- user_id or service account ID
    actor_type TEXT NOT NULL CHECK (actor_type IN ('user', 'admin', 'system', 'service')),
    target_type TEXT NOT NULL,        -- document, user, policy, chunk, etc.
    target_id TEXT,                   -- specific ID of the target
    action TEXT NOT NULL CHECK (action IN ('create', 'read', 'update', 'delete', 'share', 'export', 'execute')),
    details JSONB,                    -- event-specific details
    ip_address INET,                  -- client IP
    user_agent TEXT,                  -- client user agent
    session_id TEXT,                  -- session identifier
    correlation_id TEXT,              -- trace correlation ID
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- WORM constraints
    CONSTRAINT no_update CHECK (false)  -- Prevents UPDATE
    -- No DELETE policy enforced at application level
);

-- Prevent UPDATE and DELETE via triggers
create or replace function prevent_audit_modification()
returns trigger as $$
begin
    raise exception 'Audit logs are immutable (WORM)';
end;
$$ language plpgsql;

create trigger audit_log_no_update
    before update or delete on audit_logs
    for each row execute function prevent_audit_modification();

-- Row-level security for audit log access
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "audit_log_admin_only" ON audit_logs
    FOR SELECT TO authenticated
    USING (auth.uid() IN (SELECT user_id FROM admin_users));
```

---

## 10. AI Operations (AIOps)

### 10.1 Embedding Model Upgrades

| Step | Action | Owner | Verification | Rollback |
|------|--------|-------|------------|----------|
| 1. Benchmark | Run new model against benchmark dataset (tests/data/benchmark.json) | AI Infrastructure | MRR@10 improvement > 5% | N/A |
| 2. Dual-Write | Deploy new model alongside old; write embeddings from both | AI Infrastructure | Both models produce valid embeddings | Disable new model |
| 3. Incremental Re-embed | Re-embed changed chunks only (not full KB) | AI Infrastructure | Chunk count matches | Restore old embeddings from backup |
| 4. Monitor | Track retrieval precision for 1 week | AI Infrastructure | Precision@5 stable or improved | Switch default back to old model |
| 5. Full Re-embed | Queue full re-embedding of old chunks (low priority, off-peak) | AI Infrastructure | All chunks have new model embeddings | Restore from backup |
| 6. Switch Default | Update config to use new model as default | AI Infrastructure | All new documents use new model | Config revert |
| 7. Decommission Old | After 30 days, remove old model from inference | AI Infrastructure | No references to old model | Re-deploy old model |

### 10.2 LLM Upgrades

| Step | Action | Owner | Verification | Rollback |
|------|--------|-------|------------|----------|
| 1. Test | Deploy new model on staging | AI Infrastructure | Model loads, responds to health check | Remove from staging |
| 2. AI Evaluation | Run full AI evaluation suite (tests/ai_eval/) | AI Infrastructure | MRR@10 > 0.6, Precision@5 > 0.7, hallucination = 0 | N/A |
| 3. Canary | Deploy to production canary (5% of traffic) | AI Infrastructure | No error rate increase, latency within SLO | Disable canary |
| 4. Monitor | 3-day monitoring of grounding score, citation accuracy, latency | AI Infrastructure | All metrics stable | Disable canary |
| 5. Gradual Rollout | 25% → 50% → 100% over 7 days | AI Infrastructure | No degradation at each stage | Revert percentage |
| 6. Full Default | Update default model config | AI Infrastructure | All new requests use new model | Config revert |
| 7. Deprecate Old | After 30 days, remove old model | AI Infrastructure | No remaining references | Re-install old model |

### 10.3 Prompt Versioning

| Aspect | Specification |
|--------|-------------|
| **Storage** | All prompts in `backend/prompts/` directory, versioned with Git |
| **Naming** | `prompts/{purpose}/v{major}.{minor}.txt` (e.g., `prompts/grounding/v1.0.txt`) |
| **Change Requirements** | AI evaluation suite pass + human review (for grounding-critical prompts) + A/B test if user-facing |
| **Rollback** | `git checkout prompts/{purpose}/v{previous}.txt` + config update + reload |
| **Audit** | Every prompt change logged in ai_prompts table (version, hash, author, timestamp) |
| **Environments** | Staging uses latest; production uses pinned version; canary uses candidate |
| **Hotfix** | Emergency prompt changes require AI Infra Lead approval; bypass evaluation only for SEV-0/SEV-1 |

### 10.4 Retrieval Evaluation

| Metric | Target | Frequency | Method | Owner |
|--------|--------|-----------|--------|-------|
| MRR@10 | > 0.6 | Weekly | Benchmark dataset (tests/data/benchmark.json) | AI Infrastructure |
| Precision@5 | > 0.8 | Weekly | Manual evaluation of 50 queries | AI Infrastructure |
| Recall@10 | > 0.5 | Weekly | Benchmark dataset | AI Infrastructure |
| NDCG@10 | > 0.7 | Monthly | Benchmark dataset | AI Infrastructure |
| Latency (p95) | < 200ms | Daily | APM | AI Infrastructure |
| Cache hit rate | > 80% | Daily | Redis metrics | AI Infrastructure |

### 10.5 Grounding Evaluation

| Metric | Target | Frequency | Method | Owner |
|--------|--------|-----------|--------|-------|
| Citation verification accuracy | 100% | Per response | Automated verification | AI Infrastructure |
| Grounding score | 100% | Per response | Automated claim→chunk verification | AI Infrastructure |
| Hallucination rate | 0% | Weekly | AI evaluation suite + manual review | AI Infrastructure |
| "I don't know" rate | < 5% | Weekly | Log analysis | AI Infrastructure |
| Evidence trace completeness | 100% | Per response | Automated check | AI Infrastructure |

### 10.6 Prompt Rollback

```bash
#!/bin/bash
# Prompt Rollback Procedure
# USE CASE: Prompt causing hallucination, citation failure, or user complaints
# AUTHORIZATION: AI Infrastructure Lead or SRE Lead

set -euo pipefail

PURPOSE="${1:-}"
TARGET_VERSION="${2:-}"

if [[ -z "$PURPOSE" || -z "$TARGET_VERSION" ]]; then
    echo "Usage: $0 <purpose> <target_version>"
    echo "Example: $0 grounding v1.0"
    exit 1
fi

echo "=== Rolling back prompt: $PURPOSE → $TARGET_VERSION ==="

# Step 1: Verify target version exists
if [[ ! -f "backend/prompts/${PURPOSE}/v${TARGET_VERSION}.txt" ]]; then
    echo "ERROR: Prompt version not found"
    exit 1
fi

# Step 2: Update symlink or config
ln -sf "backend/prompts/${PURPOSE}/v${TARGET_VERSION}.txt" "backend/prompts/${PURPOSE}/current.txt"

# Step 3: Reload (if hot-reload supported) or restart
if [[ "$PURPOSE" == "grounding" ]]; then
    # Grounding prompts require service restart for safety
    supabase functions deploy --project-ref "$SUPABASE_PROD_REF" --no-verify-jwt
else
    # Non-critical prompts may support hot-reload
    curl -X POST "https://adaptive-study-planner.com/api/v3/admin/reload-prompts" \
        -H "Authorization: Bearer $ADMIN_TOKEN"
fi

# Step 4: Verify
sleep 10
TEST_RESULT=$(curl -s -X POST "https://adaptive-study-planner.com/api/v3/ask" \
    -H "Authorization: Bearer $TEST_TOKEN" \
    -d '{"question": "What is the ideal gas law?"}' | jq '.citations | length')

if [[ "$TEST_RESULT" -gt 0 ]]; then
    echo "Rollback verified: citations present ($TEST_RESULT)"
else
    echo "WARNING: Rollback verification failed. Check prompt file."
fi

# Step 5: Log
psql -c "INSERT INTO ai_prompts (purpose, version, action, actor, timestamp) VALUES ('$PURPOSE', '$TARGET_VERSION', 'rollback', '$(whoami)', NOW());"

echo "=== Rollback Complete ==="
```

### 10.7 Knowledge Base Refresh

| Refresh Type | Trigger | Scope | Duration | Owner | Impact |
|-------------|---------|-------|----------|-------|--------|
| Incremental | Daily cron (02:00 UTC) | Changed documents only | 1–2 hours | AI Infrastructure | Minimal (background) |
| Full | Quarterly, or on major model upgrade | All documents | 6–12 hours | AI Infrastructure | Elevated queue depth |
| On-Demand | User request (reprocess button) | Single document | 5–10 min | AI Infrastructure | Per-document |
| Emergency | SEV-2/SEV-1 resolution | Affected documents | Variable | AI Infrastructure | Per-document |

**Monitoring:**
- Track "freshness" metric (average age of embeddings)
- Alert if avg freshness > 30 days
- Alert if incremental refresh fails 2 consecutive days

### 10.8 Incremental Indexing

| Action | Trigger | Method | Owner | Validation |
|--------|---------|--------|-------|------------|
| Embedding incremental | Document updated/changed | Only re-embed changed chunks | AI Infrastructure | SHA-256 comparison before/after |
| Full-text incremental | Document updated/changed | Update tsvector for changed chunks | Database Engineering | Search query returns updated content |
| Metadata incremental | Document updated | Update document record | Platform Engineering | Document metadata reflects changes |
| Graph incremental | Concepts/prerequisites changed | Update affected edges | Database Engineering | Cycle detection, edge count verification |
| Vector index update | New embeddings added | No action (index auto-updates) | Database Engineering | Query performance stable |

### 10.9 Model Drift Detection

| Metric | Threshold | Detection Method | Action | Owner |
|--------|-----------|-----------------|--------|-------|
| Retrieval precision@5 drop | > 5% from baseline | Weekly benchmark | Alert AI Infra, investigate model/embeddings | AI Infrastructure |
| Hallucination rate | > 0% | Per-response verification + weekly evaluation | P0 alert, halt AI responses, manual review | AI Infrastructure |
| Citation accuracy | < 100% | Per-response verification | P1 alert, investigate prompt/pipeline | AI Infrastructure |
| Grounding score | < 95% | Per-response verification | P1 alert, investigate retrieval quality | AI Infrastructure |
| Embedding similarity drift | > 0.1 cosine shift | Daily sample of 1,000 embeddings | Alert AI Infra, re-evaluate model | AI Infrastructure |
| AI response latency spike | > 2x baseline p95 | APM | P1 alert, investigate inference capacity | AI Infrastructure |
| User complaint rate (AI) | > 1% of AI interactions | Support tickets | P2 alert, review AI quality | AI Infrastructure |

### 10.10 Hallucination Monitoring

| Layer | Detection | Response | Logging | Owner |
|-------|-----------|----------|---------|-------|
| Per-response | Citation verification (automated) | Flag unverified citations | ai_queries table | AI Infrastructure |
| Batch | Weekly AI evaluation suite (50 test queries) | Alert if hallucination > 0% | Evaluation report | AI Infrastructure |
| User feedback | "Report incorrect answer" button | Manual review, prompt update | Support ticket + AI log | AI Infrastructure |
| Automated | Grounding score < 95% | Reject response, return "I don't know" | ai_queries table | AI Infrastructure |
| Model level | Model drift detection | Trigger model re-evaluation | Model drift report | AI Infrastructure |

### 10.11 Latency Monitoring

| Operation | p50 Target | p95 Target | p99 Target | Alert Threshold | Owner |
|-----------|-----------|-----------|-----------|----------------|-------|
| API request | 50ms | 150ms | 300ms | p95 > 500ms | SRE |
| Document upload | 2s | 5s | 10s | p95 > 15s | AI Infrastructure |
| OCR (per page) | 1s | 2s | 5s | p95 > 5s | AI Infrastructure |
| Embedding (per batch) | 0.5s | 1s | 2s | p95 > 2s | AI Infrastructure |
| Retrieval (hybrid) | 50ms | 150ms | 300ms | p95 > 200ms | AI Infrastructure |
| AI response | 0.5s | 1.5s | 3s | p95 > 2s | AI Infrastructure |
| Total Q&A | 1s | 2s | 4s | p95 > 5s | AI Infrastructure |
| Graph query (≤3 hops) | 30ms | 100ms | 200ms | p95 > 150ms | Database Engineering |
| Study plan generation | 2s | 5s | 10s | p95 > 15s | AI Infrastructure |
| Export (JSON) | 1s | 3s | 5s | p95 > 10s | Platform Engineering |
| Export (Anki) | 2s | 5s | 10s | p95 > 15s | Platform Engineering |

### 10.12 Cost Monitoring

| Service | Cost Driver | Monthly Budget | Alert at | Owner | Optimization |
|---------|------------|---------------|----------|-------|------------|
| OpenAI API | Tokens / requests | $500 | 80% ($400) | AI Infrastructure | Use local models first; batch requests |
| Google Vision | Pages processed | $200 | 80% ($160) | AI Infrastructure | Use Tesseract for printed; reserve Vision for handwriting |
| MathPix | Formulas processed | $100 | 80% ($80) | AI Infrastructure | Use Tesseract formula mode for simple formulas |
| Supabase | DB + storage + egress | $300 | 80% ($240) | Platform Engineering | Read replicas, connection pooling, query optimization |
| Cloudflare Workers | Requests | $100 | 80% ($80) | Platform Engineering | Cache optimization, batch API calls |
| R2 | Storage + egress | $50 | 80% ($40) | Platform Engineering | Lifecycle policies, compression, thumbnail optimization |
| Upstash Redis | Memory + ops | $100 | 80% ($80) | Platform Engineering | Cache TTL tuning, eviction policy |
| vLLM GPU | GPU hours | $1,000 | 80% ($800) | AI Infrastructure | Auto-shutdown during off-peak, batch inference |
| Monitoring (Sentry) | Events | $50 | 80% ($40) | SRE | Sampling rate tuning, error filtering |
| PagerDuty | Users | $100 | 80% ($80) | SRE | On-call rotation optimization |
| **Total** | — | **$2,500** | — | — | — |

---

## 11. Capacity Planning

### 11.1 Current Capacity Baseline (June 2026)

| Resource | Current | Capacity | Headroom | Utilization |
|----------|---------|----------|----------|-------------|
| Monthly Active Users | 1,000 | 10,000 | 9,000 | 10% |
| Daily Active Users | 300 | 3,000 | 2,700 | 10% |
| Documents / hour | 100 | 1,000 | 900 | 10% |
| Chunks / tenant | 100,000 | 10,000,000 | 9,900,000 | 1% |
| Vector index size (pgvector) | 100 MB | 10 GB | 9.9 GB | 1% |
| Knowledge graph edges | 10,000 | 1,000,000 | 990,000 | 1% |
| R2 storage | 50 GB | 10 TB | 9.95 TB | 0.5% |
| Redis memory | 1 GB | 10 GB | 9 GB | 10% |
| GPU utilization (vLLM) | 20% | 80% | 60% | 25% |
| Database connections | 20 | 200 | 180 | 10% |
| API RPS (peak) | 50 | 5,000 | 4,950 | 1% |
| AI inference requests / hour | 500 | 5,000 | 4,500 | 10% |

### 11.2 Scaling Triggers

| Metric | Warning Threshold | Critical Threshold | Scale Action | Max Scale | Owner |
|--------|------------------|-------------------|--------------|-----------|-------|
| Active users | > 7,000 (70%) | > 9,000 (90%) | Add read replica, review worker concurrency | 10,000 | Platform Engineering |
| Documents / hour | > 700 (70%) | > 900 (90%) | Increase Edge Function concurrency, add OCR workers | 1,000 | AI Infrastructure |
| Chunks / tenant | > 7M (70%) | > 9M (90%) | Migrate to HNSW index (from IVFFlat), evaluate partitioning | 10M | Database Engineering |
| Vector index size | > 7 GB (70%) | > 9 GB (90%) | Evaluate pgvector partitioning, consider dedicated vector DB | 10 GB | Database Engineering |
| Graph edges | > 700K (70%) | > 900K (90%) | Evaluate ArangoDB migration, optimize CTE queries | 1M | Database Engineering |
| R2 storage | > 7 TB (70%) | > 9 TB (90%) | Enable lifecycle policies, review compression, evaluate S3 Glacier | 10 TB | Platform Engineering |
| Redis memory | > 7 GB (70%) | > 9 GB (90%) | Upgrade Upstash plan, review cache TTL, add eviction | 10 GB | Platform Engineering |
| GPU utilization | > 60% (75%) | > 80% (100%) | Add GPU node (Kubernetes HPA) | 10 nodes | AI Infrastructure |
| Database connections | > 140 (70%) | > 180 (90%) | Add PgBouncer instance, review connection pooling | 200 | Database Engineering |
| API RPS | > 3,500 (70%) | > 4,500 (90%) | No action (serverless auto-scales) | Unlimited | Platform Engineering |
| AI inference queue wait | > 15s (warning) | > 30s (critical) | Add GPU node, enable OpenAI fallback | 10 nodes | AI Infrastructure |

### 11.3 Growth Projections

| Quarter | Users | Documents | Chunks | Vector Index | Graph Edges | Storage | Action Required |
|---------|-------|-----------|--------|------------|-------------|---------|-----------------|
| Q3 2026 | 5,000 | 50K | 5M | 5 GB | 500K | 500 GB | Add read replica, increase GPU to 2 nodes |
| Q4 2026 | 10,000 | 100K | 10M | 10 GB | 1M | 1 TB | Migrate to HNSW index, evaluate ArangoDB |
| Q1 2027 | 25,000 | 250K | 25M | 25 GB | 2.5M | 2.5 TB | Add GPU cluster (3+ nodes), dedicated PgBouncer |
| Q2 2027 | 50,000 | 500K | 50M | 50 GB | 5M | 5 TB | Evaluate ArangoDB migration, sharding |
| Q3 2027 | 100,000 | 1M | 100M | 100 GB | 10M | 10 TB | Multi-region deployment, dedicated vector DB |

### 11.4 Scaling Policies

| Resource | Scaling Policy | Implementation | Owner |
|----------|---------------|----------------|-------|
| Cloudflare Workers | Automatic (serverless) | N/A — Cloudflare handles | Platform Engineering |
| Supabase Edge Functions | Automatic (serverless) | N/A — Supabase handles | AI Infrastructure |
| vLLM GPU | Kubernetes HPA (CPU/GPU threshold) | `kubectl autoscale deployment vllm --min=1 --max=10 --cpu-percent=80` | AI Infrastructure |
| PostgreSQL | Manual (read replicas) | Terraform `supabase_project` + `read_replica` resource | Database Engineering |
| PgBouncer | Manual (instance count) | Terraform `aws_instance` or Docker Swarm | Database Engineering |
| Redis | Manual (plan upgrade) | Upstash console or Terraform | Platform Engineering |
| R2 | Automatic (unlimited) | N/A — Cloudflare handles | Platform Engineering |
| Monitoring | Manual (plan upgrade) | Grafana Cloud + Sentry plan upgrade | SRE |

---

## 12. Performance Operations

### 12.1 Latency Budgets

| Operation | p50 Budget | p95 Budget | p99 Budget | Hard Limit | Owner |
|-----------|-----------|-----------|-----------|------------|-------|
| API request (simple) | 50ms | 150ms | 300ms | 500ms | Backend Engineering |
| API request (complex) | 100ms | 300ms | 600ms | 1,000ms | Backend Engineering |
| Document upload (small < 10MB) | 1s | 3s | 5s | 10s | Platform Engineering |
| Document upload (large > 50MB) | 3s | 10s | 15s | 30s | Platform Engineering |
| OCR (per page, printed) | 0.5s | 1s | 2s | 5s | AI Infrastructure |
| OCR (per page, handwritten) | 1s | 2s | 5s | 10s | AI Infrastructure |
| Embedding (per batch of 32) | 0.5s | 1s | 2s | 3s | AI Infrastructure |
| Retrieval (hybrid, no cache) | 50ms | 150ms | 300ms | 500ms | AI Infrastructure |
| Retrieval (cache hit) | 5ms | 20ms | 50ms | 100ms | AI Infrastructure |
| AI response (vLLM) | 0.5s | 1s | 2s | 3s | AI Infrastructure |
| AI response (OpenAI fallback) | 1s | 2s | 3s | 5s | AI Infrastructure |
| Total Q&A (end-to-end) | 1s | 2s | 4s | 5s | AI Infrastructure |
| Graph query (≤3 hops) | 20ms | 100ms | 200ms | 300ms | Database Engineering |
| Study plan generation | 1s | 3s | 5s | 10s | AI Infrastructure |
| Export (JSON) | 0.5s | 2s | 3s | 5s | Platform Engineering |
| Export (Anki deck) | 1s | 3s | 5s | 10s | Platform Engineering |
| Page load (frontend) | 0.5s | 1s | 2s | 3s | Frontend Engineering |
| Search results (frontend) | 0.2s | 0.5s | 1s | 2s | Frontend Engineering |

### 12.2 Token Budgets (AI Inference)

| Operation | Input Tokens (avg) | Output Tokens (avg) | Total Budget | Cost Impact | Owner |
|-----------|-------------------|--------------------|-------------|-------------|-------|
| Simple Q&A | 2,000 | 500 | 3,000 | Low | AI Infrastructure |
| Complex Q&A (multi-source) | 5,000 | 1,000 | 6,000 | Medium | AI Infrastructure |
| Concept extraction | 3,000 | 1,000 | 4,000 | Medium | AI Infrastructure |
| Formula extraction | 2,000 | 500 | 2,500 | Low | AI Infrastructure |
| Question extraction | 4,000 | 2,000 | 6,000 | Medium | AI Infrastructure |
| Prerequisite detection | 2,000 | 500 | 2,500 | Low | AI Infrastructure |
| Flashcard generation | 3,000 | 2,000 | 5,000 | Medium | AI Infrastructure |
| Quiz generation | 5,000 | 3,000 | 8,000 | High | AI Infrastructure |
| Study plan generation | 4,000 | 2,000 | 6,000 | Medium | AI Infrastructure |
| Summary generation | 5,000 | 1,000 | 6,000 | Medium | AI Infrastructure |
| Knowledge graph construction | 3,000 | 1,000 | 4,000 | Medium | AI Infrastructure |
| Citation verification | 2,000 | 500 | 2,500 | Low | AI Infrastructure |
| **Max per request** | — | — | **10,000** | — | AI Infrastructure |

### 12.3 Caching Strategy

| Cache | Technology | Key Format | TTL | Size | Hit Rate Target | Owner |
|-------|------------|-----------|-----|------|----------------|-------|
| Query results | Redis | `query:{sha256(question+filters)}` | 1 hour | 1 GB | 80% | AI Infrastructure |
| Embeddings | Redis | `emb:{sha256(chunk_text)}` | 24 hours | 5 GB | 90% | AI Infrastructure |
| Document metadata | Redis | `doc:{user_id}:{doc_id}` | 1 hour | 500 MB | 95% | Platform Engineering |
| AI responses | Redis | `ai:{sha256(question+context)}` | 30 minutes | 2 GB | 70% | AI Infrastructure |
| Static assets | Cloudflare CDN | URL path | 30 days | Unlimited | 99% | Frontend Engineering |
| API responses | Cloudflare Workers Cache | `api:{path}:{params}` | 5 minutes | 500 MB | 85% | Platform Engineering |
| Session data | Redis | `session:{jwt_id}` | 1 hour | 200 MB | 95% | Security Engineering |
| Rate limit counters | Redis | `ratelimit:{user_id}:{endpoint}` | 1 minute | 100 MB | N/A | Platform Engineering |
| Search results (frontend) | Browser Cache | `search:{query}` | 5 minutes | 50 MB | 80% | Frontend Engineering |
| Graph data (frontend) | Browser Cache | `graph:{user_id}:{subject}` | 10 minutes | 100 MB | 90% | Frontend Engineering |

### 12.4 Queue Management

| Queue | Max Depth | Alert Threshold | Action on Backlog | Owner |
|-------|-----------|---------------|-------------------|-------|
| Document Processing | 1,000 | 500 | Add Edge Function workers, notify AI Infra | AI Infrastructure |
| OCR | 500 | 250 | Add OCR workers, enable Google Vision fallback | AI Infrastructure |
| Embedding | 500 | 250 | Add embedding workers, increase batch size | AI Infrastructure |
| Retrieval | 10,000 | 5,000 | Increase cache TTL, review query patterns | AI Infrastructure |
| AI Inference | 500 | 250 | Add GPU node, enable OpenAI fallback | AI Infrastructure |
| Export | 100 | 50 | Add export workers, notify users of delay | Platform Engineering |
| Dead Letter | 500 | 250 | Manual review, create tickets for each item | SRE |

### 12.5 Concurrency Management

| Resource | Max Concurrent | Per-User Limit | Throttling | Owner |
|----------|---------------|----------------|------------|-------|
| API requests (free tier) | 100/min | 100/min | Token bucket, 429 response | Platform Engineering |
| API requests (pro tier) | 1,000/min | 1,000/min | Token bucket, 429 response | Platform Engineering |
| API requests (enterprise) | 10,000/min | 10,000/min | Token bucket, 429 response | Platform Engineering |
| Document uploads | 10 concurrent | 3 concurrent | Queue, 429 if full | Platform Engineering |
| AI Q&A (free tier) | 10/min | 10/min | Token bucket, 429 response | AI Infrastructure |
| AI Q&A (pro tier) | 100/min | 100/min | Token bucket, 429 response | AI Infrastructure |
| AI Q&A (enterprise) | 1,000/min | 1,000/min | Token bucket, 429 response | AI Infrastructure |
| Search (free tier) | 50/min | 50/min | Token bucket, 429 response | AI Infrastructure |
| Search (pro tier) | 500/min | 500/min | Token bucket, 429 response | AI Infrastructure |
| Search (enterprise) | 2,000/min | 2,000/min | Token bucket, 429 response | AI Infrastructure |
| Graph queries | 100/min | 50/min | Token bucket, 429 response | Database Engineering |
| Study plan generation | 10/min | 5/min | Token bucket, 429 response | AI Infrastructure |
| Export | 5/min | 2/min | Token bucket, 429 response | Platform Engineering |
| Database connections | 200 | 20 per user | Connection pool (PgBouncer) | Database Engineering |
| GPU inference slots | 50 | 5 per user | Queue, 503 if full | AI Infrastructure |

### 12.6 Rate Limiting

| Tier | Requests/Min | AI Q&A/Min | Search/Min | Uploads/Min | Burst Allowance |
|------|-------------|-----------|-----------|-------------|-----------------|
| Free | 100 | 10 | 50 | 3 | 20% above limit for 10s |
| Pro | 1,000 | 100 | 500 | 10 | 20% above limit for 10s |
| Enterprise | 10,000 | 1,000 | 2,000 | 50 | 50% above limit for 30s |
| Internal (system) | Unlimited | Unlimited | Unlimited | Unlimited | N/A |

**Rate Limit Response:**

```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "limit": 100,
  "remaining": 0,
  "reset_at": "2026-06-28T10:01:00Z"
}
```

### 12.7 Autoscaling

| Service | Metric | Scale Up Trigger | Scale Down Trigger | Min | Max | Cooldown |
|---------|--------|----------------|-------------------|-----|-----|----------|
| Cloudflare Workers | RPS | +50% capacity | -25% capacity | 1 | Unlimited | 1 min |
| vLLM GPU | GPU utilization | +1 node at > 80% | -1 node at < 30% | 1 | 10 | 5 min |
| PostgreSQL read replicas | Connection count | +1 replica at > 100 | -1 replica at < 50 | 1 | 5 | 10 min |
| PgBouncer | Pool utilization | +1 instance at > 80% | -1 instance at < 30% | 1 | 3 | 5 min |
| Redis | Memory usage | Upgrade plan at > 80% | Downgrade plan at < 40% | 1 GB | 10 GB | 1 hour |
| Monitoring | Event volume | Upgrade plan at > 80% | Downgrade plan at < 40% | Free | Enterprise | 1 hour |

---

## 13. Support Operations

### 13.1 Support Tiers

| Tier | Scope | Response Time | Resolution Target | Escalation | Channels |
|------|-------|--------------|-------------------|------------|----------|
| L1 — Self-Service | FAQ, documentation, troubleshooting guides | Immediate | N/A | Escalate to L2 if unresolved in 15 min | Help center, in-app chatbot, community forum |
| L2 — Support Engineering | User issues, password resets, basic troubleshooting, account questions | 15 minutes | 4 hours | Escalate to L3 if technical issue | Email, in-app ticket, live chat |
| L3 — Platform Engineering | API issues, performance degradation, deployment failures, non-critical infrastructure | 1 hour | 24 hours | Escalate to L4 if architectural or security | Slack #support-escalation, Jira |
| L4 — SRE / AI Infrastructure | Infrastructure outages, AI pipeline failures, data corruption, security incidents | 15 minutes | 4 hours | Escalate to L5 if complete outage or breach | PagerDuty, Slack #incidents, war room |
| L5 — Engineering Leadership | Architectural decisions, major outages, vendor escalations, budget approvals | 4 hours | 48 hours | CTO for SEV-0 or regulatory | Email, phone, executive escalation |

### 13.2 Runbook Ownership

| Runbook Category | Owner | Review Frequency | Location |
|-----------------|-------|-----------------|----------|
| Deployment runbooks | DevOps | Monthly | `docs/runbooks/deployment-*` |
| Database runbooks | Database Engineering | Monthly | `docs/runbooks/db-*` |
| AI pipeline runbooks | AI Infrastructure | Monthly | `docs/runbooks/ai-*` |
| Security runbooks | Security Engineering | Monthly | `docs/runbooks/security-*` |
| DR runbooks | SRE | Quarterly | `docs/runbooks/dr-*` |
| Incident response | SRE | Quarterly | `docs/runbooks/incident-*` |
| On-call procedures | SRE | Monthly | `docs/runbooks/oncall-*` |
| Maintenance procedures | Platform Engineering | Monthly | `docs/runbooks/maintenance-*` |

### 13.3 On-Call Rotations

| Team | Primary | Secondary | Schedule | Handoff Time | Coverage |
|------|---------|-----------|----------|--------------|----------|
| SRE | 1 engineer | 1 engineer | 1 week | Monday 09:00 UTC | 24/7 |
| AI Infrastructure | 1 engineer | 1 engineer | 1 week | Monday 09:00 UTC | 24/7 |
| Platform Engineering | 1 engineer | On-demand (pager if primary unavailable) | 1 week | Monday 09:00 UTC | 24/7 |
| Database Engineering | 1 engineer | On-demand (pager if primary unavailable) | 1 week | Monday 09:00 UTC | 24/7 (DBA for SEV-0/SEV-1 only) |
| Security Engineering | 1 engineer | CISO (escalation) | 1 week | Monday 09:00 UTC | 24/7 (security incidents only) |
| Frontend Engineering | On-demand (no 24/7) | Team Lead | Business hours | N/A | Business hours |

**On-Call Handoff Procedure:**

1. Outgoing engineer writes handoff note in `#oncall-handoff` (Slack)
2. Handoff note includes: active incidents, known issues, pending deployments, alert trends
3. Incoming engineer reviews handoff note and acknowledges
4. Both engineers verify PagerDuty rotation is correct
5. Weekly on-call review meeting (15 min, Tuesdays 10:00 UTC)

### 13.4 Escalation Matrix

```
L1 Support (15 min response)
  |
  +---> L2 Platform Engineering (1 hour response)
          |
          +---> L3 SRE / AI Infrastructure (15 min response)
                  |
                  +---> L4 Engineering Lead (4 hours response)
                          |
                          +---> L5 CTO (on-demand, SEV-0 only)
                                  |
                                  +---> Board / Legal (regulatory breach)
```

**Escalation Rules:**

- If L1 does not respond in 15 minutes, auto-escalate to L2
- If L2 does not respond in 1 hour, auto-escalate to L3
- If L3 does not respond in 15 minutes, auto-escalate to L4
- If L4 does not respond in 1 hour, auto-escalate to L5 (CTO)
- SEV-0 incidents bypass all levels and page all on-call simultaneously

### 13.5 Maintenance Windows

| Type | Frequency | Duration | Notification Lead Time | Owner | Communication |
|------|-----------|----------|------------------------|-------|---------------|
| Scheduled maintenance | Monthly (first Sunday, 02:00–03:00 UTC) | 1 hour | 48 hours | SRE | Status page, in-app banner, email to active users |
| Database maintenance | Quarterly (last Sunday, 02:00–04:00 UTC) | 2 hours | 1 week | DBA Lead | Status page, in-app banner, email to all users |
| Security patching | As needed (Critical: immediate; High: within 7 days) | 30 minutes | 24 hours (if scheduled) | Security Engineering | Status page, in-app banner |
| Emergency maintenance | As needed | Variable | Immediate (no advance notice) | SRE Lead | Status page, in-app banner, Slack #sre-alerts |
| AI model update | Monthly (third Sunday, 03:00–04:00 UTC) | 1 hour | 48 hours | AI Infrastructure | Status page, in-app banner |
| Feature flag changes | Daily (business hours only) | Instant | No notice needed | Platform Engineering | None (transparent) |

### 13.6 Known Issues

| Issue | Severity | Workaround | ETA Fix | Tracking | Impact |
|-------|----------|------------|---------|----------|--------|
| Tesseract Hindi accuracy < 70% | SEV-3 | Use Google Vision (pro tier) for Hindi documents | Q3 2026 | #BUG-142 | Hindi documents only |
| Graph traversal > 3 hops slow | SEV-3 | Limit to 3 hops in UI; evaluate ArangoDB in Q4 | Q4 2026 | #BUG-143 | Large knowledge graphs only |
| MathPix API intermittent 429s | SEV-3 | Retry + exponential backoff; skip formula extraction if fails | Q2 2026 | #BUG-144 | Formula-heavy documents |
| Large ZIP uploads timeout | SEV-3 | Chunked upload (5MB segments); resume support | Q2 2026 | #BUG-145 | ZIP files > 50MB |
| Handwritten Arabic OCR < 60% | SEV-3 | Use Google Vision (pro tier) for Arabic handwriting | Q3 2026 | #BUG-146 | Arabic handwritten documents |
| Knowledge graph cycles (rare) | SEV-3 | Manual review via admin UI; cycle detection alerts | Q2 2026 | #BUG-147 | < 1% of users |
| Mobile PWA offline sync delay | SEV-3 | Manual sync button; background sync enabled | Q2 2026 | #BUG-148 | Mobile users |
| Enterprise SSO SAML logout issue | SEV-3 | Manual logout from IdP; fix in progress | Q2 2026 | #BUG-149 | Enterprise users only |

### 13.7 Troubleshooting Guides

| Symptom | Likely Cause | Quick Check | Resolution | Runbook |
|---------|-------------|------------|------------|---------|
| API returns 500 | Worker error, database issue | `wrangler tail` | Check logs, restart Workers, verify DB | `runbooks/api-500.md` |
| Upload stuck at "processing" | Pipeline failure, queue backlog | Check queue depth, document status | Retry document, clear queue if corrupted | `runbooks/upload-stuck.md` |
| AI answer has no citations | Retrieval failure, grounding issue | Check retrieval results, citation service | Verify index, re-embed if needed | `runbooks/no-citations.md` |
| Search returns empty | Embedding corruption, index issue | Check pgvector index validity | Reindex vectors, verify embeddings | `runbooks/search-empty.md` |
| Slow AI response | GPU saturation, queue backlog | Check GPU util, queue depth | Scale GPU, enable fallback | `runbooks/slow-ai.md` |
| User can't log in | Auth service issue, RLS bug | Check Supabase Auth status, user record | Verify auth config, check RLS policies | `runbooks/login-failure.md` |
| Document not in KB | Processing failed, duplicate detected | Check document status, duplicate hash | Reprocess, check duplicate logic | `runbooks/doc-missing.md` |
| High error rate | Deployment issue, config error | Check recent deployments, feature flags | Rollback deployment, disable flag | `runbooks/high-errors.md` |
| R2 access denied | CORS issue, presigned URL expiry | Check CORS config, URL expiry | Regenerate presigned URL, fix CORS | `runbooks/r2-denied.md` |
| Cache miss spike | Cache eviction, Redis issue | Check Redis memory, eviction rate | Review TTL, increase Redis plan | `runbooks/cache-miss.md` |

### 13.8 Frequently Encountered Failures

| Failure | Root Cause | Prevention | Detection | Recovery | Frequency |
|---------|-----------|------------|-----------|----------|-----------|
| OCR engine crash (Tesseract) | Memory exhaustion on large images | Limit image size, chunked processing | Health check | Restart Tesseract, retry with Google Vision | Weekly |
| Embedding batch failure | GPU OOM on large batch | Reduce batch size, monitor GPU memory | Log analysis | Retry with smaller batch, CPU fallback | Bi-weekly |
| Database connection exhaustion | Connection leak, PgBouncer misconfig | Connection pooling, query timeout | Connection metrics | Restart PgBouncer, kill idle connections | Monthly |
| Redis memory full | Cache TTL too long, no eviction | Set maxmemory-policy, review TTLs | Memory metrics | Increase plan, flush cache | Monthly |
| LLM hallucination | Insufficient context, temperature too high | Strict grounding, temperature 0.3 | Citation verification | Update prompt, reprocess query | Rare (< 0.1%) |
| Document parsing failure | Corrupted PDF, unsupported format | Magic number validation, format check | Status = "error" | Notify user, manual review | Weekly |
| Rate limit hit | Abuse, misconfigured client | Proper client backoff, rate limit headers | Rate limit metrics | Block IP if abuse, educate user | Daily (free tier) |
| Backup failure | R2 credential expiry, network issue | Automated credential rotation, retry | Backup completion alert | Retry backup, check credentials | Monthly |
| CI/CD failure | Dependency conflict, test flake | Pin dependencies, flaky test tracking | CI status | Retry build, fix dependency | Weekly |
| Feature flag misconfiguration | Human error in LaunchDarkly | Flag review process, config validation | Flag state check | Revert flag, audit changes | Rare |

---

## 14. Operational Checklists

### 14.1 Daily (SRE On-Call)

| # | Task | Tool | Time | Owner | Sign-off |
|---|------|------|------|-------|----------|
| 1 | Check Grafana dashboard (golden signals — all services) | Grafana | 09:00 UTC | SRE On-Call | Slack #sre-daily |
| 2 | Review PagerDuty alerts (acknowledge, resolve, or escalate) | PagerDuty | 09:15 UTC | SRE On-Call | PagerDuty |
| 3 | Check error rates (Sentry — 24h summary) | Sentry | 09:30 UTC | SRE On-Call | Slack #sre-daily |
| 4 | Verify backup completion (automated check script) | Script + R2 | 09:45 UTC | SRE On-Call | Slack #sre-daily |
| 5 | Check queue depths (all Redis queues) | Redis CLI + Grafana | 10:00 UTC | SRE On-Call | Slack #sre-daily |
| 6 | Review AI grounding scores (dashboard) | Grafana | 10:15 UTC | SRE On-Call | Slack #sre-daily |
| 7 | Check citation accuracy (dashboard) | Grafana | 10:30 UTC | SRE On-Call | Slack #sre-daily |
| 8 | Review security logs (anomalies, WAF blocks) | Loki + Cloudflare | 10:45 UTC | SRE On-Call | Slack #sre-daily |
| 9 | Check cost dashboard (budget alerts) | Grafana + Cloudflare | 11:00 UTC | SRE On-Call | Slack #sre-daily |
| 10 | Update incident log (if any incidents occurred) | Jira / Confluence | 11:15 UTC | SRE On-Call | Jira |
| 11 | Review on-call handoff note (if Monday) | Slack | 11:30 UTC | SRE On-Call | Slack |
| 12 | Check SSL certificate expiry (> 30 days) | Script | 11:45 UTC | SRE On-Call | Slack #sre-daily |

### 14.2 Weekly (Platform Team)

| # | Task | Tool | Day | Owner | Sign-off |
|---|------|------|-----|-------|----------|
| 1 | Review deployment metrics (success rate, rollback count, lead time) | Grafana + GitHub | Monday | Platform Lead | Weekly review doc |
| 2 | Review performance metrics (latency trends, p95 changes) | Grafana + Sentry | Monday | Platform Lead | Weekly review doc |
| 3 | Check capacity utilization (CPU, GPU, RAM, storage, connections) | Grafana | Monday | Platform Lead | Weekly review doc |
| 4 | Review security scan results (new vulnerabilities, Dependabot PRs) | Snyk + GitHub | Tuesday | Security Engineer | Weekly review doc |
| 5 | Update dependency versions (merge Dependabot PRs after review) | GitHub | Tuesday | Platform Lead | GitHub merge |
| 6 | Review on-call feedback (pain points, alert fatigue, runbook gaps) | Slack #oncall-feedback | Wednesday | SRE Lead | Weekly review doc |
| 7 | Conduct 15-minute operational review meeting | Zoom | Wednesday | SRE Lead | Meeting notes |
| 8 | Review AI pipeline metrics (processing success, OCR accuracy, embedding quality) | Grafana | Thursday | AI Infra Lead | Weekly review doc |
| 9 | Review cost trends (week-over-week, forecast vs budget) | Grafana + Cloudflare | Thursday | SRE Lead | Weekly review doc |
| 10 | Review feature flag usage (adoption, error correlation) | LaunchDarkly | Friday | Platform Lead | Weekly review doc |
| 11 | Check database health (index bloat, vacuum status, replication lag) | Grafana + psql | Friday | DBA Lead | Weekly review doc |
| 12 | Review support tickets (trends, escalation reasons, resolution time) | Zendesk / Jira | Friday | Support Lead | Weekly review doc |

### 14.3 Monthly (SRE Lead)

| # | Task | Tool | Owner | Sign-off |
|---|------|------|-------|----------|
| 1 | Review SLO compliance (error budget status, all SLIs) | Grafana | SRE Lead | Monthly SRE review |
| 2 | Conduct postmortem review (all incidents from past month) | Jira + Confluence | SRE Lead | Monthly SRE review |
| 3 | Review DR test results (restore test on staging) | Script + Test results | SRE Lead | Monthly SRE review |
| 4 | Verify backup integrity (restore test on staging, sample verification) | Script | SRE Lead | Monthly SRE review |
| 5 | Review access logs (RBAC compliance, unauthorized access attempts) | Loki + PostgreSQL | Security Lead | Monthly security review |
| 6 | Update runbooks (if procedures changed, new incidents learned) | GitHub | SRE Lead | Monthly SRE review |
| 7 | Review cost trends and forecast (next 3 months) | Grafana + Cloudflare | SRE Lead | Monthly SRE review |
| 8 | Capacity planning review (growth projections, scaling needs) | Grafana + Capacity doc | SRE Lead | Monthly SRE review |
| 9 | Review AI model performance (drift, hallucination, grounding) | AI evaluation suite | AI Infra Lead | Monthly AI review |
| 10 | Review security posture (vulnerabilities, patches, access reviews) | Snyk + Access review | Security Lead | Monthly security review |
| 11 | Review compliance status (GDPR, DPDP, retention enforcement) | Compliance dashboard | Compliance Officer | Monthly compliance review |
| 12 | On-call rotation review (schedule conflicts, coverage gaps, handoff quality) | PagerDuty | SRE Lead | Monthly SRE review |

### 14.4 Quarterly (Engineering Leadership)

| # | Task | Tool | Owner | Sign-off |
|---|------|------|-------|----------|
| 1 | Full DR drill (RPO/RTO validation, all systems) | DR runbook | SRE Lead + CTO | DR drill report |
| 2 | Security audit (penetration test, access review, vulnerability scan) | External vendor + internal tools | Security Lead | Security audit report |
| 3 | Compliance review (GDPR, SOC 2 readiness, data residency) | Compliance checklist | Compliance Officer | Compliance review report |
| 4 | Architecture review (scaling needs, tech debt, migration plans) | Architecture review doc | Engineering Lead | Architecture review doc |
| 5 | Team retrospective (operational improvements, process changes) | Retrospective meeting | Engineering Lead | Retrospective notes |
| 6 | Update disaster recovery procedures (based on drill findings) | DR runbook | SRE Lead | Updated runbooks |
| 7 | Review and rotate secrets (if not automated) | Vault + Rotation log | Security Lead | Rotation log |
| 8 | Update incident response playbooks (based on recent incidents) | Incident playbooks | SRE Lead | Updated playbooks |
| 9 | Third-party vendor review (contracts, SLAs, security assessments) | Vendor review doc | Engineering Lead | Vendor review doc |
| 10 | Cost optimization review (identify savings, right-sizing) | Cost analysis | SRE Lead + Finance | Cost optimization report |
| 11 | AI model evaluation (benchmark new models, plan upgrades) | AI evaluation suite | AI Infra Lead | Model evaluation report |
| 12 | Documentation audit (all docs current, cross-references valid) | Documentation checklist | Technical Writer | Documentation audit report |

### 14.5 Yearly (CTO + Leadership)

| # | Task | Tool | Owner | Sign-off |
|---|------|------|-------|----------|
| 1 | Full business continuity review (BCP test, insurance, vendor alternatives) | BCP plan | CTO | BCP review report |
| 2 | Insurance review (cyber liability, business interruption, E&O) | Insurance broker | CTO | Insurance renewal |
| 3 | Vendor review (contracts, SLAs, alternatives, cost negotiation) | Vendor review | CTO | Vendor decisions |
| 4 | Regulatory compliance audit (external auditor, GDPR, SOC 2 if applicable) | External auditor | Compliance Officer | Audit report |
| 5 | Strategic capacity planning (3-year forecast, infrastructure roadmap) | Capacity model | CTO | Strategic plan |
| 6 | Disaster recovery site validation (DR region fully tested, documented) | DR drill | SRE Lead | DR validation report |
| 7 | Update all operational documentation (ORB, DGS, runbooks, playbooks) | Documentation suite | Technical Writer | Updated documentation |
| 8 | Team structure review (on-call health, staffing, training needs) | HR + SRE Lead | CTO | Staffing plan |
| 9 | Technology roadmap review (evaluate new tech, deprecate old tech) | Tech radar | Engineering Lead | Tech roadmap |
| 10 | Security architecture review (threat model, zero trust assessment) | Security architect | Security Lead | Security roadmap |
| 11 | AI ethics review (bias, fairness, transparency, user impact) | AI ethics board | AI Infra Lead | Ethics review report |
| 12 | Board presentation (operational health, risks, investments) | Board deck | CTO | Board approval |

---

## 15. Production Readiness Checklist

Before every production release, the following checklist must be completed and signed off by the designated approvers. No release may proceed without 100% completion.

### 15.1 Security

- [ ] Security scan passed (0 critical/high vulnerabilities in Snyk, Trivy, Dependabot)
- [ ] No secrets hardcoded in code (GitHub Secret Scanning + TruffleHog clean)
- [ ] RBAC policies tested (all roles verified in staging)
- [ ] API rate limiting configured (per-tier limits verified)
- [ ] WAF rules updated (if new endpoints or changed attack surface)
- [ ] Input validation schemas updated (if new API endpoints)
- [ ] CORS policies reviewed (if new domains or subdomains)
- [ ] Security headers verified (CSP, HSTS, X-Frame-Options, etc.)
- [ ] Penetration test findings addressed (if applicable)
- [ ] Privacy impact assessment complete (if data handling changes)

### 15.2 Performance

- [ ] Load test passed (200 concurrent users, < 1% error rate, p95 < SLO)
- [ ] Latency benchmarks within budget (all operations p95 < budget)
- [ ] Memory usage acceptable (no memory leaks, stable over 7-day soak test)
- [ ] Database query performance verified (no N+1 queries, index usage confirmed)
- [ ] Cache hit rate acceptable (> 70% for all cache layers)
- [ ] AI inference latency verified (vLLM and OpenAI fallback both < SLO)
- [ ] Frontend Core Web Vitals verified (LCP < 2.5s, CLS < 0.1, FID < 100ms)
- [ ] Mobile PWA performance verified (offline functionality, sync performance)

### 15.3 Testing

- [ ] Unit tests ≥ 80% coverage (verified by CI)
- [ ] Integration tests passed (100% API endpoints tested)
- [ ] AI evaluation passed (MRR@10 > 0.6, Precision@5 > 0.7, hallucination = 0)
- [ ] E2E tests passed (100% critical user flows in Cypress)
- [ ] Regression tests passed (scoring formula, plan generation, document processing)
- [ ] Security tests passed (OWASP ZAP, no critical/high findings)
- [ ] Accessibility tests passed (WCAG 2.1 AA, axe-core scan)
- [ ] Cross-browser tests passed (Chrome, Firefox, Safari, Edge latest 2 versions)
- [ ] Mobile tests passed (iOS Safari, Android Chrome)

### 15.4 Monitoring

- [ ] Metrics dashboards updated (new metrics added, old metrics verified)
- [ ] Alerts configured and tested (all P0/P1 alerts fired and acknowledged in test)
- [ ] Synthetic monitoring enabled (all monitors active and passing)
- [ ] Health checks verified (all endpoints return expected responses)
- [ ] Log aggregation confirmed (all services logging to Loki, no log loss)
- [ ] Distributed tracing confirmed (spans visible in Jaeger, no broken traces)
- [ ] SLO dashboards updated (new SLIs reflected, error budget baseline set)

### 15.5 Backups

- [ ] Database backup completed (verified by automated check)
- [ ] R2 cross-region sync verified (object count matches, sample checksums valid)
- [ ] Backup restore tested on staging (full restore from latest backup, smoke tests pass)
- [ ] WAL archiving confirmed (no gaps in WAL sequence)
- [ ] Redis snapshot verified (RDB file valid, can be restored)
- [ ] Configuration backup confirmed (Git repository up to date, Terraform state backed up)

### 15.6 Rollback

- [ ] Rollback plan documented (specific steps, estimated time, data loss assessment)
- [ ] Previous version artifacts available (container images, build artifacts, model weights)
- [ ] Feature flags configured for instant rollback (all new flags have kill switch)
- [ ] Database migration is reversible (down.sql tested and verified)
- [ ] Rollback tested on staging (full rollback procedure executed and verified)
- [ ] Previous version health checks verified (last known good version confirmed working)

### 15.7 Documentation

- [ ] API documentation updated (OpenAPI spec, example requests/responses)
- [ ] Runbook updated (if new operational procedures or changed procedures)
- [ ] Known issues list updated (new issues added, resolved issues removed)
- [ ] Customer-facing changelog prepared (user-visible changes, migration notes)
- [ ] Internal release notes written (technical changes, dependencies, deployment steps)
- [ ] Architecture diagrams updated (if infrastructure changes)
- [ ] On-call briefing document prepared (what changed, what to watch, escalation paths)

### 15.8 Compliance

- [ ] Privacy impact assessment complete (if data handling, collection, or retention changes)
- [ ] Audit trail requirements met (all new actions loggable in audit system)
- [ ] Data retention policies respected (no data categories without defined retention)
- [ ] Accessibility (WCAG 2.1 AA) verified (keyboard navigation, screen reader, color contrast)
- [ ] Terms of service / privacy policy updated (if user-facing changes)
- [ ] Data residency verified (all data stays in user-selected region)
- [ ] Export functionality verified (if new data types added)
- [ ] Deletion functionality verified (if new data types added, cascade delete works)

### 15.9 Approval Signatures

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Engineering Lead | | | |
| SRE Lead | | | |
| Product Owner | | | |
| Security Engineer | | | |
| QA Lead | | | |
| Compliance Officer (if applicable) | | | |

**Release is APPROVED for production deployment only when all checklist items are complete and all signatures are obtained.**

---

## 16. Appendices

### Appendix A: Operational Glossary

| Term | Definition | Context |
|------|------------|---------|
| SLO | Service Level Objective — internal reliability target | Monitoring, error budgets |
| SLA | Service Level Agreement — customer-facing contractual guarantee | Customer contracts, support |
| RPO | Recovery Point Objective — maximum acceptable data loss | Disaster recovery, backups |
| RTO | Recovery Time Objective — maximum acceptable downtime | Disaster recovery, incident response |
| Error Budget | Allowed downtime or failures within a period before release freeze | SRE, release planning |
| Canary Release | Gradual rollout to a subset of users | Deployment strategy |
| Blue-Green Deployment | Two identical environments, instant traffic switch | Deployment strategy |
| Rolling Deployment | Gradual replacement of instances | Deployment strategy |
| WORM | Write Once Read Many — immutable storage | Audit logs, compliance |
| PgBouncer | PostgreSQL connection pooler | Database operations |
| IVFFlat | Inverted File Flat — vector index type for < 1M vectors | Vector search |
| HNSW | Hierarchical Navigable Small World — vector index type for > 1M vectors | Vector search |
| RRF | Reciprocal Rank Fusion — result combination algorithm | Hybrid retrieval |
| AIOps | AI Operations — operational practices for AI systems | AI pipeline monitoring |
| JIT | Just-in-Time — temporary access granted for specific need | Security, admin access |
| PII | Personally Identifiable Information | Privacy, data governance |
| HSM | Hardware Security Module — tamper-resistant key storage | Key management |
| Shamir's Secret Sharing | Cryptographic scheme requiring k of n shares to reconstruct secret | Key recovery |
| Golden Signals | Latency, traffic, errors, saturation — four key metrics | Monitoring |
| Circuit Breaker | Pattern to fail fast when dependency is unhealthy | Fault tolerance |
| Feature Flag | Runtime configuration to enable/disable features | Deployment, experimentation |
| CTE | Common Table Expression — recursive SQL query | Knowledge graph |
| pg_cron | PostgreSQL extension for scheduled jobs | Background processing |
| WAL | Write-Ahead Log — database transaction log | Backup, replication |
| PITR | Point-in-Time Recovery — restore to specific moment | Disaster recovery |
| CSR | Certificate Signing Request — for TLS certificate | Security operations |
| CSP | Content Security Policy — browser security header | Web security |
| CSRF | Cross-Site Request Forgery — web attack | Security |
| XSS | Cross-Site Scripting — web attack | Security |
| OIDC | OpenID Connect — identity layer on OAuth 2.0 | Authentication |
| IdP | Identity Provider — SAML/OAuth issuer | Enterprise SSO |
| ABAC | Attribute-Based Access Control — policy based on attributes | Authorization |
| DPDP | Digital Personal Data Protection Act (India) | Compliance |
| SCC | Standard Contractual Clauses — GDPR data transfer mechanism | Compliance |
| DPIA | Data Protection Impact Assessment — GDPR requirement | Compliance |
| MRR | Mean Reciprocal Rank — retrieval metric | AI evaluation |
| NDCG | Normalized Discounted Cumulative Gain — retrieval metric | AI evaluation |
| BM25 | Best Match 25 — probabilistic ranking function | Full-text search |
| LaTeX | Document preparation system for mathematical formulas | OCR, formula extraction |
| PoC | Proof of Concept — customer demonstration | Sandbox |
| BCP | Business Continuity Plan — organizational resilience | Yearly review |
| E&O | Errors and Omissions — professional liability insurance | Yearly review |

### Appendix B: Command Reference

```bash
# ============================================================
# Health & Status
# ============================================================

# Platform health check
curl -s https://adaptive-study-planner.com/api/v3/health | jq

# Deep health check (includes all dependencies)
curl -s https://adaptive-study-planner.com/api/v3/health/deep | jq

# Database status
psql -c "SELECT NOW(), pg_database_size('postgres')/1024/1024/1024 AS size_gb, COUNT(*) as connections FROM pg_stat_activity;"

# Database replication lag
psql -c "SELECT EXTRACT(EPOCH FROM (NOW() - pg_last_xact_replay_timestamp())) AS lag_seconds;"

# Redis status
redis-cli info memory | grep used_memory_human
redis-cli info stats | grep keyspace

# R2 bucket size
rclone size r2:adaptive-study-planner-documents

# Worker queue depths
for queue in document_processing ocr embedding retrieval ai_inference export dead_letter; do
    echo "$queue: $(redis-cli LLEN ${queue}_queue)"
done

# Embedding cache hit rate
redis-cli info stats | grep -E "keyspace_hits|keyspace_misses"

# Recent errors (Sentry)
sentry-cli issues list --project adaptive-study-planner --status unresolved --last-seen 24h

# ============================================================
# Service Management
# ============================================================

# Deploy Cloudflare Workers
wrangler deploy --env production

# Deploy Supabase Edge Functions
supabase functions deploy --project-ref <ref> --all

# Tail Cloudflare Workers logs
wrangler tail --env production

# Restart vLLM
docker-compose -f docker-compose.prod.yml restart vllm

# Restart Ollama
pkill ollama && ollama serve &

# Restart PostgreSQL
pg_ctl restart -D /var/lib/postgresql/data -m smart

# Restart Redis
redis-cli shutdown save && redis-server /etc/redis/redis.conf

# ============================================================
# Database Operations
# ============================================================

# Run migration (staging)
supabase migration up --linked

# Rollback migration (staging)
supabase migration down --linked

# Create new migration
supabase migration new <migration_name>

# Check table sizes
psql -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC;"

# Check index usage
psql -c "SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read FROM pg_stat_user_indexes ORDER BY idx_scan DESC;"

# Check slow queries
psql -c "SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check replication status
psql -c "SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn FROM pg_stat_replication;"

# ============================================================
# AI Operations
# ============================================================

# Check vLLM health
curl -s http://vllm:8000/health | jq

# Check Ollama models
ollama list

# Pull new model
ollama pull <model_name>

# Run AI evaluation
pytest tests/ai_eval/ --model llama3.2

# Benchmark embedding model
python -m backend.benchmark.embedding --model BAAI/bge-m3 --dataset tests/data/benchmark.json

# Rebuild knowledge graph
python -m backend.extraction.batch_rebuild --all-documents

# ============================================================
# Security Operations
# ============================================================

# Check SSL certificate expiry
echo | openssl s_client -servername adaptive-study-planner.com -connect adaptive-study-planner.com:443 2>/dev/null | openssl x509 -noout -dates

# Check certificate details
echo | openssl s_client -servername adaptive-study-planner.com -connect adaptive-study-planner.com:443 2>/dev/null | openssl x509 -noout -text | head -20

# Rotate secret (via Vault)
vault kv put secret/adaptive-study-planner/<secret_name> value=<new_value>

# Check audit logs (last 24 hours)
psql -c "SELECT event_type, actor_type, action, COUNT(*) FROM audit_logs WHERE timestamp > NOW() - INTERVAL '24 hours' GROUP BY event_type, actor_type, action;"

# Check WAF blocks (Cloudflare)
# Via Cloudflare Dashboard → Analytics → Security

# ============================================================
# Monitoring & Alerting
# ============================================================

# Check Grafana dashboards
# https://grafana.adaptive-study-planner.com

# Check Sentry issues
# https://sentry.io/organizations/adaptive-study-planner/issues/

# Check PagerDuty incidents
# https://adaptive-study-planner.pagerduty.com/incidents

# Check status page
# https://status.adaptive-study-planner.com

# Trigger test alert (PagerDuty)
pagerduty event create --service-key=<key> --description="Test alert" --severity=warning

# ============================================================
# Backup & Recovery
# ============================================================

# Manual database backup
pg_dump -Fc postgres > /tmp/backup_$(date +%Y%m%d).dump
rclone copy /tmp/backup_$(date +%Y%m%d).dump r2:backups/db/

# Manual Redis backup
redis-cli BGSAVE
rclone copy /var/lib/redis/dump.rdb r2:backups/redis/

# List backups
rclone ls r2:backups/db/
rclone ls r2:backups/redis/

# Verify backup integrity
pg_restore -l /tmp/backup_$(date +%Y%m%d).dump > /dev/null && echo "Backup valid"
```

### Appendix C: Runbook Templates

All operational runbooks are maintained in `docs/runbooks/` directory. The following runbooks are required for production operations:

| Runbook | Purpose | Last Updated | Owner |
|---------|---------|-------------|-------|
| `runbooks/api-down.md` | API complete outage | 2026-06-28 | SRE |
| `runbooks/db-failover.md` | Database primary failure | 2026-06-28 | DBA Lead |
| `runbooks/db-restore-pitr.md` | Database point-in-time recovery | 2026-06-28 | DBA Lead |
| `runbooks/r2-failover.md` | R2 region failure | 2026-06-28 | SRE Lead |
| `runbooks/r2-restore.md` | R2 bucket/object recovery | 2026-06-28 | SRE Lead |
| `runbooks/r2-outage.md` | R2 complete outage | 2026-06-28 | SRE Lead |
| `runbooks/llm-failover.md` | AI inference cluster failure | 2026-06-28 | AI Infra Lead |
| `runbooks/llm-failover.md` | LLM service complete outage | 2026-06-28 | AI Infra Lead |
| `runbooks/ocr-recovery.md` | OCR pipeline failure | 2026-06-28 | AI Infra Lead |
| `runbooks/embedding-rebuild.md` | Embedding corruption/rebuild | 2026-06-28 | AI Infra Lead |
| `runbooks/graph-rebuild.md` | Knowledge graph rebuild | 2026-06-28 | DBA Lead |
| `runbooks/ddos-response.md` | DDoS attack response | 2026-06-28 | Security Lead |
| `runbooks/security-incident.md` | Security breach response | 2026-06-28 | Security Lead |
| `runbooks/telegram-recovery.md` | Telegram cold backup recovery | 2026-06-28 | SRE Lead |
| `runbooks/deployment-blue-green.md` | Blue-green deployment | 2026-06-28 | DevOps |
| `runbooks/deployment-rolling.md` | Rolling deployment | 2026-06-28 | DevOps |
| `runbooks/deployment-canary.md` | Canary release | 2026-06-28 | Platform Engineering |
| `runbooks/rollback-blue-green.md` | Blue-green rollback | 2026-06-28 | SRE |
| `runbooks/rollback-rolling.md` | Rolling rollback | 2026-06-28 | SRE |
| `runbooks/rollback-canary.md` | Canary rollback | 2026-06-28 | Platform Engineering |
| `runbooks/rollback-database.md` | Database migration rollback | 2026-06-28 | DBA Lead |
| `runbooks/rollback-model.md` | AI model rollback | 2026-06-28 | AI Infra Lead |
| `runbooks/rollback-secrets.md` | Secret rotation rollback | 2026-06-28 | Security Lead |
| `runbooks/emergency-maintenance.md` | Emergency maintenance | 2026-06-28 | SRE Lead |
| `runbooks/latency-degradation.md` | API latency spike | 2026-06-28 | SRE |
| `runbooks/pipeline-failure.md` | AI pipeline failure | 2026-06-28 | AI Infra Lead |
| `runbooks/cache-degradation.md` | Cache performance issue | 2026-06-28 | SRE |
| `runbooks/queue-backlog.md` | Queue backlog | 2026-06-28 | AI Infra Lead |
| `runbooks/gpu-saturation.md` | GPU resource exhaustion | 2026-06-28 | AI Infra Lead |
| `runbooks/fallback-elevated.md` | Elevated fallback usage | 2026-06-28 | AI Infra Lead |
| `runbooks/upload-stuck.md` | Document upload stuck | 2026-06-28 | AI Infra Lead |
| `runbooks/no-citations.md` | Missing AI citations | 2026-06-28 | AI Infra Lead |
| `runbooks/search-empty.md` | Empty search results | 2026-06-28 | AI Infra Lead |
| `runbooks/slow-ai.md` | Slow AI response | 2026-06-28 | AI Infra Lead |
| `runbooks/login-failure.md` | User login failure | 2026-06-28 | Security Lead |
| `runbooks/doc-missing.md` | Document not in KB | 2026-06-28 | AI Infra Lead |
| `runbooks/high-errors.md` | High error rate | 2026-06-28 | SRE |
| `runbooks/r2-denied.md` | R2 access denied | 2026-06-28 | SRE |
| `runbooks/cache-miss.md` | Cache miss spike | 2026-06-28 | SRE |
| `runbooks/dr-activation.md` | Full disaster recovery activation | 2026-06-28 | SRE Lead |
| `runbooks/hallucination-detected.md` | AI hallucination incident | 2026-06-28 | AI Infra Lead |
| `runbooks/citation-failure.md` | Citation verification failure | 2026-06-28 | AI Infra Lead |
| `runbooks/replication-lag.md` | Database replication lag | 2026-06-28 | DBA Lead |
| `runbooks/certificate-renewal.md` | SSL certificate renewal | 2026-06-28 | Platform Engineering |
| `runbooks/backup-failure.md` | Backup failure | 2026-06-28 | SRE |
| `runbooks/cost-optimization.md` | Cost optimization | 2026-06-28 | SRE |
| `runbooks/capacity-planning.md` | Capacity planning | 2026-06-28 | SRE Lead |
| `runbooks/oncall-handoff.md` | On-call handoff | 2026-06-28 | SRE |

### Appendix D: Incident Report Template

See Section 6.3 (Postmortem Template) for the full incident report template.

**Quick Incident Summary (for Slack #incidents):**

```
🚨 INCIDENT: [SEV-X] [Brief description]

Time: [HH:MM UTC]
Service: [Affected service]
Impact: [Users affected / features down]
Status: [Investigating / Identified / Mitigating / Resolved]
On-call: [Engineer name]

[Link to PagerDuty incident]
[Link to Zoom war room]
```

### Appendix E: Maintenance Checklist Template

```markdown
# Maintenance: [Title] — [Date]

## Metadata
| Field | Value |
|-------|-------|
| Type | [Scheduled / Emergency / Security] |
| Duration | [Start] – [End] |
| Authorization | [Names] |
| Impact | [Services affected] |

## Pre-Maintenance
- [ ] Maintenance mode enabled
- [ ] Users notified (status page, in-app, email)
- [ ] On-call engineer briefed
- [ ] Rollback plan ready
- [ ] Backup completed (if database involved)

## Maintenance Steps
| Step | Action | Verification | Time |
|------|--------|------------|------|
| 1 | [Action] | [Verification] | [HH:MM] |
| 2 | [Action] | [Verification] | [HH:MM] |
| 3 | [Action] | [Verification] | [HH:MM] |

## Post-Maintenance
- [ ] Health checks passed
- [ ] Golden signals within SLO
- [ ] Maintenance mode disabled
- [ ] Users notified (all clear)
- [ ] Incident log updated
- [ ] Runbook updated (if needed)
```

### Appendix F: Cross-Document References

| Section | PRD | ES | ADR | ADS | TS | DGS |
|---------|-----|-----|-----|-----|-----|-----|
| Production Architecture | 6. NFR | 9 | ADR-009 | E-026 | 6 | 7 |
| Infrastructure Inventory | 6. NFR | 1, 6 | ADR-010 | E-014 | 6 | 7 |
| Deployment Strategy | 6. NFR | 9 | — | E-026 | 6 | — |
| Monitoring | 6. NFR | 11 | — | E-026 | 6, 7 | — |
| Incident Response | 6. NFR | 12 | — | — | 6 | — |
| Disaster Recovery | 6. NFR | 13 | ADR-014 | — | 9.9 | 11 |
| Operational Procedures | 6. NFR | 9 | — | — | 6 | — |
| Security Operations | 12 | 5, 8 | — | E-014 | 8 | 7 |
| AI Operations | 4. FR | 7 | ADR-018 | E-024 | 9.8 | 6 |
| Capacity Planning | 6. NFR | 10 | — | — | 6 | — |
| Performance Operations | 6. NFR | 10, 11 | — | E-026 | 6 | — |
| Support Operations | 6. NFR | 12 | — | — | 6 | — |

---

*End of Operational Runbook v1.0.0*

*Document maintained by Platform Engineering & SRE Team.*
*For questions, corrections, or updates, contact sre@adaptive-study-planner.com or open an issue in the docs repository.*
