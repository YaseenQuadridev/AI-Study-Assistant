# AI Development Specification

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 1.0.0
**Date:** 2026-06-26
**Status:** Draft — Ready for Sprint Planning
**Author:** Engineering & AI Teams

---

## 1. Milestones

| Milestone | Target | Duration | Key Deliverables |
|-----------|--------|----------|-----------------|
| **M1: Foundation** | Week 2 | 2 weeks | Upload pipeline, basic OCR, chunking, embeddings |
| **M2: Intelligence** | Week 4 | 2 weeks | Hybrid retrieval, knowledge extraction, AI grounding |
| **M3: Auto-Setup** | Week 6 | 2 weeks | Exam database, web scraping, auto-resource collection |
| **M4: UX** | Week 8 | 2 weeks | Document management UI, search, knowledge visualization |
| **M5: Scale** | Week 10 | 2 weeks | Multi-language, image/PPTX, EPUB, mobile PWA, performance |
| **M6: Ecosystem** | Week 12 | 2 weeks | LMS integration, API v2, collaboration, monetization |

---

## 2. Epics & Features

### Epic E-001: Document Ingestion Pipeline
**Goal:** Accept, validate, and store any educational document.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-001.1 | Multi-format Upload | Drag-and-drop for PDF, DOCX, TXT, EPUB, images, ZIP | M |
| F-001.2 | File Validation | Magic number check, virus scan, size limits, duplicate detection | M |
| F-001.3 | R2 Object Storage | Stream to Cloudflare R2 with presigned URLs | M |
| F-001.4 | Upload Progress | Real-time progress bar, resumable uploads | S |
| F-001.5 | Document Metadata | Extract filename, size, page count, MIME type | S |

### Epic E-002: OCR & Text Extraction
**Goal:** Convert any document into clean, structured text.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-002.1 | Printed Text OCR | Tesseract 5.x for scanned PDFs and images | M |
| F-002.2 | Handwritten OCR | Google Vision API for handwritten notes | M |
| F-002.3 | Formula Extraction | MathPix for mathematical expressions → LaTeX | M |
| F-002.4 | Table Detection | Extract tables as Markdown/HTML tables | M |
| F-002.5 | Image Captioning | Detect images, extract with captions | S |
| F-002.6 | Text Cleaning | Remove headers, footers, watermarks, normalize whitespace | S |
| F-002.7 | Language Detection | Detect document language (10 languages) | S |

### Epic E-003: Semantic Chunking
**Goal:** Split documents into context-preserving, metadata-rich chunks.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-003.1 | Heading-Aware Chunking | Split at h1/h2/h3 boundaries, never split tables/formulas | M |
| F-003.2 | Paragraph Chunking | Split large sections by paragraph with overlap | S |
| F-003.3 | Chunk Metadata | Assign heading, page number, document ID, topic, subject | S |
| F-003.4 | Chunk Size Control | 300-800 tokens, 80-token overlap, configurable | S |

### Epic E-004: Embedding Generation
**Goal:** Convert chunks into searchable dense vectors.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-004.1 | BAAI/BGE Embedding | Generate 1024-dim vectors, L2 normalize | M |
| F-004.2 | OpenAI Fallback | Optional provider for pro tier | S |
| F-004.3 | Batch Processing | 32 chunks per batch, async queue | S |
| F-004.4 | Embedding Cache | Cache in Redis, never re-embed unchanged content | S |
| F-004.5 | pgvector Storage | Insert into Supabase with IVFFlat/HNSW index | M |

### Epic E-005: Knowledge Extraction
**Goal:** Extract concepts, definitions, formulas, questions from chunks.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-005.1 | Concept Extraction | Identify key terms and definitions | M |
| F-005.2 | Formula Detection | Detect and catalog mathematical formulas | M |
| F-005.3 | Question Bank Extraction | Extract MCQs, fill-in-blank, short answer from PYQs | M |
| F-005.4 | Learning Objectives | Infer objectives from headings and summaries | M |
| F-005.5 | Prerequisite Detection | Identify topic dependency relationships | L |
| F-005.6 | Difficulty Estimation | Estimate from question complexity, formula density | L |

