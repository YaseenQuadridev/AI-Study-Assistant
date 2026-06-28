# Operational Runbook (ORB)

## AI Study Assistant — Phase 4.1.0 ENTERPRISE

**Version:** 1.0.0
**Date:** 2026-06-27
**Status:** Approved — Production Ready
**Owner:** Platform Engineering & SRE Team
**Authors:** Principal SRE, Principal Platform Engineer, Principal Cloud Architect, Principal Security Engineer, DevSecOps Lead

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
The Adaptive Study Planner operates as a **multi-tenant SaaS platform** serving students and educators globally. The platform ingests educational documents, processes them into a structured knowledge base, and provides AI-powered study assistance grounded in trusted sources.

### 1.2 Deployment Model
- **Cloudflare Workers** (serverless edge) for API gateway and routing
- **Supabase** (managed PostgreSQL + pgvector) for data persistence and semantic search
- **Cloudflare R2** (object storage) for document storage with zero egress fees
- **Telegram** (optional cold backup) for disaster recovery
- **Ollama/vLLM** (self-hosted) for local AI inference
- **OpenAI** (optional, paid fallback) for cloud AI inference

### 1.3 Operational Philosophy
- **You build it, you run it:** Each service team owns their service in production
- **SRE principles:** Error budgets, SLO-driven prioritization, blameless postmortems
- **Automation first:** All operational procedures must be automated where possible
- **Observability by design:** Every service emits metrics, logs, and traces by default
- **Security by default:** Zero trust architecture, least privilege, defense in depth

### 1.4 Reliability Goals
| Metric | Target | SLO | SLA (Customer-facing) |
|--------|--------|-----|----------------------|
| Uptime | 99.9% | 99.95% | 99.9% |
| API p95 Latency | < 500ms | < 300ms | < 500ms |
| Retrieval p95 Latency | < 200ms | < 150ms | < 200ms |
| AI Response p95 Latency | < 2s | < 1.5s | < 2s |
| Processing Success Rate | 99.5% | 99.8% | 99.5% |
| OCR Accuracy (printed) | > 85% | > 90% | > 85% |
| Citation Verification | 100% | 100% | 100% |
| Hallucination Rate | 0% | 0% | 0% |

### 1.5 Service Ownership
| Service | Owner | On-call | Escalation |
|---------|-------|---------|------------|
| Cloudflare Workers | Platform Engineering | P1: 15 min | SRE Lead |
| Supabase PostgreSQL | Database Engineering | P1: 15 min | DBA Lead |
| Supabase Edge Functions | AI Infrastructure | P1: 15 min | AI Infra Lead |
| R2 Object Storage | Platform Engineering | P2: 1 hour | SRE Lead |
| Ollama/vLLM | AI Infrastructure | P1: 15 min | AI Infra Lead |
| OpenAI Fallback | AI Infrastructure | P2: 1 hour | AI Infra Lead |
| OCR Pipeline | AI Infrastructure | P2: 1 hour | AI Infra Lead |
| Embedding Pipeline | AI Infrastructure | P2: 1 hour | AI Infra Lead |
| Retrieval Engine | AI Infrastructure | P1: 15 min | AI Infra Lead |
| Citation Engine | AI Infrastructure | P2: 1 hour | AI Infra Lead |
| Frontend (PWA) | Frontend Engineering | P2: 1 hour | Frontend Lead |
| Monitoring/Alerting | SRE | P0: 5 min | SRE Lead |

### 1.6 Support Responsibilities
| Tier | Hours | Response Time | Scope |
|------|-------|--------------|-------|
| L1 — Support Engineering | 24/7 | 15 min | User issues, password resets, basic troubleshooting |
| L2 — Platform Engineering | 24/7 | 1 hour | API issues, performance degradation, deployment failures |
| L3 — SRE / AI Infrastructure | 24/7 | 15 min | Infrastructure outages, AI pipeline failures, data corruption |
| L4 — Engineering Lead | Business hours | 4 hours | Architectural decisions, security incidents, major outages |

---

## 2. Production Architecture

### 2.1 Production Topology (ASCII)

```
                          Internet
                             |
                    +--------v--------+
                    |   Cloudflare    |
                    |   WAF + CDN     |
                    +--------+--------+
                             |
              +--------------+--------------+
              |                             |
     +--------v--------+          +--------v--------+
     |  Cloudflare     |          |  Cloudflare     |
     |  Workers (API   |          |  Pages (Static   |
     |  Gateway)       |          |  Frontend)      |
     +--------+--------+          +-----------------+
              |
     +--------v--------+
     |  Rate Limiting   |
     |  JWT Validation  |
     |  CORS Handling   |
     +--------+--------+
              |
     +--------v--------+
     |  Supabase Edge  |
     |  Functions (AI  |
     |  Pipeline)      |
     +--------+--------+
              |
     +--------v--------+
     |  PostgreSQL +   |
     |  pgvector (Supa-|
     |  base)           |
     +--------+--------+
              |
     +--------v--------+
     |  Redis (Upstash)|
     |  Cache + Queue   |
     +--------+--------+
              |
     +--------v--------+
     |  R2 Object      |
     |  Storage (Docs)  |
     +-----------------+
```

### 2.2 Environments

#### 2.2.1 Development
- **Purpose:** Local development, feature experimentation
- **URL:** `http://localhost:8787`
- **Database:** Local PostgreSQL + pgvector (Docker)
- **AI:** Local Ollama (llama3.2)
- **Storage:** Local MinIO
- **Access:** Individual developers
- **Data:** Synthetic test data only
- **Deployment:** Manual (`wrangler dev`)

#### 2.2.2 Testing (CI)
- **Purpose:** Automated test execution
- **URL:** Ephemeral (GitHub Actions runners)
- **Database:** Supabase dev project (isolated schema)
- **AI:** Ollama (CI runner)
- **Storage:** R2 dev bucket
- **Access:** CI/CD pipeline only
- **Data:** Synthetic + anonymized snapshots
- **Deployment:** Automated on every PR

