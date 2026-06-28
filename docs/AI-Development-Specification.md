# AI Development Specification

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 2.1.0
**Date:** 2026-06-27
**Status:** Approved — Sprint Ready
**Product:** Adaptive Study Planner v4.1.0-ENTERPRISE
**Author:** AI & Engineering Team

---

## 1. Architecture Overview

See `Engineering-Specification.md` for system architecture.

Key AI pipeline components:
- **OCR** → Tesseract (local) + Google Vision (cloud)
- **Parsing** → Docling (structured Markdown extraction)
- **Extraction** → LLM (concepts, formulas, prerequisites, difficulty)
- **Chunking** → Heading-aware semantic splitting
- **Embedding** → BAAI/bge-large-en-v1.5 (local) + OpenAI (optional)
- **Graph** → PostgreSQL recursive CTEs (ArangoDB Phase 4)
- **Retrieval** → Hybrid (dense + sparse + metadata + graph + re-rank)
- **Citation** → Verification + evidence trace

---

## 2. Epics

### Epic E-001: Document Upload & OCR (Existing — Updated)
**Scope:** Upload, validate, OCR, parse documents
**Updated:** Added chunked upload, duplicate detection, virus scan, encoding detection
**Complexity:** 55 SP

### Epic E-002: Topic & Concept Extraction (Existing — Updated)
**Scope:** Extract topics, chapters, concepts, formulas, questions
**Updated:** Added prerequisite detection, difficulty classification, metadata extraction
**Complexity:** 55 SP

### Epic E-003: Semantic Search & Embeddings (Existing — Updated)
**Scope:** Chunking, embedding, vector search
**Updated:** Added semantic chunking, adaptive chunk size, Redis cache, incremental updates
**Complexity:** 55 SP

### Epic E-004: Knowledge Base & Question Answering (Existing — Updated)
**Scope:** RAG-based Q&A, source tracking, confidence scoring
**Updated:** Added hybrid retrieval, intent detection, query planning, re-ranking, citation verification
**Complexity:** 55 SP

### Epic E-005: Flashcard Generation (Existing)
**Scope:** AI flashcard generation from content
**Complexity:** 34 SP

### Epic E-006: Quiz Generation (Existing)
**Scope:** AI quiz generation from PYQs
**Complexity:** 34 SP

### Epic E-007: Revision Plan Generation (Existing)
**Scope:** Personalized study plan from document analysis
**Updated:** Added prerequisite-aware planning, concept gap analysis
**Complexity:** 55 SP

### Epic E-008: Exam Auto-Setup (Existing — Updated)
**Scope:** Auto-collect official resources for zero-upload setup
**Updated:** Added resource ranking, rate-limited crawling, user approval workflow, DuckDuckGo/Google fallback
**Complexity:** 55 SP

### Epic E-009: Multi-User Platform (Existing)
**Scope:** Shared plans, real-time collaboration, group management
**Updated:** Added knowledge sharing, collaborative annotations, permission levels
**Complexity:** 55 SP

### Epic E-010: Subscription & Billing (Existing)
**Scope:** Stripe billing, subscription management
**Complexity:** 34 SP

### Epic E-011: Phase 2 (Existing)
**Scope:** Multi-session collaboration, user comments, API keys
**Complexity:** 55 SP

### Epic E-012: Phase 3 (Existing)
**Scope:** Performance optimization, mobile PWA, export (Anki, CSV)
**Updated:** Added knowledge graph export, prerequisite export
**Complexity:** 55 SP

### Epic E-013: Phase 4 (Existing)
**Scope:** LMS integration, custom templates, AI quality benchmarking, admin dashboard, AI explainability
**Updated:** Added knowledge graph visualization, prerequisite analytics, grounding audit dashboard
**Complexity:** 89 SP

### Epic E-014: Infrastructure (Existing)
**Scope:** Scalable, fault-tolerant, observable infrastructure
**Updated:** Added monitoring & alerting stack (Sentry, Grafana, PagerDuty), distributed tracing (OpenTelemetry + Jaeger)
**Complexity:** 55 SP

---

### Epic E-015: Upload Infrastructure (New)
**Scope:** Multi-format, chunked, resume, drag-drop, folder upload, duplicate detection
**Complexity:** 34 SP

**User Stories:**
- US-001: Upload PDF/DOCX/PPTX (existing, updated with chunked upload)
- US-011: Chunked upload for large files (new)
- US-012: Folder upload (ZIP extraction) (new)

**Backend Tasks:**
- [ ] POST /api/v3/upload endpoint (multi-file, multipart)
- [ ] POST /api/v3/upload/chunk endpoint (5MB segments, resume support)
- [ ] FileValidator (magic numbers, size limits, virus scan integration)
- [ ] DuplicateDetector (SHA-256 + perceptual hash)
- [ ] ChunkedUploader (parallel upload, retry logic)
- [ ] R2Uploader (presigned URLs, multipart upload)
- [ ] Progress tracker (Redis, WebSocket push)
- [ ] ZIP extraction service (recursive, validate contents)

