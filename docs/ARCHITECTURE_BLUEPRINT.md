# Phase 4 Enterprise Architecture Blueprint
# Adaptive Study Planner — Universal Knowledge Ingestion & AI Knowledge Layer
# Version: 4.1.0-ENTERPRISE
# Date: 2026-06-27
# Status: Master Blueprint for Documentation Upgrade

---

## 1. Unified Terminology Glossary

| Term | Definition | Used In |
|------|------------|---------|
| **Universal Knowledge Ingestion** | The platform capability to accept, parse, and index any educational document into a structured knowledge base | PRD, ES, ADR, ADS, TS |
| **AI Knowledge Layer** | The semantic layer that connects extracted concepts, relationships, and embeddings to enable grounded AI responses | PRD, ES, ADR, ADS, TS |
| **Mode A — User Knowledge** | Student uploads their own documents (notes, textbooks, PDFs, etc.) | PRD, ES, ADS |
| **Mode B — Automatic Knowledge Collection** | System discovers and ingests official resources when student has no uploads | PRD, ES, ADS |
| **Trusted Source Hierarchy** | 10-tier confidence ranking for document sources (Government → Community) | PRD, ADR, TS |
| **Hybrid Retrieval** | Combines dense (vector), sparse (keyword), metadata, and graph traversal | PRD, ES, ADR, ADS, TS |
| **Semantic Chunking** | Heading-aware document splitting with overlap and metadata preservation | PRD, ES, ADR, ADS, TS |
| **Knowledge Graph** | Graph of concepts, topics, formulas, and their prerequisite relationships | PRD, ES, ADR, ADS, TS |
| **Grounded AI Response** | AI answer that cites specific source documents with confidence scores | PRD, ES, ADR, ADS, TS |
| **Citation Service** | Formats and verifies source references in every AI response | PRD, ES, ADS, TS |
| **Knowledge Processing Pipeline** | End-to-end flow: Upload → Validation → OCR → Parsing → Cleaning → Extraction → Chunking → Embedding → Graph → Index | PRD, ES, ADS, TS |

---

## 2. Service Catalog

### 2.1 Upload Service
- Upload (single file)
- Folder Upload (ZIP extraction)
- Drag & Drop
- Resume Uploads (chunked)
- File Validation (magic numbers, size limits)
- Duplicate Detection (SHA-256 + perceptual hash)

### 2.2 Document Validation Service
- File Validation (magic numbers, extensions)
- Virus Scan (ClamAV / cloud-native)
- File Integrity (corruption detection)
- File Type Detection (libmagic)
- Encoding Detection (chardet)
- Language Detection (langdetect / fastText)

### 2.3 OCR Service
- OCR (Tesseract 5.x — printed text)
- Handwritten OCR (Google Vision API)
- Image OCR (diagram extraction)
- Diagram OCR (detect + caption)
- Formula OCR (MathPix → LaTeX)
- Multi-language OCR (10+ languages)

### 2.4 Document Processing Service
- PDF Parsing (Docling → structured Markdown)
- DOCX Parsing (python-docx)
- PPT Parsing (python-pptx)
- EPUB Parsing (ebooklib)
- Image Extraction (extract + caption)
- Table Extraction (Markdown tables)
- Formula Extraction (LaTeX preservation)
- Diagram Extraction (SVG + caption)

### 2.5 Knowledge Extraction Service
- Topic Detection
- Chapter Detection
- Concept Extraction (key terms + definitions)
- Learning Objectives inference
- Formula Detection (LaTeX)
- Example Extraction
- Question Extraction (MCQ, fill-in-blank, short answer)
- Difficulty Classification (formula density, language level, question complexity)
- Prerequisite Detection (topic dependency chains)
- Metadata Extraction (source, author, page count, confidence)

### 2.6 Semantic Chunking Service
- Adaptive Chunk Size (300-800 tokens, configurable)
- Semantic Chunking (heading-aware)
- Overlap (80 tokens between chunks)
- Metadata Preservation (heading, page, document ID, topic, subject)
- Parent/Child Relationships (document → chapter → section → chunk)