#### 2.2.3 Staging
- **Purpose:** Pre-production validation, integration testing
- **URL:** `https://staging.adaptive-study-planner.com`
- **Database:** Supabase staging project (migrated nightly from production)
- **AI:** vLLM (GPU, staging cluster)
- **Storage:** R2 staging bucket
- **Access:** Engineering team, QA team
- **Data:** Anonymized production snapshot (7 days old)
- **Deployment:** Automated on merge to `develop` branch

#### 2.2.4 Production
- **Purpose:** Live customer-facing service
- **URL:** `https://adaptive-study-planner.com`
- **Database:** Supabase production project (primary + read replicas)
- **AI:** vLLM (GPU, production cluster) + OpenAI fallback
- **Storage:** R2 production bucket (cross-region replicated)
- **Access:** Customers, SRE on-call, emergency admin access
- **Data:** All customer data, encrypted at rest
- **Deployment:** Manual approval after staging validation

#### 2.2.5 Disaster Recovery
- **Purpose:** Recovery from catastrophic failure
- **URL:** Activated on DR declaration only
- **Database:** Point-in-time recovery from backups (7-day retention)
- **AI:** Ollama (CPU, no GPU dependency)
- **Storage:** R2 cross-region replica + Telegram cold backup
- **Access:** SRE Lead, CTO
- **Data:** Last successful backup (RPO < 1 hour)
- **Deployment:** Runbook-driven recovery procedure

#### 2.2.6 Sandbox
- **Purpose:** Customer PoC, security testing, penetration testing
- **URL:** `https://sandbox.adaptive-study-planner.com`
- **Database:** Isolated Supabase project (reset weekly)
- **AI:** Ollama (CPU only)
- **Storage:** Dedicated R2 bucket
- **Access:** Approved external parties, security team
- **Data:** Dummy data, no PII
- **Deployment:** Automated from `sandbox` branch

---

## 3. Infrastructure Inventory

### 3.1 Frontend
| Component | Technology | Purpose | Owner |
|-----------|------------|---------|-------|
| PWA | Vanilla JS + Tailwind CSS | User interface | Frontend Engineering |
| Static Hosting | Cloudflare Pages | CDN-delivered frontend | Platform Engineering |
| Service Worker | Workbox | Offline caching, PWA | Frontend Engineering |

### 3.2 Backend
| Component | Technology | Purpose | Owner |
|-----------|------------|---------|-------|
| API Gateway | Cloudflare Workers | Route, validate, rate limit | Platform Engineering |
| Edge Functions | Supabase Edge Functions | AI pipeline, document processing | AI Infrastructure |
| Webhooks | Cloudflare Workers | Async processing triggers | Platform Engineering |

### 3.3 Authentication
| Component | Technology | Purpose | Owner |
|-----------|------------|---------|-------|
| Auth Provider | Supabase Auth | JWT, OAuth, SAML | Security Engineering |
| MFA | TOTP (RFC 6238) | Enterprise 2FA | Security Engineering |
| API Keys | Scoped JWT (RS256) | Programmatic access | Security Engineering |

### 3.4 Storage
| Component | Technology | Purpose | Owner |
|-----------|------------|---------|-------|
| Object Storage (Primary) | Cloudflare R2 | Raw documents, audio, exports | Platform Engineering |
| Object Storage (Fallback) | AWS S3 | Enterprise multi-cloud | Platform Engineering |
| Cold Backup | Telegram Bot API | Optional off-site backup | SRE |
| Cache | Upstash Redis | Rate limiting, query cache, embedding cache | Platform Engineering |

### 3.5 Database
| Component | Technology | Purpose | Owner |
|-----------|------------|---------|-------|
| Primary DB | Supabase PostgreSQL 15 | Metadata, users, documents, chunks | Database Engineering |
| Vector Extension | pgvector 0.5.1 | Semantic search embeddings | Database Engineering |
| Full-Text Index | PostgreSQL GIN tsvector | BM25 keyword search | Database Engineering |
| Read Replicas | PostgreSQL Streaming | Read-heavy query offloading | Database Engineering |
| Connection Pool | PgBouncer | Connection management | Database Engineering |

### 3.6 Knowledge Graph
| Component | Technology | Purpose | Owner |
|-----------|------------|---------|-------|
| Graph Store (Phase 3) | PostgreSQL recursive CTEs | Concept relationships | Database Engineering |
| Graph Store (Phase 4) | ArangoDB (eval) | Multi-model graph (if needed) | Database Engineering |
| Graph Visualization | D3.js / Cytoscape.js | Frontend graph rendering | Frontend Engineering |

### 3.7 Monitoring
| Component | Technology | Purpose | Owner |
|-----------|------------|---------|-------|
| Metrics | Grafana + Prometheus | Dashboards, alerts | SRE |
| Logs | Loki / Sentry | Centralized log aggregation | SRE |
| Traces | OpenTelemetry + Jaeger | Distributed tracing | SRE |
| APM | Sentry | Error tracking, performance | SRE |
| Synthetic | UptimeRobot / Pingdom | External health checks | SRE |
| Alerting | PagerDuty + Slack | P0/P1/P2 alert routing | SRE |

### 3.8 Logging
| Component | Technology | Purpose | Retention |
|-----------|------------|---------|-----------|
| Application Logs | Structured JSON (stdout) | Correlation ID, request details | 30 days hot, 1 year cold |
| Audit Logs | PostgreSQL WORM table | Immutable user/system actions | 7 years |
| Security Logs | Sentry + SIEM | Auth, access, anomalies | 2 years |
| AI Logs | PostgreSQL | Grounding audit, citation verification | 2 years |

### 3.9 Tracing
| Component | Technology | Purpose | Sampling |
|-----------|------------|---------|----------|
| Distributed Traces | OpenTelemetry + Jaeger | End-to-end request flow | 10% (production), 100% (staging) |
| Span Context | W3C Trace Context | Propagation across services | All requests |

### 3.10 CI/CD
| Component | Technology | Purpose | Owner |
|-----------|------------|---------|-------|
| Source Control | GitHub | Git repository | DevOps |
| CI Pipeline | GitHub Actions | Lint, test, build, deploy | DevOps |
| IaC | Terraform + Wrangler | Infrastructure as code | Platform Engineering |
| Artifact Registry | GitHub Packages / R2 | Build artifacts | DevOps |
| Feature Flags | LaunchDarkly | Gradual rollout | Platform Engineering |