### Epic E-006: Knowledge Organization
**Goal:** Structure extracted knowledge into browsable hierarchies.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-006.1 | Topic Hierarchy | Subject → Chapter → Topic → Subtopic tree | M |
| F-006.2 | Knowledge Graph | Nodes (concepts) + edges (prerequisite, related, part-of) | L |
| F-006.3 | Metadata Index | Document properties, tags, upload date, processing status | S |
| F-006.4 | Full-Text Index | PostgreSQL tsvector for keyword search | M |

### Epic E-007: Hybrid Retrieval
**Goal:** Find the most relevant knowledge for any query.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-007.1 | Dense Retrieval | pgvector similarity search (top-10) | M |
| F-007.2 | Sparse Retrieval | PostgreSQL BM25 full-text search (top-10) | M |
| F-007.3 | Metadata Filtering | SQL WHERE on subject, document, confidence, date | S |
| F-007.4 | Graph Traversal | Follow prerequisite chains (PostgreSQL recursive CTE) | M |
| F-007.5 | Re-Ranking | BAAI/bge-reranker cross-encoder | M |
| F-007.6 | RRF Fusion | Reciprocal Rank Fusion (k=60) | S |
| F-007.7 | Query Cache | Cache frequent queries in Redis (1h TTL) | S |

### Epic E-008: AI Grounding & Generation
**Goal:** Generate AI responses strictly grounded in retrieved knowledge.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-008.1 | Prompt Template | "Answer using ONLY the context below. Cite [n]." | S |
| F-008.2 | Citation Extraction | Parse [1], [2] from LLM output | S |
| F-008.3 | Citation Verification | Verify cited chunks exist in retrieved results | S |
| F-008.4 | Grounded Answer | Return answer + structured citations | M |
| F-008.5 | "I Don't Know" | Honest response when no relevant content found | S |
| F-008.6 | Source Confidence | Filter citations by confidence threshold (> 0.50) | S |

### Epic E-009: Exam Auto-Setup
**Goal:** Build knowledge bases automatically from official resources.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-009.1 | Exam Database | Curate 100+ top exams with metadata | M |
| F-009.2 | Web Scraping | Polite crawling of official sites for syllabus/PYQs | L |
| F-009.3 | Resource Search | DuckDuckGo/Google search for official resources | M |
| F-009.4 | User Approval | Present found resources, allow selection | S |
| F-009.5 | Auto-Processing | Download, validate, process approved resources | M |
| F-009.6 | Source Confidence | Auto-assign confidence scores to found resources | S |

### Epic E-010: User Management & UX
**Goal:** Enable users to manage documents and interact with knowledge.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-010.1 | Document CRUD | Upload, view, delete, replace, reprocess | M |
| F-010.2 | Document Organization | Folders, tags, favorites | S |
| F-010.3 | Search UI | Full-text + semantic search with filters | M |
| F-010.4 | Knowledge Visualization | Topic tree, concept graph, document map | L |
| F-010.5 | Processing Status | Real-time status updates (polling / Realtime) | M |
| F-010.6 | Document Preview | Thumbnails, page previews, extracted text | S |

### Epic E-011: Content Generation
**Goal:** Generate learning materials from knowledge base.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-011.1 | Flashcard Generation | Extract key terms → Q&A pairs | M |
| F-011.2 | Quiz Generation | Generate MCQ, true/false, short answer from content | M |
| F-011.3 | Summary Generation | AI-generated summaries per topic/document | M |
| F-011.4 | Revision Plan Integration | Feed extracted topics into existing planner | M |
| F-011.5 | Export | Anki deck, PDF, Markdown export | S |

### Epic E-012: Multi-Language & Format Support
**Goal:** Support diverse content types and languages.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-012.1 | Multi-Language OCR | English, Spanish, Hindi, Mandarin, Arabic, French, German, Portuguese, Russian, Japanese | L |
| F-012.2 | Image Support | JPG, PNG, TIFF, HEIC upload and OCR | M |
| F-012.3 | PPTX Support | Extract slides and speaker notes | M |
| F-012.4 | EPUB Support | Extract chapters and metadata | M |
| F-012.5 | ZIP Folder Upload | Recursive extraction and processing | S |

