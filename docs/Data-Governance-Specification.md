# Data Governance Specification (DGS)

## AI Study Assistant — Phase 4.1.0 ENTERPRISE

**Version:** 1.0.0
**Date:** 2026-06-27
**Status:** Approved
**Owner:** Data Architecture & Compliance Team
**Authors:** Principal Data Architect, Principal Security Engineer, Compliance Architect, Principal AI Infrastructure Engineer

---

## Table of Contents

1. Data Governance Principles
2. Data Classification
3. Data Ownership
4. Data Lifecycle
5. Metadata Standards
6. AI Data Governance
7. Data Security
8. Privacy
9. Compliance
10. Retention Policy
11. Backup & Archival
12. Data Quality
13. Data Lineage
14. Audit Requirements
15. Governance Metrics
16. Risk Register
17. Future Roadmap

---

## 1. Data Governance Principles

### 1.1 Principles
| Principle | Description | Implementation |
|-----------|-------------|---------------|
| **Ownership** | Every dataset has a designated owner accountable for its quality, security, and compliance. | Documented in Section 3 |
| **Accountability** | Data stewards are responsible for day-to-day data management. | Assigned per dataset |
| **Transparency** | Users are informed about what data is collected, how it is used, and who can access it. | Privacy policy, in-app disclosures |
| **Privacy** | Data collection is minimized to what is strictly necessary for platform functionality. | Data minimization review per feature |
| **Security** | Data is protected at rest, in transit, and in use through encryption and access controls. | Section 7 |
| **Integrity** | Data is accurate, complete, and consistent throughout its lifecycle. | Section 12 |
| **Availability** | Data is accessible to authorized users when needed. | 99.9% SLA, backups, DR |
| **Compliance** | All data practices align with applicable regulations (GDPR, CCPA, DPDP, SOC 2). | Section 9 |
| **Least Privilege** | Users and systems can only access data required for their specific role. | RBAC, RLS |
| **Defense in Depth** | Multiple layers of security protect data at every stage. | Encryption + access control + audit |

---

## 2. Data Classification

### 2.1 Classification Levels
| Level | Definition | Handling Requirements | Examples |
|-------|------------|----------------------|----------|
| **Public** | Data intended for public consumption. No restrictions. | None | Marketing website, public API docs, open-source code |
| **Internal** | Data for internal use only. No sensitive information. | Access controlled to employees/contractors | Internal wikis, engineering docs, non-sensitive metrics |
| **Confidential** | Sensitive business or user data. Unauthorized disclosure could harm users or business. | Encryption at rest, access logging, need-to-know | User profiles, study plans, AI conversations, document metadata |
| **Restricted** | Highly sensitive data. Unauthorized disclosure could cause significant harm. | Encryption at rest + in transit, field-level encryption, strict RBAC, quarterly access reviews | Raw uploaded documents, OCR text, embeddings, knowledge graphs, API keys |
| **Highly Restricted** | Critical data. Unauthorized disclosure could be catastrophic. | All Restricted controls + dedicated key management, air-gapped backups, multi-party approval for access | Audit logs, WORM logs, secrets, encryption keys, payment data |

### 2.2 Dataset Classification Matrix
| Dataset | Classification | Rationale |
|---------|---------------|-----------|
| User Profiles (email, name, preferences) | Confidential | PII, privacy-regulated |
| Study Plans (topics, schedules, scores) | Confidential | User-generated, personal |
| AI Conversations (queries, responses) | Confidential | Personal learning data, may contain PII |
| Uploaded Notes / Textbooks / PDFs | Restricted | Raw content, may contain copyrighted material, personal notes |
| PYQs / Sample Papers | Restricted | Exam content, potential copyright |
| OCR Results | Restricted | Extracted text from personal documents |
| Embeddings (1024-dim vectors) | Restricted | Reversible to text with sufficient compute, privacy-sensitive |
| Knowledge Graph (concepts, edges) | Restricted | Derived from personal documents, reveals learning patterns |
| Metadata (document properties, tags) | Confidential | Business data, not highly sensitive |
| Application Logs | Internal | Operational data, may contain user IDs |
| Security Logs | Highly Restricted | Authentication events, access patterns, potential attack vectors |
| Audit Logs | Highly Restricted | Immutable record of all actions, compliance-critical |
| Analytics (aggregated, anonymized) | Internal | No PII, statistical use only |
| Telemetry (performance, errors) | Internal | Operational data, no PII |
| API Keys / Secrets | Highly Restricted | Credential material, catastrophic if leaked |
| Backups (all types) | Restricted | Complete copy of all data, highest protection |
| Telegram Cold Storage | Restricted | Third-party backup, requires verification |

---

## 3. Data Ownership