### 3.11 Background Workers
| Worker Type | Technology | Purpose | Concurrency |
|-------------|------------|---------|-------------|
| OCR Workers | Supabase Edge Functions | Image → text extraction | 10 parallel |
| Embedding Workers | Supabase Edge Functions | Chunk → vector embedding | 20 parallel |
| Retrieval Workers | Cloudflare Workers | Query → hybrid search | 200 concurrent |
| AI Workers | vLLM / OpenAI | LLM inference | 50 concurrent |
| Citation Workers | Supabase Edge Functions | Citation verification | 20 concurrent |
| Graph Workers | PostgreSQL CTE | Graph traversal | 10 concurrent |

### 3.12 Queues
| Queue | Technology | Purpose | TTL |
|-------|------------|---------|-----|
| Document Processing | Redis (Upstash) | Upload → processing pipeline | 24 hours |
| OCR Queue | Redis (Upstash) | Pending OCR jobs | 12 hours |
| Embedding Queue | Redis (Upstash) | Pending embedding jobs | 12 hours |
| Retrieval Queue | Redis (Upstash) | Query caching | 1 hour |
| Dead Letter Queue | Redis (Upstash) | Failed jobs for manual review | 7 days |

### 3.13 Secrets Management
| Component | Technology | Purpose | Rotation |
|-----------|------------|---------|----------|
| API Keys | Supabase Vault | Cloud service credentials | 90 days |
| DB Credentials | Supabase Vault | PostgreSQL passwords | 90 days |
| JWT Keys | Supabase Auth | RS256 signing keys | 180 days |
| OAuth Secrets | HashiCorp Vault | Google, GitHub OAuth | 90 days |
| LLM API Keys | HashiCorp Vault | OpenAI, Google Vision | 90 days |
| TLS Certificates | Let's Encrypt + Cloudflare | HTTPS termination | 90 days |

---

## 4. Deployment Strategy

### 4.1 Blue-Green Deployment
- **Use case:** Major version releases, database schema changes
- **Process:**
  1. Deploy new version to green environment (staging)
  2. Run full validation suite against green
  3. Switch traffic from blue to green via DNS/Cloudflare
  4. Monitor green for 1 hour
  5. If issues, rollback to blue (DNS switchback)
- **Downtime:** < 30 seconds (DNS TTL)
- **Risk:** Low (instant rollback)

### 4.2 Rolling Deployment
- **Use case:** Minor patches, bug fixes, non-breaking changes
- **Process:**
  1. Deploy to 10% of Cloudflare Workers (canary)
  2. Monitor error rate and latency for 10 minutes
  3. If healthy, deploy to 50%
  4. If healthy, deploy to 100%
- **Downtime:** Zero (gradual rollout)
- **Risk:** Medium (partial exposure)

### 4.3 Canary Releases
- **Use case:** New features, UI changes, AI model updates
- **Process:**
  1. Enable feature flag for 5% of users
  2. Monitor feature-specific metrics (adoption, errors, latency)
  3. Gradually increase to 25%, 50%, 100%
  4. At each stage, require approval from Product Owner
- **Rollback:** Disable feature flag (instant)
- **Duration:** 1-7 days per stage

### 4.4 Feature Flags
| Flag | System | Default | Rollout Strategy |
|------|--------|---------|------------------|
| `hybrid_retrieval` | LaunchDarkly | ON | 100% (core feature) |
| `google_vision_ocr` | LaunchDarkly | OFF | Pro tier only |
| `mathpix_formula` | LaunchDarkly | OFF | Pro tier only |
| `openai_fallback` | LaunchDarkly | ON | 100% (fallback) |
| `graph_visualization` | LaunchDarkly | ON | 100% (core feature) |
| `knowledge_sharing` | LaunchDarkly | OFF | Gradual (beta) |
| `auto_resource_setup` | LaunchDarkly | ON | 100% (core feature) |

### 4.5 Rollback Strategy
| Deployment Type | Rollback Method | Time to Rollback | Data Loss |
|-----------------|-----------------|-----------------|-----------|
| Blue-Green | DNS switch | < 30s | None |
| Rolling | Re-deploy previous version | < 5 min | None |
| Canary | Disable feature flag | < 10s | None |
| Database Migration | Reverse migration script | < 10 min | None (if reversible) |
| Hotfix | Direct commit to main | < 15 min | None |

### 4.6 Emergency Rollback Procedure
```bash
# 1. Identify last known good version
LAST_GOOD=$(git log --oneline -10 | grep -i "stable\|hotfix" | head -1 | awk '{print $1}')

# 2. Re-deploy immediately
wrangler deploy --tag $LAST_GOOD

# 3. Disable problematic feature flags
launchdarkly flag disable new_feature --env production

# 4. Verify health
curl https://adaptive-study-planner.com/api/v3/health

# 5. Notify stakeholders
slack send "Emergency rollback to $LAST_GOOD completed" #sre-alerts
```

### 4.7 Hotfix Process
1. **Declare:** Create `hotfix/` branch from `main`
2. **Fix:** Apply minimal fix (no feature additions)
3. **Test:** Run targeted tests + smoke tests
4. **Review:** Expedited review (1 approver, 15 min SLA)
5. **Deploy:** Direct deploy to production (skip staging)
6. **Monitor:** 1-hour enhanced monitoring
7. **Merge:** Back-merge to `develop` and `main`

### 4.8 Deployment Checklist
- [ ] All tests passing (unit, integration, AI eval, E2E)
- [ ] Security scan: 0 critical/high vulnerabilities
- [ ] Database migration tested on staging (reversible)
- [ ] Feature flags configured (default states)
- [ ] Monitoring dashboards updated
- [ ] Alerts verified (PagerDuty, Slack)
- [ ] Runbook updated (if new operational procedure)
- [ ] Customer communication prepared (if user-facing change)
- [ ] Rollback plan documented and tested
- [ ] On-call engineer briefed on changes

---

## 5. Monitoring