### Epic E-013: Security & Compliance
**Goal:** Ensure data privacy, security, and regulatory compliance.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-013.1 | RLS Policies | Row-level security on all tables | M |
| F-013.2 | Data Encryption | AES-256 at rest, TLS 1.3 in transit | S |
| F-013.3 | GDPR Compliance | Data portability, right to erasure, consent management | M |
| F-013.4 | Audit Trails | Immutable logs of all user and system actions | M |
| F-013.5 | Rate Limiting | Per-IP and per-user rate limits | S |
| F-013.6 | Virus Scanning | ClamAV or cloud-native scanning | S |

### Epic E-014: DevOps & Infrastructure
**Goal:** Deploy, monitor, and scale the platform reliably.

| Feature | ID | Description | Complexity |
|---------|-----|-------------|------------|
| F-014.1 | Edge Function Deployment | Deploy Supabase Edge Functions | S |
| F-014.2 | Cloudflare Worker | API gateway, CORS, rate limiting | M |
| F-014.3 | Database Migrations | Schema versioning, rollback capability | M |
| F-014.4 | CI/CD Pipeline | GitHub Actions: lint, test, security scan, deploy | M |
| F-014.5 | Monitoring & Alerting | Sentry + Cloudflare Analytics + custom dashboards | M |
| F-014.6 | Backup & DR | Daily backups, cross-region replication, runbooks | M |

---

## 3. User Stories & Engineering Tasks

### Story US-001: Upload PDF Documents
**As a** student, **I want to** drag and drop my PDF notes, **so that** they become part of my AI knowledge base.

**Backend Tasks:**
- [ ] BE-001.1: Create `POST /upload` endpoint (multipart/form-data, JWT validation)
- [ ] BE-001.2: Implement `FileValidator` (magic numbers, size limits, virus scan)
- [ ] BE-001.3: Implement `R2Uploader` (stream to Cloudflare R2 with presigned URLs)
- [ ] BE-001.4: Insert document record into PostgreSQL (status: "uploaded")
- [ ] BE-001.5: Trigger processing pipeline webhook (async)
- [ ] BE-001.6: Implement `GET /documents/:id/status` endpoint
- [ ] BE-001.7: Implement `DuplicateDetector` (SHA-256 + perceptual hash)

**Frontend Tasks:**
- [ ] FE-001.1: Create drag-and-drop upload zone component
- [ ] FE-001.2: Show upload progress bar per file
- [ ] FE-001.3: Display upload status (uploading / processing / ready / error)
- [ ] FE-001.4: Show duplicate detection warning
- [ ] FE-001.5: Handle validation errors (file type, size, virus)

**AI Tasks:**
- [ ] AI-001.1: No AI tasks (upload is deterministic)

**Testing Tasks:**
- [ ] TE-001.1: Unit test `FileValidator` with valid/invalid files
- [ ] TE-001.2: Integration test upload → R2 → PostgreSQL
- [ ] TE-001.3: E2E test drag-and-drop upload flow

**Definition of Done:**
- User can upload 1-10 PDFs via drag-and-drop
- Files are stored in R2 with correct path
- PostgreSQL records are created with correct metadata
- Processing pipeline is triggered automatically
- Status endpoint returns correct state
- Duplicate detection works for identical files
- All tests pass

---

### Story US-002: OCR on Scanned Notes
**As a** student with handwritten notes, **I want to** upload scanned images, **so that** the AI can read my handwriting.

**Backend Tasks:**
- [ ] BE-002.1: Implement `OCRPipeline` with Tesseract (primary) and Google Vision (fallback)
- [ ] BE-002.2: Implement engine selection logic (printed vs. handwritten vs. formula)
- [ ] BE-002.3: Store OCR text alongside original image in R2
- [ ] BE-002.4: Log OCR confidence scores per page
- [ ] BE-002.5: Flag low-confidence results (< 60%) for manual review
- [ ] BE-002.6: Implement MathPix integration for formula extraction

**Frontend Tasks:**
- [ ] FE-002.1: Show OCR confidence badge per document (green/yellow/red)
- [ ] FE-002.2: Display extracted text alongside original image
- [ ] FE-002.3: Allow manual correction of low-confidence OCR
- [ ] FE-002.4: Show processing stage: "OCR in progress..."