### 2.7 Embedding Service
- BAAI/bge-large-en-v1.5 (default, 1024-dim, local)
- OpenAI text-embedding-3-small (optional, 1536-dim, paid)
- Batch Processing (32 chunks per batch)
- L2 Normalization
- Incremental Updates (only changed chunks re-embedded)
- Cache (Redis, 24h TTL)

### 2.8 Knowledge Graph Service
- Nodes: subjects, chapters, concepts, topics, formulas, questions
- Edges: prerequisite, related, part-of, covers
- Graph Traversal (recursive CTE in PostgreSQL, Phase 4 → ArangoDB)
- Prerequisite Chain Analysis
- Learning Path Optimization
- Concept Gap Detection

### 2.9 Hybrid Retrieval Engine
- Intent Detection (query classification)
- Query Planning (route to appropriate retrieval strategy)
- Dense Retrieval (pgvector similarity, top-10)
- Keyword Retrieval (PostgreSQL BM25 tsvector, top-10)
- Metadata Filtering (SQL WHERE on subject, document, confidence, date)
- Knowledge Graph Traversal (prerequisite chains, related concepts, top-5)
- Re-ranking (BAAI/bge-reranker cross-encoder)
- Source Ranking (confidence-based)
- Context Assembly (top-5 chunks with citations)
- Reciprocal Rank Fusion (RRF, k=60)

### 2.10 Citation Service
- Source Reference extraction
- Confidence scoring per citation
- Retrieved Document tracking
- Supporting Page linking
- Evidence Trace (chunk → document → page → confidence)
- Citation Verification (verify cited chunks exist in retrieved results)

---

## 3. Knowledge Processing Pipeline

```
Upload
  ↓
Validation (magic numbers, size, virus scan)
  ↓ [FAIL] → Dead Letter Queue
Virus Scan
  ↓ [FAIL] → Quarantine
OCR (if scanned/image)
  ↓ [FAIL] → Flag for manual review
Parsing (Docling → structured Markdown)
  ↓ [FAIL] → Corrupted document queue
Cleaning (remove headers, footers, watermarks, normalize)
  ↓
Metadata Extraction (filename, size, page count, language)
  ↓
Topic Detection (subject classification)
  ↓
Chapter Detection (heading hierarchy)
  ↓
Concept Extraction (LLM with structured JSON output)
  ↓
Difficulty Classification (per-topic difficulty score)
  ↓
Duplicate Removal (deduplicate across documents)
  ↓
Semantic Chunking (heading-aware, 300-800 tokens, 80 overlap)
  ↓
Embeddings (BAAI/BGE, 1024-dim, L2 normalized, batch 32)
  ↓
Knowledge Graph Construction (concepts → prerequisites → relationships)
  ↓
Vector Index (pgvector IVFFlat / HNSW)
  ↓
Full-Text Index (PostgreSQL GIN tsvector)
  ↓
Metadata Index (document properties, tags, status)
  ↓
Status = "ready"
```

**Failure Paths & Retry:**
- Transient errors (network, rate limit): retry 3x with exponential backoff (1s, 2s, 4s)
- Permanent errors (corrupted file, unsupported format): move to dead letter queue
- Low OCR confidence (< 60%): flag for manual review, notify user
- Low extraction confidence: partial processing, mark as "ready_with_warnings"

---

## 4. Storage Architecture

### 4.1 Object Storage (Cloudflare R2)
- Primary: Raw documents (PDFs, images, books, notes)
- Path: `users/{user_id}/documents/{document_id}/original.{ext}`
- Extracted: `users/{user_id}/documents/{document_id}/extracted.md`
- Thumbnails: `users/{user_id}/documents/{document_id}/thumbnails/page-{n}.jpg`
- Audio: `users/{user_id}/audio/{cache_key}.mp3`
- Exports: `users/{user_id}/exports/{export_id}/`
- Backups: `users/{user_id}/backups/{date}/`
- Encryption: AES-256 server-side
- Presigned URLs: 5-minute expiry
- Lifecycle: delete after account deletion + 30-day grace

