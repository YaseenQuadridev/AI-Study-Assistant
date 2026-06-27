# Engineering Specification

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 1.0.0
**Date:** 2026-06-26
**Status:** Draft — Ready for Review
**Author:** Engineering Architecture Team

---

## 1. System Architecture

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Web App    │  │  Mobile PWA │  │  CLI Tool   │  │  LMS LTI Plugin │  │
│  │ (React/Vue) │  │  (Capacitor)│  │  (Python)   │  │  (JavaScript)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘  │
└─────────┼────────────────┼────────────────┼─────────────────┼──────────┘
          │                │                │                 │
          └────────────────┴────────────────┴─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Cloudflare Worker (Edge)                                         │   │
│  │  - CORS proxy                                                     │   │
│  │  - Rate limiting                                                  │   │
│  │  - Auth token validation (JWT)                                  │   │
│  │  - Route to services                                              │   │
│  │  - Cache static responses (Cache API)                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SERVICE LAYER (Serverless)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ Upload       │  │ Processing   │  │ Retrieval    │  │ AI          │  │
│  │ Service      │  │ Pipeline     │  │ Service      │  │ Orchestrator│  │
│  │ (Edge Func)  │  │ (Edge Func)  │  │ (Edge Func)  │  │ (Edge Func) │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
│         │                 │                 │                 │         │
│         │                 │                 │                 │         │
│  ┌──────▼──────┐  ┌───────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐  │
│  │ Document    │  │ Chunking     │  │ Vector       │  │ LLMProvider  │  │
│  │ Validation  │  │ Service      │  │ Search       │  │ Interface   │  │
│  │ (Edge Func) │  │ (Edge Func)  │  │ (Edge Func)  │  │ (Edge Func) │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
          │                 │                 │                 │
          └─────────────────┴─────────────────┴─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA & STORAGE LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Object      │  │ PostgreSQL  │  │ pgvector    │  │ Cache           │  │
│  │ Storage     │  │ (Metadata)  │  │ (Embeddings)│  │ (Redis/Upstash) │  │
│  │ (R2)        │  │ (Supabase)  │  │ (Supabase)  │  │ (Cloudflare)    │  │
│  │             │  │             │  │             │  │                 │  │
│  │ Raw PDFs    │  │ Documents   │  │ Chunk       │  │ Session state   │  │
│  │ Images      │  │ Chunks      │  │ embeddings  │  │ Search results  │  │
│  │ Videos      │  │ Topics      │  │             │  │ Rate limit      │  │
│  │             │  │ Users       │  │             │  │                 │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │ ArangoDB (Optional Phase 4) — Knowledge Graph                      │  │
│  │  - Concept nodes, prerequisite edges, related-concept edges          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Docling     │  │ Tesseract   │  │ BAAI/BGE    │  │ vLLM/SGLang │    │
│  │ (Parser)    │  │ (OCR)       │  │ (Embeddings)│  │ (Inference) │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ MathPix     │  │ Google      │  │ OpenAI      │  │ Stripe      │    │
│  │ (Formulas)  │  │ Vision      │  │ (Optional)  │  │ (Billing)   │    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Architecture Principles

1. **Edge-First**: Process as close to the user as possible. Cloudflare Workers handle auth, caching, and routing at 300+ edge locations.
2. **Serverless**: Supabase Edge Functions for stateless processing. No server management.
3. **Event-Driven**: Document upload triggers processing pipeline via webhooks.
4. **Local-First Defaults**: BAAI/BGE (local), Ollama (local), Kokoro (local). Cloud AI only for optional paid tiers.
5. **Immutable Storage**: Raw documents never modified. All processing creates derived data in PostgreSQL.
6. **Multi-Tenant Isolation**: RLS policies enforce strict tenant boundaries. No cross-tenant data leakage possible.

---

## 2. Component Architecture

### 2.1 Upload Service (Supabase Edge Function)

**Responsibility:** Accept file uploads, validate, store in R2, trigger processing pipeline.

**API:**
```
POST /upload
  Content-Type: multipart/form-data
  Body: file[] (multiple files), metadata: { exam_id, subject, tags }
  Response: { upload_id, status, files: [{ filename, size, status, document_id }] }
```

**Components:**
- `FileValidator`: checks magic numbers, max size, virus scan
- `R2Uploader`: streams to Cloudflare R2 (S3-compatible)
- `MetadataExtractor`: filename, size, MIME type, page count (PDF)
- `DuplicateDetector`: content hash (SHA-256) + perceptual hash (pHash)
- `Trigger`: POST to Processing Pipeline webhook

