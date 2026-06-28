# Engineering Specification

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 2.1.0
**Date:** 2026-06-27
**Status:** Approved — Phase 4 Enterprise Active
**Product:** Adaptive Study Planner v4.1.0-ENTERPRISE
**Author:** Engineering Team

---

## 1. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Vanilla JavaScript + Tailwind CSS | UI, PWA |
| Backend API | Cloudflare Workers | API gateway, rate limiting, CORS |
| AI Orchestration | Supabase Edge Functions | AI pipeline, document processing |
| Database | Supabase PostgreSQL + pgvector | Data persistence, vector search |
| Cache | Upstash Redis (or self-hosted Redis) | Rate limiting, JWT blacklist, query cache, embedding cache |
| Object Storage | Cloudflare R2 (primary) | Document storage |
| Backup | Cloudflare R2 (cross-region) + Telegram (optional cold) | Disaster recovery |
| AI Inference | Ollama (local) / vLLM (cloud) / OpenAI (optional) | LLM, embeddings, reranking |
| OCR | Tesseract 5.x (local) / Google Vision (pro) | Text extraction |
| Formula OCR | MathPix (pro) | LaTeX conversion |
| Authentication | Supabase Auth (JWT) | User management |
| Monitoring | Sentry + Grafana | Error tracking, metrics |
| **CI/CD** | **GitHub Actions** | **Lint, test, security scan, deploy** |
| **IaC** | **Terraform / Cloudflare Wrangler** | **Infrastructure as code** |
| **Tracing** | **OpenTelemetry + Jaeger** | **Distributed tracing** |
| **Log Storage** | **S3 Glacier / R2** | **Cold log archival** |

---

## 2. Component Architecture

### 2.1 Upload Service

```
+-----------------------------------+
|         Upload Service            |
+-----------------------------------+
|  +-----------------------------+  |
|  | FileValidator               |  |
|  | - magic numbers             |  |
|  | - size limits               |  |
|  | - virus scan (ClamAV)       |  |
|  +-----------------------------+  |
|  +-----------------------------+  |
|  | DuplicateDetector           |  |
|  | - SHA-256 hash              |  |
|  | - perceptual hash (pHash)   |  |
|  +-----------------------------+  |
|  +-----------------------------+  |
|  | ChunkedUploader             |  |
|  | - 5MB chunks                |  |
|  | - resume support            |  |
|  | - parallel upload           |  |
|  +-----------------------------+  |
|  +-----------------------------+  |
|  | R2Uploader                  |  |
|  | - presigned URLs            |  |
|  | - multipart upload          |  |
|  +-----------------------------+  |
+-----------------------------------+
         |           |          |
    R2   |     PostgreSQL   |   Redis
```

**API:**
- `POST /api/v3/upload` — Multi-file upload, returns upload_id
- `POST /api/v3/upload/chunk` — Chunked upload (5MB segments), returns chunk_id
- `GET /api/v3/upload/:id/progress` — Upload progress percentage
- `GET /api/v3/upload/:id/status` — Upload status (pending, uploading, complete, error)

**State Machine:**
```
PENDING → UPLOADING → VALIDATING → SCANNING → COMPLETE
  |           |          |          |         |
  +----------->+---------->+---------->+         |
  |           |          |          |         |
  +-- ERROR (dead letter queue) <---+         |
```

### 2.2 Document Validation Service

**Responsibilities:**
- File type validation (magic numbers via python-magic)
- File size validation (per-file and per-batch limits)
- Virus scanning (ClamAV daemon or cloud-native)
- File integrity check (corruption detection)
- Encoding detection (chardet / charset-normalizer)
- Language detection (langdetect / fastText for 10+ languages)
- Password-protected file detection and rejection
- Executable content detection (embedded in PDFs)

**Validation Rules:**
| Check | Action on Failure | Retry |
|-------|-------------------|-------|
| Magic number mismatch | Reject with error code | No |
| Size > 100MB | Reject with error code | No |
| Virus detected | Quarantine, notify user | No |
| Corrupted file | Reject, suggest re-upload | No |
| Password protected | Reject, request unlocked copy | No |
| Unknown encoding | Process as UTF-8 with warning | No |
| Low confidence language | Process with default (English) | No |

### 2.3 OCR Service

**Multi-Engine Strategy:**
```
Document Upload
  |
  +---> Is it an image/scanned PDF?
  |       |
  |       YES
  |       |
  |       +---> Tesseract 5.x (primary, free, local)
  |       |     |
  |       |     +---> Confidence > 85%? → Success
  |       |     |
  |       |     +---> Confidence 60-85%? → Flag warning
  |       |     |
  |       |     +---> Confidence < 60%? → Try Google Vision
  |       |           |
  |       |           +---> Pro tier? → Google Vision
  |       |           |     |
  |       |           |     +---> Success or Manual Review
  |       |           |
  |       |           +---> Free tier? → Manual Review
  |       |
  |       +---> Contains formulas?
  |             |
  |             +---> MathPix (pro tier) → LaTeX
  |             |
  |             +---> Free tier? → Tesseract formula mode
  |       |
  |       NO (digital PDF) → Skip OCR, go to Parsing
```

**OCR Engines:**
| Engine | Use Case | Accuracy | Cost | Availability |
|--------|----------|----------|------|-------------|
| Tesseract 5.x | Printed text, 100+ languages | > 85% | Free | Always |
| Google Vision | Handwriting, poor scans | > 70% | $1.50/1K pages | Pro tier |
| MathPix | Formulas, LaTeX | > 80% | $0.02/formula | Pro tier |
| Custom (future) | Diagrams, tables | TBD | TBD | Phase 4 |