### 3.1 Ownership Matrix
| Dataset | Owner | Custodian | Consumers | Retention | Sensitivity | Encryption | Backup | Deletion |
|---------|-------|-----------|-----------|-----------|-------------|------------|--------|----------|
| User Profiles | Product | Database Engineering | Auth, Billing, Support | Account lifetime + 30 days | Confidential | AES-256 | Daily | 30 days after request |
| Study Plans | Product | Database Engineering | AI Pipeline, Frontend | Account lifetime + 30 days | Confidential | AES-256 | Daily | 30 days after request |
| Uploaded Documents | Product | Platform Engineering | AI Pipeline, Storage | Account lifetime + 30 days | Restricted | AES-256 + user key | Daily | 30 days after request |
| OCR Results | AI Infrastructure | AI Infrastructure | AI Pipeline, Retrieval | Account lifetime + 30 days | Restricted | AES-256 | Daily | 30 days after request |
| Embeddings | AI Infrastructure | AI Infrastructure | Retrieval Engine | Account lifetime + 30 days | Restricted | AES-256 | Daily | 30 days after request |
| Knowledge Graph | AI Infrastructure | Database Engineering | Retrieval Engine, Frontend | Account lifetime + 30 days | Restricted | AES-256 | Daily | 30 days after request |
| Application Logs | SRE | Platform Engineering | SRE, Security | 30 days hot, 1 year cold | Internal | AES-256 | Weekly | 1 year |
| Security Logs | Security Engineering | Security Engineering | Security, Compliance | 2 years | Highly Restricted | AES-256 + field-level | Daily | 7 years |
| Audit Logs | Compliance | Security Engineering | Compliance, Legal | 7 years | Highly Restricted | AES-256 + WORM | Daily | 7 years |
| API Keys | Security Engineering | Security Engineering | Services | Until revoked | Highly Restricted | AES-256 + HSM | Daily | Immediate on revocation |
| Backups | SRE | Platform Engineering | SRE | Per backup policy | Restricted | AES-256 | N/A (is backup) | 90 days after account deletion |

---

## 4. Data Lifecycle

### 4.1 Lifecycle Stages
```
Creation → Validation → Processing → Storage → Usage → Sharing → Archival → Deletion → Recovery
```

### 4.2 Per-Stage Governance
| Stage | Input | Process | Output | Retention | Owner |
|-------|-------|---------|--------|-----------|-------|
| **Creation** | User uploads document | File upload, metadata extraction | Document record + raw file | Immediate | User (upload), Platform (storage) |
| **Validation** | Raw file | Magic number check, virus scan, encoding detection | Validated file | Immediate | Validation Service |
| **Processing** | Validated file | OCR, parsing, extraction, chunking, embedding | Structured knowledge base | Until account deletion | AI Pipeline |
| **Storage** | Processed data | PostgreSQL, pgvector, R2, Redis | Persisted data | Per retention policy | Platform Engineering |
| **Usage** | Stored data | Search, Q&A, flashcards, quizzes | AI responses | Ephemeral (cached 30 min) | AI Pipeline |
| **Sharing** | User data | Topic sharing, group collaboration | Shared data with permissions | Until revoked | User |
| **Archival** | Account deleted data | Backup to cold storage, WORM logs | Archived data | 90 days | SRE |
| **Deletion** | Deletion request | Cascade delete, cache purge, backup purge | No data | Permanent | User (request), Platform (execution) |
| **Recovery** | Backup data | Restore from R2/Telegram, re-index | Recovered data | Until restored | SRE (admin only) |

---

## 5. Metadata Standards

### 5.1 Required Metadata (per document)
| Field | Type | Source | Description | Example |
|-------|------|--------|-------------|---------|
| `document_id` | UUID | System | Unique identifier | `550e8400-e29b-41d4-a716-446655440000` |
| `owner_id` | UUID | Auth | User who uploaded | `user_123` |
| `version` | Integer | System | Document version | `1` |
| `source_type` | Enum | Auto-detected | Origin classification | `user_upload`, `official_exam`, `ncert` |
| `source_confidence` | Float | Auto-detected | Trust score (0-1) | `0.95` |
| `language` | ISO 639-1 | Auto-detected | Document language | `en`, `hi`, `es` |
| `encoding` | String | Auto-detected | Text encoding | `utf-8` |
| `mime_type` | String | Auto-detected | File format | `application/pdf` |
| `sha256` | Hex | System | Content hash | `a1b2c3d4...` |
| `phash` | Hex | System | Perceptual hash (images) | `e5f6g7h8...` |
| `processing_status` | Enum | Pipeline | Current stage | `uploaded`, `ready`, `error` |
| `ocr_engine` | String | Pipeline | OCR engine used | `tesseract`, `google_vision` |
| `ocr_confidence` | Float | Pipeline | Average OCR accuracy | `0.87` |
| `embedding_model` | String | Pipeline | Model version | `BAAI/bge-large-en-v1.5` |
| `embedding_version` | String | Pipeline | Model version tag | `v1.0.0` |
| `chunks_count` | Integer | Pipeline | Number of chunks | `45` |
| `concepts_count` | Integer | Pipeline | Extracted concepts | `12` |
| `formulas_count` | Integer | Pipeline | Extracted formulas | `8` |
| `questions_count` | Integer | Pipeline | Extracted questions | `20` |
| `retention_class` | Enum | Policy | Data retention category | `standard`, `extended`, `compliance` |
| `created_at` | ISO 8601 | System | Upload timestamp | `2026-06-27T10:00:00Z` |
| `updated_at` | ISO 8601 | System | Last modification | `2026-06-27T12:00:00Z` |
| `deleted_at` | ISO 8601 | System | Soft deletion timestamp | `null` |