### 5.1 Golden Signals (per service)
| Signal | Metric | Alert Threshold | Dashboard |
|--------|--------|-----------------|-----------|
| Latency | p95 request duration | > 500ms for 5 min | Grafana |
| Traffic | Requests per second | > 10,000 RPS | Grafana |
| Errors | HTTP 5xx rate | > 0.1% for 2 min | Grafana |
| Saturation | CPU / GPU utilization | > 80% for 5 min | Grafana |

### 5.2 SLIs, SLOs, SLAs
| SLI | SLO | SLA | Measurement |
|-----|-----|-----|-------------|
| API availability | 99.95% | 99.9% | Synthetic probe every 30s |
| API latency (p95) | < 300ms | < 500ms | APM (Sentry) |
| Retrieval latency (p95) | < 150ms | < 200ms | APM |
| AI response latency (p95) | < 1.5s | < 2s | APM |
| Processing success rate | 99.8% | 99.5% | Log analysis |
| OCR accuracy (printed) | > 90% | > 85% | Weekly sample |
| Citation accuracy | 100% | 100% | Per-response verification |
| Hallucination rate | 0% | 0% | Weekly AI evaluation |

### 5.3 Error Budgets
- **Monthly error budget:** 0.05% downtime (21.6 minutes)
- **Quarterly error budget:** 0.15% downtime (65 minutes)
- **If budget exceeded:** Freeze all non-critical releases until next period
- **Tracking:** Grafana dashboard + monthly SRE review

### 5.4 Alert Thresholds
| Priority | Metric | Threshold | Duration | Channel | Response Time |
|----------|--------|-----------|----------|---------|---------------|
| P0 | API down | 0% success | 1 min | PagerDuty + Phone | 5 min |
| P0 | Database unreachable | Connection failure | 1 min | PagerDuty + Phone | 5 min |
| P1 | API p95 > 500ms | > 500ms | 5 min | Slack #sre-alerts | 15 min |
| P1 | Processing failure rate > 1% | > 1% | 5 min | Slack #sre-alerts | 15 min |
| P1 | OCR accuracy < 80% | < 80% | 1 hour | Slack #ai-alerts | 1 hour |
| P2 | Cache hit rate < 60% | < 60% | 1 hour | Slack #warnings | 4 hours |
| P2 | Embedding queue depth > 100 | > 100 | 30 min | Slack #warnings | 4 hours |
| P3 | Disk usage > 80% | > 80% | 1 day | Email | 24 hours |

### 5.5 Health Checks
| Endpoint | Frequency | Expected | Action on Failure |
|----------|-----------|----------|-------------------|
| GET /api/v3/health | Every 30s | 200 OK | Alert P0 |
| Database ping | Every 30s | < 100ms | Alert P0 |
| Redis ping | Every 30s | PONG | Alert P1 |
| R2 bucket list | Every 5 min | Success | Alert P1 |
| vLLM health | Every 30s | 200 OK | Alert P0 (fallback to OpenAI) |
| OCR engine health | Every 5 min | Tesseract available | Alert P2 |

---

## 6. Incident Response

### 6.1 Severity Levels

#### SEV-0 — Critical (All-Hands)
- **Definition:** Complete platform outage or data breach
- **Examples:** All Workers down, database corruption, security breach, R2 total loss
- **Response Time:** 5 minutes (24/7)
- **Escalation:** Auto-page all on-call engineers + CTO
- **Communication:** War room (Zoom), public status page updated every 15 min
- **Postmortem:** Required within 4 hours of resolution, mandatory attendance

#### SEV-1 — Major
- **Definition:** Major feature unavailable or severe degradation
- **Examples:** AI pipeline down, upload service failing, retrieval returning empty results, >50% error rate
- **Response Time:** 15 minutes (24/7)
- **Escalation:** Page SRE + AI Infrastructure leads
- **Communication:** Slack #incidents, status page updated every 30 min
- **Postmortem:** Required within 24 hours

#### SEV-2 — Significant
- **Definition:** Degraded performance affecting some users
- **Examples:** Slow AI responses (>5s), OCR accuracy drop, partial feature failure, >10% error rate
- **Response Time:** 1 hour (business hours)
- **Escalation:** Slack #incidents, assign to owning team
- **Communication:** Slack #incidents, no status page unless >1 hour
- **Postmortem:** Required within 48 hours

#### SEV-3 — Minor
- **Definition:** Isolated issue, workaround available
- **Examples:** Single user upload failure, intermittent 500s, non-critical feature bug
- **Response Time:** 4 hours (business hours)
- **Escalation:** Support ticket, assigned to engineering
- **Communication:** Internal ticket tracking
- **Postmortem:** Optional, at team lead discretion

#### SEV-4 — Informational
- **Definition:** No user impact, proactive issue
- **Examples:** Latency approaching threshold, non-critical alert, capacity warning
- **Response Time:** Next business day
- **Escalation:** Ticket backlog
- **Communication:** Weekly ops review
- **Postmortem:** Not required

### 6.2 Incident Response Flow
```
Alert Fires
  |
  +---> P0: Page on-call + SRE Lead + CTO (5 min)
  +---> P1: Page on-call + team lead (15 min)
  +---> P2: Slack alert + ticket (1 hour)
  +---> P3: Email digest (24 hours)
  |
  +---> Acknowledge (mark as "acknowledged" in PagerDuty)
  |
  +---> Triage (determine severity, scope, impact)
  |
  +---> Mitigate (apply workaround, enable fallback, scale up)
  |
  +---> Communicate (status page, Slack, customer comms if needed)
  |
  +---> Resolve (verify fix, monitor for 30 min)
  |
  +---> Postmortem (within SLA deadline)
```

### 6.3 Postmortem Template
```markdown
# Postmortem: [Incident Title] — [Date] — [SEV-X]

## Summary
One-paragraph description of what happened and impact.

## Timeline
- HH:MM — Alert fired
- HH:MM — On-call acknowledged
- HH:MM — Root cause identified
- HH:MM — Mitigation applied
- HH:MM — Service restored
- HH:MM — Monitoring confirmed stable

## Root Cause
Technical explanation of why the incident occurred.

## Impact
- Users affected: [number]
- Duration: [minutes]
- Data loss: [yes/no, amount]
- Revenue impact: [if applicable]

## What Went Well
- [Bullet points]

## What Went Wrong
- [Bullet points]

## Action Items
| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| [Fix] | [Name] | [Date] | P[X] |

## Lessons Learned
[Free-form reflection]
```