**Error Handling:**
- Invalid file: 400 with detailed error
- Virus detected: 400 with scan report
- Upload too large: 413 with size info
- R2 failure: 500, retry 3x with exponential backoff

### 2.2 Processing Pipeline (Supabase Edge Function)

**Responsibility:** Orchestrate document processing: OCR → extraction → chunking → embedding → indexing.

**Pipeline Stages:**
```
Stage 1: OCR & Text Extraction
  Input:  raw document (R2 URL)
  Output: structured markdown, extracted images, detected language
  Tools:  Docling (primary), Tesseract (fallback), MathPix (formulas)
  
Stage 2: Semantic Chunking
  Input:  structured markdown
  Output: chunks with metadata (heading, page, topic, subject)
  Rules:  respect headings, never split tables/formulas, 300-800 tokens
  
Stage 3: Knowledge Extraction
  Input:  chunks
  Output: concepts, definitions, formulas, question banks, prerequisites
  Tools:  LLM (Ollama/vLLM) with structured output (JSON schema)
  
Stage 4: Embedding Generation
  Input:  chunks
  Output: 1024-dimensional vectors (BAAI/BGE)
  Batch:  32 chunks per batch
  
Stage 5: Indexing
  Input:  chunks + embeddings + metadata
  Output: pgvector records, full-text index, metadata index
  
Stage 6: Knowledge Graph Construction
  Input:  extracted concepts + prerequisites
  Output: graph nodes and edges in ArangoDB (or PostgreSQL graph tables)
```

**State Machine:**
```
[uploaded] → [validating] → [extracting] → [chunking] → [embedding] → [indexing] → [ready]
                ↓                ↓              ↓            ↓            ↓
              [error]        [error]        [error]      [error]      [error]
```

**Retry Logic:**
- Transient failures (network, rate limit): retry 3x with 2^N * 1s delay
- Permanent failures (corrupted file, unsupported format): move to dead letter queue
- Dead letter queue: admin UI for manual review and reprocessing

### 2.3 Retrieval Service (Supabase Edge Function)

**Responsibility:** Hybrid retrieval from vector + keyword + metadata + graph.

**API:**
```
POST /retrieve
  Body: { query, filters: { subject, document_ids, date_range, confidence_min }, k: 5 }
  Response: { results: [{ chunk, score, source, confidence, citation }] }
```

**Components:**
- `QueryPreprocessor`: spell correction, synonym expansion, query rewriting
- `DenseRetriever`: vector similarity search via pgvector (top-10)
- `SparseRetriever`: full-text BM25 search via PostgreSQL tsvector (top-10)
- `MetadataFilter`: SQL WHERE clause on subject, document, confidence, date
- `GraphTraverser`: follow prerequisite edges, related concepts (ArangoDB)
- `ReRanker`: cross-encoder (BAAI/bge-reranker) on combined candidates
- `FusionEngine`: Reciprocal Rank Fusion (RRF) to merge all scores
- `CitationFormatter`: format [1], [2] with source document + page

**Caching:**
- Cache frequent queries in Upstash Redis (1-hour TTL)
- Cache key: hash(query + filters) → results
- Cache invalidation: on document reprocessing

### 2.4 AI Orchestrator (Supabase Edge Function)

**Responsibility:** Generate AI responses grounded in retrieved knowledge.

**API:**
```
POST /ask
  Body: { question, context: { restrict_documents, restrict_topics, max_sources: 5 } }
  Response: { answer, citations: [{ index, source, page, confidence, snippet }] }
```

**Pipeline:**
```
1. Receive question
2. Call Retrieval Service with question + context filters
3. Format retrieved chunks as context string
4. Build prompt: "Answer using ONLY the following context. Cite sources [n]. If insufficient, say 'I don't have enough information.'"
5. Call LLMProvider (Ollama/vLLM/OpenAI)
6. Parse response, extract citations
7. Verify citations match retrieved chunks
8. Return answer + structured citations
```

**Prompt Template:**
```
You are a helpful study assistant. Use ONLY the context below to answer the question.
If the context doesn't contain the answer, say "I don't have enough information in your knowledge base."

Context:
{context}

Question: {question}

Answer (cite sources with [n] format):
```

### 2.5 Document Management Service

**Responsibility:** CRUD operations for user documents.