### 5.2 Metadata Validation
- All metadata fields are validated on insertion
- `source_confidence` must be in [0, 1]
- `language` must be valid ISO 639-1 code
- `sha256` must be 64-character hex
- `processing_status` must be from allowed enum
- `retention_class` determines deletion schedule

---

## 6. AI Data Governance

### 6.1 Data Categories
| Category | Definition | Sensitivity | Governance |
|----------|------------|-------------|------------|
| **Training Data** | Data used to train or fine-tune AI models | Highly Restricted | Explicit opt-in required, anonymized, no raw documents |
| **Inference Data** | User queries and context sent to LLM for response generation | Confidential | No training without opt-in, 30-day retention |
| **Prompt Data** | System prompts, templates, and instructions | Internal | Versioned, access-controlled, no PII in prompts |
| **Conversation Data** | User-AI interaction history | Confidential | User owns data, exportable, deletable |
| **Grounding Data** | Retrieved chunks used to ground AI responses | Restricted | Must be cited, traceable, verifiable |
| **Citation Data** | Citation markers, source references, confidence scores | Restricted | Immutable, auditable, linked to chunks |
| **Evaluation Data** | Benchmark datasets for AI quality measurement | Internal | Anonymized, synthetic where possible |
| **Hallucination Logs** | Records of AI responses with unsupported claims | Confidential | Used for model improvement, anonymized |
| **Retrieval Logs** | Query → retrieval → ranking → selection records | Internal | 30-day retention, used for improving retrieval |
| **Knowledge Graph Updates** | Changes to concept relationships and prerequisites | Restricted | Versioned, reversible, auditable |
| **Embedding Refresh** | Re-embedding events (model upgrades, corrections) | Restricted | Logged, reversible, versioned |
| **Model Lineage** | Model versions, training runs, deployment history | Internal | Immutable, traceable for compliance |

### 6.2 AI Data Policies
- **No training on user data without explicit opt-in:** Default is "no training."
- **Inference data is ephemeral:** Queries and responses are cached for 30 minutes, then purged.
- **Conversation history is user-owned:** Users can export or delete at any time.
- **Grounding data is mandatory:** Every AI response must cite specific chunks from the user's knowledge base.
- **Hallucination logging is opt-in:** Users can choose to share hallucination data for model improvement.
- **Model lineage is immutable:** All model versions, prompts, and parameters are logged permanently.

---

## 7. Data Security

### 7.1 Encryption at Rest
| Layer | Technology | Key Management | Rotation |
|-------|------------|---------------|----------|
| PostgreSQL | AES-256-GCM | Cloud KMS (Supabase-managed) | Automatic |
| R2 Objects | AES-256 | Cloudflare-managed | Automatic |
| Redis | AES-256 | Upstash-managed | Automatic |
| Field-level PII | AES-256-GCM | User-specific keys (envelope encryption) | 90 days |
| Document Content | AES-256-GCM | User-specific keys (zero-knowledge) | 90 days |
| Backups | AES-256-GCM | Separate backup key | 90 days |
| WORM Audit Logs | AES-256-GCM | HSM-backed key | 180 days |

### 7.2 Encryption in Transit
- TLS 1.3 for all API endpoints
- Certificate pinning for mobile clients
- HSTS headers (max-age=31536000, includeSubDomains)
- mTLS for service-to-service communication (where applicable)

### 7.3 Key Management
| Key Type | Storage | Access | Rotation | Recovery |
|----------|---------|--------|----------|----------|
| Database encryption key | Cloud KMS | Database Engineering | Auto (90 days) | Cloud KMS backup |
| User content keys | Supabase Vault | User (via auth) | 90 days (on request) | Account recovery flow |
| API keys | HashiCorp Vault | Security Engineering | 90 days | Vault backup |
| JWT signing keys | Supabase Auth | Security Engineering | 180 days | Auth system backup |
| Backup keys | HSM (air-gapped) | SRE Lead + Security Lead | 180 days | Shamir's Secret Sharing (3 of 5) |

### 7.4 Access Control
- **Row-Level Security (RLS):** All tables have RLS policies enforced
- **Column-Level Security:** PII columns encrypted with user-specific keys
- **Role-Based Access Control (RBAC):** User, Editor, Admin, System, Enterprise roles
- **Attribute-Based Access Control (ABAC):** Group membership, document ownership, sharing permissions
- **Just-in-Time (JIT) Access:** Admin access requires approval + time-bound session
- **Access Reviews:** Quarterly review of all admin and system access

### 7.5 Database Auditing
- All DDL operations logged (CREATE, ALTER, DROP)
- All DML operations on sensitive tables logged (INSERT, UPDATE, DELETE on documents, chunks, users)
- Query logs retained for 30 days (hot), 1 year (cold)
- Audit trail is immutable (WORM storage)