**Frontend Tasks:**
- [ ] Drag-and-drop zone (multi-file, folder drop)
- [ ] Upload progress bar (per file, per chunk)
- [ ] Resume UI (show incomplete uploads, resume button)
- [ ] Duplicate warning ("This file already exists. Replace or keep both?")
- [ ] Folder upload preview (show files before upload)

**AI Tasks:**
- [ ] None (upload is deterministic)

**Infrastructure Tasks:**
- [ ] R2 bucket configuration (CORS, lifecycle, encryption)
- [ ] Presigned URL generation (5-minute expiry)
- [ ] Chunked upload URL generation

**DevOps Tasks:**
- [ ] CI/CD for upload service
- [ ] Upload latency monitoring
- [ ] Upload success rate alerting

**Database Tasks:**
- [ ] documents table schema (SHA-256, pHash, status enum)
- [ ] Index on sha256_hash for duplicate detection
- [ ] Index on user_id + status for progress queries

**APIs:**
- POST /api/v3/upload — Request: {files: multipart}, Response: {upload_id, status}
- POST /api/v3/upload/chunk — Request: {chunk_id, chunk_data, upload_id}, Response: {chunk_status}
- GET /api/v3/upload/:id/progress — Response: {percentage, bytes_uploaded, total_bytes}

**Dependencies:** R2, Supabase Auth, Redis
**Risks:** Large file uploads timing out, network interruptions, R2 rate limits
**DoD:** All formats supported, resume works, duplicates detected, progress tracked, tests pass

---

### Epic E-016: Validation Pipeline (New)
**Scope:** Magic numbers, virus scan, encoding detection, language detection
**Complexity:** 34 SP

**User Stories:**
- US-001 (validation AC): File validation before processing

**Backend Tasks:**
- [ ] FileValidator (magic numbers via python-magic, extension whitelist)
- [ ] VirusScanner (ClamAV daemon integration or cloud-native API)
- [ ] EncodingDetector (chardet / charset-normalizer)
- [ ] LanguageDetector (fastText / langdetect for 10+ languages)
- [ ] PasswordProtectedDetector (reject encrypted PDFs)
- [ ] ExecutableContentDetector (scan PDFs for embedded executables)

**Frontend Tasks:**
- [ ] Validation error messages (clear, actionable)
- [ ] Pre-upload checks (client-side size, type preview)
- [ ] Virus detected notification (quarantine, rescan option)

**AI Tasks:**
- [ ] Language detection model evaluation (accuracy per language)
- [ ] Encoding detection benchmark (UTF-8, Latin-1, Windows-1252)

**Infrastructure Tasks:**
- [ ] ClamAV daemon setup (or cloud virus scan API)
- [ ] fastText model download (language detection)

**DevOps Tasks:**
- [ ] Security scanning in CI/CD (Trivy, OWASP ZAP)
- [ ] Virus scan latency monitoring

**Database Tasks:**
- [ ] None (stateless processing)

**APIs:**
- Internal validation pipeline (called by Upload Service)

**Dependencies:** ClamAV or cloud scanner, libmagic, chardet, fastText
**Risks:** False positives in virus scan, encoding misdetection, language detection accuracy
**DoD:** All file types validated, viruses rejected, encoding detected, tests pass

---

### Epic E-017: OCR Engine (New)
**Scope:** Multi-engine OCR (Tesseract, Google Vision, MathPix) with automatic selection
**Complexity:** 55 SP

**User Stories:**
- US-002 (OCR): OCR on scanned notes

**Backend Tasks:**
- [ ] OCRPipeline (orchestrator)
- [ ] TesseractEngine (primary, printed text, 100+ languages)
- [ ] GoogleVisionEngine (handwriting, poor scans, pro tier)
- [ ] MathPixEngine (formulas, LaTeX, pro tier)
- [ ] EngineSelector (auto-select based on document type, confidence, user tier)
- [ ] ConfidenceLogger (per-page OCR confidence tracking)
- [ ] ManualReviewQueue (flag low-confidence pages)
- [ ] OCRResultStore (PostgreSQL, per-page results)

**Frontend Tasks:**
- [ ] OCR confidence badge (per document, per page)
- [ ] Manual review UI (show low-confidence pages, allow correction)
- [ ] OCR progress indicator ("OCR in progress: 45/50 pages")

**AI Tasks:**
- [ ] Tesseract configuration optimization (PSM modes, language packs)
- [ ] Google Vision benchmarking (accuracy vs Tesseract on handwritten samples)
- [ ] MathPix benchmarking (formula extraction accuracy)
- [ ] Multi-language OCR evaluation (10+ languages)
- [ ] OCR confidence threshold tuning (60% flag, 85% pass)