**API Endpoints:**
```
GET    /documents          → list user documents with status
GET    /documents/:id      → get document metadata + processing status
DELETE /documents/:id      → soft delete (flag + 30-day grace period)
PUT    /documents/:id      → update metadata (tags, name)
POST   /documents/:id/reprocess → re-trigger processing pipeline
GET    /documents/:id/download → download original file from R2
```

### 2.6 Knowledge Base Service

**Responsibility:** Query and visualize the user's knowledge base.

**API Endpoints:**
```
GET /knowledge/topics              → topic hierarchy tree
GET /knowledge/concepts            → flat list of extracted concepts
GET /knowledge/graph               → nodes and edges for visualization
GET /knowledge/search?q=...        → full-text + semantic search
GET /knowledge/summary/:topic_id → AI-generated summary of topic
```

### 2.7 Generation Service

**Responsibility:** Generate learning materials from knowledge base.

**API Endpoints:**
```
POST /generate/flashcards  → { topic_id, count: 20 } → flashcards[]
POST /generate/quiz        → { topic_id, count: 10, type: "mcq" } → questions[]
POST /generate/summary     → { document_ids } → summary text
POST /generate/plan        → { exam_id, subjects, days_until_exam } → study plan
```

---

## 3. Data Flow

### 3.1 Upload & Process Flow

```
User drops PDF into web app
  │
  ▼
Web App → POST /upload (multipart/form-data, JWT token)
  │
  ▼
Cloudflare Worker validates JWT, checks rate limit
  │
  ▼
Supabase Edge Function (Upload Service):
  1. Validate file (magic number, size, virus scan)
  2. Generate SHA-256 content hash
  3. Check for duplicates (hash match)
  4. Stream to R2: users/{user_id}/documents/{document_id}/original.pdf
  5. Insert document record into PostgreSQL (status: "uploaded")
  6. Trigger Processing Pipeline (async webhook)
  7. Return 202 Accepted with upload_id
  │
  ▼
Processing Pipeline (Supabase Edge Function):
  Stage 1: Download from R2 → Docling → structured markdown
  Stage 2: Chunk markdown → metadata-enriched chunks
  Stage 3: LLM extraction → concepts, formulas, questions
  Stage 4: Batch embed chunks → BAAI/BGE → vectors
  Stage 5: Insert chunks + embeddings into pgvector
  Stage 6: Insert concepts + relationships into knowledge graph
  Stage 7: Update document record (status: "ready")
  │
  ▼
Web App polls GET /documents/:id/status
  │
  ▼
When status = "ready", show user: "Processing complete! 47 topics extracted."
```

### 3.2 Question & Answer Flow

```
User asks: "What is the ideal gas law?"
  │
  ▼
Web App → POST /ask (question, filters: { restrict_to: "Chemistry Textbook" })
  │
  ▼
Cloudflare Worker validates JWT, rate limit
  │
  ▼
AI Orchestrator:
  1. Preprocess query: "ideal gas law chemistry"
  2. Call Retrieval Service:
     a. Dense: vector search "ideal gas law" → top 10 chunks
     b. Sparse: BM25 "ideal gas law" → top 10 chunks
     c. Metadata: filter by document_id = "Chemistry Textbook"
     d. Graph: traverse from "Thermodynamics" → related concepts
     e. Re-rank: BAAI/bge-reranker on combined 20 candidates
     f. RRF fusion → top 5 results
  3. Format context: "[1] Page 45: The ideal gas law states PV = nRT..."
  4. Build prompt with context + question
  5. Call LLMProvider.generate(prompt, temperature=0.3)
  6. LLM returns: "The ideal gas law is PV = nRT [1], where P is pressure..."
  7. Verify citation [1] exists in retrieved chunks
  8. Return { answer, citations: [{ index: 1, source: "Chemistry Textbook", page: 45, confidence: 0.95 }] }
  │
  ▼
Web App renders answer with clickable citations
```

---

## 4. Service Interactions

### 4.1 Synchronous Interactions

| From | To | Purpose | Timeout |
|------|-----|---------|---------|
| Client | Cloudflare Worker | Auth, routing, caching | 5s |
| Cloudflare Worker | Supabase Edge Function | API request | 30s |
| Edge Function | PostgreSQL | CRUD operations | 5s |
| Edge Function | pgvector | Vector search | 2s |
| Edge Function | R2 | File upload/download | 30s |
| Edge Function | Redis | Cache read/write | 100ms |