**AI Tasks:**
- [ ] AI-002.1: Configure Tesseract 5.x with language packs (English, Spanish, Hindi, etc.)
- [ ] AI-002.2: Benchmark OCR accuracy on sample documents (printed vs. handwritten)
- [ ] AI-002.3: Evaluate Google Vision accuracy on handwritten samples
- [ ] AI-002.4: Evaluate MathPix formula extraction accuracy

**Testing Tasks:**
- [ ] TE-002.1: Unit test OCR engine selection logic
- [ ] TE-002.2: Integration test Tesseract on printed PDF samples
- [ ] TE-002.3: Integration test Google Vision on handwritten samples
- [ ] TE-002.4: Accuracy test: compare OCR output to ground truth
- [ ] TE-002.5: Benchmark processing time per page

**Definition of Done:**
- Printed text OCR accuracy > 85% on sample documents
- Handwritten OCR accuracy > 70% on clear samples
- Formula extraction accuracy > 80% on math samples
- Low-confidence pages are flagged for manual review
- Processing time < 2 seconds per page (printed), < 5 seconds (handwritten)
- All tests pass

---

### Story US-003: Semantic Chunking
**As a** student, **I want to** my documents split into meaningful chunks, **so that** the AI retrieves complete ideas, not broken sentences.

**Backend Tasks:**
- [ ] BE-003.1: Implement `SemanticChunker` with heading-aware splitting
- [ ] BE-003.2: Implement paragraph chunking for large sections
- [ ] BE-003.3: Implement overlap logic (80 tokens)
- [ ] BE-003.4: Implement chunk metadata extraction (heading, page, document ID)
- [ ] BE-003.5: Insert chunks into PostgreSQL with metadata

**Frontend Tasks:**
- [ ] FE-003.1: Display chunk count per document in document list
- [ ] FE-003.2: Show sample chunks in document preview
- [ ] FE-003.3: Allow manual merge/split of chunks

**AI Tasks:**
- [ ] AI-003.1: No AI tasks (chunking is deterministic)

**Testing Tasks:**
- [ ] TE-003.1: Unit test heading-aware chunking on sample Markdown
- [ ] TE-003.2: Unit test paragraph chunking on large sections
- [ ] TE-003.3: Verify no table/formula splits in chunks
- [ ] TE-003.4: Benchmark chunk quality (MRR@10 on retrieval)

**Definition of Done:**
- Chunks respect heading boundaries (no mid-heading splits)
- Chunks respect table/formula boundaries (no mid-table splits)
- Chunk size: 300-800 tokens (95% of chunks in range)
- Overlap: 80 tokens between consecutive chunks
- Metadata includes heading, page number, document ID
- All tests pass

---

### Story US-004: Embedding Generation
**As a** student, **I want to** my chunks converted into searchable vectors, **so that** semantic search finds related concepts even with different wording.

**Backend Tasks:**
- [ ] BE-004.1: Implement `BAAIEmbeddingProvider` (load model, batch embed)
- [ ] BE-004.2: Implement `OpenAIEmbeddingProvider` (optional fallback)
- [ ] BE-004.3: Implement batch processing (32 chunks per batch)
- [ ] BE-004.4: Implement embedding cache (Redis, 24h TTL)
- [ ] BE-004.5: Insert embeddings into pgvector with L2 normalization
- [ ] BE-004.6: Create IVFFlat index on embedding column

**Frontend Tasks:**
- [ ] FE-004.1: Show embedding status in document processing tracker
- [ ] FE-004.2: Display "AI-ready" badge when embeddings complete

**AI Tasks:**
- [ ] AI-004.1: Download and configure BAAI/bge-large-en-v1.5 model (~1GB)
- [ ] AI-004.2: Benchmark embedding quality (cosine similarity on related chunks)
- [ ] AI-004.3: Benchmark processing speed (chunks per second on CPU vs GPU)

**Testing Tasks:**
- [ ] TE-004.1: Unit test embedding generation for sample chunks
- [ ] TE-004.2: Verify L2 normalization (magnitude ≈ 1.0)
- [ ] TE-004.3: Verify pgvector insert and search
- [ ] TE-004.4: Benchmark retrieval precision@5 on test queries
- [ ] TE-004.5: Test cache hit/miss behavior