**Infrastructure Tasks:**
- [ ] Tesseract 5.x installation + language packs
- [ ] Google Vision API key management (pro tier)
- [ ] MathPix API key management (pro tier)

**DevOps Tasks:**
- [ ] OCR model deployment (Tesseract language packs)
- [ ] OCR accuracy monitoring (dashboard)
- [ ] API cost tracking (Google Vision, MathPix)

**Database Tasks:**
- [ ] ocr_results table (document_id, page_number, text, confidence, engine)

**APIs:**
- Internal OCR pipeline (called by Processing Pipeline)

**Dependencies:** Tesseract 5.x, Google Vision API, MathPix API, Pillow
**Risks:** OCR accuracy on poor scans, API costs for pro tier, manual review backlog
**DoD:** Printed >85% accuracy, handwritten >70%, formulas >80%, flagged for manual review, tests pass

---

### Epic E-018: Parsing Engine (New)
**Scope:** Docling for PDF/DOCX/PPTX/EPUB, structure preservation
**Complexity:** 55 SP

**User Stories:**
- US-001 (parsing): Parse uploaded documents
- US-003 (structure): Preserve document structure

**Backend Tasks:**
- [ ] DoclingParser (PDF, DOCX, PPTX, EPUB)
- [ ] TableExtractor (detect structure, convert to Markdown)
- [ ] FormulaExtractor (LaTeX preservation, inline/display detection)
- [ ] ImageExtractor (extract embedded images, generate captions)
- [ ] TextCleaner (remove headers, footers, watermarks, normalize whitespace)
- [ ] StructurePreserver (heading hierarchy, lists, paragraphs, citations)
- [ ] ParsingResultStore (PostgreSQL, structured Markdown output)

**Frontend Tasks:**
- [ ] Document preview (render structured Markdown)
- [ ] Structure tree view (headings, expandable)
- [ ] Table preview (rendered Markdown table)
- [ ] Formula preview (LaTeX rendering with KaTeX)

**AI Tasks:**
- [ ] None (parsing is deterministic with Docling)

**Infrastructure Tasks:**
- [ ] Docling Docker image (+500MB, Python 3.10+)
- [ ] Resource allocation (2GB RAM per parsing job)

**DevOps Tasks:**
- [ ] Parser deployment (Docker/Kubernetes)
- [ ] Resource monitoring (CPU, memory per parsing job)
- [ ] Parsing queue depth alerting

**Database Tasks:**
- [ ] parsed_documents table (document_id, markdown_text, structure_json)

**APIs:**
- Internal parsing pipeline (called by Processing Pipeline)

**Dependencies:** Docling, python-docx, python-pptx, ebooklib, Pillow
**Risks:** Docling maintenance, slower processing (+30% vs PyPDF2), memory usage
**DoD:** Headings preserved, tables as Markdown, formulas as LaTeX, images with captions, tests pass

---

### Epic E-019: Knowledge Extraction (New)
**Scope:** LLM-based concept/formula/question/prerequisite extraction
**Complexity:** 55 SP

**User Stories:**
- US-004 (view knowledge): View extracted topics and concepts
- US-005 (search): Search by concept
- US-006 (grounded questions): Ask AI grounded questions

**Backend Tasks:**
- [ ] KnowledgeExtractor (orchestrator)
- [ ] ConceptExtractor (key terms + definitions, structured JSON)
- [ ] FormulaDetector (LaTeX expressions, catalog)
- [ ] QuestionExtractor (MCQ, fill-in-blank, short answer from PYQs)
- [ ] PrerequisiteDetector (topic dependency chains)
- [ ] DifficultyEstimator (formula density, language complexity, question structure)
- [ ] ChapterDetector (heading hierarchy extraction)
- [ ] TopicClassifier (subject/topic auto-tagging)
- [ ] ExampleExtractor (worked problems, case studies)
- [ ] MetadataExtractor (author, publisher, edition, source type)

**Frontend Tasks:**
- [ ] Concept map (interactive visualization)
- [ ] Formula gallery (searchable, LaTeX rendered)
- [ ] Topic tree (expandable hierarchy)
- [ ] Question bank (filterable by topic, difficulty, type)
- [ ] Prerequisite chain view (visual graph)

**AI Tasks:**
- [ ] Prompt templates for each extraction type (versioned, benchmarked)
- [ ] Structured JSON output schemas (Pydantic validation)
- [ ] Benchmark accuracy: Concept F1 > 0.70, Formula > 80%, Prerequisite > 60%
- [ ] LLM provider abstraction (Ollama, vLLM, OpenAI)
- [ ] Extraction cost optimization (batch processing, caching)

**Infrastructure Tasks:**
- [ ] LLM endpoint (Ollama/vLLM/OpenAI)
- [ ] Extraction queue (Redis, priority-based)

**DevOps Tasks:**
- [ ] Extraction pipeline monitoring (accuracy, latency, cost)
- [ ] Extraction quality dashboard (per-document metrics)