### 4.2 Asynchronous Interactions

| From | To | Trigger | Queue |
|------|-----|---------|-------|
| Upload Service | Processing Pipeline | Webhook POST | — (direct invoke) |
| Processing Pipeline | Embedding Service | After chunking | Supabase Realtime |
| Processing Pipeline | Knowledge Graph | After extraction | — (direct invoke) |
| Document Reprocess | All Pipeline Stages | User clicks "Reprocess" | Background job |

### 4.3 Data Consistency

- **Upload → R2**: Strong consistency (R2 is strongly consistent)
- **R2 → PostgreSQL**: Eventual consistency (pipeline may lag 1-5 minutes)
- **PostgreSQL → pgvector**: Eventual consistency (embedding generation async)
- **Cache → Source**: TTL-based (1 hour default, invalidate on reprocess)

---

## 5. API Specification

### 5.1 Upload API

```
POST /api/v3/upload
Content-Type: multipart/form-data
Authorization: Bearer <jwt>

Body:
  files[]: <binary files>
  metadata: {
    "exam_id": "jee-2026",
    "subject": "Physics",
    "tags": ["thermodynamics", "coaching-notes"]
  }

Response 202:
{
  "upload_id": "uuid",
  "status": "processing",
  "files": [
    {
      "document_id": "uuid",
      "filename": "Thermodynamics_Chapter3.pdf",
      "size": 2457600,
      "status": "processing",
      "estimated_time_seconds": 180
    }
  ]
}

Response 400:
{
  "error": "INVALID_FILE_TYPE",
  "message": "File 'virus.exe' is not a supported format. Allowed: PDF, DOCX, TXT, EPUB, JPG, PNG, ZIP",
  "invalid_files": ["virus.exe"]
}
```

### 5.2 Ask API

```
POST /api/v3/ask
Content-Type: application/json
Authorization: Bearer <jwt>

Body:
{
  "question": "What is the ideal gas law?",
  "context": {
    "restrict_documents": ["doc-uuid-1"],
    "restrict_topics": ["thermodynamics"],
    "max_sources": 5,
    "min_confidence": 0.7
  }
}

Response 200:
{
  "answer": "The ideal gas law is PV = nRT [1], where P is pressure, V is volume, n is moles, R is the gas constant, and T is temperature in Kelvin.",
  "citations": [
    {
      "index": 1,
      "document_id": "doc-uuid-1",
      "document_name": "Chemistry Textbook",
      "page": 45,
      "chunk_id": "chunk-uuid",
      "snippet": "The ideal gas law states that PV = nRT, where...",
      "confidence": 0.95
    }
  ],
  "retrieval_time_ms": 120,
  "generation_time_ms": 850
}

Response 200 (no relevant content):
{
  "answer": "I don't have enough information in your knowledge base to answer this question.",
  "citations": [],
  "suggestion": "Try uploading a chemistry textbook or searching for 'gas laws' in your documents."
}
```

### 5.3 Document List API

```
GET /api/v3/documents?page=1&limit=20&status=ready
Authorization: Bearer <jwt>

Response 200:
{
  "documents": [
    {
      "id": "doc-uuid",
      "filename": "Thermodynamics_Chapter3.pdf",
      "size": 2457600,
      "status": "ready",
      "subject": "Physics",
      "tags": ["thermodynamics"],
      "topics_extracted": 12,
      "chunks_count": 47,
      "uploaded_at": "2026-06-26T10:00:00Z",
      "processed_at": "2026-06-26T10:03:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 156
  }
}
```

### 5.4 Search API

```
POST /api/v3/search
Content-Type: application/json
Authorization: Bearer <jwt>

Body:
{
  "query": "ideal gas law",
  "filters": {
    "subject": "Physics",
    "document_ids": ["doc-uuid-1"],
    "date_from": "2026-01-01"
  },
  "mode": "hybrid",
  "k": 10
}

Response 200:
{
  "results": [
    {
      "chunk_id": "chunk-uuid",
      "text": "The ideal gas law states PV = nRT...",
      "document_id": "doc-uuid-1",
      "document_name": "Chemistry Textbook",
      "page": 45,
      "heading": "Gas Laws",
      "score": 0.92,
      "highlight_ranges": [[12, 25]]
    }
  ],
  "search_time_ms": 85
}
```

---

## 6. Storage Architecture

### 6.1 Object Storage (Cloudflare R2)