### 7.6 Object Storage Policies
- R2 bucket policies: CORS restricted to `https://adaptive-study-planner.com`
- Presigned URLs: 5-minute expiry
- Lifecycle: Delete 30 days after account deletion
- Cross-region replication: Enabled for production bucket
- Versioning: Enabled (keep last 3 versions)
- MFA delete: Enabled for production bucket

### 7.7 Vector Security
- Embeddings are stored in the same database as metadata (no separate vector store)
- RLS policies apply to vector queries (users can only search their own embeddings)
- Vector index queries are logged (query embedding, results, timestamp)
- No reverse-engineering of embeddings to raw text (theoretically possible but computationally infeasible at 1024 dimensions)

### 7.8 Knowledge Graph Security
- Graph edges are user-scoped (no cross-tenant traversal)
- Prerequisite chains are private to the user who owns the documents
- Graph visualization data is filtered by RLS before sending to frontend
- Graph export requires user authentication and authorization

---

## 8. Privacy

### 8.1 Consent Management
- **Explicit opt-in for AI training:** Users must actively consent to using their data for model training. Default is "no."
- **Granular consent for data sharing:** Users can choose to share specific topics/documents with study groups. Default is "none."
- **Cookie consent:** Non-essential cookies (analytics, tracking) require explicit consent. Essential cookies (auth, security) are functional.
- **Consent revocation:** Users can revoke consent at any time. Data used for training is purged within 30 days.

### 8.2 User Rights (GDPR / CCPA / DPDP)
| Right | Implementation | SLA |
|-------|---------------|-----|
| **Right to Access** | Export all data as JSON (complete knowledge base) | 30 days |
| **Right to Rectification** | Edit profile, topic names, document metadata | Immediate |
| **Right to Erasure** | Delete account + all data | 30 days |
| **Right to Restriction** | Pause processing, retain data only | Immediate |
| **Right to Portability** | Export in machine-readable JSON | 30 days |
| **Right to Object** | Opt-out of analytics, training, marketing | Immediate |
| **Right to Explanation** | Show AI reasoning, citations, confidence | Per response |

### 8.3 Data Export Procedure
```bash
# 1. User requests export via UI or API
# 2. System generates JSON export:
{
  "user_id": "...",
  "export_date": "2026-06-27T10:00:00Z",
  "documents": [...],
  "chunks": [...],
  "concepts": [...],
  "formulas": [...],
  "questions": [...],
  "knowledge_graph": { "nodes": [...], "edges": [...] },
  "study_plans": [...],
  "ai_conversations": [...]
}
# 3. Export is encrypted with user's public key
# 4. Download link emailed (expires in 7 days)
# 5. Export event logged in audit trail
```

### 8.4 Account Deletion Procedure
```sql
-- 1. User initiates deletion (30-day grace period)
UPDATE users SET deletion_requested_at = NOW() WHERE id = 'user_id';

-- 2. After 30 days, cascade delete:
DELETE FROM chunks WHERE user_id = 'user_id';
DELETE FROM concepts WHERE user_id = 'user_id';
DELETE FROM formulas WHERE user_id = 'user_id';
DELETE FROM questions WHERE user_id = 'user_id';
DELETE FROM knowledge_edges WHERE user_id = 'user_id';
DELETE FROM ocr_results WHERE document_id IN (SELECT id FROM documents WHERE user_id = 'user_id');
DELETE FROM documents WHERE user_id = 'user_id';
DELETE FROM ai_queries WHERE user_id = 'user_id';
DELETE FROM users WHERE id = 'user_id';

-- 3. R2 objects deleted (async, within 7 days)
-- 4. Backups purged (within 90 days)
-- 5. Audit log entry retained (7 years, anonymized user_id)
```

### 8.5 Data Minimization
- Only collect data necessary for platform functionality
- No browsing history tracking outside platform
- No third-party analytics without consent
- No sale of user data to third parties (ever)
- Anonymous analytics only (no PII in logs)

---

## 9. Compliance

### 9.1 Regulatory Mapping
| Regulation | Requirement | Status | Evidence |
|------------|------------|--------|----------|
| **GDPR** | Data protection, user rights, breach notification | Implemented | Privacy policy, consent management, data export, erasure |
| **CCPA** | Consumer rights, opt-out, disclosure | Implemented | Privacy policy, opt-out mechanisms, data portability |
| **India DPDP Act** | Consent, data fiduciaries, grievance redressal | Implemented | Consent framework, grievance officer, data localization option |
| **SOC 2 Type II** | Security, availability, processing integrity, confidentiality | In Progress | Target: 12 months from launch. Controls documented, audit scheduled |
| **ISO/IEC 27001** | Information security management | Roadmap | Target: 18 months from launch |
| **WCAG 2.1 AA** | Accessibility | Implemented | Frontend audits, keyboard navigation, screen reader support |
| **COPPA** | Children's privacy | Implemented | Parental consent for <16, minimal data collection |
| **FERPA** (if US education) | Educational records | Roadmap | Target: 24 months from launch |