**Database Tasks:**
- [ ] concepts table (name, definition, subject, confidence, source)
- [ ] formulas table (formula, latex, context, document_id)
- [ ] questions table (type, question, answer, options, difficulty, topic)
- [ ] knowledge_edges table (source_node, target_node, relationship, confidence)

**APIs:**
- Internal extraction pipeline (called by Processing Pipeline)
- GET /api/v3/knowledge/concepts (list concepts)
- GET /api/v3/knowledge/topics (topic hierarchy)

**Dependencies:** LLMProvider, Docling output, PostgreSQL
**Risks:** Extraction accuracy varies by domain, LLM costs, hallucination in extraction
**DoD:** Concept extraction F1 > 0.70, formula extraction > 80%, prerequisite detection > 60%, tests pass

---

### Epic E-020: Embedding Pipeline (New)
**Scope:** BAAI/BGE default, OpenAI optional, batch processing, cache
**Complexity:** 34 SP

**User Stories:**
- US-004 (AI-ready): Document becomes AI-ready after embedding
- US-005 (semantic search): Search by semantic similarity

**Backend Tasks:**
- [ ] BAAIEmbeddingProvider (default, local, 1024-dim)
- [ ] OpenAIEmbeddingProvider (optional, paid, 1536-dim)
- [ ] BatchProcessor (32 chunks per batch, configurable)
- [ ] EmbeddingCache (Redis, SHA-256 key, 24h TTL)
- [ ] NormalizationVerifier (L2 normalization check)
- [ ] IncrementalUpdater (only re-embed changed chunks)
- [ ] ModelDownloader (BAAI model, ~1GB, first use)

**Frontend Tasks:**
- [ ] Embedding status tracker ("Embedding: 45/100 chunks")
- [ ] "AI-ready" badge (shown when document is fully embedded)
- [ ] Embedding progress in document list

**AI Tasks:**
- [ ] BAAI model download and setup (~1GB, Python sentence-transformers)
- [ ] Benchmark similarity (cosine similarity on known related chunks)
- [ ] CPU vs GPU speed benchmark (target: < 2s per batch on CPU)
- [ ] Dimension verification (1024 for BAAI, 1536 for OpenAI)

**Infrastructure Tasks:**
- [ ] Model storage (persistent volume, ~1GB)
- [ ] GPU optional (CUDA for BAAI, significant speedup)
- [ ] Redis cache for embedding storage

**DevOps Tasks:**
- [ ] Model versioning (tag embeddings with model version)
- [ ] Cache monitoring (hit rate, memory usage)
- [ ] Embedding latency tracking (p95)

**Database Tasks:**
- [ ] pgvector schema (embedding VECTOR(1024))
- [ ] IVFFlat index (lists = 100, for < 1M vectors)
- [ ] HNSW index migration (m = 16, ef_construction = 64, for > 1M vectors)

**APIs:**
- Internal embedding pipeline (called by Processing Pipeline)

**Dependencies:** BAAI/bge-large-en-v1.5, sentence-transformers, pgvector, Redis
**Risks:** Model download time, CPU slowness, GPU cost, cache invalidation
**DoD:** L2 normalized, batch 32, < 2s per batch on CPU, cache hit rate tracked, tests pass

---

### Epic E-021: Knowledge Graph (New)
**Scope:** Concept relationships, prerequisites, learning paths
**Complexity:** 55 SP

**User Stories:**
- US-012 (view graph): View knowledge graph
- US-013 (browse topics): Browse topic hierarchy
- US-019 (prerequisites): Track prerequisite completion

**Backend Tasks:**
- [ ] GraphBuilder (extract relationships from LLM output)
- [ ] GraphTraverser (recursive CTE, max depth 5)
- [ ] PrerequisiteAnalyzer (detect prerequisite chains)
- [ ] LearningPathOptimizer (shortest path to exam readiness)
- [ ] ConceptGapDetector (missing prerequisites for target topics)
- [ ] RelationshipClassifier (prerequisite, related, part-of, covers, example-of)
- [ ] GraphConsistencyChecker (cycle detection, orphan detection)
- [ ] GraphExport (JSON, GraphML, Cypher)

**Frontend Tasks:**
- [ ] Graph visualization (D3.js or Cytoscape.js)
- [ ] Node interactions (click for definition, hover for preview)
- [ ] Edge filtering (show only prerequisites, or only related)
- [ ] Prerequisite chain view (linear list, expandable)
- [ ] Concept gap alert ("You're missing 3 prerequisites for Thermodynamics")
- [ ] Learning path view ("Study this → then this → then this")

**AI Tasks:**
- [ ] Prerequisite detection prompt ("What must a student know before understanding X?")
- [ ] Relationship classification prompt ("Is A a prerequisite, related, or part of B?")
- [ ] Graph embedding (node2vec for concept similarity, Phase 4)
- [ ] Benchmark: Prerequisite detection accuracy > 60%