**Definition of Done:**
- BAAI model loads successfully on first use
- Embeddings are L2 normalized
- Batch processing: 32 chunks per batch, < 2s per batch on CPU
- Cache: unchanged chunks are not re-embedded
- pgvector search returns results in < 200ms
- Retrieval precision@5 > 70% on test queries
- All tests pass

---

### Story US-005: Knowledge Extraction
**As a** student, **I want to** the AI to extract key concepts from my documents, **so that** I can review them as flashcards.

**Backend Tasks:**
- [ ] BE-005.1: Implement `KnowledgeExtractor` using LLM with structured output
- [ ] BE-005.2: Define JSON schema for extracted concepts
- [ ] BE-005.3: Implement formula detection and LaTeX extraction
- [ ] BE-005.4: Implement question bank extraction from PYQs
- [ ] BE-005.5: Implement prerequisite relationship detection
- [ ] BE-005.6: Implement difficulty estimation
- [ ] BE-005.7: Store extracted knowledge in PostgreSQL

**Frontend Tasks:**
- [ ] FE-005.1: Display extracted concepts in document view
- [ ] FE-005.2: Show concept map (nodes and edges)
- [ ] FE-005.3: Allow editing of extracted concepts
- [ ] FE-005.4: Show formula gallery per document

**AI Tasks:**
- [ ] AI-005.1: Design prompt template for concept extraction
- [ ] AI-005.2: Design prompt template for formula extraction
- [ ] AI-005.3: Design prompt template for question extraction
- [ ] AI-005.4: Design prompt template for prerequisite detection
- [ ] AI-005.5: Benchmark extraction accuracy on sample documents
- [ ] AI-005.6: Implement structured output parsing (JSON schema validation)

**Testing Tasks:**
- [ ] TE-005.1: Unit test structured output parsing
- [ ] TE-005.2: Integration test concept extraction on sample PDF
- [ ] TE-005.3: Accuracy test: compare extracted concepts to ground truth
- [ ] TE-005.4: Verify formula extraction accuracy on math samples
- [ ] TE-005.5: Verify prerequisite detection on topic chains

**Definition of Done:**
- Concept extraction accuracy > 80% on sample documents
- Formula extraction accuracy > 80% on math samples
- Question extraction accuracy > 70% on PYQ samples
- Prerequisite detection accuracy > 60% (hard task)
- Structured output is validated against JSON schema
- All tests pass

---

### Story US-006: Hybrid Retrieval
**As a** student, **I want to** search my knowledge base with natural language, **so that** I find relevant content even when my wording differs from the document.

**Backend Tasks:**
- [ ] BE-006.1: Implement `DenseRetriever` (pgvector similarity search)
- [ ] BE-006.2: Implement `SparseRetriever` (PostgreSQL BM25 tsvector)
- [ ] BE-006.3: Implement `MetadataFilter` (SQL WHERE clause generation)
- [ ] BE-006.4: Implement `GraphTraverser` (PostgreSQL recursive CTE)
- [ ] BE-006.5: Implement `ReRanker` (BAAI/bge-reranker cross-encoder)
- [ ] BE-006.6: Implement `FusionEngine` (RRF with k=60)
- [ ] BE-006.7: Implement `QueryCache` (Redis, hash of query + filters)
- [ ] BE-006.8: Implement `CitationFormatter` (format [1] with source info)

**Frontend Tasks:**
- [ ] FE-006.1: Create search bar with autocomplete suggestions
- [ ] FE-006.2: Display search results with snippet previews
- [ ] FE-006.3: Show filters (subject, document, date range, confidence)
- [ ] FE-006.4: Highlight search terms in results
- [ ] FE-006.5: Show result scores and source confidence badges

**AI Tasks:**
- [ ] AI-006.1: Configure BAAI/bge-reranker model for cross-encoding
- [ ] AI-006.2: Benchmark retrieval precision@5 on test queries
- [ ] AI-006.3: Benchmark retrieval recall@10 on test queries
- [ ] AI-006.4: Compare hybrid vs. dense-only vs. sparse-only on MRR@10

