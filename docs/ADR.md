# Architecture Decision Records

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 1.0.0
**Date:** 2026-06-26
**Status:** Approved
**Author:** Architecture Team

---

## ADR-001: Document Parser — Docling vs. PyPDF2 / pdfplumber

### Status
**Accepted**

### Context
Document parsing is the foundation of the knowledge layer. The parser must convert PDFs, DOCX, PPTX, and EPUBs into structured text that preserves headings, tables, formulas, images, and citations. Poor parsing propagates errors through chunking, embedding, and retrieval.

The original codebase used generic PDF extractors (PyPDF2, pdfplumber) that produced raw text without structure.

### Problem
Generic PDF extractors lose critical document structure:
- Headings become plain text mixed with body paragraphs
- Tables become unformatted text blobs
- Mathematical formulas become garbled characters
- Image captions are separated from images
- Citation links are lost

This structural loss degrades chunk quality, reduces retrieval accuracy, and makes formula extraction impossible.

### Decision
**Adopt Docling** (by IBM Research) as the primary document parser.

Docling produces structured Markdown output with:
- Preserved heading hierarchy (#, ##, ###)
- Tables as Markdown tables
- Formulas as LaTeX
- Images with captions and bounding boxes
- Citation references preserved
- Page numbers and document metadata

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **PyPDF2 / pdfplumber** | Simple, fast, well-known | Loses all structure, formulas garbled, tables destroyed | Rejected — insufficient quality |
| **Apache Tika** | Supports many formats, mature | Heavy (Java dependency), mediocre structure preservation | Rejected — operational complexity |
| **Marker** (by Facebook) | Excellent academic paper parsing | Limited to PDF, no DOCX/PPTX, slower than Docling | Rejected — format coverage insufficient |
| **Unstructured.io** | Cloud API, many formats | Requires API key, not self-hostable, vendor lock-in | Rejected — violates local-first principle |
| **Docling** | Structured Markdown, multi-format, open-source, IBM maintained | Heavier than PyPDF2, slower startup | **Accepted** |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Superior chunk quality (heading-aware) | Larger Docker image (+500MB) |
| Formula preservation (LaTeX) | Slower processing (+30% vs PyPDF2) |
| Table preservation (Markdown) | Requires Python 3.10+ |
| Active maintenance (IBM) | Newer library (less community) |
| Multi-format (PDF, DOCX, PPTX, HTML) | |

### Consequences
- Chunking quality improves significantly (headings respected)
- Formula extraction becomes possible (MathPix on LaTeX output)
- Table extraction becomes possible (Markdown → structured data)
- Processing time increases by ~30% for PDFs
- Docker image size increases by ~500MB

### Future Implications
- If Docling maintenance slows, evaluate Marker as fallback for academic PDFs
- If IBM changes license, evaluate Apache Tika or self-hosted Unstructured
- Future: fine-tune Docling on domain-specific documents (medical, legal)

---

## ADR-002: OCR Engine — Tesseract + Google Vision vs. Single Engine

### Status
**Accepted**

### Context
OCR converts scanned documents and handwritten notes into machine-readable text. Quality varies dramatically by source: printed textbooks are easy, handwritten notes are hard, low-resolution scans are noisy.

### Problem
No single OCR engine handles all scenarios well:
- Tesseract excels at printed text but fails on handwriting and poor scans
- Google Vision handles handwriting but requires API keys and network
- AWS Textract handles tables but is expensive
- MathPix handles formulas but is expensive and slow

### Decision
**Use a multi-engine OCR strategy** with automatic fallback:

1. **Primary**: Tesseract 5.x (local, free, printed text)
2. **Secondary**: Google Vision API (handwriting, poor scans, pro tier only)
3. **Formula**: MathPix API (LaTeX formulas, pro tier only)
4. **Fallback**: If both fail, flag document for manual review

Engine selection is automatic based on:
- Document type (scanned vs. digital)
- Text clarity (confidence score from Tesseract)
- Language (Tesseract supports 100+ languages natively)
- User tier (free = Tesseract only, pro = Google Vision + MathPix)

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Tesseract only** | Free, local, fast, 100+ languages | Fails on handwriting, poor scans, complex tables | Rejected — insufficient quality for all use cases |
| **Google Vision only** | Excellent accuracy, handwriting support | Requires API key, network dependency, cost per page | Rejected — violates local-first principle for free tier |
| **AWS Textract only** | Excellent table extraction | AWS dependency, expensive, complex pricing | Rejected — vendor lock-in, cost |
| **Multi-engine (chosen)** | Best quality per scenario, local-first default, optional cloud | More complex orchestration, pro tier required for cloud OCR | **Accepted** |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Printed text: free, fast, local | Handwriting: requires pro tier |
| Handwriting: excellent (Google Vision) | Google Vision: $1.50 per 1000 pages |
| Formulas: excellent (MathPix) | MathPix: $0.02 per formula |
| Automatic engine selection | More complex pipeline |
| Graceful degradation (always works) | Manual review queue for edge cases |

### Consequences
- Free tier users get Tesseract only (sufficient for 80% of documents)
- Pro tier users get full multi-engine (handwriting, formulas, tables)
- OCR pipeline has 4 exit paths: success, fallback engine, manual review, error
- Processing cost increases for pro tier but quality justifies price

### Future Implications
- Monitor Tesseract 6.x development (may improve handwriting)
- Evaluate PaddleOCR (Baidu) for Chinese language support
- Evaluate self-hosted Google Vision alternative (e.g., EasyOCR for handwriting)

---

## ADR-003: Vector Database — pgvector (Supabase) vs. FAISS vs. Pinecone

### Status
**Accepted**

### Context
The knowledge layer requires vector storage for semantic search. Vectors represent the meaning of text chunks, enabling similarity-based retrieval.

### Problem
- FAISS (current) is in-memory and loses data on restart
- Pinecone is cloud-only and expensive at scale
- pgvector is PostgreSQL-native but may be slower than dedicated vector DBs
- We need persistence, scalability, and multi-tenancy

### Decision
**Use pgvector (Supabase-managed PostgreSQL)** as the vector store.

Index strategy:
- < 1M vectors per user: IVFFlat index (fast build, good recall)
- > 1M vectors per user: HNSW index (slower build, better recall, faster search)
- Partition by user_id for query performance

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **FAISS (current)** | Fast, local, no network | In-memory only, loses data on restart, no multi-tenancy | Rejected — insufficient for production |
| **Pinecone** | Managed, fast, excellent SDK | Cloud-only, expensive ($0.10/GB/hour), vendor lock-in | Rejected — violates local-first principle, cost |
| **Weaviate** | Open-source, GraphQL, hybrid search | Complex to self-host, requires Kubernetes | Rejected — operational complexity |
| **Milvus** | Open-source, distributed, fast | Complex deployment, requires etcd + MinIO | Rejected — operational complexity |
| **pgvector** | PostgreSQL-native, ACID, managed by Supabase, RLS-compatible | Slower than dedicated vector DBs for > 10M vectors | **Accepted** |
| **Chroma** | Simple, embeddable, SQLite-based | Not production-ready, no multi-tenancy | Rejected — immature |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Single database (PostgreSQL) for metadata + vectors | Search latency ~2x slower than FAISS for small datasets |
| ACID transactions (no data loss) | Index build time slower than FAISS |
| Multi-tenancy via RLS (no data leakage) | Memory usage higher than FAISS |
| Managed by Supabase (no ops) | Cost scales with database size |
| SQL queries join vectors + metadata | |
| Hybrid search (vector + keyword) in one query | |

### Consequences
- No separate vector database to manage
- RLS policies apply to vectors automatically
- SQL queries can JOIN chunks with documents, topics, users
- Search latency acceptable for < 1M vectors per user (target: < 200ms)
- If a user exceeds 1M vectors, consider HNSW index or sharding

### Future Implications
- If pgvector performance degrades at > 10M vectors, evaluate Pinecone for enterprise tier
- If Supabase adds vector-specific optimizations, migrate to newer index types
- Consider pgvector + ivfflat → HNSW migration script for growing users

---

## ADR-004: Embedding Model — BAAI/BGE vs. OpenAI text-embedding-3

### Status
**Accepted**

### Context
Text embeddings convert text chunks into dense vectors for semantic search. The model choice affects retrieval quality, processing cost, and privacy.

### Problem
- OpenAI embeddings are high-quality but require API keys, network, and payment
- BAAI/BGE embeddings are free and local but may have lower quality on some domains
- We need a default that works offline and preserves privacy

### Decision
**Use BAAI/bge-large-en-v1.5 as the default embedding model.**

Configuration:
- Model: BAAI/bge-large-en-v1.5
- Dimension: 1024
- Normalization: L2 (required for cosine similarity via inner product)
- Device: CPU (default), CUDA (optional for GPU acceleration)
- Batch size: 32 chunks

**OpenAI text-embedding-3-small is an optional paid provider** for users who prefer cloud quality.

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **OpenAI text-embedding-3-small** | Excellent quality, 1536-dim, fast | Requires API key, paid ($0.02/M tokens), privacy risk | Rejected as default — violates local-first principle |
| **OpenAI text-embedding-3-large** | Best quality, 3072-dim | Expensive ($0.13/M tokens), slower | Rejected as default — too expensive |
| **BAAI/bge-large-en-v1.5** | Free, local, excellent quality, 1024-dim | Slower on CPU, requires model download (~1GB) | **Accepted** |
| **BAAI/bge-base-en-v1.5** | Faster, smaller (~500MB) | Lower quality than large | Rejected — quality is critical |
| **Nomic Embed** | Open-source, 768-dim, multi-modal | Newer, less proven | Rejected — prefer established model |
| **Jina Embeddings** | Open-source, 768-dim, excellent long-context | Requires API or self-host | Rejected — BAAI is more established |
| **all-MiniLM-L6-v2** | Fast, small (~100MB) | Lower quality | Rejected — insufficient for academic content |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Free, no API costs | Initial model download (~1GB) |
| Local, no network dependency | Slower on CPU (~2s per 100 chunks) |
| Privacy-preserving (no data leaves server) | GPU recommended for production |
| Excellent quality on academic content | Not as good as OpenAI on creative writing |
| Active community (BAAI) | |

### Consequences
- Free tier users get full embedding quality without cost
- Pro tier users can optionally switch to OpenAI for marginal quality gain
- Processing time: ~2 seconds per 100 chunks on CPU, ~0.2s on GPU
- Model file size: ~1GB download on first use
- Vector dimension: 1024 (matches pgvector column definition)

### Future Implications
- Evaluate BAAI/bge-m3 (multilingual, 2024) when stable
- Evaluate fine-tuning BAAI on domain-specific corpora (medical, legal, engineering)
- If BAAI quality degrades relative to OpenAI, switch default (with user notification)

---

## ADR-005: LLM Provider — Ollama vs. vLLM vs. OpenAI

### Status
**Accepted**

### Context
The LLM provider generates answers, summaries, and explanations from retrieved knowledge. The provider choice affects cost, latency, quality, and privacy.

### Problem
- OpenAI is high-quality but expensive and privacy-risky
- Ollama is free and local but slow and limited throughput
- vLLM is fast and production-ready but requires GPU infrastructure
- We need a strategy that works for all tiers

### Decision
**Tiered LLM strategy:**

1. **Free tier (default):** Ollama (local, Llama 3.1 8B)
2. **Pro tier (optional):** vLLM (GPU, Llama 3.1 8B, 10x faster)
3. **Enterprise tier (fallback):** OpenAI (GPT-4o-mini, always available)
4. **Circuit breaker:** If primary fails, fallback to next tier

**LLMProvider interface** abstracts all differences. Swap providers by changing config.

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **OpenAI only** | Best quality, always available, no ops | Expensive ($0.15/M input tokens), privacy risk, vendor lock-in | Rejected — violates local-first principle |
| **Ollama only** | Free, local, private, simple | Slow, low throughput, requires GPU for scale | Rejected — insufficient for production scale |
| **vLLM only** | Fast, production-ready, open-source | Requires GPU infrastructure, ops burden | Rejected — too expensive for free tier |
| **Anthropic Claude** | Excellent reasoning, long context | Expensive, API-only | Rejected — not default |
| **Google Gemini** | Multilingual, free tier available | API-only, privacy concerns | Rejected — not default |
| **Tiered (chosen)** | Local-first for free, GPU for pro, cloud fallback | Complex configuration, circuit breaker needed | **Accepted** |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Free tier: zero cost, full privacy | Free tier: slower responses (~5s) |
| Pro tier: 10x faster, GPU quality | Pro tier: GPU cost (~$200/month) |
| Enterprise: always available | Enterprise: cloud costs |
| No vendor lock-in | More complex ops |
| Transparent cost structure | User education needed |

### Consequences
- Free tier users get quality answers but wait ~5 seconds
- Pro tier users get ~500ms responses with GPU
- Circuit breaker ensures 99.9% availability (fallback chain)
- LLMProvider interface enables future providers (SGLang, Groq, etc.)

### Future Implications
- Evaluate vLLM continuous batching for higher throughput
- Evaluate SGLang for structured generation (JSON schema enforcement)
- Evaluate Groq API for ultra-fast inference (if cost-effective)
- Monitor Llama 4 release for quality improvement

---

## ADR-006: Object Storage — Cloudflare R2 vs. AWS S3 vs. Supabase Storage

### Status
**Accepted**

### Context
Raw documents (PDFs, images, etc.) need durable, scalable object storage. The storage must support presigned URLs, lifecycle policies, and cross-region replication.

### Problem
- Supabase Storage is convenient but expensive at scale ($0.021/GB/month + egress fees)
- AWS S3 is the standard but has egress fees and AWS dependency
- Cloudflare R2 is S3-compatible with zero egress fees
- We need cost-effective storage for user-uploaded documents

### Decision
**Use Cloudflare R2 as the primary object storage.**

Configuration:
- Bucket: `adaptive-study-planner-documents`
- Structure: `users/{user_id}/documents/{document_id}/original.pdf`
- Encryption: AES-256 server-side
- Presigned URLs: 5-minute expiry for downloads
- CORS: restricted to `https://adaptive-study-planner.com`
- Lifecycle: delete after user account deletion + 30 days

**Supabase Storage as fallback** for small files (< 1MB) and metadata attachments.

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **AWS S3** | Standard, mature, many tools | Egress fees ($0.09/GB), AWS dependency, complex pricing | Rejected — egress fees expensive at scale |
| **Supabase Storage** | Integrated with auth, simple API | Expensive ($0.021/GB + $0.09/GB egress), smaller ecosystem | Rejected — cost at scale |
| **Cloudflare R2** | Zero egress fees, S3-compatible, cheaper ($0.015/GB) | Newer service, smaller ecosystem | **Accepted** |
| **MinIO (self-hosted)** | Free, S3-compatible, full control | Ops burden, requires infrastructure | Rejected — ops complexity |
| **Backblaze B2** | Cheap ($0.005/GB), free egress | Slower than R2, smaller ecosystem | Rejected — performance |
| **Telegram** | Free, simple API | Not a storage service, no SLA, unreliable | Rejected — only as cold backup |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Zero egress fees (saves ~$0.09/GB) | Newer service (less ecosystem tooling) |
| Cheaper than S3 ($0.015 vs $0.023/GB) | Requires separate auth from Supabase |
| S3-compatible API (drop-in replacement) | Cloudflare dependency |
| Global edge network (fast downloads) | |
| No request fees (vs S3 $0.005/1K requests) | |

### Consequences
- Storage cost: ~50% lower than S3 at equivalent scale
- Egress cost: ~$0 (vs $0.09/GB with S3)
- Requires presigned URL generation in Cloudflare Worker
- Backup strategy: cross-region replication to R2 bucket in secondary region

### Future Implications
- If R2 pricing changes, evaluate Backblaze B2 as alternative
- If multi-cloud is needed, add S3-compatible abstraction layer
- Evaluate R2's "Custom Domains" for branded download URLs

---

## ADR-007: Knowledge Graph — ArangoDB vs. PostgreSQL Graph Tables

### Status
**Provisional — Phase 4**

### Context
Concept relationships (prerequisites, related topics) are best represented as a graph. The graph enables traversal queries like "What are all prerequisites for Thermodynamics?" or "Find related concepts to Integration."

### Problem
- PostgreSQL relational tables can store graph data but traversal is slow (recursive CTEs)
- Dedicated graph databases (Neo4j, ArangoDB) excel at traversals but add infrastructure
- We need to decide if graph queries are common enough to justify a separate database

### Decision (Provisional)
**Phase 3: Use PostgreSQL graph tables** (simple, sufficient for < 10K edges per user)
**Phase 4: Evaluate ArangoDB** if graph traversal performance becomes critical.

PostgreSQL graph schema:
```sql
CREATE TABLE knowledge_edges (
    user_id UUID,
    source_node TEXT,
    target_node TEXT,
    relationship TEXT,
    confidence REAL,
    PRIMARY KEY (user_id, source_node, target_node, relationship)
);
```

Traversal query:
```sql
WITH RECURSIVE prerequisites AS (
    SELECT target_node AS concept FROM knowledge_edges
    WHERE source_node = 'Thermodynamics' AND relationship = 'prerequisite'
    UNION ALL
    SELECT e.target_node FROM knowledge_edges e
    JOIN prerequisites p ON e.source_node = p.concept
    WHERE e.relationship = 'prerequisite'
)
SELECT * FROM prerequisites;
```

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Neo4j** | Native graph, excellent Cypher queries, visualization | Requires separate service, expensive, complex ops | Deferred to Phase 4 |
| **ArangoDB** | Multi-model (documents + graph + search), AQL queries, managed service | Newer, smaller community | Deferred to Phase 4 |
| **PostgreSQL + recursive CTEs** | Single database, no new infrastructure, ACID | Slow for deep traversals (> 3 hops) | **Accepted for Phase 3** |
| **RedisGraph** | Fast, in-memory, Redis-compatible | Deprecated (Redis Labs dropped support) | Rejected — deprecated |

### Trade-offs (PostgreSQL approach)

| Positive | Negative |
|----------|----------|
| No new infrastructure | Traversal > 3 hops: slow (> 100ms) |
| ACID transactions | No native graph visualization |
| RLS policies apply | Complex queries for graph analytics |
| Single backup strategy | |

### Future Implications
- If users have > 10K edges or need > 3-hop traversals, migrate to ArangoDB
- ArangoDB migration: export PostgreSQL edges → ArangoDB import → update queries
- Graph visualization: use D3.js or Cytoscape.js in frontend (not database-dependent)

---

## ADR-008: Retrieval Strategy — Hybrid vs. Dense-Only vs. Sparse-Only

### Status
**Accepted**

### Context
The retrieval layer must find the most relevant chunks for a user query. Pure vector search (dense) finds semantically similar content but misses exact keyword matches. Pure keyword search (sparse) finds exact matches but misses semantic meaning.

### Problem
- Dense retrieval (vector) misses exact phrases like "PV = nRT" (formulas, definitions)
- Sparse retrieval (BM25) misses paraphrases like "what is the gas law?" (synonyms, rephrasing)
- Metadata filtering (subject, document) is necessary for user control
- Graph traversal adds prerequisite context but is slow

### Decision
**Use Hybrid Retrieval with Reciprocal Rank Fusion (RRF).**

Pipeline:
1. Dense retrieval: pgvector similarity search → top 10
2. Sparse retrieval: PostgreSQL BM25 (tsvector) → top 10
3. Metadata filtering: SQL WHERE clause → filter candidates
4. Graph traversal: ArangoDB/PostgreSQL recursive CTE → top 5 related
5. Re-ranking: BAAI/bge-reranker → score all candidates 0-1
6. Fusion: RRF (k=60) → combine all ranks into final score
7. Final output: top 5 chunks with citations

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Dense only** | Simple, fast, semantic understanding | Misses exact keyword matches, formulas, definitions | Rejected — insufficient for academic content |
| **Sparse only** | Fast, exact matches, good for names/dates | Misses paraphrases, synonyms, semantic meaning | Rejected — insufficient for natural language questions |
| **Hybrid (chosen)** | Best of both worlds, robust, handles all query types | More complex, requires multiple indexes | **Accepted** |
| **Hybrid + Graph** | Adds prerequisite context | Slower, adds database query | Accepted as optional (graph traversal can be disabled) |
| **Hybrid + LLM Re-rank** | Best quality | Expensive, requires LLM call per query | Accepted as optional (pro tier) |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Handles all query types (exact, semantic, paraphrase) | More complex pipeline (4+ components) |
| Reduces single-point-of-failure (one engine can fail, others compensate) | Higher latency (~200ms vs 50ms for single engine) |
| Configurable (users can disable graph or re-ranker) | More indexes to maintain |
| RRF is simple and effective | |

### Consequences
- Retrieval latency: ~200ms p95 (acceptable for user-facing queries)
- Requires 3 indexes: pgvector (dense), GIN tsvector (sparse), B-tree (metadata)
- Re-ranker adds ~50ms but significantly improves precision
- Graph traversal adds ~50ms but can be disabled for speed

### Future Implications
- Evaluate late interaction models (ColBERT) for higher precision
- Evaluate query expansion (HyDE) for better recall
- Evaluate learned sparse retrieval (SPLADE) to replace BM25

---

## ADR-009: Chunking Strategy — Semantic vs. Fixed-Size vs. Sliding Window

### Status
**Accepted**

### Context
Documents must be split into chunks for embedding and retrieval. Chunk quality directly affects retrieval accuracy. Poor chunking splits tables, formulas, or logical sections.

### Problem
- Fixed-size chunks (e.g., 512 tokens) split tables and formulas mid-way
- Sliding window chunks create redundancy but don't respect document structure
- Semantic chunks (heading-aware) are better but harder to implement

### Decision
**Use Semantic Chunking with the following rules:**

1. **Primary boundary:** Document headings (h1, h2, h3)
2. **Secondary boundary:** Paragraphs (separated by blank lines)
3. **Never split:** Tables, code blocks, formulas, lists
4. **Chunk size:** 300-800 tokens (target 500)
5. **Overlap:** 80 tokens between consecutive chunks
6. **Metadata per chunk:** heading, page number, document ID, topic, subject

Algorithm:
```python
def semantic_chunk(markdown):
    sections = split_by_headings(markdown)
    for section in sections:
        if len(section) < 300 tokens:
            yield section  # small section = one chunk
        elif len(section) > 800 tokens:
            yield from split_by_paragraphs(section, max_tokens=800, overlap=80)
        else:
            yield section  # medium section = one chunk
```

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Fixed-size (512 tokens)** | Simple, fast, predictable | Splits tables, formulas, mid-sentence | Rejected — degrades retrieval quality |
| **Sliding window (512 tokens, 128 overlap)** | Simple, no context loss | High redundancy, duplicates in index | Rejected — wastes storage, pollutes retrieval |
| **Semantic (heading-aware)** | Respects structure, better retrieval | More complex, requires parser output | **Accepted** |
| **Agentic chunking (LLM-based)** | Best quality, understands content | Expensive, slow, requires LLM per document | Rejected — overkill for Phase 3 |
| **Recursive chunking** | Balanced, configurable | Still can split tables | Rejected — semantic is better |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Tables and formulas preserved intact | Slightly more complex implementation |
| Better retrieval accuracy (+15-20% vs fixed-size) | Variable chunk sizes (harder to optimize batch processing) |
| Metadata-rich chunks (heading, page) | |
| Overlap ensures context continuity | |

### Consequences
- Chunk count varies per document (e.g., 100-page textbook → 200-400 chunks)
- Embedding batch sizes vary (must pad or handle variable lengths)
- Storage per document: ~1MB for 100 pages (text + embeddings + metadata)
- Retrieval quality: significantly better than fixed-size (validated via MRR@10)

### Future Implications
- Evaluate agentic chunking (LLM-based) for Phase 4 if quality plateaus
- Evaluate chunking by semantic similarity (clustering embeddings) for Phase 4
- Evaluate hierarchical chunking (document → chapter → section → paragraph) for Phase 4

---

## ADR-010: Source Confidence Scoring — Rule-Based vs. ML-Based

### Status
**Accepted**

### Context
Not all sources are equally trustworthy. Official exam board documents should be trusted more than random internet blogs. The system must score source confidence for retrieval ranking and user transparency.

### Problem
- ML-based confidence scoring requires training data (expensive, slow)
- Rule-based scoring is transparent but may miss edge cases
- We need a system that is explainable and maintainable

### Decision
**Use Rule-Based Confidence Scoring with explicit, documented rules.**

Rules:
| Source Type | Base Confidence | Cross-Validation Boost |
|-------------|----------------|----------------------|
| Official exam board | 1.00 | +0.10 (if corroborated) |
| Government portal | 0.95 | +0.10 |
| NCERT / Open Edu | 0.90 | +0.10 |
| Trusted publisher | 0.85 | +0.10 |
| Coaching institute | 0.70 | +0.10 |
| User class notes | 0.65 | +0.10 |
| Community content | 0.40 | +0.10 |
| Unverified internet | 0.20 | +0.10 |

**Cross-validation:** If a fact appears in multiple sources, boost confidence by +0.10 (capped at 1.00).

**User override:** Users can manually adjust confidence scores for their documents.

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **ML-based (train classifier)** | Can learn subtle patterns, adapts to user feedback | Requires labeled training data, black box, hard to explain | Rejected — transparency is critical for education |
| **Rule-based (chosen)** | Transparent, explainable, fast, no training | May miss edge cases, requires manual rule updates | **Accepted** |
| **Hybrid (rules + ML)** | Best of both worlds | Complex, still requires training data | Rejected — rules are sufficient for Phase 3 |
| **User-only scoring** | Democratic, community-driven | Susceptible to gaming, inconsistent | Rejected — needs authoritative baseline |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Transparent to users ("Why is this source trusted?") | Requires manual rule updates for new source types |
| Fast (no ML inference needed) | May not capture nuanced quality differences |
| Explainable (compliance-friendly) | |
| User can override | |

### Consequences
- Confidence scores are computed at indexing time (not at query time)
- Scores stored in PostgreSQL metadata column (fast filtering)
- Retrieval filters can use `confidence > 0.7` for high-trust results
- UI shows confidence badges (green/yellow/red) per source

### Future Implications
- If user feedback loop is strong, evaluate Bayesian updating for confidence scores
- If source diversity grows, add ML-based supplement to rules (not replacement)
- Evaluate PageRank-style propagation for source authority (Phase 4)

---

## ADR-011: Processing Architecture — Synchronous vs. Asynchronous

### Status
**Accepted**

### Context
Document processing (OCR → extraction → chunking → embedding → indexing) takes 1-5 minutes for a 100-page PDF. The user cannot wait synchronously.

### Problem
- Synchronous processing blocks the user (poor UX)
- Asynchronous processing requires queue management and status tracking
- We need to balance UX simplicity with architectural complexity

### Decision
**Use Asynchronous Processing with Webhook-Based Status Updates.**

Flow:
1. User uploads document → receives `upload_id` immediately (202 Accepted)
2. Processing pipeline runs in background (Supabase Edge Function)
3. Pipeline updates document status in PostgreSQL (state machine)
4. Frontend polls `GET /documents/:id/status` every 5 seconds
5. When status = "ready", frontend shows notification: "Processing complete!"
6. Optional: Supabase Realtime pushes status updates to frontend (no polling)

**State Machine:**
```
uploaded → validating → extracting → chunking → embedding → indexing → ready
   ↓           ↓            ↓          ↓           ↓          ↓
 error       error        error      error       error      error
```

**Retry Logic:**
- Transient errors: retry 3x with exponential backoff (1s, 2s, 4s)
- Permanent errors: move to dead letter queue, notify user
- Dead letter queue: admin UI for manual reprocessing

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Synchronous (wait for processing)** | Simple, no queue management | User waits 1-5 minutes, HTTP timeout risk, poor UX | Rejected — unacceptable UX |
| **Asynchronous + polling (chosen)** | Good UX, simple to implement, works everywhere | Polling adds load, slight delay in notification | **Accepted** |
| **Asynchronous + WebSocket** | Real-time push, no polling | Requires WebSocket infrastructure, more complex | Rejected — polling is sufficient for Phase 3 |
| **Asynchronous + Server-Sent Events** | Real-time push, simpler than WebSocket | Less supported than polling, requires persistent connection | Rejected — polling is sufficient |
| **Asynchronous + Supabase Realtime** | Real-time push, native to stack | Requires subscription setup, slightly more complex | Accepted as optional enhancement |

### Trade-offs

| Positive | Negative |
|----------|----------|
| User uploads and continues using app immediately | Slight delay before knowledge is searchable (1-5 min) |
| No HTTP timeout risk | Requires status polling or push infrastructure |
| Scalable (can process many documents in parallel) | Requires queue management |
| Failed documents don't block others | Dead letter queue requires admin attention |

### Consequences
- Frontend must handle "processing" state gracefully (show spinner, disable search)
- Backend must handle concurrent processing (queue depth, worker limits)
- PostgreSQL must track processing status per document
- User can upload multiple documents and they process in parallel

### Future Implications
- If polling load becomes significant, migrate to Supabase Realtime (push-based)
- If processing volume exceeds capacity, add queue-based workers (BullMQ, SQS)
- If real-time collaboration is needed, WebSocket infrastructure becomes necessary anyway

---

## ADR-012: Multi-Tenancy Strategy — Row-Level Security vs. Schema Isolation

### Status
**Accepted**

### Context
The platform must support multiple users (tenants) with strict data isolation. Each user's documents, chunks, and knowledge must be invisible to other users.

### Problem
- Schema isolation (one schema per user) is secure but complex and expensive
- Row-level security (RLS) is simpler but requires careful policy design
- We need a balance between security, performance, and operational simplicity

### Decision
**Use Row-Level Security (RLS) with PostgreSQL.**

Design:
- All tables have `user_id UUID REFERENCES auth.users(id)` column
- Every table has RLS policies: `FOR SELECT USING (user_id = auth.uid())`
- Application role (no `BYPASSRLS`) — all queries go through RLS
- No shared tables (no global documents, no public content in user tables)

**Why RLS over schema isolation:**
- Simpler: one schema, one set of indexes, one backup strategy
- Cheaper: no per-user schema overhead
- Faster: no cross-schema joins, no dynamic schema selection
- Scalable: PostgreSQL handles millions of rows with RLS efficiently

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Schema isolation (one schema per user)** | Strongest isolation, independent migrations | Complex, expensive, per-schema overhead, harder to query across users | Rejected — overkill for SaaS |
| **Database isolation (one DB per user)** | Maximum isolation, independent scaling | Extremely expensive, ops nightmare | Rejected — only for enterprise on-premise |
| **Row-Level Security (chosen)** | Simple, cheap, fast, native to PostgreSQL | Requires careful policy design, potential performance impact on complex queries | **Accepted** |
| **Application-level filtering** | Flexible, no database dependency | Error-prone, bypass risk, harder to audit | Rejected — security must be at database level |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Native PostgreSQL feature (no custom code) | Complex queries may need RLS optimization |
| Enforced at database level (cannot be bypassed) | Slight performance overhead (~5-10%) |
| Simple operational model (one schema) | Policy bugs can expose data (must be tested rigorously) |
| Works with connection pooling (PgBouncer) | |

### Consequences
- All SQL queries must include `user_id` or rely on RLS
- All tests must validate RLS policies (test with different user roles)
- Database migrations must not disable RLS accidentally
- Performance: RLS adds ~5-10% overhead on queries (acceptable)

### Future Implications
- If enterprise customers need schema isolation, offer it as a premium add-on
- If RLS performance degrades, evaluate partition by user_id (table partitioning)
- If compliance requires per-user encryption, evaluate column-level encryption (not schema isolation)

---

## ADR-013: Platform Architecture — Cloudflare + Supabase vs. AWS Full Stack

### Status
**Accepted**

### Context
The platform needs a full-stack infrastructure: frontend hosting, API gateway, compute, database, object storage, and edge caching.

### Problem
- AWS is the enterprise standard but complex and expensive
- Supabase is simpler but limited to PostgreSQL/Edge Functions
- Cloudflare is excellent at edge but lacks a database
- We need a combination that is simple, cost-effective, and scalable

### Decision
**Use Cloudflare + Supabase as the primary stack.**

Stack:
- **Frontend:** Cloudflare Pages (static hosting, global CDN)
- **API Gateway:** Cloudflare Worker (edge compute, CORS, rate limiting)
- **Compute:** Supabase Edge Functions (serverless, TypeScript/Deno)
- **Database:** Supabase PostgreSQL + pgvector (managed, RLS)
- **Object Storage:** Cloudflare R2 (S3-compatible, zero egress)
- **Cache:** Upstash Redis (managed, Redis-compatible)
- **Auth:** Supabase Auth (JWT, OAuth, email/password)
- **Monitoring:** Sentry (error tracking) + Cloudflare Analytics

**AWS is used only for:**
- vLLM GPU inference (EC2 g5.xlarge) — if pro tier requires GPU
- Backup storage (S3 Glacier) — if R2 cross-region is insufficient

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **AWS Full Stack (ECS, RDS, S3, CloudFront)** | Enterprise standard, many tools, proven | Complex, expensive, requires DevOps expertise, vendor lock-in | Rejected — too complex for Phase 3 |
| **Vercel + PlanetScale + AWS S3** | Simple frontend, MySQL, good DX | PlanetScale lacks pgvector, Vercel functions limited, cost | Rejected — no vector support |
| **Google Cloud (Cloud Run, Firestore, Cloud Storage)** | Good AI/ML integration, Firebase | Firestore not relational, no vector search, GCP dependency | Rejected — no vector support |
| **Azure (App Service, Cosmos DB, Blob Storage)** | Enterprise friendly, good for .NET | Cosmos DB expensive, complex, not PostgreSQL-compatible | Rejected — complexity |
| **Cloudflare + Supabase (chosen)** | Simple, cost-effective, edge-first, pgvector, no egress fees | Less enterprise recognition, smaller ecosystem | **Accepted** |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Zero egress fees (R2) | Smaller ecosystem than AWS |
| Edge compute (Workers) | Less third-party tooling |
| Managed database (Supabase) | Supabase pricing at scale |
| Simple operational model | |
| Cost-effective for startups | |
| Fast global performance (edge) | |

### Consequences
- Operational simplicity: 2 vendors instead of 5+ (AWS)
- Cost: ~50% lower than equivalent AWS stack at same scale
- Performance: faster for global users (edge network)
- Hiring: engineers may prefer AWS experience on resume
- Risk: vendor lock-in to Cloudflare + Supabase (but both have data portability)

### Future Implications
- If enterprise sales require AWS, offer AWS deployment as an option (same code, different infrastructure)
- If Supabase limits are reached, evaluate self-hosted PostgreSQL + pgvector on AWS RDS
- If Cloudflare Workers limits are reached, evaluate AWS Lambda as fallback

---

## ADR-014: Audio Generation — Kokoro vs. ElevenLabs vs. Coqui

### Status
**Accepted**

### Context
Audio generation (TTS) converts text explanations into narrated lessons. Audio is a major rendering format and must be cached forever after first generation.

### Problem
- ElevenLabs is high-quality but expensive ($5/month for 30 minutes)
- Kokoro is free, local, and high-quality but requires model download
- Coqui is free but lower quality and maintenance is uncertain
- We need a free default with optional paid upgrade

### Decision
**Use Kokoro as the default TTS engine.**

Configuration:
- Model: Kokoro v0.3 (ONNX-based, runs on CPU)
- Voices: `af_heart`, `af_bella`, `af_nicole` (female), `am_michael` (male)
- Speed: 1.0x (default), 0.8x - 1.2x (user-configurable)
- Output: 24kHz WAV → compressed to MP3 (128kbps) for storage
- Cache key: SHA-256 of `{text}:{voice}:{speed}` → never regenerate
- Storage: R2 `users/{user_id}/audio/{cache_key}.mp3`

**ElevenLabs as optional paid provider** (pro tier only).

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **ElevenLabs** | Best quality, many voices, emotion control | Expensive ($5/month), API-only, privacy risk | Rejected as default — violates local-first |
| **Kokoro (chosen)** | Free, local, excellent quality, small model (~300MB) | CPU-only (GPU support limited), fewer voices | **Accepted** |
| **Coqui TTS** | Free, open-source, many models | Lower quality, maintenance uncertain, complex setup | Rejected — quality insufficient |
| **Piper** | Free, local, fast, lightweight | Robotic quality, limited languages | Rejected — quality insufficient |
| **Google Cloud TTS** | Good quality, many languages | API-only, paid, privacy risk | Rejected — not default |
| **Amazon Polly** | Good quality, many voices | API-only, paid, AWS dependency | Rejected — not default |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Free, no API costs | Fewer voices than ElevenLabs |
| Local, no network dependency | No emotion/style control |
| Excellent quality (comparable to ElevenLabs) | CPU usage during generation |
| Cache forever (no regeneration cost) | |
| Privacy-preserving | |

### Consequences
- Audio generation: ~1 second per 10 words of text on CPU
- Cache hit rate: > 95% (most content is reused across study sessions)
- Storage per audio file: ~50KB per minute (MP3 128kbps)
- Pro tier users can switch to ElevenLabs for premium voices

### Future Implications
- Evaluate Kokoro GPU support for faster generation
- Evaluate fine-tuning Kokoro on domain-specific pronunciation (medical terms, chemical names)
- Evaluate multilingual TTS (Kokoro v1.0 promises 10+ languages)
- If ElevenLabs price drops significantly, reconsider as default

---

## ADR-015: Video Rendering — Scene Planner Pipeline vs. Generative AI Diffusion

### Status
**Provisional — Phase 4**

### Context
Video is a powerful learning medium but expensive and complex to generate. The system must produce educational video without relying on generative AI diffusion models (which are costly, inconsistent, and not educationally useful).

### Problem
- Generative AI video (Sora, Runway) is cinematic but expensive and unpredictable
- Educational video needs structure, clarity, and consistency — not cinema
- Manual video creation is too slow for personalized content
- We need a deterministic, cost-effective video pipeline

### Decision
**Use a deterministic Scene Planner + SVG + Animation + TTS pipeline.**

Pipeline:
```
Knowledge Content
│
▼
Scene Planner (deterministic):
  - Parse content into scenes (what to show, what to say, in what order)
  - Each scene: title, text, diagram type, duration, narration text
│
▼
SVG Generator:
  - Generate vector diagrams per scene (graphs, formulas, charts, flowcharts)
  - Use D3.js or custom SVG templates
│
▼
Animation Engine:
  - Apply transitions: fade, slide, highlight, morph
  - Animate SVG elements (path drawing, color transitions, motion)
  - Use CSS animations or SVG SMIL
│
▼
Audio Composer:
  - Generate TTS narration per scene (Kokoro, cached)
  - Stitch audio segments with scene timings
│
▼
Video Composition (ffmpeg):
  - Concatenate scenes (image sequences + audio)
  - Export: MP4 (h.264) or WebM (VP9)
```

**No generative AI diffusion.** Video is a rendering pipeline, not an AI generation task.

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Generative AI diffusion (Sora, Runway)** | Cinematic, impressive | Expensive ($0.01-0.10/second), unpredictable, slow, not educationally useful | Rejected — violates cost and consistency principles |
| **Scene Planner + SVG + Animation (chosen)** | Deterministic, cheap, fast, educational | Less cinematic, requires design templates | **Accepted** |
| **Manual video creation** | Highest quality, fully controlled | Too slow, not scalable | Rejected — not scalable |
| **Screen recording + TTS** | Simple, fast | Not interactive, not reusable | Rejected — not a rendering pipeline |
| **Third-party video API (D-ID, HeyGen)** | Realistic avatars | Expensive, API-only, not educational | Rejected — not educationally useful |

### Trade-offs

| Positive | Negative |
|----------|----------|
| Deterministic (same input → same video) | Less visually impressive than diffusion |
| Fast (~2 min per minute of content) | Requires design templates for each subject |
| Cheap (CPU + ffmpeg, no GPU needed) | Limited to vector graphics (no photorealism) |
| Educationally effective (clear, structured) | |
| Reusable components (scenes, templates) | |

### Consequences
- Video quality is "educational" not "cinematic" (acceptable for the product vision)
- Scene templates must be designed per subject (math, physics, chemistry, biology)
- SVG templates can be community-contributed (open-source asset library)
- Audio is cached (TTS only generated once per narration text)

### Future Implications
- If user research shows demand for cinematic video, evaluate diffusion as an optional renderer (not default)
- If scene templates grow, create a marketplace for educational SVG templates
- Evaluate WebCodecs API for browser-side video composition (no server needed)
- Evaluate HLS streaming for long videos (adaptive bitrate)

---

*End of Architecture Decision Records*