**Infrastructure Tasks:**
- [ ] PostgreSQL recursive CTEs (Phase 3, sufficient for < 10K edges)
- [ ] ArangoDB evaluation (Phase 4, if performance critical)
- [ ] Graph visualization library (D3.js or Cytoscape.js)

**DevOps Tasks:**
- [ ] Graph performance monitoring (query latency, edge count)
- [ ] Graph quality metrics (cycle count, orphan count, coverage)

**Database Tasks:**
- [ ] knowledge_edges table (source_node, target_node, relationship, confidence)
- [ ] concepts table (name, definition, subject, confidence, source)
- [ ] Graph indexes (user_id, source_node, target_node, relationship)
- [ ] Recursive CTE performance optimization (materialized views)

**APIs:**
- GET /api/v3/knowledge/graph — Response: {nodes: [...], edges: [...]}
- GET /api/v3/knowledge/topics — Response: {topics: [...], hierarchy: {...}}
- GET /api/v3/knowledge/prerequisites/:concept — Response: {prerequisites: [...], depth: N}
- GET /api/v3/knowledge/gaps — Response: {missing: [...], suggestions: [...]}

**Dependencies:** PostgreSQL, optional ArangoDB, D3.js/Cytoscape.js
**Risks:** Graph traversal slow >3 hops, large graphs memory intensive, prerequisite detection accuracy
**DoD:** Graph queries < 100ms, prerequisite chains accurate, visualization renders, tests pass

---

### Epic E-022: Hybrid Retrieval (New)
**Scope:** Dense + sparse + metadata + graph + re-rank + RRF
**Complexity:** 55 SP

**User Stories:**
- US-005 (search): Hybrid search
- US-006 (grounded questions): AI answers with citations
- US-014 (concept search): Search by concept

**Backend Tasks:**
- [ ] DenseRetriever (pgvector similarity, top 10)
- [ ] SparseRetriever (PostgreSQL BM25 tsvector, top 10)
- [ ] MetadataFilter (SQL WHERE pre-filtering)
- [ ] GraphTraverser (prerequisite traversal, top 5)
- [ ] ReRanker (BAAI/bge-reranker cross-encoder, score 0-1)
- [ ] FusionEngine (RRF, k=60)
- [ ] QueryCache (Redis, 1h TTL, hash of query + filters)
- [ ] IntentDetector (query classification: definition, problem, comparison, summary)
- [ ] QueryPlanner (select strategy based on intent)
- [ ] QueryPreprocessor (spell correction, synonym expansion, HyDE optional)

**Frontend Tasks:**
- [ ] Search bar with filters (subject, document, confidence, date range)
- [ ] Result highlighting (matched terms, semantic similarity)
- [ ] Confidence badges (green/yellow/red per source)
- [ ] Graph expansion ("Show related concepts")
- [ ] Citation preview (hover over citation for snippet)
- [ ] Search suggestions (autocomplete, trending searches)

**AI Tasks:**
- [ ] Query preprocessing (spell correction, synonym expansion)
- [ ] Re-ranker model configuration (BAAI/bge-reranker)
- [ ] Intent detection model (lightweight classifier or rule-based)
- [ ] HyDE evaluation (optional, Phase 4)
- [ ] Benchmark: Precision@5 > 80%, Recall@10 > 50%

**Infrastructure Tasks:**
- [ ] pgvector index (IVFFlat or HNSW)
- [ ] GIN tsvector index (full-text search)
- [ ] B-tree metadata indexes (subject, document, confidence, date)
- [ ] Redis cache (query results, 1h TTL)
- [ ] BAAI/bge-reranker model (cross-encoder, ~500MB)

**DevOps Tasks:**
- [ ] Retrieval latency monitoring (per stage: dense, sparse, re-rank)
- [ ] Cache hit rate tracking (target: > 80%)
- [ ] Precision/recall dashboard (weekly evaluation)

**Database Tasks:**
- [ ] Vector index (pgvector)
- [ ] Full-text index (GIN tsvector)
- [ ] Metadata composite indexes (subject + confidence + date)
- [ ] Query log table (query, filters, results, latency, user_id)

**APIs:**
- POST /api/v3/search — Request: {query, filters, max_results}, Response: {results, total, latency}
- POST /api/v3/retrieve — Request: {query, filters}, Response: {chunks, scores, citations}

**Dependencies:** pgvector, BAAI/bge-reranker, Redis, PostgreSQL
**Risks:** Latency > 200ms p95, index build time, cache invalidation, re-ranker model size
**DoD:** Dense < 100ms, Sparse < 50ms, Re-rank < 50ms, End-to-end < 200ms p95, Precision@5 > 80%, tests pass

---

### Epic E-023: Web Resource Collector (New)
**Scope:** Auto-discovery of official resources for zero-upload setup
**Complexity:** 34 SP

**User Stories:**
- US-003 (zero-upload): Auto-collect resources
- US-011 (auto-setup): Exam setup without uploads