### 2.4 Document Processing Service

**Responsibilities:**
- PDF parsing (Docling → structured Markdown)
- DOCX parsing (python-docx)
- PPTX parsing (python-pptx)
- EPUB parsing (ebooklib)
- Image extraction (PIL, extract embedded images)
- Table extraction (detect structure, convert to Markdown tables)
- Formula extraction (preserve LaTeX, detect inline/display math)
- Diagram extraction (detect diagrams, extract as SVG with captions)
- Text cleaning (remove headers, footers, watermarks, normalize whitespace)
- Structure preservation (headings, lists, paragraphs, citations)

**Parsing Pipeline:**
```
Input: Validated document
  |
  +---> Docling Parser (PDF/DOCX/PPTX/EPUB)
  |     |
  |     +---> Structured Markdown output
  |     |
  |     +---> Heading hierarchy (h1, h2, h3)
  |     |
  |     +---> Table structures (rows, columns, headers)
  |     |
  |     +---> Formula annotations (LaTeX blocks)
  |     |
  |     +---> Image locations (page, coordinates)
  |
  +---> Text Cleaner
  |     |
  |     +---> Remove headers/footers (regex patterns)
  |     |
  |     +---> Remove watermarks (repeated text detection)
  |     |
  |     +---> Normalize whitespace (collapse multiple spaces)
  |     |
  |     +---> Preserve citations (author-date, numeric)
  |
  +---> Output: Clean Markdown with metadata
```

### 2.5 Knowledge Extraction Service

**Extracts from parsed documents:**
- Topics (subject classification, heading hierarchy)
- Chapters (heading-level 1/2/3 detection)
- Concepts (key terms + definitions via LLM)
- Definitions (concept explanations)
- Learning objectives (inferred from chapter summaries)
- Formulae (LaTeX expressions, detected via regex + LLM)
- Examples (worked problems, case studies)
- Questions (MCQ, fill-in-blank, short answer from PYQs)
- Difficulty (formula density, language complexity, question structure)
- Prerequisites (topic dependency chains via LLM)
- Metadata (author, publisher, edition, page count, source type)

**Extraction Prompts:**
| Extraction Type | LLM Prompt | Output Format |
|-----------------|------------|---------------|
| Concepts | "Extract key concepts and definitions from this text" | JSON array: [{"concept", "definition", "confidence"}] |
| Formulas | "Detect all mathematical formulas and convert to LaTeX" | JSON array: [{"formula", "latex", "context"}] |
| Questions | "Extract all questions (MCQ, fill-in-blank, short answer)" | JSON array: [{"type", "question", "answer", "options"}] |
| Prerequisites | "What topics must a student know before understanding this?" | JSON array: [{"prerequisite", "confidence"}] |
| Difficulty | "Rate the difficulty of this content from 1-5" | JSON: {"score", "reasoning"} |

### 2.6 Semantic Chunking Service

**Chunking Rules:**
1. Primary boundary: Document headings (h1, h2, h3)
2. Secondary boundary: Paragraphs (separated by blank lines)
3. Never split: Tables, code blocks, formulas, lists
4. Chunk size: 300-800 tokens (target 500)
5. Overlap: 80 tokens between consecutive chunks
6. Metadata per chunk: heading, page number, document ID, topic, subject, chunk level
7. Parent/child relationships: document → chapter → section → paragraph
8. Adaptive size: dense content (formulas) → smaller chunks; prose → larger chunks

**Chunk Hierarchy:**
```
document_id
  |
  +---> chunk_level_1 (chapter)
  |       |
  |       +---> chunk_level_2 (section)
  |       |       |
  |       |       +---> chunk_level_3 (paragraph)
  |       |       |       |
  |       |       |       +---> chunk_level_4 (sub-paragraph)
```

### 2.7 Embedding Service

**Model Configuration:**
- Default: BAAI/bge-large-en-v1.5 (1024-dim, free, local)
- Optional: OpenAI text-embedding-3-small (1536-dim, paid, cloud)
- Batch size: 32 chunks
- Normalization: L2 (for cosine similarity via inner product)
- Device: CPU (default), CUDA (optional)
- Cache: Redis (24h TTL, key = SHA-256 of chunk text)
- Incremental: only re-embed changed chunks

**Embedding Pipeline:**
```
Clean Chunks
  |
  +---> Check Redis Cache (SHA-256 key)
  |     |
  |     +---> Cache hit? → Return cached embedding
  |     |
  |     +---> Cache miss? → Generate embedding
  |
  +---> Batch Processor (32 chunks per batch)
  |     |
  |     +---> BAAI/BGE (default, local)
  |     |
  |     +---> OpenAI (optional, pro tier)
  |
  +---> L2 Normalization
  |
  +---> Store in pgvector
  |
  +---> Update Redis Cache
```

### 2.8 Knowledge Graph Service

**Graph Schema (PostgreSQL):**
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

**Graph Traversal (PostgreSQL recursive CTE):**
```sql
WITH RECURSIVE prerequisites AS (
    SELECT target_node AS concept, 1 AS depth
    FROM knowledge_edges
    WHERE source_node = 'Thermodynamics' 
      AND relationship = 'prerequisite'
      AND user_id = '...'
    
    UNION ALL
    
    SELECT e.target_node, p.depth + 1
    FROM knowledge_edges e
    JOIN prerequisites p ON e.source_node = p.concept
    WHERE e.relationship = 'prerequisite'
      AND e.user_id = '...'
      AND p.depth < 5
)
SELECT * FROM prerequisites;
```