---

## 7. Disaster Recovery

### 7.1 Backup Policy
| Component | Frequency | Retention | Location | Method |
|-----------|-----------|-----------|----------|--------|
| PostgreSQL (full) | Daily | 7 days | Cross-region R2 | `pg_dump` |
| PostgreSQL (WAL) | Continuous | 7 days | Same region | WAL archiving |
| R2 Documents | Real-time | 30 days | Cross-region R2 | Replication |
| Redis | Daily | 7 days | R2 | RDB snapshot |
| Telegram | On upload | Unlimited | Telegram | Bot API |
| Configuration | On change | 1 year | GitHub | Git history |

### 7.2 Restore Procedures

#### PostgreSQL Point-in-Time Recovery
```bash
# 1. Identify target recovery time
target_time="2026-06-27 14:00:00 UTC"

# 2. Download latest base backup from R2
rclone copy r2:backup/db/$(date +%Y%m%d)_basebackup.tar.gz ./restore/

# 3. Extract
tar -xzf restore/basebackup.tar.gz -C /var/lib/postgresql/data

# 4. Configure recovery.conf
cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = 'cp /backups/wal/%f %p'
recovery_target_time = '$target_time'
recovery_target_action = 'promote'
EOF

# 5. Start PostgreSQL
pg_ctl start -D /var/lib/postgresql/data

# 6. Verify
psql -c "SELECT NOW(), pg_last_xact_replay_timestamp();"
```

#### R2 Document Recovery
```bash
# 1. List objects in cross-region bucket
aws s3 ls s3://backup-r2/users/ --recursive --profile backup

# 2. Sync to primary bucket
aws s3 sync s3://backup-r2/users/ s3://primary-r2/users/ --profile backup

# 3. Verify integrity (sample 10%)
find /restore -type f | head -n $(( $(find /restore -type f | wc -l) / 10 )) | xargs sha256sum -c checksums.txt
```

#### Telegram Cold Backup Recovery
```bash
# 1. Identify missing document IDs
psql -c "SELECT id FROM documents WHERE r2_path IS NULL;"

# 2. Query Telegram bot for each document
# (Manual admin process — see `docs/runbooks/telegram-recovery.md`)
# 3. Download and validate checksum
# 4. Restore to R2 and re-index
```

### 7.3 RPO and RTO
| Scenario | RPO | RTO | Procedure |
|----------|-----|-----|-----------|
| Database corruption | < 1 hour | < 2 hours | PITR from WAL |
| R2 bucket deletion | < 1 hour | < 1 hour | Cross-region sync |
| Complete region failure | < 1 hour | < 4 hours | Activate DR region |
| Telegram-only recovery | N/A | < 24 hours | Manual recovery |

### 7.4 Recovery Validation
- **Monthly:** Restore test on staging (automated)
- **Quarterly:** Full DR drill (manual, scheduled)
- **Validation criteria:**
  - All user documents accessible
  - All embeddings searchable
  - All knowledge graph edges intact
  - AI responses grounded correctly
  - Citation verification passes

---

## 8. Operational Procedures

### 8.1 Starting Services
```bash
# Cloudflare Workers
wrangler deploy --env production

# Supabase Edge Functions
supabase functions deploy --project-ref <ref>

# vLLM (GPU)
docker-compose -f docker-compose.prod.yml up -d vllm

# Ollama (local)
ollama serve &
ollama pull llama3.2

# PostgreSQL
pg_ctl start -D /var/lib/postgresql/data

# Redis
redis-server /etc/redis/redis.conf

# Grafana + Jaeger
docker-compose -f monitoring/docker-compose.yml up -d
```

### 8.2 Stopping Services
```bash
# Graceful shutdown (drain connections first)
wrangler deploy --env production --no-dispatch
supabase functions stop --project-ref <ref>
docker-compose -f docker-compose.prod.yml down --timeout 60
pg_ctl stop -D /var/lib/postgresql/data -m smart
redis-cli shutdown save
```

### 8.3 Scaling Services
| Service | Scale Trigger | Scale Action | Max |
|---------|--------------|--------------|-----|
| Cloudflare Workers | RPS > 5,000 | Auto (serverless) | Unlimited |
| Supabase Edge Functions | Queue depth > 100 | Auto (serverless) | Unlimited |
| vLLM GPU | GPU util > 80% | Add GPU node | 10 nodes |
| PostgreSQL | Connection count > 100 | Add read replica | 5 replicas |
| Redis | Memory > 80% | Upgrade plan | 10GB |
| R2 | Storage growth | Auto (unlimited) | Unlimited |

### 8.4 Rotating Secrets
```bash
# 1. Generate new secret
new_key=$(openssl rand -hex 32)

# 2. Update in HashiCorp Vault
vault kv put secret/adaptive-study-planner/api-key value=$new_key

# 3. Update in Supabase Vault (for DB credentials)
supabase vault set-secret db-password $new_key

# 4. Deploy with new secret (zero-downtime)
wrangler secret put API_KEY --env production

# 5. Verify
wrangler tail --env production | grep "API_KEY"

# 6. Revoke old secret (24 hours later)
vault kv delete secret/adaptive-study-planner/api-key-old
```

### 8.5 Database Migrations
```bash
# 1. Create migration (reversible required)
supabase migration new add_knowledge_graph_indexes

# 2. Write migration (up.sql + down.sql)
# up.sql: CREATE INDEX ...
# down.sql: DROP INDEX ...

# 3. Test on staging
supabase db reset --linked
supabase migration up --linked

# 4. Deploy to production (maintenance window if > 1 min downtime)
supabase migration up --linked

# 5. Verify
psql -c "\d knowledge_edges"

# 6. If failure, rollback
supabase migration down --linked
```