**Backend Tasks:**
- [ ] ExamDatabase (100+ exams, metadata, official URLs)
- [ ] WebScraper (polite, rate-limited, robots.txt compliant)
- [ ] ResourceSearcher (DuckDuckGo API, Google Search API fallback)
- [ ] ResourceRanker (confidence scoring based on source type)
- [ ] ApprovalWorkflow (present resources, collect user approval/rejection)
- [ ] AutoDownloader (download approved resources, validate, process)
- [ ] RateLimiter (max 1 request/sec per domain)
- [ ] UserAgentRotator (avoid bot detection)
- [ ] robots.txt compliance checker

**Frontend Tasks:**
- [ ] Exam setup wizard (step-by-step: exam → board → subjects → year → target score)
- [ ] Found resources list (ranked, with confidence scores, source badges)
- [ ] Resource preview (thumbnail, metadata, source URL)
- [ ] Approve/reject buttons (per resource, bulk actions)
- [ ] Processing progress ("Downloading 3 of 5 resources...")

**AI Tasks:**
- [ ] None (deterministic scraping)

**Infrastructure Tasks:**
- [ ] Proxy rotation (if needed for rate limiting)
- [ ] Caching layer for discovered resources (Redis, 24h TTL)

**DevOps Tasks:**
- [ ] Scraper monitoring (success rate, rate limit compliance)
- [ ] Legal compliance tracking (robots.txt violations, DMCA notices)

**Database Tasks:**
- [ ] exams table (name, board, country, subjects, official_urls, metadata)
- [ ] found_resources table (exam_id, url, title, source_type, confidence, status)

**APIs:**
- POST /api/v3/setup/auto — Request: {exam, board, country, subjects, year, language, target_score}, Response: {setup_id, status}
- GET /api/v3/setup/resources — Request: {setup_id}, Response: {resources: [...], status}
- POST /api/v3/setup/approve — Request: {setup_id, resource_ids}, Response: {status}

**Dependencies:** DuckDuckGo API, Google Search API, scraping libraries (requests, BeautifulSoup)
**Risks:** Site blocking, legal compliance, accuracy of found resources, rate limiting
**DoD:** 100+ exams in database, 80% official resources found, user approval workflow works, tests pass

---

### Epic E-024: Citation Engine (New)
**Scope:** Source verification, confidence scoring, citation formatting
**Complexity:** 34 SP

**User Stories:**
- US-006 (grounded questions): AI answers with citations
- US-015 (citation verification): Verify citations

**Backend Tasks:**
- [ ] CitationExtractor (regex [1], [2] from LLM output)
- [ ] CitationVerifier (verify against retrieved chunks)
- [ ] ConfidenceScorer (aggregate confidence from source + cross-validation)
- [ ] EvidenceTracer (claim → chunk → document → page → confidence)
- [ ] CitationFormatter (format: [1] Source Name, Page X, Confidence Y)
- [ ] InventedCitationDetector (flag citations not in retrieved results)
- [ ] CitationSummaryGenerator (table of all citations per response)
- [ ] GroundingScoreCalculator (% of claims with verified citations)

**Frontend Tasks:**
- [ ] Clickable citations [1], [2] (open source preview popup)
- [ ] Citation preview (source document, page, snippet, confidence)
- [ ] Evidence trace (expandable: claim → chunk → document → page)
- [ ] Grounding score badge ("100% grounded", "Partially grounded")
- [ ] Unverified citation warning (yellow badge)

**AI Tasks:**
- [ ] Prompt engineering for citation format (strict template)
- [ ] Verification logic (fuzzy matching for paraphrased citations)
- [ ] Grounding audit prompt ("Verify every claim against context")

**Infrastructure Tasks:**
- [ ] None (stateless processing)

**DevOps Tasks:**
- [ ] Citation accuracy monitoring (per-response verification results)
- [ ] Invented citation alerting (prompt engineering review trigger)

**Database Tasks:**
- [ ] ai_queries table (query, response, citations, verification_result, grounding_score)
- [ ] grounding_audit table (user_id, query, retrieval_results, response, score, timestamp)

**APIs:**
- Internal citation API (part of /ask response)
- GET /api/v3/grounding/audit — Response: {queries: [...], scores: [...]} (admin only)

**Dependencies:** Retrieval pipeline, LLM output, PostgreSQL
**Risks:** LLM invents citations, formatting errors, verification false positives
**DoD:** 100% citations verified, confidence > 0.50, clickable links work, grounding score tracked, tests pass

---

### Epic E-025: Knowledge Management Dashboard (New)
**Scope:** Document CRUD, topic tree, concept graph, search, export, sharing
**Complexity:** 34 SP

**User Stories:**
- US-004 (view knowledge): View knowledge base
- US-007 (flashcards): Generate flashcards
- US-008 (quiz): Generate quiz
- US-017 (export): Export knowledge base
- US-018 (share): Share with study group