### 4.2 Metadata Database (Supabase PostgreSQL)
- Tables: users, documents, chunks, topics, concepts, formulas, questions, knowledge_edges, study_sessions, user_profiles, study_groups, group_members, shared_topics, app_state, subscriptions
- RLS: every table has row-level security
- Indices: B-tree (metadata), GIN (full-text), IVFFlat/HNSW (vectors)

### 4.3 Vector Database (Supabase pgvector)
- Column: `embedding VECTOR(1024)` in chunks table
- Index: IVFFlat for < 1M vectors, HNSW for > 1M
- Distance: cosine similarity (via inner product with L2 normalization)
- Partition: by user_id for query performance

### 4.4 Knowledge Graph (PostgreSQL → ArangoDB Phase 4)
- PostgreSQL Phase 3: `knowledge_edges` table with recursive CTE traversal
- ArangoDB Phase 4: multi-model graph database for > 10K edges per user
- Schema: nodes (concepts, topics, formulas), edges (prerequisite, related, part-of, covers)

### 4.5 Optional Telegram Cold Storage
- **Purpose:** Off-site backup/archive for raw documents
- **Benefits:** Free unlimited storage, simple API, cloud-independent
- **Limitations:** No SLA, not searchable, manual recovery only, file size limits (2GB)
- **Recovery Flow:** Admin initiates recovery → bot downloads from Telegram → validates → re-ingests
- **Use Case:** Disaster recovery when primary storage fails, not primary access path

---

## 5. Retrieval Architecture

```
User Query
  ↓
Intent Detection (classify: definition, problem, comparison, summary, quiz_request)
  ↓
Query Planning (select retrieval strategy based on intent)
  ↓
Hybrid Retrieval (parallel fork-join)
  ├─ Dense: pgvector similarity → top 10
  ├─ Sparse: BM25 tsvector → top 10
  └─ Graph: prerequisite traversal → top 5
  ↓
Metadata Filtering (apply SQL WHERE: subject, document, confidence > 0.5, date range)
  ↓
Knowledge Graph Expansion (follow related concepts, add context)
  ↓
Re-ranking (BAAI/bge-reranker cross-encoder on combined candidates → scores 0-1)
  ↓
Source Ranking (boost by confidence score: official > publisher > community)
  ↓
Context Builder (assemble top 5 chunks with citations, format for LLM)
  ↓
LLM (Ollama/vLLM/OpenAI with strict grounding prompt)
  ↓
Citation Generator (extract [1], [2] from LLM output, verify against retrieved chunks)
  ↓
Final Response (answer + structured citations + confidence scores + source previews)
```

---

## 6. AI Agents

| Agent | Responsibility | Triggers |
|-------|-----------------|----------|
| **Upload Agent** | Orchestrates upload, validation, virus scan, duplicate detection | File drop |
| **OCR Agent** | Selects OCR engine, processes images/scans, handles confidence thresholds | Scanned document upload |
| **Parser Agent** | Runs Docling, extracts structure, preserves headings/tables/formulas | Valid document |
| **Knowledge Extraction Agent** | Extracts concepts, definitions, formulas, questions, prerequisites, difficulty | Parsed document |
| **Classification Agent** | Detects subject, topic, language, document type, source confidence | Parsed document |
| **Embedding Agent** | Generates embeddings, manages cache, handles batch processing | Chunked document |
| **Retrieval Agent** | Plans query strategy, executes hybrid retrieval, assembles context | User query |
| **Citation Agent** | Verifies citations, formats sources, assigns confidence scores | LLM response |
| **Quiz Agent** | Generates MCQ, true/false, fill-in-blank, short answer from knowledge base | User request |
| **Flashcard Agent** | Extracts key terms → Q&A pairs, supports image-based cards | User request |
| **Study Planner Agent** | Integrates knowledge base topics into existing planner scoring (D, P, U, S) | Document ready |
| **Tutor Agent** | Generates grounded explanations, answers questions, provides examples | User question |