### 9.2 Compliance Controls (SOC 2 Type II — In Progress)
| Control | Implementation | Evidence |
|---------|---------------|----------|
| Access Control | RBAC + RLS + MFA | Access logs, quarterly reviews |
| Change Management | GitHub PR + CI/CD + approval gates | Git history, deployment logs |
| Backup & Recovery | Daily backups, DR drills, RPO/RTO | Backup logs, DR test reports |
| Incident Response | Incident response plan, postmortems | Incident logs, postmortem docs |
| Monitoring | Grafana, Sentry, PagerDuty | Dashboards, alert history |
| Encryption | AES-256 at rest, TLS 1.3 in transit | Key management logs, certificate audits |
| Vendor Management | Cloudflare, Supabase, OpenAI contracts | SLAs, security assessments |

### 9.3 Data Residency
- User-selectable region: US, EU, India, Singapore
- All data stored and processed in selected region only
- No cross-border data transfer without explicit consent
- GDPR Article 44 compliance for international transfers (SCCs in place)

---

## 10. Retention Policy

### 10.1 Retention Schedule
| Data Category | Retention Period | Trigger | Action After Retention |
|---------------|-----------------|---------|----------------------|
| User Profiles | Account lifetime + 30 days | Account deletion | Cascade delete |
| Study Plans | Account lifetime + 30 days | Account deletion | Cascade delete |
| Uploaded Documents | Account lifetime + 30 days | Account deletion | Delete from R2 |
| OCR Results | Account lifetime + 30 days | Account deletion | Cascade delete |
| Embeddings | Account lifetime + 30 days | Account deletion | Cascade delete |
| Knowledge Graph | Account lifetime + 30 days | Account deletion | Cascade delete |
| AI Conversations | Account lifetime + 30 days | Account deletion | Cascade delete |
| Application Logs | 30 days hot, 1 year cold | Time-based | Archive to S3 Glacier |
| Security Logs | 2 years | Time-based | Archive to WORM storage |
| Audit Logs | 7 years | Time-based | Immutable WORM storage |
| Analytics (aggregated) | 2 years | Time-based | Anonymize after 1 year |
| Telemetry | 30 days hot, 1 year cold | Time-based | Archive to S3 Glacier |
| Backups (full) | 7 days | Time-based | Delete after 7 days |
| Backups (WAL) | 7 days | Time-based | Delete after 7 days |
| Cross-region backups | 30 days | Time-based | Delete after 30 days |
| Telegram backups | Unlimited | Account deletion | Admin manual deletion |
| API Keys | Until revoked | Revocation | Immediate deletion |
| Deleted Account Data | 30 days (grace period) | Deletion request | Permanent purge |

### 10.2 Retention Enforcement
- Automated cron jobs purge expired data daily
- Soft deletion (30-day grace) before permanent deletion
- User can request immediate deletion (bypasses grace period)
- Backup purging: 90 days after account deletion (to ensure recovery window)
- Audit log retention: Immutable, cannot be deleted even by admins

---

## 11. Backup & Archival

### 11.1 Backup Schedule
| Type | Frequency | Retention | Storage | Encryption | Validation |
|------|-----------|-----------|---------|----------|------------|
| PostgreSQL Full | Daily | 7 days | R2 cross-region | AES-256 | Monthly restore test |
| PostgreSQL WAL | Continuous | 7 days | Same region | AES-256 | Automated |
| R2 Documents | Real-time replication | 30 days | Cross-region R2 | AES-256 | Quarterly integrity check |
| Redis | Daily | 7 days | R2 | AES-256 | Monthly restore test |
| Configuration | On change | 1 year | GitHub | N/A | N/A |
| Audit Logs | Real-time | 7 years | WORM storage | AES-256 + HSM | Annual integrity audit |

### 11.2 Immutable Backups (WORM)
- Audit logs: Write Once Read Many (WORM) storage
- Cannot be modified or deleted by any user, including admins
- Retention lock: Cannot be shortened until retention period expires
- Geographic redundancy: Stored in 2+ regions