### 8.6 Reindexing Vectors
```bash
# 1. Create new index concurrently
CREATE INDEX CONCURRENTLY idx_chunks_embedding_new
ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 200);

# 2. Verify index is valid
SELECT pg_index_is_valid('idx_chunks_embedding_new'::regclass);

# 3. Drop old index
DROP INDEX CONCURRENTLY idx_chunks_embedding;

# 4. Rename new index
ALTER INDEX idx_chunks_embedding_new RENAME TO idx_chunks_embedding;
```

### 8.7 Rebuilding Knowledge Graph
```bash
# 1. Truncate existing edges (preserve nodes)
psql -c "TRUNCATE knowledge_edges;"

# 2. Re-run extraction for all documents
python -m backend.extraction.batch_rebuild --all-documents

# 3. Verify edge count
psql -c "SELECT COUNT(*) FROM knowledge_edges;"

# 4. Check for cycles
psql -c "SELECT * FROM detect_cycles();"
```

### 8.8 Emergency Maintenance
```bash
# 1. Enable maintenance mode
wrangler kv put MAINTENANCE_MODE "true" --env production

# 2. Notify users (status page + in-app banner)
curl -X POST https://status.adaptive-study-planner.com/incidents   -d '{"status": "maintenance", "message": "Scheduled maintenance in progress"}'

# 3. Perform maintenance
# ...

# 4. Disable maintenance mode
wrangler kv put MAINTENANCE_MODE "false" --env production

# 5. Verify health
for i in {1..10}; do
  curl -s https://adaptive-study-planner.com/api/v3/health | grep "ok" && break
  sleep 5
done
```

---

## 9. Security Operations

### 9.1 IAM / RBAC
| Role | Permissions | Scope |
|------|-------------|-------|
| user | CRUD own documents, search own KB, generate flashcards/quizzes | Own data only |
| editor | user + edit shared topics, add comments | Group-shared data |
| admin | editor + manage group members, view group analytics | Group data |
| system | Read all data for processing, write logs/metrics | Internal |
| enterprise | admin + SSO, API access, custom branding | Tenant data |
| sre | Read metrics, restart services, trigger DR | Infrastructure |
| security_admin | Read audit logs, rotate secrets, manage RLS | Security |

### 9.2 Secrets Rotation Schedule
| Secret Type | Rotation Frequency | Owner | Method |
|-------------|-------------------|-------|--------|
| JWT signing keys | 180 days | Security Engineering | Key rotation API |
| Database passwords | 90 days | Database Engineering | Supabase Vault |
| API keys (OpenAI) | 90 days | AI Infrastructure | OpenAI dashboard |
| API keys (Google Vision) | 90 days | AI Infrastructure | Google Cloud Console |
| API keys (MathPix) | 90 days | AI Infrastructure | MathPix dashboard |
| OAuth client secrets | 90 days | Security Engineering | Provider dashboard |
| TLS certificates | 90 days | Platform Engineering | Let's Encrypt + Cloudflare |
| Telegram bot token | 180 days | SRE | BotFather |

### 9.3 Certificate Rotation
```bash
# 1. Check expiry
echo | openssl s_client -servername adaptive-study-planner.com -connect adaptive-study-planner.com:443 2>/dev/null | openssl x509 -noout -dates

# 2. Renew (Cloudflare auto-renews, but verify)
cloudflare cert show --zone adaptive-study-planner.com

# 3. If manual (Let's Encrypt):
certbot renew --force-renewal
wrangler secret put TLS_CERT --env production < /etc/letsencrypt/live/adaptive-study-planner.com/fullchain.pem
```

### 9.4 Vulnerability Management
- **Dependency scanning:** Daily (Dependabot + Snyk)
- **Container scanning:** Weekly (Trivy)
- **Runtime scanning:** Continuous (Sentry + Cloudflare WAF)
- **Patch SLA:**
  - Critical (CVSS 9.0+): 24 hours
  - High (CVSS 7.0-8.9): 7 days
  - Medium (CVSS 4.0-6.9): 30 days
  - Low (CVSS < 4.0): 90 days

### 9.5 Audit Logging
All security-relevant events are logged to an immutable WORM table:
| Event | Logged Fields | Retention |
|-------|--------------|-----------|
| Login | user_id, IP, timestamp, success/failure, MFA used | 7 years |
| API key usage | key_id, endpoint, timestamp, IP | 7 years |
| Data export | user_id, export_type, timestamp, size | 7 years |
| Data deletion | user_id, document_ids, timestamp, reason | 7 years |
| Admin action | admin_id, action, target, timestamp | 7 years |
| RLS policy change | admin_id, policy, timestamp | 7 years |
| Secret rotation | secret_type, timestamp, admin_id | 7 years |

---

## 10. AI Operations (AIOps)

### 10.1 Embedding Model Upgrades
```bash
# 1. Benchmark new model against current
python -m backend.benchmark.embedding --model BAAI/bge-m3 --dataset tests/data/benchmark.json

# 2. If benchmark > current + 5% improvement:
#    a. Deploy new model alongside old (dual-write)
#    b. Incremental re-embed changed chunks only
#    c. Monitor retrieval precision for 1 week
#    d. If stable, switch default model
#    e. Queue full re-embedding for old chunks (low priority)
```

### 10.2 LLM Upgrades
```bash
# 1. Test new model on staging
ollama pull llama3.3
supabase functions deploy --env staging

# 2. Run AI evaluation suite
pytest tests/ai_eval/ --model llama3.3

# 3. If MRR@10 > 0.6 and Precision@5 > 0.7:
#    a. Deploy to production (canary 5%)
#    b. Monitor for 3 days
#    c. Gradual rollout to 100%
```

### 10.3 Prompt Versioning
- All prompts stored in `backend/prompts/` with semantic versioning
- Prompt changes require:
  - AI evaluation suite pass
  - Human review (for grounding-critical prompts)
  - A/B test if user-facing output format changes
- Rollback: `git checkout prompts/v{version}`

### 10.4 Knowledge Base Refresh
- **Incremental refresh:** Only re-process changed documents (daily cron)
- **Full refresh:** Re-process all documents (quarterly, or on major model upgrade)
- **Monitoring:** Track "freshness" metric (avg age of embeddings)