**Testing Tasks:**
- [ ] TE-006.1: Unit test dense retrieval (cosine similarity)
- [ ] TE-006.2: Unit test sparse retrieval (BM25 scoring)
- [ ] TE-006.3: Unit test RRF fusion (known rankings)
- [ ] TE-006.4: Integration test full hybrid pipeline
- [ ] TE-006.5: Performance test: latency < 200ms p95 for 1000 queries
- [ ] TE-006.6: Accuracy test: precision@5 > 80% on test set

**Definition of Done:**
- Dense retrieval: pgvector similarity search, < 100ms per query
- Sparse retrieval: BM25 full-text search, < 50ms per query
- Metadata filtering: SQL WHERE clause, < 20ms per query
- Re-ranking: cross-encoder scoring, < 50ms per query
- Fusion: RRF combines all sources, final ranking coherent
- End-to-end latency: < 200ms p95 for 1000 queries
- Precision@5: > 80% on test query set
- All tests pass

---

### Story US-007: AI Grounded Answers
**As a** student, **I want to** ask questions and get answers only from my documents, **so that** I don't learn content outside my syllabus.

**Backend Tasks:**
- [ ] BE-007.1: Implement `AIOrchestrator` (query → retrieve → prompt → generate)
- [ ] BE-007.2: Implement prompt template with strict grounding instructions
- [ ] BE-007.3: Implement citation extraction and verification
- [ ] BE-007.4: Implement "I don't know" detection (no relevant chunks)
- [ ] BE-007.5: Implement source confidence filtering (confidence > 0.50)
- [ ] BE-007.6: Implement response caching (Redis, 1h TTL)

**Frontend Tasks:**
- [ ] FE-007.1: Create Q&A chat interface
- [ ] FE-007.2: Display citations as clickable links [1], [2]
- [ ] FE-007.3: Show source document preview on citation click
- [ ] FE-007.4: Allow restricting search to specific documents
- [ ] FE-007.5: Show "grounded in your knowledge base" indicator

**AI Tasks:**
- [ ] AI-007.1: Design grounding prompt template (strict context adherence)
- [ ] AI-007.2: Benchmark groundedness (no hallucination on test set)
- [ ] AI-007.3: Benchmark citation accuracy (cited chunks exist in context)
- [ ] AI-007.4: Compare LLM providers (Ollama vs. vLLM vs. OpenAI) on grounding quality

**Testing Tasks:**
- [ ] TE-007.1: Unit test citation extraction from LLM output
- [ ] TE-007.2: Integration test: query → retrieve → generate → verify
- [ ] TE-007.3: Groundedness test: verify no hallucination on 100 test questions
- [ ] TE-007.4: Citation accuracy test: 100% of cited chunks exist in context
- [ ] TE-007.5: E2E test: ask question → see answer → click citation → verify source
- [ ] TE-007.6: "I don't know" test: ask off-topic question → verify honest response

**Definition of Done:**
- 100% of AI responses cite specific source chunks
- 0% hallucination on test set (content not in retrieved chunks)
- "I don't know" response for off-topic questions
- Citation links work (click → show source document + page)
- Response latency < 2s (including retrieval + generation)
- All tests pass

---

### Story US-008: Exam Auto-Setup
**As a** student with no materials, **I want to** enter my exam details and have the AI find official resources, **so that** I can start studying immediately.

**Backend Tasks:**
- [ ] BE-008.1: Create exam database (100+ exams, boards, countries, subjects)
- [ ] BE-008.2: Implement web scraping for official sites (polite, rate-limited)
- [ ] BE-008.3: Implement search API for official resources (DuckDuckGo / Google)
- [ ] BE-008.4: Implement resource ranking (official > publisher > community)
- [ ] BE-008.5: Implement user approval workflow (present → select → process)
- [ ] BE-008.6: Implement auto-download and processing pipeline

**Frontend Tasks:**
- [ ] FE-008.1: Create exam setup wizard (step-by-step form)
- [ ] FE-008.2: Show found resources with confidence scores
- [ ] FE-008.3: Allow user to approve/reject each resource
- [ ] FE-008.4: Show processing progress for approved resources
- [ ] FE-008.5: Display "Auto-setup complete" notification with summary

**AI Tasks:**
- [ ] AI-008.1: No AI tasks (auto-setup is deterministic web scraping)