**Structure:**
```
bucket: adaptive-study-planner-documents
  └── users/
      └── {user_id}/
          ├── documents/
          │   └── {document_id}/
          │       ├── original.pdf          (immutable, user-uploaded)
          │       ├── extracted.md          (Docling output)
          │       └── thumbnails/
          │           └── page-{n}.jpg
          ├── exports/
          │   └── {export_id}/
          │       ├── flashcards.json
          │       └── quiz.json
          └── backups/
              └── {date}/
                  └── telegram-cold-backup.zip
```

**Lifecycle:**
- Original documents: retained until user deletes account + 30-day grace
- Extracted markdown: retained until document deleted
- Thumbnails: auto-generated, cached for 30 days
- Exports: user-generated, retained until user deletes
- Backups: daily to cold storage (R2 Glacier), 1-year retention

**Security:**
- Presigned URLs with 5-minute expiry for download
- No public bucket access
- CORS restricted to `https://adaptive-study-planner.com`
- Server-side encryption (AES-256)

### 6.2 PostgreSQL (Supabase)

**Schema (excerpt):**

```sql
-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    r2_path TEXT NOT NULL,
    sha256_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'validating', 'extracting', 'chunking', 'embedding', 'indexing', 'ready', 'error')),
    subject TEXT,
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    page_count INTEGER,
    topics_extracted INTEGER DEFAULT 0,
    chunks_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ  -- soft delete
);

-- Chunks table (with pgvector)
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    heading TEXT,
    page_number INTEGER,
    token_count INTEGER,
    embedding VECTOR(1024),  -- pgvector
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Full-text search index
CREATE INDEX idx_chunks_fts ON chunks USING gin(to_tsvector('english', text));

-- Vector index (IVFFlat for < 1M vectors, HNSW for > 1M)
CREATE INDEX idx_chunks_embedding ON chunks USING ivfflat (embedding vector_ip_ops) WITH (lists = 100);

-- Knowledge graph edges
CREATE TABLE knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    source_node TEXT NOT NULL,      -- e.g., "concept:ideal_gas_law"
    target_node TEXT NOT NULL,      -- e.g., "concept:thermodynamics"
    relationship TEXT NOT NULL,     -- e.g., "prerequisite", "related", "part-of"
    confidence REAL NOT NULL DEFAULT 0.5,
    source_document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 6.3 Cache (Upstash Redis / Cloudflare Cache API)

**Cache Layers:**

| Layer | Key Pattern | TTL | Size |
|-------|-------------|-----|------|
| Query Results | `query:{hash}` | 1 hour | 10KB per result |
| Search Results | `search:{hash}` | 30 min | 5KB per result |
| Embeddings | `emb:{chunk_id}` | 24 hours | 4KB per vector |
| User Session | `session:{user_id}` | 24 hours | 1KB per user |
| Rate Limit | `rate:{ip}` | 1 min | 100 bytes |

---

## 7. AI Pipeline Architecture

### 7.1 Document Processing Pipeline

```
Raw Document (PDF/DOCX/etc.)
│
▼
[Docling Parser] ────────────────────► Structured Markdown
│                                      (headings, tables, formulas, images)
│
▼
[OCR Module] ────────────────────────► Text from scanned pages / images
│                                      (Tesseract for printed, Google Vision for handwritten)
│
▼
[Formula Extractor] ─────────────────► LaTeX formulas
│                                      (MathPix API for complex math)
│
▼
[Text Cleaner] ──────────────────────► Cleaned text
│                                      (remove headers, footers, watermarks, normalize whitespace)
│
▼
[Semantic Chunker] ──────────────────► Chunks with metadata
│                                      (300-800 tokens, heading-aware, overlap 80 tokens)
│
▼
[Knowledge Extractor (LLM)] ──────────► Extracted concepts, definitions, formulas, questions
│                                      (structured JSON output: { concepts: [...], definitions: [...], formulas: [...] })
│
▼
[Embedding Generator] ──────────────► 1024-dim vectors
│                                      (BAAI/bge-large-en-v1.5, batch size 32, L2 normalized)
│
▼
[Indexer] ───────────────────────────► pgvector + full-text index + metadata index
│
▼
[Knowledge Graph Builder] ────────────► Nodes & edges in graph DB
│                                      (concepts → prerequisites → related)
│
▼
[Status Updater] ────────────────────► Document status = "ready"
```

### 7.2 Retrieval Pipeline

```
User Query: "ideal gas law"
│
▼
[Query Preprocessor]
  - Spell correction
  - Synonym expansion ("ideal gas" → "perfect gas")
  - Language detection