**Graph Traversal (ArangoDB - Phase 4):**
```aql
FOR v, e, p IN 1..5 OUTBOUND 'concepts/Thermodynamics' GRAPH 'knowledge_graph'
  FILTER e.relationship == 'prerequisite'
  RETURN {concept: v.name, depth: LENGTH(p.edges), confidence: e.confidence}
```

### 2.9 Hybrid Retrieval Engine

**Architecture:**
```
User Query
  |
  +---> Intent Detection (classify: definition, problem, comparison, summary)
  |     |
  |     +---> Definition query → Dense + Graph
  |     +---> Problem query → Sparse + Metadata
  |     +---> Comparison query → Dense + Sparse + Graph
  |     +---> Summary query → Dense + Metadata
  |
  +---> Query Planning (select strategy based on intent)
  |
  +---> Parallel Retrieval (fork-join)
  |     |
  |     +---> Dense Retrieval (pgvector, top 10)
  |     |     |
  |     |     +---> SELECT * FROM chunks
  |     |           ORDER BY embedding <-> query_embedding
  |     |           LIMIT 10;
  |     |
  |     +---> Sparse Retrieval (BM25, top 10)
  |     |     |
  |     |     +---> SELECT * FROM chunks
  |     |           WHERE text_search @@ to_tsquery('english', query)
  |     |           ORDER BY ts_rank(text_search, query) DESC
  |     |           LIMIT 10;
  |     |
  |     +---> Graph Traversal (prerequisites, top 5)
  |     |     |
  |     |     +---> Recursive CTE on knowledge_edges
  |     |           WHERE source_node = query_concept
  |     |           LIMIT 5;
  |     |
  |     +---> Metadata Filtering (pre-filter)
  |           |
  |           +---> WHERE subject = 'Physics' 
  |                 AND confidence > 0.7
  |                 AND created_at > '2024-01-01'
  |
  +---> Combine Results (deduplicate, merge scores)
  |
  +---> Re-ranking (BAAI/bge-reranker, cross-encoder)
  |     |
  |     +---> Score each candidate 0-1
  |
  +---> Source Ranking (boost by confidence)
  |     |
  |     +---> Official sources: ×1.5
  |     +---> Publisher sources: ×1.2
  |     +---> Community sources: ×0.8
  |
  +---> Reciprocal Rank Fusion (RRF, k=60)
  |     |
  |     +---> score = Σ(1 / (k + rank_i))
  |
  +---> Final Output: Top 5 chunks with citations
```

**Latency Targets:**
| Stage | Target | Max |
|-------|--------|-----|
| Intent Detection | 10ms | 20ms |
| Dense Retrieval | 50ms | 100ms |
| Sparse Retrieval | 30ms | 50ms |
| Metadata Filtering | 20ms | 30ms |
| Graph Traversal | 50ms | 100ms |
| Re-ranking | 50ms | 100ms |
| Source Ranking | 10ms | 20ms |
| RRF Fusion | 5ms | 10ms |
| **Total** | **225ms** | **430ms** |
| **Cache Hit** | **50ms** | **100ms** |

### 2.10 Citation Service

**Responsibilities:**
- Extract citation markers [1], [2] from LLM output
- Verify each citation against retrieved chunks
- Format citations with source name, page, confidence
- Handle missing citations (flag as invented)
- Generate evidence trace (claim → chunk → document → page → confidence)
- Produce citation summary table per response

**Citation Format:**
```
[1] Physics Textbook, Chapter 3, Page 42, Confidence: 0.92
[2] NCERT Class 12, Page 156, Confidence: 0.88
[3] User Class Notes, Page 5, Confidence: 0.65
```

**Verification Algorithm:**
```python
def verify_citations(response, retrieved_chunks):
    citations = re.findall(r'\[(\d+)\]', response)
    verified = []
    for citation in citations:
        idx = int(citation) - 1  # [1] → index 0
        if 0 <= idx < len(retrieved_chunks):
            verified.append({
                "index": citation,
                "chunk_id": retrieved_chunks[idx].id,
                "verified": True,
                "confidence": retrieved_chunks[idx].confidence
            })
        else:
            verified.append({
                "index": citation,
                "verified": False,
                "flag": "INVENTED_CITATION"
            })
    return verified
```

---

## 3. Data Flow

### 3.1 Document Upload & Processing Flow

```
User (Browser)
  | POST /api/v3/upload (multipart, JWT)
  v
Cloudflare Worker
  | Validate JWT, rate limit
  v
Upload Service
  | Validate file (magic, size, virus)
  | Check duplicates (SHA-256, pHash)
  | Stream to R2: users/{uid}/docs/{id}/original.pdf
  | Insert document record (status: "uploaded")
  v
Processing Pipeline (async, Supabase Edge Function)
  | Stage 1: Validation → Virus Scan → Encoding → Language
  | Stage 2: OCR (if scanned) → Text Extraction
  | Stage 3: Parsing (Docling) → Structured Markdown
  | Stage 4: Cleaning (headers, footers, watermarks)
  | Stage 5: Metadata Extraction (topics, chapters, concepts, formulas, questions)
  | Stage 6: Difficulty Classification
  | Stage 7: Duplicate Removal (across documents)
  | Stage 8: Semantic Chunking (heading-aware, 300-800 tokens, 80 overlap)
  | Stage 9: Embedding (BAAI/BGE, 1024-dim, batch 32)
  | Stage 10: Knowledge Graph Construction (concepts → prerequisites → edges)
  | Stage 11: Vector Index (pgvector IVFFlat / HNSW)
  | Stage 12: Full-Text Index (PostgreSQL GIN tsvector)
  | Stage 13: Metadata Index (document properties, tags, status)
  | Stage 14: Status = "ready"
  v
PostgreSQL (update document status)
  | WebSocket push to client
  v
User (Browser)
  | Sees "Processing complete! X topics, Y concepts, Z formulas"
```