---

## 7. Trusted Source Hierarchy (Confidence Scores)

| Rank | Source Type | Base Confidence | Cross-Validation Boost |
|------|-------------|---------------|----------------------|
| 1 | Official Government Sources | 1.00 | +0.10 |
| 2 | Official Exam Authorities | 1.00 | +0.10 |
| 3 | Official Syllabus | 1.00 | +0.10 |
| 4 | Official PYQs | 0.98 | +0.10 |
| 5 | Official Answer Keys | 0.98 | +0.10 |
| 6 | NCERT / Open Educational Resources | 0.90 | +0.10 |
| 7 | Trusted Publishers (Wiley, Pearson, etc.) | 0.85 | +0.10 |
| 8 | Verified Educational Platforms | 0.75 | +0.10 |
| 9 | Coaching Institute Materials | 0.70 | +0.10 |
| 10 | User Class Notes | 0.65 | +0.10 |
| 11 | Community Resources | 0.40 | +0.10 |
| 12 | Unverified Internet Sources | 0.20 | +0.10 |

**Cross-validation:** If a fact appears in multiple sources, boost confidence by +0.10 (capped at 1.00).
**User override:** Users can manually adjust confidence scores for their documents.

---

## 8. New ADRs to Add (009-018)

| ADR | Title | Status |
|-----|-------|--------|
| ADR-009 | Hybrid Retrieval Architecture | Accepted |
| ADR-010 | Object Storage Strategy — R2 + S3 + Telegram | Accepted |
| ADR-011 | Semantic Chunking Strategy — Heading-Aware vs Fixed-Size | Accepted |
| ADR-012 | Knowledge Graph Architecture — PostgreSQL vs ArangoDB | Provisional |
| ADR-013 | Trusted Source Ranking — Rule-Based Confidence Scoring | Accepted |
| ADR-014 | Telegram Cold Storage — Optional Backup Layer | Accepted |
| ADR-015 | OCR Processing Pipeline — Multi-Engine Strategy | Accepted |
| ADR-016 | Embedding Model Strategy — BAAI/BGE vs OpenAI | Accepted |
| ADR-017 | Metadata-Driven Retrieval — Filtering & Ranking | Accepted |
| ADR-018 | AI Grounding & Citation Policy — Strict Context Adherence | Accepted |

---

## 9. New Epics to Add (ADS)

| Epic | Title | Description |
|------|-------|-------------|
| E-015 | Upload Infrastructure | Multi-format, chunked, resume, drag-drop |
| E-016 | Validation Pipeline | Magic numbers, virus scan, integrity, encoding |
| E-017 | OCR Engine | Multi-engine (Tesseract + Google Vision + MathPix) |
| E-018 | Parsing Engine | Docling for PDF/DOCX/PPTX/EPUB, structure preservation |
| E-019 | Knowledge Extraction | LLM-based concept/formula/question/prerequisite extraction |
| E-020 | Embedding Pipeline | BAAI/BGE default, OpenAI optional, batch processing, cache |
| E-021 | Knowledge Graph | Concept relationships, prerequisites, learning paths |
| E-022 | Hybrid Retrieval | Dense + sparse + metadata + graph + re-rank + RRF |
| E-023 | Web Resource Collector | Auto-discovery of official resources for zero-upload setup |
| E-024 | Citation Engine | Source verification, confidence scoring, citation formatting |
| E-025 | Knowledge Management Dashboard | Document CRUD, topic tree, concept graph, search |
| E-026 | Monitoring & Analytics | Processing metrics, retrieval quality, usage analytics |

---

## 10. New Test Categories (TS)