### 10.5 Model Drift Detection
| Metric | Threshold | Action |
|--------|-----------|--------|
| Retrieval precision@5 drop | > 5% from baseline | Alert AI Infra, investigate model/embeddings |
| Hallucination rate | > 0% | P0 alert, halt AI responses, manual review |
| Citation accuracy | < 100% | P1 alert, investigate prompt/pipeline |
| Grounding score | < 95% | P1 alert, investigate retrieval quality |
| Embedding similarity drift | > 0.1 cosine shift | Alert AI Infra, re-evaluate model |

### 10.6 Cost Monitoring
| Service | Cost Driver | Budget | Alert |
|---------|------------|--------|-------|
| OpenAI API | Tokens / requests | $500/month | 80% of budget |
| Google Vision | Pages processed | $200/month | 80% of budget |
| MathPix | Formulas processed | $100/month | 80% of budget |
| Supabase | DB + storage + egress | $300/month | 80% of budget |
| Cloudflare Workers | Requests | $100/month | 80% of budget |
| R2 | Storage + egress | $50/month | 80% of budget |

---

## 11. Capacity Planning

### 11.1 Current Capacity (Baseline)
| Resource | Current | Capacity | Headroom |
|----------|---------|----------|----------|
| Active Users | 1,000 | 10,000 | 9,000 |
| Documents/hour | 100 | 1,000 | 900 |
| Chunks/tenant | 100,000 | 10,000,000 | 9,900,000 |
| Vector index size | 100MB | 10GB | 9.9GB |
| Knowledge graph edges | 10,000 | 1,000,000 | 990,000 |
| R2 storage | 50GB | 10TB | 9.95TB |

### 11.2 Scaling Triggers
| Metric | Trigger | Scale Action |
|--------|---------|--------------|
| Active users > 8,000 | Alert | Add read replica, review worker concurrency |
| Documents/hour > 800 | Alert | Increase Edge Function concurrency |
| Chunks/tenant > 8M | Alert | Migrate to HNSW index (from IVFFlat) |
| Vector index > 8GB | Alert | Evaluate pgvector partitioning |
| Graph edges > 800K | Alert | Evaluate ArangoDB migration |
| R2 storage > 8TB | Alert | Enable lifecycle policies, review compression |
| GPU util > 80% | Alert | Add GPU node |
| DB connections > 80 | Alert | Add PgBouncer instance |

### 11.3 Growth Projections
| Quarter | Users | Documents | Chunks | Action |
|---------|-------|-----------|--------|--------|
| Q3 2026 | 5,000 | 50K | 5M | Add read replica |
| Q4 2026 | 10,000 | 100K | 10M | Migrate to HNSW |
| Q1 2027 | 25,000 | 250K | 25M | Add GPU cluster |
| Q2 2027 | 50,000 | 500K | 50M | Evaluate ArangoDB |

---

## 12. Performance Operations

### 12.1 Latency Budgets
| Operation | p50 | p95 | p99 | Budget |
|-----------|-----|-----|-----|--------|
| API request | 50ms | 150ms | 300ms | 500ms |
| Document upload | 2s | 5s | 10s | 15s |
| OCR (per page) | 1s | 2s | 5s | 5s |
| Embedding (per batch) | 0.5s | 1s | 2s | 2s |
| Retrieval (hybrid) | 50ms | 150ms | 300ms | 200ms |
| AI response | 0.5s | 1.5s | 3s | 2s |
| Total Q&A | 1s | 2s | 4s | 5s |

### 12.2 Caching Strategy
| Cache | Technology | TTL | Size | Hit Rate Target |
|-------|------------|-----|------|-----------------|
| Query results | Redis | 1 hour | 1GB | 80% |
| Embeddings | Redis | 24 hours | 5GB | 90% |
| Document metadata | Redis | 1 hour | 500MB | 95% |
| AI responses | Redis | 30 min | 2GB | 70% |
| Static assets | Cloudflare CDN | 30 days | — | 99% |
| API responses | Cloudflare Workers | 5 min | 500MB | 85% |

### 12.3 Autoscaling Policies
| Service | Metric | Scale Up | Scale Down | Min | Max |
|---------|--------|----------|------------|-----|-----|
| Cloudflare Workers | RPS | +50% | -25% | 1 | Unlimited |
| vLLM GPU | GPU util | +1 node | -1 node | 1 | 10 |
| PostgreSQL | Connections | +1 replica | -1 replica | 1 | 5 |
| Redis | Memory | Upgrade plan | — | 1GB | 10GB |

---

## 13. Support Operations

### 13.1 On-Call Rotations
| Team | Primary | Secondary | Schedule | Handoff |
|------|---------|-----------|----------|---------|
| SRE | 1 engineer | 1 engineer | 1 week | Monday 09:00 UTC |
| AI Infrastructure | 1 engineer | 1 engineer | 1 week | Monday 09:00 UTC |
| Platform Engineering | 1 engineer | 1 engineer | 1 week | Monday 09:00 UTC |
| Database Engineering | 1 engineer | On-demand | 1 week | Monday 09:00 UTC |

### 13.2 Escalation Matrix
```
L1 Support (15 min)
  |
  +---> L2 Platform Engineering (1 hour)
          |
          +---> L3 SRE / AI Infra (15 min)
                  |
                  +---> L4 Engineering Lead (4 hours)
                          |
                          +---> CTO (if SEV-0)
```

### 13.3 Maintenance Windows
| Type | Frequency | Duration | Notification |
|------|-----------|----------|--------------|
| Scheduled maintenance | Monthly | 1 hour | 48 hours advance |
| Database maintenance | Quarterly | 2 hours | 1 week advance |
| Security patching | As needed | 30 min | 24 hours advance |
| Emergency maintenance | As needed | Variable | Immediate |

### 13.4 Known Issues
| Issue | Severity | Workaround | ETA Fix | Tracking |
|-------|----------|------------|---------|----------|
| Tesseract Hindi accuracy < 70% | SEV-3 | Use Google Vision (pro tier) | Q3 2026 | #BUG-142 |
| Graph traversal > 3 hops slow | SEV-3 | Limit to 3 hops | Q4 2026 | #BUG-143 |
| MathPix API intermittent 429s | SEV-3 | Retry + exponential backoff | Q2 2026 | #BUG-144 |
| Large ZIP uploads timeout | SEV-3 | Chunked upload | Q2 2026 | #BUG-145 |