### 11.3 Cold Storage (Telegram)
- **Purpose:** Optional off-site backup for raw documents
- **Process:** After document processing, optionally upload to Telegram
- **Retention:** Unlimited (Telegram's policy)
- **Recovery:** Manual admin process (see Operational Runbook)
- **Limitations:** 2GB file limit, no SLA, no search, manual recovery only

### 11.4 Recovery Validation
- **Monthly:** Automated restore test on staging (PostgreSQL + R2)
- **Quarterly:** Full DR drill (manual, all systems)
- **Validation criteria:**
  - All documents accessible and uncorrupted
  - All embeddings searchable with correct similarity
  - All knowledge graph edges intact
  - AI responses correctly grounded
  - Citation verification passes

---

## 12. Data Quality

### 12.1 Quality Dimensions
| Dimension | Definition | Metric | Target | Monitoring |
|-----------|------------|--------|--------|------------|
| **Completeness** | All expected data is present | % of documents with all metadata fields | 100% | Daily |
| **Accuracy** | Data correctly represents reality | OCR accuracy (WER) | < 15% printed | Weekly |
| **Consistency** | Data is consistent across systems | % of chunks with matching embeddings and metadata | 100% | Daily |
| **Freshness** | Data is up-to-date | Avg age of embeddings | < 30 days | Daily |
| **Uniqueness** | No duplicate data | % duplicate documents detected | < 1% | Daily |
| **Validity** | Data conforms to defined formats | % of documents passing validation | > 99% | Per upload |

### 12.2 Quality Monitoring
| Check | Frequency | Owner | Action on Failure |
|-------|-----------|-------|-------------------|
| OCR accuracy sample | Weekly | AI Infrastructure | Alert if < 85%, investigate engine |
| Embedding validation | Daily | AI Infrastructure | Re-embed invalid chunks |
| Chunk consistency | Daily | AI Infrastructure | Reprocess corrupted documents |
| Graph integrity | Weekly | Database Engineering | Fix orphaned edges, detect cycles |
| Duplicate detection | Daily | Platform Engineering | Merge or flag duplicates |
| Metadata completeness | Daily | Platform Engineering | Backfill missing metadata |
| Citation accuracy | Per response | AI Infrastructure | Flag unverified citations |
| Grounding score | Per response | AI Infrastructure | Alert if < 100% |

### 12.3 Quality KPIs
| KPI | Target | Measurement |
|-----|--------|-------------|
| Document processing success rate | > 99.5% | Daily |
| OCR accuracy (printed) | > 85% | Weekly sample |
| OCR accuracy (handwritten) | > 70% | Weekly sample |
| Retrieval precision@5 | > 80% | Weekly benchmark |
| Citation verification accuracy | 100% | Per response |
| Grounding score | 100% | Per response |
| Hallucination rate | 0% | Weekly AI evaluation |
| Data completeness | 100% | Daily |
| Duplicate rate | < 1% | Daily |

---

## 13. Data Lineage

### 13.1 Complete Lineage Diagram
```
User Upload
  |
  +---> Upload Service (validation, duplicate detection)
  |     |
  |     +---> R2 Object Storage (raw file: users/{uid}/docs/{id}/original.pdf)
  |     |
  |     +---> PostgreSQL (document metadata: status="uploaded")
  |
  +---> Validation Service (magic numbers, virus scan, encoding, language)
  |     |
  |     +---> PostgreSQL (document metadata: status="validating")
  |     |
  |     +---> If invalid → Dead Letter Queue (manual review)
  |
  +---> OCR Service (if scanned/image)
  |     |
  |     +---> Tesseract (primary) or Google Vision (handwriting) or MathPix (formulas)
  |     |
  |     +---> PostgreSQL (ocr_results: text, confidence, engine, page)
  |     |
  |     +---> If low confidence (< 60%) → Flag for manual review
  |
  +---> Document Processing Service (Docling parsing)
  |     |
  |     +---> Structured Markdown (headings, tables, formulas, images)
  |     |
  |     +---> Text Cleaning (headers, footers, watermarks removed)
  |     |
  |     +---> PostgreSQL (document metadata: status="extracting")
  |
  +---> Knowledge Extraction Service (LLM-based)
  |     |
  |     +---> Concepts (name, definition, confidence)
  |     +---> Formulas (LaTeX, context, confidence)
  |     +---> Questions (type, question, answer, options)
  |     +---> Prerequisites (topic dependency chains)
  |     +---> Difficulty (formula density, language complexity)
  |     |
  |     +---> PostgreSQL (concepts, formulas, questions tables)
  |
  +---> Semantic Chunking Service (heading-aware)
  |     |
  |     +---> Chunks (300-800 tokens, 80 overlap, metadata preserved)
  |     |
  |     +---> PostgreSQL (chunks table)
  |
  +---> Embedding Service (BAAI/BGE or OpenAI)
  |     |
  |     +---> Vectors (1024-dim, L2 normalized, batch 32)
  |     |
  |     +---> PostgreSQL pgvector (embedding column)
  |     |
  |     +---> Redis Cache (SHA-256 key, 24h TTL)
  |
  +---> Knowledge Graph Service
  |     |
  |     +---> Nodes (concepts, formulas, topics)
  |     +---> Edges (prerequisite, related, part-of)
  |     |
  |     +---> PostgreSQL (knowledge_edges table)
  |
  +---> Indexing (PostgreSQL)
  |     |
  |     +---> Vector Index (pgvector IVFFlat / HNSW)
  |     +---> Full-Text Index (GIN tsvector)
  |     +---> Metadata Index (B-tree)
  |     |
  |     +---> PostgreSQL (document metadata: status="ready")
  |
  +---> User Query
  |     |
  |     +---> Hybrid Retrieval Engine
  |     |     |
  |     |     +---> Intent Detection (query classification)
  |     |     +---> Dense Retrieval (pgvector similarity)
  |     |     +---> Sparse Retrieval (BM25 tsvector)
  |     |     +---> Metadata Filtering (SQL WHERE)
  |     |     +---> Graph Traversal (prerequisite chains)
  |     |     +---> Re-ranking (BAAI/bge-reranker)
  |     |     +---> RRF Fusion (final ranking)
  |     |     |
  |     |     +---> Top 5 chunks with citations
  |     |
  |     +---> LLM (Ollama / vLLM / OpenAI)
  |     |     |
  |     |     +---> Strict grounding prompt (temperature 0.3)
  |     |     +---> Citation markers [1], [2] in output
  |     |     |
  |     |     +---> AI Response (answer + citations)
  |     |
  |     +---> Citation Service
  |     |     |
  |     |     +---> Extract [1], [2] from response
  |     |     +---> Verify against retrieved chunks
  |     |     +---> Flag invented citations
  |     |     +---> Evidence trace (claim → chunk → document → page)
  |     |     |
  |     |     +---> PostgreSQL (ai_queries: query, response, citations, grounding_score)
  |     |
  |     +---> Final Response to User
  |           (answer + verified citations + confidence scores + evidence trace)
```

### 13.2 Lineage Tracking
Every data transformation is logged with:
- Source dataset ID
- Transformation name
- Transformation version
- Timestamp
- Operator (service or user)
- Output dataset ID
- Validation status

---

## 14. Audit Requirements

### 14.1 Audit Events
| Event | Logged Data | Retention | Immutable |
|-------|------------|-----------|-----------|
| User login | user_id, IP, timestamp, success, MFA used | 7 years | Yes |
| User logout | user_id, timestamp, IP | 7 years | Yes |
| Document upload | user_id, document_id, filename, size, timestamp | 7 years | Yes |
| Document delete | user_id, document_id, timestamp, reason | 7 years | Yes |
| Document reprocess | user_id, document_id, timestamp | 7 years | Yes |
| AI query | user_id, query_hash, retrieval_time, generation_time, grounding_score | 2 years | Yes |
| AI response | user_id, response_hash, citation_count, grounding_score | 2 years | Yes |
| Data export | user_id, export_type, size, timestamp | 7 years | Yes |
| Data share | user_id, shared_with, topic_id, permission, timestamp | 7 years | Yes |
| Admin action | admin_id, action, target, timestamp, reason | 7 years | Yes |
| RLS policy change | admin_id, policy, old_value, new_value, timestamp | 7 years | Yes |
| Secret rotation | secret_type, timestamp, admin_id | 7 years | Yes |
| Model deployment | model_name, version, timestamp, deployer | 2 years | Yes |
| Feature flag change | flag_name, old_value, new_value, timestamp, changer | 2 years | Yes |

### 14.2 Audit Log Schema
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    user_id UUID,
    actor_type TEXT NOT NULL CHECK (actor_type IN ('user', 'admin', 'system', 'service')),
    target_type TEXT NOT NULL, -- document, user, policy, etc.
    target_id TEXT,
    action TEXT NOT NULL, -- create, read, update, delete, share, export
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    correlation_id TEXT
);
```

### 14.3 Audit Log Protection
- **WORM (Write Once Read Many):** Audit logs cannot be modified or deleted
- **Append-only:** Only INSERT operations allowed (no UPDATE, no DELETE)
- **Row-level security:** Even admins cannot read other users' audit logs without explicit permission
- **Encryption:** AES-256 at rest, field-level encryption for sensitive details
- **Replication:** Real-time replication to separate audit database (cross-region)
- **Access:** Audit logs are readable only by Compliance and Security teams (with JIT approval)

---

## 15. Governance Metrics

### 15.1 KPIs
| KPI | Target | Measurement | Owner |
|-----|--------|-------------|-------|
| Storage Growth | < 50% QoQ | R2 + PostgreSQL size | Platform Engineering |
| Embedding Growth | < 50% QoQ | pgvector table size | AI Infrastructure |
| Knowledge Coverage | > 90% of docs have concepts | Concepts per document | AI Infrastructure |
| Duplicate Rate | < 1% | Duplicate detection hits | Platform Engineering |
| OCR Accuracy (printed) | > 85% | Weekly sample | AI Infrastructure |
| OCR Accuracy (handwritten) | > 70% | Weekly sample | AI Infrastructure |
| Retrieval Precision@5 | > 80% | Weekly benchmark | AI Infrastructure |
| Citation Accuracy | 100% | Per-response verification | AI Infrastructure |
| Grounding Score | 100% | Per-response verification | AI Infrastructure |
| Deletion SLA | 100% within 30 days | Account deletion tracking | Platform Engineering |
| Backup Success Rate | 100% | Daily backup validation | SRE |
| Recovery Success Rate | 100% | Monthly DR test | SRE |
| Audit Completeness | 100% | Missing audit events | Security Engineering |
| Data Quality Score | > 98% | Completeness + accuracy + consistency | Data Architecture |

### 15.2 Reporting
| Report | Frequency | Audience | Content |
|--------|-----------|----------|---------|
| Data Quality Dashboard | Real-time | AI Infra, Data Architecture | Quality KPIs, trends, alerts |
| Storage & Growth Report | Weekly | Platform Engineering, Finance | Storage usage, cost, growth projections |
| Privacy Compliance Report | Monthly | Compliance, Legal | Consent status, erasure requests, data exports |
| Security Audit Report | Monthly | Security Engineering | Access reviews, vulnerabilities, incidents |
| AI Governance Report | Monthly | AI Infrastructure | Model drift, hallucination rate, grounding scores |
| Backup & DR Report | Monthly | SRE | Backup success, DR test results, RPO/RTO compliance |
| Comprehensive Governance Report | Quarterly | CTO, Board | All KPIs, risk register, roadmap |

---

## 16. Risk Register

| Risk | Probability | Impact | Mitigation | Owner | Residual Risk |
|------|------------|--------|------------|-------|---------------|
| Data breach (unauthorized access) | Low | Critical | Encryption, RBAC, RLS, MFA, audit logs | Security Engineering | Low |
| Data loss (storage failure) | Low | Critical | Cross-region replication, daily backups, DR tests | SRE | Low |
| Data corruption (processing error) | Medium | High | Validation, checksums, integrity checks, reprocessing | AI Infrastructure | Medium |
| Regulatory non-compliance (GDPR/CCPA/DPDP) | Medium | Critical | Privacy by design, consent management, data portability, audit trails | Compliance | Low |
| AI bias / unfair treatment | Medium | High | Diverse training data, fairness metrics, human oversight | AI Infrastructure | Medium |
| Model drift (degrading quality) | Medium | Medium | Continuous evaluation, drift detection, retraining pipeline | AI Infrastructure | Low |
| Hallucination (incorrect AI answers) | Low | High | Strict grounding, citation verification, "I don't know" policy | AI Infrastructure | Low |
| Insider threat (malicious admin) | Low | Critical | Least privilege, JIT access, audit logs, anomaly detection | Security Engineering | Low |
| Third-party dependency (Cloudflare/Supabase/OpenAI) | Medium | Medium | Multi-cloud fallback, S3 backup, Ollama default | Platform Engineering | Low |
| Data residency violation | Low | Critical | Region selection, data localization, no cross-border transfer | Compliance | Low |
| Telegram backup compromise | Low | Medium | Encryption before upload, optional only, not primary | SRE | Low |
| Audit log tampering | Low | Critical | WORM storage, immutable, append-only, HSM keys | Security Engineering | Low |
| User data deletion failure | Low | High | Cascade delete, verification, 30-day grace, audit trail | Platform Engineering | Low |
| Embedding reverse-engineering | Very Low | Medium | 1024-dim vectors, no raw text in embeddings, legal protections | AI Infrastructure | Low |

---

## 17. Future Roadmap

### 17.1 Q3 2026 (Phase 4.1)
- [ ] Implement field-level encryption for PII columns
- [ ] Deploy automated data quality monitoring dashboard
- [ ] Complete SOC 2 Type II readiness assessment
- [ ] Implement data lineage visualization (frontend)
- [ ] Deploy automated retention policy enforcement

### 17.2 Q4 2026 (Phase 4.2)
- [ ] Achieve SOC 2 Type II certification
- [ ] Implement AI fairness metrics and bias detection
- [ ] Deploy data anonymization pipeline for analytics
- [ ] Implement automated data classification (ML-based)
- [ ] Complete ISO/IEC 27001 readiness assessment

### 17.3 Q1 2027 (Phase 4.3)
- [ ] Achieve ISO/IEC 27001 certification
- [ ] Implement differential privacy for analytics queries
- [ ] Deploy synthetic data generation for testing
- [ ] Implement blockchain-based audit log verification (optional)
- [ ] Complete FERPA readiness (if US education market)

### 17.4 Q2 2027 (Phase 4.4)
- [ ] Implement federated learning for model improvement (no raw data sharing)
- [ ] Deploy automated data governance policy enforcement
- [ ] Implement real-time data quality scoring
- [ ] Complete GDPR Article 35 (DPIA) automation
- [ ] Achieve educational privacy certifications (FERPA, COPPA)

---

## Appendices

### Appendix A: Data Governance Glossary
| Term | Definition |
|------|------------|
| WORM | Write Once Read Many — immutable storage |
| RLS | Row-Level Security — database-level access control |
| RBAC | Role-Based Access Control |
| ABAC | Attribute-Based Access Control |
| JIT | Just-in-Time — temporary access granted for specific need |
| PII | Personally Identifiable Information |
| DPDP | Digital Personal Data Protection (India) |
| SCC | Standard Contractual Clauses (GDPR) |
| DPIA | Data Protection Impact Assessment |
| Differential Privacy | Mathematical technique to prevent identification in aggregated data |

### Appendix B: Cross-Document References
| Section | PRD | ES | ADR | ADS | TS | ORB |
|---------|-----|-----|-----|-----|-----|-----|
| Data Classification | 6. NFR | 8 | — | E-014 | 8 | 9 |
| Encryption | 6. NFR | 8 | ADR-010 | E-014 | 8 | 9 |
| Retention | 6. NFR | 8 | — | E-014 | 8 | 10 |
| Backup | 6. NFR | 13 | ADR-014 | E-014 | 9 | 7 |
| Audit | 6. NFR | 8 | — | E-026 | 8 | 14 |
| Privacy | 6. NFR | 8 | — | — | 8 | 8 |
| Compliance | 6. NFR | 8 | — | — | 8 | 9 |
| Data Lineage | 4. FR | 7 | — | E-019 | 8 | 13 |
| AI Governance | 4. FR | 2.10 | ADR-018 | E-024 | 8 | 10 |

---

*End of Data Governance Specification*