**Backend Tasks:**
- [ ] DocumentCRUD (upload, view, delete, replace, reprocess, version history)
- [ ] TopicHierarchyAPI (CRUD topics, move, merge, split)
- [ ] ConceptGraphAPI (graph data, nodes, edges, traversal)
- [ ] SearchAPI (full-text, semantic, filtered, faceted)
- [ ] ExportService (JSON, Markdown, Anki, PDF)
- [ ] SharingService (share topics/documents, permissions, revoke)
- [ ] AnnotationService (comments, highlights, threaded discussions)
- [ ] NotificationService (share invites, comment notifications)

**Frontend Tasks:**
- [ ] Dashboard UI (document list, status badges, actions)
- [ ] Topic tree (expandable, drag-and-drop reorder)
- [ ] Concept map (interactive graph, D3.js/Cytoscape.js)
- [ ] Search interface (search bar, filters, results, highlights)
- [ ] Export buttons (JSON, Markdown, Anki, PDF)
- [ ] Share dialog (select topics, select users/groups, permission level)
- [ ] Annotation UI (highlight text, add comment, threaded view)
- [ ] Notification panel (share invites, comments, system alerts)

**AI Tasks:**
- [ ] None (UI/CRUD operations)

**Infrastructure Tasks:**
- [ ] Static hosting (Cloudflare Pages)
- [ ] CDN caching (30-day TTL for static assets)

**DevOps Tasks:**
- [ ] Frontend deployment (Cloudflare Pages)
- [ ] CDN cache invalidation on deploy
- [ ] Frontend performance monitoring (Lighthouse, Core Web Vitals)

**Database Tasks:**
- [ ] All tables (documents, chunks, concepts, formulas, questions, knowledge_edges, study_groups, shared_topics, annotations)
- [ ] RLS policies for all tables

**APIs:**
- Full CRUD APIs for documents, topics, concepts, exports, shares, annotations

**Dependencies:** Frontend framework, D3.js/Cytoscape.js, KaTeX (LaTeX rendering)
**Risks:** Large knowledge graphs slow to render, export complexity, real-time collaboration sync
**DoD:** All CRUD works, graph renders, exports valid, sharing works, annotations work, tests pass

---

### Epic E-026: Monitoring & Analytics (New)
**Scope:** Processing metrics, retrieval quality, usage analytics, alerting
**Complexity:** 34 SP

**User Stories:**
- Internal: Operations team needs visibility into system health
- Internal: Product team needs usage analytics
- Internal: AI team needs quality metrics

**Backend Tasks:**
- [ ] MetricsCollector (processing time, success rate, queue depth, cache hit rate)
- [ ] AnalyticsPipeline (usage events, user behavior, feature adoption)
- [ ] DashboardAPI (metrics for Grafana, custom analytics)
- [ ] AlertManager (PagerDuty, Slack, email integration)
- [ ] GroundingAuditAPI (per-response grounding scores, citation accuracy)
- [ ] RetrievalQualityAPI (precision@5, recall@10, MRR@10)
- [ ] CostTrackingAPI (LLM costs, API costs, storage costs per user)

**Frontend Tasks:**
- [ ] Admin dashboard (system health, metrics, alerts)
- [ ] Analytics charts (DAU, document processing, search volume, AI queries)
- [ ] Quality dashboard (OCR accuracy, retrieval precision, hallucination rate)
- [ ] Cost dashboard (per-user cost, per-tenant cost, trend analysis)
- [ ] Alert configuration (thresholds, channels, escalation)

**AI Tasks:**
- [ ] None (metrics and analytics)

**Infrastructure Tasks:**
- [ ] Sentry (error tracking)
- [ ] Grafana (metrics visualization)
- [ ] PagerDuty (alerting)
- [ ] Slack (alert notifications)
- [ ] OpenTelemetry (distributed tracing)
- [ ] Jaeger (trace visualization)

**DevOps Tasks:**
- [ ] Monitoring stack setup (Sentry, Grafana, PagerDuty)
- [ ] Alert tuning (reduce false positives)
- [ ] Runbook updates (alert response procedures)
- [ ] Dashboard provisioning (Grafana as code)

**Database Tasks:**
- [ ] metrics table (metric_name, value, timestamp, labels)
- [ ] analytics_events table (event_type, user_id, properties, timestamp)
- [ ] grounding_audit table (query, response, score, citations, timestamp)

**APIs:**
- Internal metrics APIs (admin only)
- GET /api/v3/admin/metrics — Response: {metrics: [...]}
- GET /api/v3/admin/grounding — Response: {scores: [...], trends: [...]}

**Dependencies:** Sentry, Grafana, PagerDuty, Slack, OpenTelemetry, Jaeger
**Risks:** Alert fatigue, metrics overhead, dashboard performance with large datasets
**DoD:** Dashboards configured, alerts tested, runbooks updated, tests pass

---

## 3. Dependency Graph