**Testing Tasks:**
- [ ] TE-008.1: Unit test web scraping for known exam sites
- [ ] TE-008.2: Integration test: exam name → find resources → process
- [ ] TE-008.3: Verify resource ranking (official > community)
- [ ] TE-008.4: E2E test: complete exam setup wizard flow
- [ ] TE-008.5: Test rate limiting on web scraper (no site overload)

**Definition of Done:**
- Exam database covers 100+ top exams
- Web scraper finds official syllabus and PYQs for 80% of exams
- Resources are ranked by confidence (official > publisher > community)
- User can approve/reject each found resource
- Approved resources are processed automatically
- All tests pass

---

### Story US-009: Generate Flashcards from Documents
**As a** student, **I want to** generate flashcards from my uploaded chapters, **so that** I can review key concepts efficiently.

**Backend Tasks:**
- [ ] BE-009.1: Implement flashcard generation from extracted concepts
- [ ] BE-009.2: Implement flashcard generation from formulas (formula → explanation)
- [ ] BE-009.3: Implement flashcard generation from definitions (term → definition)
- [ ] BE-009.4: Implement Anki export format (.apkg)
- [ ] BE-009.5: Store generated flashcards in PostgreSQL

**Frontend Tasks:**
- [ ] FE-009.1: Create flashcard generation UI (select topic → generate → preview)
- [ ] FE-009.2: Display flashcards in flip-card format (front/back)
- [ ] FE-009.3: Allow manual editing of flashcards before saving
- [ ] FE-009.4: Export flashcards to Anki format
- [ ] FE-009.5: Show flashcard count per topic

**AI Tasks:**
- [ ] AI-009.1: Design prompt for flashcard generation from concepts
- [ ] AI-009.2: Design prompt for flashcard generation from formulas
- [ ] AI-009.3: Benchmark flashcard quality (relevance, accuracy)

**Testing Tasks:**
- [ ] TE-009.1: Unit test flashcard generation from sample concepts
- [ ] TE-009.2: Verify Anki export format correctness
- [ ] TE-009.3: Accuracy test: flashcard content matches source document
- [ ] TE-009.4: E2E test: select topic → generate → export → import to Anki

**Definition of Done:**
- Flashcards generated from concepts, formulas, and definitions
- Flashcards include source citation
- Anki export format is valid (.apkg)
- User can edit flashcards before saving
- Flashcard quality validated by sample review
- All tests pass

---

### Story US-010: Generate Quizzes from Documents
**As a** student, **I want to** generate quizzes from my PYQs, **so that** I can test my understanding.

**Backend Tasks:**
- [ ] BE-010.1: Implement quiz generation from extracted questions
- [ ] BE-010.2: Implement quiz generation from content (new questions)
- [ ] BE-010.3: Support MCQ, true/false, fill-in-blank, short answer
- [ ] BE-010.4: Track quiz performance per topic
- [ ] BE-010.5: Store quiz results in PostgreSQL

**Frontend Tasks:**
- [ ] FE-010.1: Create quiz generation UI (select topic → select type → generate)
- [ ] FE-010.2: Display quiz in interactive format (radio buttons, text inputs)
- [ ] FE-010.3: Show instant feedback (correct/incorrect + explanation)
- [ ] FE-010.4: Show explanation with source citation
- [ ] FE-010.5: Track and display quiz history and performance trends

**AI Tasks:**
- [ ] AI-010.1: Design prompt for new question generation from content
- [ ] AI-010.2: Benchmark question quality (relevance, difficulty, accuracy)
- [ ] AI-010.3: Implement question difficulty estimation

**Testing Tasks:**
- [ ] TE-010.1: Unit test question generation from sample content
- [ ] TE-010.2: Verify question accuracy (correct answer matches source)
- [ ] TE-010.3: Verify difficulty estimation on test questions
- [ ] TE-010.4: E2E test: generate quiz → take quiz → view results

**Definition of Done:**
- Quiz generation supports MCQ, true/false, fill-in-blank, short answer
- Questions are grounded in source content (with citations)
- Instant feedback with explanations
- Performance tracking per topic
- Question quality validated by sample review
- All tests pass

---

## 4. Dependencies

### Dependency Graph