│
▼
┌──────────────────────────────────────────────────┐
│  PARALLEL RETRIEVAL (fork-join)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │ Dense (vector)│  │ Sparse (BM25)│  │ Graph   │ │
│  │ Top 10        │  │ Top 10        │  │ Top 5   │ │
│  │ < 200ms       │  │ < 100ms       │  │ < 50ms  │ │
│  └──────────────┘  └──────────────┘  └─────────┘ │
└──────────────────────────────────────────────────┘
│
▼
[Metadata Filter] ───────────────────► Apply SQL filters (subject, document, confidence)
│
▼
[Re-Ranker] ──────────────────────────► BAAI/bge-reranker on combined candidates
│                                        (cross-encoder, scores 0-1)
│
▼
[Fusion Engine] ──────────────────────► RRF: score = sum(1 / (k + rank)) for each source
│                                        (k = 60, standard RRF parameter)
│
▼
[Top-K Selector] ─────────────────────► Return top 5 results
│
▼
[Citation Formatter] ─────────────────► Format: [1] Source Name, Page X, Confidence Y
```

### 7.3 LLM Provider Configuration

```yaml
# Default (local, free)
provider: ollama
model: llama3.1:8b
base_url: http://localhost:11434
max_tokens: 2048
temperature: 0.3

# Production (GPU, high throughput)
provider: vllm
model: meta-llama/Meta-Llama-3.1-8B-Instruct
base_url: http://vllm.internal:8000/v1
max_tokens: 2048
temperature: 0.3

# Fallback (paid, always available)
provider: openai
model: gpt-4o-mini
api_key: ${OPENAI_API_KEY}
max_tokens: 2048
temperature: 0.3
```

---

## 8. Security Architecture

### 8.1 Authentication & Authorization

```
User (Browser)
│
▼
[Login] ────────► Supabase Auth (email/password, OAuth, SAML)
│                   JWT token returned (RS256, 1-hour expiry)
│
▼
[API Request] ──► Cloudflare Worker
│                   Validate JWT signature (Supabase public key)
│                   Check token expiry
│                   Extract user_id from JWT sub claim
│
▼
[Supabase Edge Function]
│                   RLS policy: WHERE user_id = auth.uid()
│                   Query only returns user's own data
│
▼
[PostgreSQL]
│                   RLS enforced at database level
│                   No bypass possible even with raw SQL
```

### 8.2 Data Encryption

| Data | Encryption | Key Management |
|------|-----------|----------------|
| Raw documents (R2) | AES-256 server-side | Cloudflare-managed |
| Document metadata (PostgreSQL) | AES-256 at rest | Supabase-managed |
| Embeddings (pgvector) | AES-256 at rest | Supabase-managed |
| User passwords | bcrypt (cost 12) | Supabase Auth |
| API keys | Hashed (SHA-256) | Application-managed |
| JWT tokens | RS256 signed | Supabase Auth |
| In transit (all APIs) | TLS 1.3 | Cloudflare edge |

### 8.3 Multi-Tenancy Isolation

```sql
-- RLS Policy Example (documents table)
CREATE POLICY "documents_select_own" ON documents
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "documents_insert_own" ON documents
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "documents_update_own" ON documents
  FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "documents_delete_own" ON documents
  FOR DELETE USING (user_id = auth.uid());