- Upload Tests (all formats, edge cases, chunked, resume)
- OCR Accuracy Tests (printed > 85%, handwritten > 70%, formula > 80%)
- Parsing Tests (structure preservation, table extraction, formula LaTeX)
- Embedding Validation (L2 normalization, dimension correctness, cosine similarity)
- Chunking Validation (heading respect, no table/formula splits, size range, overlap)
- Retrieval Precision (precision@5 > 80%)
- Retrieval Recall (recall@10 > 50%)
- Hallucination Tests (0 hallucinations on test set)
- Grounding Tests (100% citations verified)
- Citation Tests (accuracy, confidence threshold, format correctness)
- Source Ranking Tests (official sources ranked above community)
- Duplicate Detection Tests (SHA-256, perceptual hash, cross-document)
- Security Tests (XSS, SQL injection, RLS bypass, rate limiting)
- Authorization Tests (JWT, RLS, role-based access)
- Load Tests (k6, 200 concurrent users, < 1% error)
- Performance Tests (p95 latency, processing time benchmarks)
- Stress Tests (50 concurrent uploads, 1000 queries)
- Scalability Tests (10K users, 1M chunks)
- Disaster Recovery Tests (backup restore, RPO/RTO)
- Telegram Backup Tests (upload, download, integrity)
- Regression Tests (scoring formula, plan generation)

---

## 11. Non-Functional Requirements (New)

- **Scalability:** 10,000 concurrent users, 1,000 documents/hour, 10M chunks/tenant
- **High Availability:** 99.9% uptime SLA, circuit breaker, graceful degradation
- **Reliability:** 99.5% document processing success, 3 retries with exponential backoff
- **Security:** TLS 1.3, AES-256 at rest, zero-knowledge architecture, RBAC
- **Encryption:** Document content encrypted with user-specific keys
- **Compliance:** GDPR, CCPA, India's DPDP Act, SOC 2 Type II target
- **Privacy:** No training on user docs without opt-in, data residency choice, right to erasure
- **Cost Optimization:** Local-first defaults (Ollama, BAAI, Kokoro), tiered pricing
- **Observability:** Structured JSON logging, OpenTelemetry, Grafana, PagerDuty alerts
- **Metrics:** Processing time, success rate, queue depth, cache hit rate, retrieval precision
- **Logging:** Correlation IDs, 30 days hot / 1 year cold (S3 Glacier)
- **Tracing:** Distributed tracing with Jaeger
- **Audit Trails:** Immutable WORM logs, 7-year retention, all user/system actions
- **Disaster Recovery:** Daily backups, cross-region replication, RPO < 1h, RTO < 4h
- **Fault Tolerance:** Microservices fail independently, circuit breaker, fallback chains
- **Rate Limiting:** 100 req/min free, 1,000 pro, 10,000 enterprise
- **Multi-tenancy:** Strict RLS isolation, per-tenant quotas, no cross-tenant leakage

---

## 12. API Surface (New Endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v3/upload` | POST | Multi-file upload with metadata |
| `/api/v3/upload/chunk` | POST | Chunked upload (resume support) |
| `/api/v3/documents` | GET | List user documents with status |
| `/api/v3/documents/:id` | GET | Document metadata + processing status |
| `/api/v3/documents/:id/reprocess` | POST | Re-trigger processing pipeline |
| `/api/v3/documents/:id/download` | GET | Download original from R2 |
| `/api/v3/documents/:id/chunks` | GET | List chunks for a document |
| `/api/v3/ask` | POST | Grounded AI question answering |
| `/api/v3/search` | POST | Hybrid search (semantic + keyword) |
| `/api/v3/retrieve` | POST | Raw retrieval (chunks + scores) |
| `/api/v3/knowledge/topics` | GET | Topic hierarchy tree |
| `/api/v3/knowledge/concepts` | GET | Extracted concepts list |
| `/api/v3/knowledge/graph` | GET | Knowledge graph nodes + edges |
| `/api/v3/generate/flashcards` | POST | Generate flashcards from topic |
| `/api/v3/generate/quiz` | POST | Generate quiz from topic |
| `/api/v3/generate/summary` | POST | AI summary of topic/document |
| `/api/v3/generate/plan` | POST | Study plan from knowledge base |
| `/api/v3/setup/auto` | POST | Zero-upload exam setup |
| `/api/v3/setup/resources` | GET | Found resources for exam |
| `/api/v3/health` | GET | Health check + version |