### 3.2 Q&A Flow (Grounded AI)

```
User (Browser)
  | POST /api/v3/ask (question, filters, JWT)
  v
Cloudflare Worker
  | Validate JWT, rate limit
  v
Hybrid Retrieval Engine
  | Intent Detection (query type)
  | Query Planning (strategy selection)
  | Dense Retrieval (pgvector, top 10)
  | Sparse Retrieval (BM25, top 10)
  | Metadata Filtering (subject, document, confidence)
  | Graph Traversal (prerequisites, related)
  | Re-ranking (BAAI/bge-reranker)
  | Source Ranking (confidence boost)
  | RRF Fusion (top 5)
  v
Context Builder
  | Assemble top 5 chunks with citations
  | Format: "Context: [1] ... [2] ... [3] ..."
  v
LLM (Ollama / vLLM / OpenAI)
  | Prompt: "Answer using ONLY the context below. Cite [n]. ..."
  | Temperature: 0.3
  | Generate response
  v
Citation Service
  | Extract [1], [2] from LLM output
  | Verify each against retrieved chunks
  | Flag invented citations
  | Format evidence trace
  v
PostgreSQL (log query, retrieval, response, verification)
  v
User (Browser)
  | Sees: AI response + citations [1], [2] + confidence scores
```

### 3.3 Zero-Upload Auto-Setup Flow

```
User (Browser)
  | POST /api/v3/setup/auto (exam, board, country, subjects, year, JWT)
  v
Cloudflare Worker
  | Validate JWT, rate limit
  v
Web Resource Collector
  | Query exam database (100+ exams)
  | Search official websites (polite, rate-limited)
  | Search DuckDuckGo/Google (fallback)
  | Rank resources by source confidence
  v
PostgreSQL (store found_resources, status: "pending_approval")
  v
User (Browser)
  | GET /api/v3/setup/resources
  | Sees: ranked list of resources with confidence scores
  | Approves/rejects each resource
  v
Cloudflare Worker
  | POST /api/v3/setup/approve (resource_ids)
  v
Processing Pipeline
  | Download approved resources
  | Validate, OCR, Parse, Extract, Chunk, Embed, Index
  v
PostgreSQL (status: "ready")
  v
User (Browser)
  | Sees: "Auto-setup complete! X resources imported."
```

### 3.4 Knowledge Graph Query Flow

```
User (Browser)
  | GET /api/v3/knowledge/graph?subject=Physics
  v
Cloudflare Worker
  | Validate JWT
  v
Knowledge Graph Service
  | Query nodes: SELECT * FROM concepts WHERE user_id = ... AND subject = 'Physics'
  | Query edges: SELECT * FROM knowledge_edges WHERE user_id = ...
  | Traverse prerequisite chains (recursive CTE, max depth 5)
  | Calculate learning path optimization (shortest path)
  | Detect concept gaps (missing prerequisites for target topics)
  v
PostgreSQL
  v
User (Browser)
  | Sees: Interactive graph (D3.js/Cytoscape.js)
  | Nodes: concepts, topics, formulas
  | Edges: prerequisites, related, part-of
  | Clickable: definition, source, confidence
```

---

## 4. API Specification

### New Endpoints (v4.1.0)

| Endpoint | Method | Auth | Description | Rate Limit |
|----------|--------|------|-------------|----------|
| `/api/v3/upload` | POST | JWT | Multi-file upload | 100/min |
| `/api/v3/upload/chunk` | POST | JWT | Chunked upload (5MB) | 100/min |
| `/api/v3/upload/:id/progress` | GET | JWT | Upload progress | 100/min |
| `/api/v3/documents` | GET | JWT | List user documents | 100/min |
| `/api/v3/documents/:id` | GET | JWT | Document metadata | 100/min |
| `/api/v3/documents/:id/reprocess` | POST | JWT | Re-trigger pipeline | 10/min |
| `/api/v3/documents/:id/download` | GET | JWT | Download original | 50/min |
| `/api/v3/documents/:id/chunks` | GET | JWT | List chunks | 100/min |
| `/api/v3/ask` | POST | JWT | Grounded AI Q&A | 100/min |
| `/api/v3/search` | POST | JWT | Hybrid search | 200/min |
| `/api/v3/retrieve` | POST | JWT | Raw retrieval | 200/min |
| `/api/v3/knowledge/topics` | GET | JWT | Topic hierarchy | 100/min |
| `/api/v3/knowledge/concepts` | GET | JWT | Concepts list | 100/min |
| `/api/v3/knowledge/graph` | GET | JWT | Knowledge graph | 50/min |
| `/api/v3/generate/flashcards` | POST | JWT | Generate flashcards | 50/min |
| `/api/v3/generate/quiz` | POST | JWT | Generate quiz | 50/min |
| `/api/v3/generate/summary` | POST | JWT | AI summary | 50/min |
| `/api/v3/generate/plan` | POST | JWT | Study plan from KB | 50/min |
| `/api/v3/setup/auto` | POST | JWT | Zero-upload setup | 10/min |
| `/api/v3/setup/resources` | GET | JWT | Found resources | 50/min |
| `/api/v3/health` | GET | None | Health check | Unlimited |

### Example: POST /api/v3/ask

**Request:**
```json
{
  "question": "What is the ideal gas law?",
  "filters": {
    "subject": "Physics",
    "documents": ["doc-123", "doc-456"],
    "confidence_min": 0.7
  },
  "max_tokens": 1024
}
```