```

**Tenant Isolation Guarantee:**
- Every table has `user_id` column
- Every query has RLS policy enforced
- No `SUPERUSER` or `BYPASSRLS` roles for application
- Row-level, not schema-level isolation (simpler, more scalable)

### 8.4 Rate Limiting & DDoS Protection

| Layer | Mechanism | Limit |
|-------|-----------|-------|
| Cloudflare | WAF + DDoS protection | Automatic |
| Cloudflare Worker | Per-IP rate limit | 100 req/min free, 1000 pro |
| Supabase API | Project-level rate limit | 10,000 req/min |
| PostgreSQL | Connection pool limit | 100 concurrent |
| LLM API | Token bucket per user | 10,000 tokens/min free |

---

## 9. Deployment Architecture

### 9.1 Environment Strategy

| Environment | Purpose | Infrastructure |
|-------------|---------|----------------|
| Local | Developer testing | Docker Compose (Ollama, PostgreSQL, R2 local) |
| Dev | Feature testing | Supabase branch, Cloudflare Workers dev |
| Staging | Pre-release testing | Supabase project, Cloudflare Workers staging |
| Production | Live users | Supabase production, Cloudflare Workers production |

### 9.2 CI/CD Pipeline

```
GitHub Push
│
▼
GitHub Actions
├── Lint (eslint, prettier, flake8)
├── Unit Tests (pytest, jest)
├── Integration Tests (Supabase local, R2 local)
├── Security Scan (npm audit, pip-audit, Trivy)
│
▼
Build & Deploy (Staging)
├── Deploy Edge Functions (Supabase CLI)
├── Deploy Cloudflare Worker (Wrangler)
│
▼
Manual Approval (Production)
│
▼
Deploy Production
├── Deploy Edge Functions
├── Deploy Cloudflare Worker
├── Run Database Migrations
├── Smoke Tests (health checks)
```

### 9.3 Monitoring & Alerting

| Metric | Tool | Threshold | Alert |
|--------|------|-----------|-------|
| API Error Rate | Sentry | > 1% | PagerDuty |
| API Latency p95 | Cloudflare Analytics | > 500ms | Slack |
| Document Processing Time | Custom Dashboard | > 10 min | Slack |
| Vector Search Latency | PostgreSQL Logs | > 200ms | Slack |
| LLM Token Usage | Custom Dashboard | > 90% quota | Email |
| R2 Storage Usage | Cloudflare Dashboard | > 80% capacity | Email |
| Database Connections | PostgreSQL Logs | > 80% pool | PagerDuty |

---

## 10. Sequence Diagrams

### 10.1 Document Upload & Processing

```
User        Web App    Cloudflare    Upload Edge    R2    Processing    PostgreSQL
 │             │            │              │          │      Edge Func       │
 │──select──▶│            │              │          │                    │
 │  files    │            │              │          │                    │
 │           │──POST /upload──▶│         │          │                    │
 │           │  JWT + multipart           │          │                    │
 │           │            │──validate──▶│          │                    │
 │           │            │  JWT + rate limit      │                    │
 │           │            │◀─ok────────│          │                    │
 │           │            │            │──upload──▶│                    │
 │           │            │            │          │──store──▶│          │
 │           │            │            │          │◀─url────│          │
 │           │            │            │◀─url────│          │          │
 │           │            │◀─202───────│          │          │          │
 │           │◀─upload_id─┤            │          │          │          │
 │           │            │            │──trigger webhook──▶│        │
 │           │            │            │          │          │──download──▶│
 │           │            │            │          │          │◀─file────│
 │           │            │            │          │          │──extract──▶│
 │           │            │            │          │          │◀─markdown│
 │           │            │            │          │          │──chunk───▶│
 │           │            │            │          │          │◀─chunks──│
 │           │            │            │          │          │──embed───▶│
 │           │            │            │          │          │◀─vectors─│
 │           │            │            │          │          │──index───▶│
 │           │            │            │          │          │◀─ok─────│
 │           │──GET /status───────────▶│          │          │          │
 │           │            │──query───▶│          │          │          │
 │           │            │          │◀─ready───│          │          │
 │           │◀─status=ready────────│          │          │          │
 │◀─"Done!"─┤            │              │          │                    │
```

### 10.2 Question & Answer

```
User        Web App    Cloudflare    AI Orchestrator    Retrieval    LLM
 │             │            │                │              │         │
 │──type───▶│            │                │              │         │
 │ question  │            │                │              │         │
 │           │──POST /ask──▶│              │              │         │
 │           │  JWT + question              │              │         │
 │           │            │──validate──▶│  │              │         │
 │           │            │◀─ok────────│  │              │         │
 │           │            │            │──preprocess──▶│           │
 │           │            │            │◀─query──────│  │         │
 │           │            │            │──retrieve───▶│  │         │
 │           │            │            │              │──dense───▶│
 │           │            │            │              │◀─top10───│
 │           │            │            │              │──sparse──▶│
 │           │            │            │              │◀─top10───│
 │           │            │            │              │──rerank──▶│
 │           │            │            │              │◀─top5────│
 │           │            │            │◀─results───│  │         │
 │           │            │            │──build prompt──▶│        │
 │           │            │            │◀─prompt────│  │         │
 │           │            │            │──generate───▶│  │       │
 │           │            │            │              │──call───▶│
 │           │            │            │              │◀─answer─│
 │           │            │            │◀─answer────│  │         │
 │           │            │            │──verify───▶│  │         │
 │           │            │            │◀─citations─│  │         │
 │           │            │◀─response──│  │              │         │
 │           │◀─answer + citations────│  │              │         │
 │◀─render──┤            │                │              │         │