---

## 13. Data Models (New/Expanded)

### documents table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    r2_path TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'uploaded' 
        CHECK (status IN ('uploaded', 'validating', 'scanning', 'extracting', 'chunking', 'embedding', 'indexing', 'ready', 'error', 'ready_with_warnings')),
    subject TEXT,
    tags TEXT[],
    language TEXT DEFAULT 'en',
    source_type TEXT DEFAULT 'user_upload',
    source_confidence REAL DEFAULT 0.65,
    metadata JSONB DEFAULT '{}',
    page_count INTEGER,
    topics_extracted INTEGER DEFAULT 0,
    chunks_count INTEGER DEFAULT 0,
    concepts_count INTEGER DEFAULT 0,
    formulas_count INTEGER DEFAULT 0,
    questions_count INTEGER DEFAULT 0,
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);
```

### chunks table (with pgvector)
```sql
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    heading TEXT,
    page_number INTEGER,
    token_count INTEGER,
    embedding VECTOR(1024),
    metadata JSONB DEFAULT '{}',
    parent_chunk_id UUID REFERENCES chunks(id),
    chunk_level INTEGER DEFAULT 1, -- 1=document, 2=chapter, 3=section, 4=paragraph
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### knowledge_edges table
```sql
CREATE TABLE knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK (relationship IN ('prerequisite', 'related', 'part-of', 'covers', 'example-of')),
    confidence REAL NOT NULL DEFAULT 0.5,
    source_document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, source_node, target_node, relationship)
);
```

### concepts table
```sql
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    definition TEXT,
    subject TEXT,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES chunks(id) ON DELETE CASCADE,
    confidence REAL DEFAULT 0.5,
    source_type TEXT DEFAULT 'extracted',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 14. Cross-Document Traceability Matrix

| Concept | PRD Section | ES Section | ADR | ADS Epic | TS Section |
|-----------|-------------|------------|-----|----------|------------|
| Upload Service | 4. FR-01 | 2.1 | — | E-015 | 3.1, 10 |
| Validation | 4. FR-02 | 2.2 | — | E-016 | 3.1, 8.1 |
| OCR | 4. FR-03 | 2.3 | ADR-015 | E-017 | 3.2, 9.2 |
| Parsing | 4. FR-04 | 2.4 | ADR-001 | E-018 | 3.2, 9.3 |
| Semantic Chunking | 4. FR-05 | 2.6 | ADR-011 | E-019 | 3.3, 9.4 |
| Embedding | 4. FR-06 | 2.7 | ADR-016 | E-020 | 3.4, 9.5 |
| Knowledge Graph | 4. FR-08 | 2.8 | ADR-012 | E-021 | 3.5, 9.6 |
| Hybrid Retrieval | 4. FR-09 | 2.9 | ADR-009 | E-022 | 3.6, 9.1 |
| Source Confidence | 4. FR-10 | 2.10 | ADR-013 | E-024 | 3.7, 9.7 |
| Citation | 4. FR-12 | 2.10 | ADR-018 | E-024 | 3.8, 9.8 |
| Auto-Setup | 4. FR-13 | 3.3 | — | E-023 | 3.9, 10 |
| Object Storage | 6. NFR-06 | 6.1 | ADR-010 | E-014 | 3.10 |
| Telegram Backup | 6. NFR-08 | 6.5 | ADR-014 | — | 3.11, 9.9 |

---

*End of Blueprint*