**Response:**
```json
{
  "answer": "The ideal gas law states that PV = nRT [1], where P is pressure, V is volume, n is the number of moles, R is the gas constant, and T is temperature [2].",
  "citations": [
    {
      "index": 1,
      "chunk_id": "chunk-789",
      "document_id": "doc-123",
      "document_name": "Physics Textbook",
      "page": 42,
      "confidence": 0.92,
      "verified": true
    },
    {
      "index": 2,
      "chunk_id": "chunk-790",
      "document_id": "doc-456",
      "document_name": "NCERT Class 12",
      "page": 156,
      "confidence": 0.88,
      "verified": true
    }
  ],
  "grounding_score": 1.0,
  "retrieval_time_ms": 150,
  "generation_time_ms": 800
}
```

---

## 5. Security Architecture

### 5.1 Authentication Flow

```
User Login
  |
  +---> OAuth 2.0 (Google, GitHub) → Supabase Auth
  |     |
  |     +---> JWT (RS256, 1-hour expiry)
  |     |
  |     +---> Refresh token (7-day expiry)
  |
  +---> SAML 2.0 / LDAP (Enterprise SSO)
  |     |
  |     +---> Identity Provider (IdP) → SAML Assertion
  |     |
  |     +---> JWT generation from SAML attributes
  |
  +---> API Keys (Programmatic Access)
        |
        +---> Scoped: read, write, admin
        +---> Rotation: 90 days
        +---> Revocation: immediate
```

### 5.2 Authorization (RBAC)

| Role | Permissions |
|------|-------------|
| **user** | CRUD own documents, search own knowledge base, generate flashcards/quizzes, view analytics |
| **editor** | user + edit shared topics, add comments, manage group content |
| **admin** | editor + manage group members, view group analytics, moderate content |
| **system** | Internal service-to-service auth, read all data for processing |
| **enterprise** | admin + SAML SSO, API access, custom branding, dedicated support |

### 5.3 Row-Level Security (RLS)

All tables must have RLS policies:
```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access their own documents"
ON documents FOR ALL
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Service role can access all documents"
ON documents FOR ALL
TO service_role
USING (true);
```

### 5.4 Data Encryption

| Layer | Method | Key Management |
|-------|--------|---------------|
| Transport | TLS 1.3 | Let's Encrypt auto-renew |
| At Rest (R2) | AES-256 | Cloudflare-managed keys |
| At Rest (PostgreSQL) | AES-256 | Supabase-managed keys |
| Field-Level (PII) | AES-256-GCM | User-specific keys, KMS rotation |
| Document Content | AES-256-GCM | User-specific encryption keys (zero-knowledge) |

---

## 6. Storage Architecture

### 6.1 Object Storage (R2)

```
Bucket: adaptive-study-planner-documents
  |
  +---> users/{user_id}/
  |     |
  |     +---> documents/{document_id}/
  |     |     |
  |     |     +---> original.pdf (raw upload)
  |     |     +---> extracted.md (parsed text)
  |     |     +---> thumbnails/page-{n}.jpg (page previews)
  |     |
  |     +---> audio/{cache_key}.mp3 (TTS audio)
  |     |
  |     +---> exports/{export_id}/
  |     |     +---> knowledge-base.json
  |     |     +---> study-guide.md
  |     |     +---> flashcards.apkg
  |     |
  |     +---> backups/{date}/
  |           +---> document-{id}-v{version}.pdf
  |
  +---> system/
        +---> models/ (BAAI/BGE model files)
        +---> cache/ (temporary processing files)
```

### 6.2 Metadata Database (PostgreSQL)

**documents table:**
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

**chunks table (with pgvector):**
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
    chunk_level INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**knowledge_edges table:**
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

### 6.3 Vector Database (pgvector)

```sql
-- IVFFlat index (for < 1M vectors)
CREATE INDEX idx_chunks_embedding_ivfflat 
ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- HNSW index (for > 1M vectors, Phase 4)
CREATE INDEX idx_chunks_embedding_hnsw 
ON chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Full-text search index
CREATE INDEX idx_chunks_text_search 
ON chunks USING GIN (to_tsvector('english', text));

-- Metadata indexes
CREATE INDEX idx_chunks_user_id ON chunks(user_id);
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_heading ON chunks(heading);
```

### 6.4 Knowledge Graph (PostgreSQL → ArangoDB)

**Phase 3 (PostgreSQL):**
- Single `knowledge_edges` table with recursive CTE traversal
- Sufficient for < 10K edges per user
- Latency: < 100ms for 3-hop traversal

**Phase 4 (ArangoDB migration):**
- Multi-model graph database
- AQL queries for complex traversals
- Native graph visualization support
- Migration script: export PostgreSQL edges → ArangoDB import → update queries

### 6.5 Telegram Cold Storage

**Purpose:** Optional off-site backup for raw documents

**Benefits:**
- Free unlimited storage
- Cloud-independent (not R2, not AWS)
- Simple API (HTTP POST with file)
- Preserves original file format