```
E-015 (Upload) → E-016 (Validation) → E-017 (OCR) → E-018 (Parsing)
  |                |                    |              |
  +----------------+--------------------+--------------+---> E-019 (Extraction)
                                                          |
                                                          +---> E-020 (Embedding)
                                                          |
                                                          +---> E-021 (Graph)
                                                          |
                                                          +---> E-022 (Retrieval)
                                                          |
                                                          +---> E-024 (Citation)
                                                          |
                                                          +---> E-025 (Dashboard)
                                                          |
E-023 (Web Collector) ------------------------------------>
                                                          |
E-026 (Monitoring) -------------------------------------->
```

**Critical Path:** E-015 → E-016 → E-017 → E-018 → E-019 → E-020 → E-021 → E-022 → E-024 → E-025

---

## 4. Estimated Complexity

| Epic | Complexity | Story Points | Priority |
|------|------------|-------------|----------|
| E-015 Upload | Medium | 34 | P0 |
| E-016 Validation | Medium | 34 | P0 |
| E-017 OCR | High | 55 | P0 |
| E-018 Parsing | High | 55 | P0 |
| E-019 Extraction | High | 55 | P0 |
| E-020 Embedding | Medium | 34 | P0 |
| E-021 Graph | High | 55 | P0 |
| E-022 Retrieval | High | 55 | P0 |
| E-023 Web Collector | Medium | 34 | P1 |
| E-024 Citation | Medium | 34 | P0 |
| E-025 Dashboard | Medium | 34 | P1 |
| E-026 Monitoring | Medium | 34 | P2 |
| **Total (New)** | | **517 SP** | |
| **Total (All)** | | **1,344 SP** | |

---

## 5. Definition of Done (Global)

- [ ] Code reviewed (peer review, no self-merges)
- [ ] Unit tests written (coverage ≥ 80%)
- [ ] Integration tests written (100% API endpoints)
- [ ] AI evaluation passed (MRR@10 > 0.6, Precision@5 > 0.7)
- [ ] Security scan passed (0 critical/high vulnerabilities)
- [ ] Performance benchmark passed (p95 latency < 200ms for retrieval)
- [ ] Documentation updated (API docs, runbooks, architecture diagrams)
- [ ] Feature flag enabled (launch darkly, gradual rollout)
- [ ] Monitoring configured (metrics, alerts, dashboards)
- [ ] Accessibility audit passed (WCAG 2.1 AA)
- [ ] Mobile responsiveness verified (PWA)
- [ ] Cross-browser testing passed (Chrome, Firefox, Safari, Edge)
- [ ] **Grounding audit configured (per-response citation verification)**
- [ ] **Retrieval quality benchmark passed (Precision@5 > 80%, Recall@10 > 50%)**
- [ ] **OCR accuracy benchmark passed (printed > 85%, handwritten > 70%)**
- [ ] **Citation accuracy: 100% verified**

---

## 6. Milestones

| Milestone | Target | Deliverables | Status |
|-----------|--------|-------------|--------|
| M1 | Week 1 | Foundation: Basic upload, OCR, chunking | ✅ |
| M2 | Week 2 | Intelligence: Extraction, search, Q&A | ✅ |
| M3 | Week 4 | Scale: Embeddings, full-text search, user management | ✅ |
| M4 | Week 6 | Content: Flashcards, quiz, revision plan | ✅ |
| M5 | Week 8 | Enterprise: Sharing, subscriptions, API, admin | ✅ |
| M6 | Week 10 | Phase 4: LMS integration, custom templates, benchmarking | ✅ |
| **M7** | **Week 12** | **Knowledge Layer: Upload, Validation, OCR, Parsing, Extraction** | **🎯** |
| **M8** | **Week 14** | **Knowledge Layer: Chunking, Embedding, Graph, Retrieval** | **🎯** |
| **M9** | **Week 16** | **Knowledge Layer: Citation, Dashboard, Export, Collaboration** | **🎯** |
| **M10** | **Week 18** | **Auto-Setup: Web scraping, resource ranking, approval workflow** | **🎯** |
| **M11** | **Week 20** | **Enterprise: SSO, API v2, enterprise tenant isolation** | **🎯** |
| **M12** | **Week 22** | **Monitoring: Sentry, Grafana, PagerDuty, OpenTelemetry, Jaeger** | **🎯** |

---

## 7. Critical Path

**Path 1 (Knowledge Base):** E-015 → E-016 → E-017 → E-018 → E-019 → E-020 → E-021 → E-022 → E-024 → E-025
**Path 2 (Auto-Setup):** E-023 → E-019 → E-020 → E-021 → E-022 → E-024 → E-025
**Path 3 (Monitoring):** E-026 → (all other epics)

**Longest path:** 10 epics, ~22 weeks
**Critical dependencies:** E-019 (Extraction) blocks E-021 (Graph), E-022 (Retrieval), E-024 (Citation)

---

*End of AI Development Specification*