```

---

## 11. Scalability Strategy

### 11.1 Horizontal Scaling

| Component | Current Capacity | Scaling Strategy | Bottleneck |
|-----------|------------------|------------------|------------|
| Cloudflare Worker | 100k req/day | Automatic (serverless) | None |
| Supabase Edge Func | 10k invocations/hour | Automatic (serverless) | Cold start (1-2s) |
| PostgreSQL | 100 connections | Connection pooling (PgBouncer) | CPU on complex queries |
| pgvector | 1M vectors | HNSW index + partition by user | Memory for HNSW |
| R2 | Unlimited | Automatic (object storage) | Egress costs |
| vLLM | 100 concurrent | Auto-scale GPU instances (1-3) | GPU cost |
| Redis | 10k keys | Upgrade plan | Memory |

### 11.2 Performance Optimization

1. **Embedding Caching**: Cache embeddings in Redis (24h TTL). Only re-embed changed chunks.
2. **Query Caching**: Cache search results (1h TTL). 80% of queries are repeated.
3. **Connection Pooling**: PgBouncer for PostgreSQL (100 connections → 1000 clients).
4. **Read Replicas**: Route read queries to PostgreSQL replicas. Writes go to primary.
5. **CDN Caching**: Cache static assets (JS, CSS, images) at Cloudflare edge.
6. **Lazy Loading**: Load document chunks on demand, not all at once.
7. **Batch Processing**: Process documents in batches of 10 during off-peak hours.

---

## 12. Failure Handling

### 12.1 Failure Scenarios

| Scenario | Detection | Automatic Response | Manual Response |
|----------|-----------|-------------------|-----------------|
| Document upload fails | R2 5xx | Retry 3x, then queue for manual review | Admin reprocesses from queue |
| OCR fails | Low confidence (< 60%) | Flag for manual review, notify user | User reviews and approves/corrects |
| Embedding generation fails | BAAI model error | Retry with OpenAI fallback (if pro tier) | Admin investigates model health |
| Vector search slow | > 200ms p95 | Switch to HNSW index, warm cache | DBA optimizes index |
| LLM timeout | > 30s | Return cached response or "try again later" | Ops checks GPU health |
| Database connection exhausted | Pool saturation | Queue requests, alert on-call | DBA increases pool size |
| JWT validation failure | Invalid signature | 401 Unauthorized, prompt re-login | Security team investigates |
| RLS bypass attempt | Query without user_id | Reject query, log incident | Security audit |

### 12.2 Circuit Breaker Pattern

```
LLM Service (Ollama/vLLM)
│
├─ State: CLOSED (normal)
│  ├─ Request succeeds → pass through
│  └─ 5 failures in 60s → OPEN
│
├─ State: OPEN (failing)
│  ├─ All requests fail fast → return 503
│  ├─ Wait 30s → HALF-OPEN
│  └─ Log alert: "LLM circuit open"
│
└─ State: HALF-OPEN (testing)
   ├─ 1 test request → if success → CLOSED
   └─ If failure → OPEN (wait 30s)

Fallback chain: vLLM → OpenAI → Cached response → "Service unavailable"
```

---

## 13. Cost Estimates (Monthly, 1000 active users)

| Component | Service | Cost | Notes |
|-----------|---------|------|-------|
| Database | Supabase Pro | $25 | 8GB storage, 500k Edge Func invocations |
| Object Storage | Cloudflare R2 | $15 | 500GB storage, 1TB egress |
| Cache | Upstash Redis | $10 | 1GB memory |
| Edge Computing | Cloudflare Workers | $5 | 10M requests |
| AI Inference | Ollama (local) | $0 | Free, self-hosted |
| Embeddings | BAAI (local) | $0 | Free, self-hosted |
| OCR | Tesseract (local) | $0 | Free |
| Formula OCR | MathPix | $20 | 1000 requests |
| Handwriting OCR | Google Vision | $30 | 5000 pages |
| Backup | Telegram / R2 Glacier | $5 | Cold storage |
| **Total** | | **$110** | |

**Pro tier (cloud AI):** +$50/month for OpenAI API + vLLM GPU ($200/month shared across users)

---

*End of Engineering Specification*