**Limitations:**
- Not a storage service (no SLA)
- No search capability
- Manual recovery only (requires admin intervention)
- 2GB file size limit per file
- Recovery is slow (download via Telegram API)
- Privacy concerns (Telegram's encryption model)

**Recovery Flow:**
1. Admin triggers recovery for user_id + document_id
2. Bot searches Telegram channel for matching caption
3. Bot downloads file to temporary storage
4. System validates file (SHA-256 checksum, magic numbers)
5. If valid, file is restored to R2 and re-indexed
6. If invalid, admin is notified for manual intervention

---

## 7. AI Pipeline Architecture

### 7.1 Document Processing Pipeline (13 Stages)

```
Upload
  |
  +---> [Stage 1] Validation
  |     | Magic numbers, size, virus scan
  |     | [FAIL] → Dead Letter Queue
  |
  +---> [Stage 2] Virus Scan
  |     | ClamAV or cloud-native
  |     | [FAIL] → Quarantine, notify user
  |
  +---> [Stage 3] Encoding Detection
  |     | chardet / charset-normalizer
  |     | [FAIL] → Process as UTF-8 with warning
  |
  +---> [Stage 4] Language Detection
  |     | fastText / langdetect
  |     | [FAIL] → Default to English
  |
  +---> [Stage 5] OCR (if scanned/image)
  |     | Tesseract → Google Vision (fallback)
  |     | [FAIL] → Flag for manual review
  |
  +---> [Stage 6] Parsing
  |     | Docling → Structured Markdown
  |     | [FAIL] → Corrupted document queue
  |
  +---> [Stage 7] Cleaning
  |     | Remove headers, footers, watermarks
  |     | Normalize whitespace
  |
  +---> [Stage 8] Metadata Extraction
  |     | Topics, chapters, concepts, formulas, questions
  |     | Difficulty classification
  |
  +---> [Stage 9] Duplicate Removal
  |     | SHA-256 + pHash across documents
  |     | Deduplicate chunks
  |
  +---> [Stage 10] Semantic Chunking
  |     | Heading-aware, 300-800 tokens, 80 overlap
  |     | Parent/child relationships
  |
  +---> [Stage 11] Embedding
  |     | BAAI/BGE (default) or OpenAI (optional)
  |     | Batch 32, L2 normalized, Redis cache
  |
  +---> [Stage 12] Knowledge Graph Construction
  |     | Concepts → Prerequisites → Relationships
  |     | Edge confidence scoring
  |
  +---> [Stage 13] Indexing
  |     | Vector index (pgvector)
  |     | Full-text index (GIN tsvector)
  |     | Metadata index (B-tree)
  |
  +---> Status = "ready"
```

**Failure & Retry:**
- Transient errors (network, rate limit): retry 3x with exponential backoff (1s, 2s, 4s)
- Permanent errors (corrupted file, unsupported format): move to dead letter queue, notify user
- Low OCR confidence (< 60%): flag for manual review, mark "ready_with_warnings"
- Virus detected: reject, quarantine, notify user
- Duplicate detected: offer "replace existing" or "keep both"

### 7.2 Retrieval Pipeline

```
User Query
  |
  +---> [1] Intent Detection
  |     | Classify: definition, problem, comparison, summary, quiz_request
  |     | Model: lightweight classifier (BERT-tiny or rule-based)
  |
  +---> [2] Query Planning
  |     | Select strategy based on intent
  |     | Definition → Dense + Graph
  |     | Problem → Sparse + Metadata
  |     | Comparison → Dense + Sparse + Graph
  |
  +---> [3] Parallel Retrieval (fork-join)
  |     |
  |     +---> Dense: pgvector similarity (top 10)
  |     +---> Sparse: BM25 tsvector (top 10)
  |     +---> Graph: Prerequisite traversal (top 5)
  |     +---> Metadata: SQL WHERE pre-filtering
  |
  +---> [4] Combine & Deduplicate
  |     | Merge results from all engines
  |     | Remove duplicates (same chunk from multiple engines)
  |
  +---> [5] Re-ranking
  |     | BAAI/bge-reranker cross-encoder
  |     | Score each candidate 0-1
  |
  +---> [6] Source Ranking
  |     | Boost by confidence: official ×1.5, publisher ×1.2, community ×0.8
  |
  +---> [7] Reciprocal Rank Fusion (RRF, k=60)
  |     | score = Σ(1 / (k + rank_i))
  |
  +---> [8] Context Assembly
  |     | Top 5 chunks formatted for LLM
  |     | Include citations and metadata
  |
  +---> [9] LLM Generation
  |     | Strict grounding prompt
  |     | Temperature: 0.3
  |
  +---> [10] Citation Verification
  |     | Extract [1], [2] from LLM output
  |     | Verify against retrieved chunks
  |     | Flag invented citations
  |
  +---> [11] Final Response
        | Answer + citations + confidence scores + evidence trace
```

---

## 8. Sequence Diagrams

### 8.1 Document Upload & Processing (Full Pipeline)

```
User    Browser    Worker    R2    PostgreSQL    Edge Function    Redis
 |         |         |      |         |              |             |
 |--drag drop-->|     |      |         |              |             |
 |         |--POST /upload->| |         |              |             |
 |         |     |--validate JWT-->|     |              |             |
 |         |     |--rate limit check->|  |              |             |
 |         |     |--upload file->|     |              |             |
 |         |     |     |--stream->|   |              |             |
 |         |     |     |         |--insert doc-->|     |             |
 |         |     |     |         |--status: uploaded-->|            |
 |         |     |--202 Accepted-->|   |              |             |
 |         |<--show progress--|    |   |              |             |
 |         |     |     |         |--trigger webhook-->|            |
 |         |     |     |         |              |--process stage 1-13|
 |         |     |     |         |              |--update status-->|
 |         |     |     |         |--status: ready-->|             |
 |         |<--WebSocket: ready--| |              |             |
 |         |<--show results--|    |              |             |
```

### 8.2 Zero-Upload Exam Setup

```
User    Browser    Worker    PostgreSQL    Web Scraper    DuckDuckGo
 |         |         |         |              |             |
 |--enter exam-->|   |         |              |             |
 |         |--POST /setup/auto->| |            |             |
 |         |     |--query exam DB-->|          |             |
 |         |     |     |--return exam metadata-->|          |
 |         |     |     |         |--search official sites-->| |
 |         |     |     |         |              |--return results|
 |         |     |     |--store found_resources-->|          |
 |         |<--return ranked resources--|        |             |
 |--approve resources-->| |         |              |             |
 |         |--POST /setup/approve->| |          |             |
 |         |     |     |--download & process-->|            |
 |         |     |     |--status: ready-->|     |             |
 |         |<--completion notification--|      |             |
```

### 8.3 Hybrid Retrieval Execution

```
User    Browser    Worker    PostgreSQL    Redis    LLM
 |         |         |         |             |       |
 |--ask question-->|  |         |             |       |
 |         |--POST /ask->|     |             |       |
 |         |     |--intent detection->|        |       |
 |         |     |--query cache check->|     |       |
 |         |     |     |--cache hit?-->      |       |
 |         |     |     |     |               |       |
 |         |     |     |     |--cache miss-->|       |
 |         |     |     |     |               |       |
 |         |     |--parallel retrieval-------->|       |
 |         |     |     |--dense + sparse + graph-->  |
 |         |     |     |--return candidates-->|     |
 |         |     |--re-rank + source rank-->|  |     |
 |         |     |--RRF fusion-->|          |       |
 |         |     |--assemble context-->|      |       |
 |         |     |--generate with LLM-------->|       |
 |         |     |     |     |               |--response|
 |         |     |--verify citations-->|      |       |
 |         |     |--cache response-->        |       |
 |         |<--return answer + citations--| |       |
```

### 8.4 Knowledge Graph Query

```
User    Browser    Worker    PostgreSQL
 |         |         |         |
 |--view graph-->|   |         |
 |         |--GET /knowledge/graph->|     |
 |         |     |--query concepts-->|     |
 |         |     |--query edges-->|      |
 |         |     |--traverse prerequisites-->| |
 |         |     |     |--return graph data-->| |
 |         |<--return nodes + edges--|     |
 |         |<--render D3.js graph--|      |
```

---

## 9. Deployment Architecture

### 9.1 Environment Strategy

| Environment | Purpose | Database | AI | Storage |
|-------------|---------|----------|-----|---------|
| Local | Developer testing | Local PostgreSQL + pgvector | Local Ollama | Local MinIO |
| Dev | Feature testing | Supabase dev project | Local Ollama | R2 dev bucket |
| Staging | Pre-release validation | Supabase staging | vLLM (GPU) | R2 staging bucket |
| Production | Live users | Supabase production | vLLM (GPU) + OpenAI fallback | R2 production bucket |

### 9.2 CI/CD Pipeline (GitHub Actions)

```
Push to main
  |
  +---> [1] Lint (ESLint, flake8, black)
  |
  +---> [2] Unit Tests (pytest, jest)
  |     | Coverage ≥ 80%
  |
  +---> [3] Security Scan (bandit, safety, Trivy, OWASP ZAP)
  |     | 0 critical/high vulnerabilities
  |
  +---> [4] Integration Tests (pytest integration/)
  |     | 100% API endpoints tested
  |
  +---> [5] AI Evaluation (Ollama, benchmark dataset)
  |     | MRR@10 > 0.6, Precision@5 > 0.7
  |
  +---> [6] Deploy to Staging
  |     | Terraform apply / Wrangler deploy
  |
  +---> [7] E2E Tests (Cypress)
  |     | 100% critical user flows
  |
  +---> [8] Performance Tests (k6)
  |     | 200 concurrent users, < 1% error
  |
  +---> [9] Manual Approval (production deploy)
  |
  +---> [10] Deploy to Production
        | Terraform apply / Wrangler deploy
        | Database migration (reversible)
        | Feature flags (launch darkly)
```

### 9.3 Infrastructure as Code

| Component | Tool | Files |
|-----------|------|-------|
| Cloudflare Workers | Wrangler | `wrangler.toml` |
| R2 Buckets | Terraform | `terraform/r2.tf` |
| D1 / KV / Cache | Wrangler CLI | `wrangler.toml` |
| Supabase | Supabase CLI | `supabase/config.toml` |
| Monitoring | Terraform | `terraform/grafana.tf` |

---

## 10. Scaling Strategy

### 10.1 Horizontal Scaling

| Component | Scaling Strategy | Trigger |
|-----------|------------------|---------|
| Cloudflare Workers | Auto-scale (serverless) | Traffic |
| Supabase Edge Functions | Auto-scale (serverless) | Traffic |
| PostgreSQL | Read replicas, PgBouncer | Connection count > 100 |
| pgvector | IVFFlat → HNSW, partitioning | Vector count > 1M |
| Redis | Upstash auto-scale | Memory > 80% |
| R2 | Unlimited (object storage) | Storage |
| Ollama | Kubernetes HPA | GPU utilization > 80% |
| vLLM | Kubernetes HPA | GPU utilization > 80% |

### 10.2 Connection Pooling

```
Application → PgBouncer → PostgreSQL
  |
  +---> Pool size: 20 connections per app instance
  +---> Max connections: 200 per database
  +---> Transaction pooling mode
  +---> Idle timeout: 300s
```

### 10.3 Read Replicas

```
Write → Primary PostgreSQL (us-east-1)
  |
Read → Replica 1 (us-east-1)
Read → Replica 2 (eu-west-1)
Read → Replica 3 (ap-south-1)
```

---

## 11. Monitoring & Observability

### 11.1 Metrics

| Metric | Type | Target | Alert |
|--------|------|--------|-------|
| Processing success rate | Gauge | > 99.5% | P0 if < 99% |
| Processing latency p95 | Histogram | < 5 min | P1 if > 10 min |
| Retrieval latency p95 | Histogram | < 200ms | P1 if > 500ms |
| AI response latency | Histogram | < 2s | P1 if > 5s |
| Cache hit rate | Gauge | > 80% | P2 if < 60% |
| OCR accuracy | Gauge | > 85% | P2 if < 80% |
| Retrieval precision@5 | Gauge | > 80% | P0 if < 70% |
| Hallucination rate | Counter | 0% | P0 if > 0% |
| Citation accuracy | Gauge | 100% | P0 if < 100% |
| Active users | Counter | 10,000 | — |
| Documents processed | Counter | 100,000/month | — |
| Knowledge graph edges | Counter | 10M total | — |

### 11.2 Distributed Tracing

```
Request ID (correlation ID)
  |
  +---> Cloudflare Worker (trace span: gateway)
  +---> PostgreSQL (trace span: database)
  +---> Redis (trace span: cache)
  +---> R2 (trace span: storage)
  +---> Edge Function (trace span: processing)
  +---> LLM (trace span: inference)
```

**Tools:** OpenTelemetry SDK → Jaeger → Grafana

### 11.3 Alerts

| Priority | Channel | Response Time | Examples |
|----------|---------|---------------|----------|
| P0 | PagerDuty + Phone | 15 min | Database down, R2 outage, security breach |
| P1 | Slack #alerts | 1 hour | Latency > 500ms, processing failures > 1% |
| P2 | Slack #warnings | 4 hours | Cache hit rate < 60%, OCR accuracy < 80% |
| P3 | Email digest | 24 hours | Minor performance degradation, non-critical errors |

---

## 12. Error Handling & Retry Strategy

### 12.1 Retry Logic

| Service | Max Retries | Backoff | Strategy | Fallback |
|---------|------------|---------|----------|----------|
| PostgreSQL | 3 | 1s, 2s, 4s | Exponential | Read replica |
| R2 | 3 | 1s, 2s, 4s | Exponential | S3 |
| Redis | 3 | 500ms, 1s, 2s | Exponential | In-memory cache |
| LLM (Ollama) | 3 | 2s, 4s, 8s | Exponential | vLLM → OpenAI |
| OCR (Tesseract) | 2 | 1s, 2s | Exponential | Google Vision |
| MathPix | 3 | 1s, 2s, 4s | Exponential | Skip formula extraction |
| Google Vision | 3 | 1s, 2s, 4s | Exponential | Manual review queue |
| DuckDuckGo | 2 | 2s, 4s | Exponential | Google Search |

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

## 13. Disaster Recovery

### 13.1 Backup Strategy

| Component | Frequency | Retention | Location | Method |
|-----------|-----------|-----------|----------|--------|
| PostgreSQL | Daily | 7 days | Cross-region R2 | pg_dump |
| PostgreSQL | Hourly | 24 hours | Same region | WAL archiving |
| R2 Documents | Real-time | 30 days | Cross-region R2 | Replication |
| Redis | Daily | 7 days | R2 | RDB snapshot |
| Telegram | On upload | Unlimited | Telegram | Bot API |

### 13.2 Recovery Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| RPO (Recovery Point Objective) | < 1 hour | Max data loss |
| RTO (Recovery Time Objective) | < 4 hours | Max downtime |
| Database restore | < 2 hours | From latest backup |
| Document restore | < 1 hour | From R2 cross-region |
| Telegram recovery | < 24 hours | Manual admin process |

### 13.3 Runbooks

| Scenario | Runbook | Link |
|----------|---------|------|
| PostgreSQL primary failure | Failover to read replica | `runbooks/db-failover.md` |
| R2 outage | Switch to S3 fallback | `runbooks/r2-outage.md` |
| LLM service down | Enable OpenAI fallback | `runbooks/llm-failover.md` |
| DDoS attack | Enable Cloudflare WAF rules | `runbooks/ddos-response.md` |
| Data breach | Incident response plan | `runbooks/security-incident.md` |
| Telegram backup recovery | Manual recovery process | `runbooks/telegram-recovery.md` |

---

## 14. Cross-Document Traceability

| Engineering Section | PRD | ADR | AI Dev Spec | Test Spec |
|---------------------|-----|-----|-------------|-----------|
| 2.1 Upload Service | FR-01 | — | E-015 | 3.7, 10 |
| 2.2 Validation | FR-02 | — | E-016 | 3.8, 8.1 |
| 2.3 OCR | FR-03 | ADR-015 | E-017 | 3.9, 9.2 |
| 2.4 Parsing | FR-04 | ADR-001 | E-018 | 3.10, 9.3 |
| 2.5 Extraction | FR-07 | — | E-019 | 3.5, 9.6 |
| 2.6 Chunking | FR-05 | ADR-011 | E-019 | 3.12, 9.4 |
| 2.7 Embedding | FR-06 | ADR-016 | E-020 | 3.11, 9.5 |
| 2.8 Knowledge Graph | FR-08 | ADR-012 | E-021 | 3.20, 9.6 |
| 2.9 Hybrid Retrieval | FR-09 | ADR-009 | E-022 | 3.13, 3.14, 9.1 |
| 2.10 Citation | FR-12 | ADR-018 | E-024 | 3.17, 9.8 |
| 3.3 Auto-Setup | FR-13 | — | E-023 | 3.21, 10 |
| 5 Security | 12 | — | E-014 | 8 |
| 6 Storage | 6 | ADR-010 | E-014 | 3.10 |
| 7 Pipeline | 4, 8 | — | E-019 | 3.5, 9.6 |
| 11 Monitoring | 13 | — | E-026 | 6, 7 |
| 12 Error Handling | 6 | — | E-026 | 6.3 |
| 13 Disaster Recovery | 6 | ADR-014 | — | 6.3, 9.9 |

---

*End of Engineering Specification*