```
E-001 (Upload)
│
├─ E-002 (OCR) ── E-003 (Chunking) ── E-004 (Embedding) ── E-006 (Retrieval)
│       │                │                  │                    │
│       └─ E-005 (Knowledge Extraction) ────────────────────────┘
│
├─ E-007 (AI Grounding) ── E-010 (Quizzes) ── E-011 (Flashcards)
│
├─ E-008 (Exam Auto-Setup) ── E-001 (Upload)
│
├─ E-009 (UX) ── E-006 (Retrieval) ── E-007 (AI Grounding)
│
└─ E-012 (Multi-Language) ── E-002 (OCR)
```

### Critical Path

```
Week 1-2: E-001 → E-002 → E-003 → E-004
Week 3-4: E-005 → E-006 → E-007
Week 5-6: E-008 → E-009
Week 7-8: E-010 → E-011 → E-012
Week 9-10: E-013 (Security) → E-014 (DevOps)
```

### External Dependencies

| Dependency | Provider | Status | Risk |
|------------|----------|--------|------|
| Supabase project | Supabase | ✅ Ready | Low |
| Cloudflare Worker | Cloudflare | ✅ Ready | Low |
| BAAI/BGE model | Hugging Face | ✅ Ready | Low |
| Docling library | IBM Research | ✅ Ready | Medium (newer library) |
| Tesseract OCR | Google / Open Source | ✅ Ready | Low |
| Google Vision API | Google Cloud | 🔄 API key needed | Medium (cost) |
| MathPix API | MathPix | 🔄 API key needed | Medium (cost) |
| OpenAI API | OpenAI | 🔄 API key needed | Low (optional) |
| Stripe | Stripe | 🔄 Account setup | Low (Phase 6) |

---

## 5. Estimated Complexity

| Epic | Total Story Points | Complexity |
|------|-------------------|------------|
| E-001: Document Ingestion | 34 | Medium |
| E-002: OCR & Text Extraction | 55 | High |
| E-003: Semantic Chunking | 21 | Medium |
| E-004: Embedding Generation | 34 | Medium |
| E-005: Knowledge Extraction | 55 | High |
| E-006: Knowledge Organization | 34 | Medium |
| E-007: Hybrid Retrieval | 55 | High |
| E-008: AI Grounding | 34 | Medium |
| E-009: Exam Auto-Setup | 34 | Medium |
| E-010: User Management | 34 | Medium |
| E-011: Content Generation | 34 | Medium |
| E-012: Multi-Language | 55 | High |
| E-013: Security | 34 | Medium |
| E-014: DevOps | 34 | Medium |
| **Total** | **587** | **High** |

**Team Velocity (estimated):** 40 story points per week (4 engineers × 10 SP/week)
**Estimated Duration:** 15 weeks (with buffer for risks)
**Compressed Duration:** 12 weeks (with overtime, parallel work, reduced scope)

---

## 6. Definition of Done (Global)

For every feature, story, and task:

### Code
- [ ] Code is written and reviewed (PR approved by 1+ engineer)
- [ ] Code follows project style guide (linting passes)
- [ ] No console.log or debug statements in production code
- [ ] Error handling covers all edge cases
- [ ] Logging is structured (JSON) with correlation IDs

### Tests
- [ ] Unit tests cover all business logic (target: 80% coverage)
- [ ] Integration tests cover all API endpoints
- [ ] E2E tests cover all critical user flows
- [ ] AI tests validate accuracy on test datasets
- [ ] Security tests pass (no vulnerabilities in dependencies)
- [ ] Performance tests meet latency targets

### Documentation
- [ ] API documentation updated (OpenAPI spec)
- [ ] README updated with setup instructions
- [ ] Architecture Decision Record updated (if applicable)
- [ ] Runbook updated for operational procedures

### Deployment
- [ ] Feature deployed to staging environment
- [ ] Smoke tests pass in staging
- [ ] Database migrations are reversible
- [ ] Feature flagged (can be disabled in production)
- [ ] Monitoring and alerting configured

### Acceptance
- [ ] Product Manager accepts the feature
- [ ] QA signs off on test coverage
- [ ] Security review completed (if applicable)
- [ ] Performance benchmarks met

---

*End of AI Development Specification*