---

## 14. Operational Checklists

### 14.1 Daily (SRE On-Call)
- [ ] Check Grafana dashboard (golden signals)
- [ ] Review PagerDuty alerts (acknowledge/resolve)
- [ ] Check error rates (Sentry)
- [ ] Verify backup completion (automated check)
- [ ] Check queue depths (Redis)
- [ ] Review AI grounding scores (dashboard)
- [ ] Check citation accuracy (dashboard)
- [ ] Review security logs (anomalies)
- [ ] Check cost dashboard (budget alerts)
- [ ] Update incident log (if any)

### 14.2 Weekly (Platform Team)
- [ ] Review deployment metrics (success rate, rollback count)
- [ ] Review performance metrics (latency trends)
- [ ] Check capacity utilization (CPU, GPU, RAM, storage)
- [ ] Review security scan results (new vulnerabilities)
- [ ] Update dependency versions (Dependabot PRs)
- [ ] Review on-call feedback (pain points)
- [ ] Conduct 15-min operational review meeting

### 14.3 Monthly (SRE Lead)
- [ ] Review SLO compliance (error budget status)
- [ ] Conduct postmortem review (all incidents from past month)
- [ ] Review DR test results
- [ ] Verify backup integrity (restore test on staging)
- [ ] Review access logs (RBAC compliance)
- [ ] Update runbooks (if procedures changed)
- [ ] Review cost trends and forecast
- [ ] Capacity planning review (growth projections)

### 14.4 Quarterly (Engineering Leadership)
- [ ] Full DR drill (RPO/RTO validation)
- [ ] Security audit (penetration test results)
- [ ] Compliance review (GDPR, SOC 2 readiness)
- [ ] Architecture review (scaling needs, tech debt)
- [ ] Team retrospective (operational improvements)
- [ ] Update disaster recovery procedures
- [ ] Review and rotate secrets (if not automated)
- [ ] Update incident response playbooks

### 14.5 Yearly (CTO + Leadership)
- [ ] Full business continuity review
- [ ] Insurance review (cyber liability, business interruption)
- [ ] Vendor review (contracts, SLAs, alternatives)
- [ ] Regulatory compliance audit (external)
- [ ] Strategic capacity planning (3-year forecast)
- [ ] Disaster recovery site validation
- [ ] Update all operational documentation

---

## 15. Production Readiness Checklist

Before every production release, verify:

### Security
- [ ] Security scan passed (0 critical/high)
- [ ] Secrets not hardcoded in code
- [ ] RBAC policies tested
- [ ] API rate limiting configured
- [ ] WAF rules updated (if needed)

### Performance
- [ ] Load test passed (200 concurrent users)
- [ ] Latency benchmarks within budget
- [ ] Memory usage acceptable
- [ ] No memory leaks (7-day soak test)

### Testing
- [ ] Unit tests ≥ 80% coverage
- [ ] Integration tests passed
- [ ] AI evaluation passed (MRR@10 > 0.6)
- [ ] E2E tests passed (100% critical flows)
- [ ] Regression tests passed

### Monitoring
- [ ] Metrics dashboards updated
- [ ] Alerts configured and tested
- [ ] Synthetic monitoring enabled
- [ ] Health checks verified

### Backups
- [ ] Database backup completed
- [ ] R2 cross-region sync verified
- [ ] Backup restore tested on staging

### Rollback
- [ ] Rollback plan documented
- [ ] Previous version artifacts available
- [ ] Feature flags configured for instant rollback
- [ ] Database migration is reversible

### Documentation
- [ ] API documentation updated
- [ ] Runbook updated (if new procedures)
- [ ] Known issues list updated
- [ ] Customer-facing changelog prepared

### Compliance
- [ ] Privacy impact assessment (if data handling changes)
- [ ] Audit trail requirements met
- [ ] Data retention policies respected
- [ ] Accessibility (WCAG 2.1 AA) verified

---

## 16. Appendices

### Appendix A: Operational Glossary
| Term | Definition |
|------|------------|
| SLO | Service Level Objective — internal reliability target |
| SLA | Service Level Agreement — customer-facing contractual guarantee |
| RPO | Recovery Point Objective — maximum acceptable data loss |
| RTO | Recovery Time Objective — maximum acceptable downtime |
| Error Budget | Allowed downtime within a period before release freeze |
| Canary Release | Gradual rollout to a subset of users |
| Blue-Green | Two identical environments, instant switch |
| WORM | Write Once Read Many — immutable storage |
| PgBouncer | PostgreSQL connection pooler |
| IVFFlat | Inverted File Flat — vector index type |
| HNSW | Hierarchical Navigable Small World — vector index type |
| RRF | Reciprocal Rank Fusion — result combination algorithm |
| AIOps | AI Operations — operational practices for AI systems |

### Appendix B: Command Reference
```bash
# Health check
curl https://adaptive-study-planner.com/api/v3/health

# Database status
psql -c "SELECT NOW(), pg_database_size('postgres'), pg_stat_activity.count FROM pg_stat_activity;"

# Redis status
redis-cli info memory

# R2 bucket size
aws s3 ls s3://adaptive-study-planner-documents --recursive --human-readable --summarize

# Worker queue depth
redis-cli LLEN document_processing_queue

# Embedding cache hit rate
redis-cli info stats | grep keyspace

# Recent errors
sentry-cli issues list --project adaptive-study-planner --status unresolved
```

### Appendix C: Runbook Templates
See `docs/runbooks/` directory for:
- `db-failover.md`
- `r2-outage.md`
- `llm-failover.md`
- `ddos-response.md`
- `security-incident.md`
- `telegram-recovery.md`
- `ocr-recovery.md`
- `embedding-rebuild.md`

### Appendix D: Incident Report Template
See Section 6.3 (Postmortem Template)

### Appendix E: Maintenance Checklist Template
See Section 14 (Operational Checklists)

---

*End of Operational Runbook*
