# Product Requirements Document

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 1.0.0
**Date:** 2026-06-26
**Status:** Draft — Ready for Engineering Review
**Product:** Adaptive Study Planner v3.1.0
**Author:** Product & Engineering Team

---

## 1. Vision

Every student has a unique set of study materials: textbooks, class notes, formula sheets, previous year question papers, and handwritten annotations. These documents are the single most trusted source of knowledge for exam preparation. Yet, no existing study platform treats a student's own documents as first-class citizens in the learning experience.

**The Universal Knowledge Ingestion & AI Knowledge Layer transforms any educational document into a structured, searchable, AI-ready knowledge base.** Students upload their materials. The system extracts, organizes, embeds, and connects every concept. From that point forward, every AI interaction — every quiz, every explanation, every revision plan — is grounded in the student's own trusted sources, not generic internet content.

> **"Your knowledge. Your exam. Your AI."**

---

## 2. Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| O1. Enable universal document ingestion | Support 15+ file formats | Format coverage score |
| O2. Build trusted knowledge bases automatically | 80% of resources from official sources | Source confidence audit |
| O3. Make knowledge AI-ready in < 5 minutes per 100 pages | < 5 min | Processing latency |
| O4. Ensure every AI response is grounded | 100% of responses cite sources | Retrieval coverage |
| O5. Support zero-upload exam setup | Auto-collect resources for top 100 exams | Coverage matrix |
| O6. Maintain user data privacy | Zero third-party sharing of raw documents | Compliance audit |

---

## 3. User Personas

### Persona 1: Priya — JEE Aspirant
- 17 years old, preparing for IIT-JEE (India)
- Has 50+ PDFs: NCERT textbooks, coaching notes, PYQs, formula sheets
- Wants to ask: "Explain this thermodynamics problem from my coaching material"
- Struggles with: generic AI answers that don't match her board's syllabus

### Persona 2: David — CPA Candidate
- 28 years old, preparing for US CPA certification
- Uses official Wiley textbooks, Becker notes, AICPA released questions
- Wants to: generate flashcards automatically from his highlighted notes
- Struggles with: organizing 2000+ pages across 4 subjects

### Persona 3: Maria — Medical Student
- 22 years old, preparing for medical licensing exam (Spain)
- Uploads handwritten notes, anatomy diagrams, clinical case summaries
- Wants to: search her notes by concept, not by filename
- Struggles with: OCR quality on handwritten Spanish text

### Persona 4: Ahmed — High School Student
- 15 years old, no study materials yet
- Has exam name and date only
- Wants the AI to find and organize official resources for him
- Struggles with: knowing which sources are trustworthy

---

## 4. User Stories

### US-01: Upload Documents
**As a** student, **I want to** drag and drop my PDF notes into the platform, **so that** they become part of my AI knowledge base.

**Acceptance Criteria:**
- [ ] Support drag-and-drop for single and multiple files
- [ ] Support folder upload (ZIP extraction)
- [ ] Show upload progress per file
- [ ] Validate file type before upload
- [ ] Reject files > 100MB with clear error message
- [ ] Support PDF, DOCX, PPTX, TXT, EPUB, images, ZIP

### US-02: OCR on Scanned Notes
**As a** student with handwritten notes, **I want to** upload scanned images, **so that** the AI can read and search my handwriting.

**Acceptance Criteria:**
- [ ] Support JPG, PNG, TIFF, HEIC
- [ ] OCR accuracy > 85% for printed text
- [ ] OCR accuracy > 70% for clear handwriting
- [ ] Preserve text layout (columns, tables)
- [ ] Support multilingual OCR (English, Spanish, Hindi, Chinese, Arabic)

### US-03: Zero-Upload Exam Setup
**As a** student with no materials, **I want to** enter my exam details, **so that** the AI finds official resources for me.

**Acceptance Criteria:**
- [ ] Collect: exam name, board, country, year, subjects, language, target score, exam date
- [ ] Auto-search official websites for syllabus PDFs
- [ ] Auto-search for official PYQs
- [ ] Present found resources for user approval
- [ ] Download and process approved resources automatically
- [ ] Show confidence score for each auto-found source

### US-04: View Knowledge Base
**As a** student, **I want to** see what topics the AI extracted from my documents, **so that** I can verify correctness.

**Acceptance Criteria:**
- [ ] Show topic hierarchy (subject → chapter → topic → subtopic)
- [ ] Show source document for each topic
- [ ] Show extracted concepts, definitions, formulas
- [ ] Allow editing topic names and hierarchy
- [ ] Show processing status per document (pending / processing / ready / error)

### US-05: Search Knowledge Base
**As a** student, **I want to** search "integration by parts" across all my documents, **so that** I find every occurrence quickly.

**Acceptance Criteria:**
- [ ] Support full-text search across all documents
- [ ] Support semantic search ("find similar to this concept")
- [ ] Filter by document, subject, chapter, date range
- [ ] Show snippet previews with highlighting
- [ ] Rank results by relevance and source confidence

### US-06: Ask Grounded Questions
**As a** student, **I want to** ask "What are the main causes of WWI?" and get an answer only from my uploaded textbook, **so that** I don't learn content not in my syllabus.

**Acceptance Criteria:**
- [ ] Every AI response cites specific source document(s)
- [ ] Option to restrict search to specific documents or topics
- [ ] Show confidence score for each cited source
- [ ] "I don't know" response when no relevant content found
- [ ] No hallucination of content not in knowledge base

### US-07: Generate Flashcards from Documents
**As a** student, **I want to** select a chapter and generate flashcards, **so that** I can review key concepts efficiently.

**Acceptance Criteria:**
- [ ] Extract key terms, definitions, formulas from selected content
- [ ] Generate question-answer pairs
- [ ] Allow manual editing before saving
- [ ] Support image-based flashcards (diagrams, formulas)
- [ ] Export to Anki format

### US-08: Generate Quizzes from Documents
**As a** student, **I want to** generate a 10-question quiz from my PYQs, **so that** I can test my understanding.

**Acceptance Criteria:**
- [ ] Extract questions from uploaded question banks
- [ ] Generate new questions from content (not just extract)
- [ ] Support MCQ, true/false, fill-in-the-blank, short answer
- [ ] Track performance per topic
- [ ] Show explanation with source citation

### US-09: Generate Revision Plan from Documents
**As a** student, **I want to** generate a daily study plan based on my document content, **so that** I prioritize what's in my syllabus.

**Acceptance Criteria:**
- [ ] Extract topic difficulty from document analysis
- [ ] Extract past paper frequency from PYQs
- [ ] Integrate with existing planner scoring (D, P, U, S)
- [ ] Show which documents each plan item comes from
- [ ] Allow manual override of auto-generated priorities

### US-10: Reprocess Documents
**As a** student, **I want to** re-upload a corrected version of my notes and have the AI reprocess it, **so that** my knowledge base stays accurate.

**Acceptance Criteria:**
- [ ] Detect duplicate documents by content hash
- [ ] Offer "replace existing" or "keep both" options
- [ ] Preserve manual edits (topic names, hierarchy) where possible
- [ ] Show diff of changes between versions
- [ ] Incremental reprocessing (only changed sections)

---

## 5. Functional Requirements

### FR-01: File Upload
- Support PDF, DOCX, PPTX, TXT, EPUB, JPG, PNG, TIFF, HEIC, ZIP
- Max file size: 100MB per file, 1GB total per upload batch
- ZIP auto-extract and process contents recursively
- Virus scan all uploads (ClamAV or cloud-native)
- Reject encrypted/password-protected PDFs with clear error

### FR-02: Document Validation
- Verify file magic numbers (not just extensions)
- Detect corrupted files before processing
- Extract basic metadata: filename, size, page count, creation date
- Check for duplicate content (perceptual hash + content hash)
- Flag suspicious files (e.g., executable content embedded in PDF)

### FR-03: OCR Pipeline
- Printed text: Tesseract 5.x or cloud OCR (Google Vision / AWS Textract)
- Handwritten text: Google Vision Handwriting API or custom model
- Mathematical formulas: MathPix or LaTeX OCR
- Diagrams: Detect and extract as images with captions
- Tables: Detect structure and convert to markdown/HTML tables
- Languages: English, Spanish, Hindi, Mandarin, Arabic, French, German, Portuguese, Russian, Japanese
- Confidence threshold: reject OCR results below 60% confidence; flag for manual review

### FR-04: Text Extraction & Cleaning
- Extract text while preserving document structure (headings, lists, paragraphs)
- Remove headers, footers, page numbers
- Remove watermarks (detect and exclude repeated text)
- Normalize whitespace and line breaks
- Preserve mathematical formulas as LaTeX
- Preserve code blocks with language detection
- Detect and preserve citations/references

### FR-05: Semantic Chunking
- Chunk size: 300-800 tokens (configurable)
- Overlap: 80 tokens between chunks
- Respect document boundaries: never split headings, tables, formulas, or code blocks
- Create hierarchical chunks: document → chapter → section → paragraph
- Metadata per chunk: source doc, page number, heading, topic, subject

### FR-06: Embedding Generation
- Model: BAAI/bge-large-en-v1.5 (default) or OpenAI text-embedding-3-small (optional)
- Batch size: 32 chunks per batch
- Dimension: 1024 (BAAI) or 1536 (OpenAI)
- Normalization: L2 normalize all vectors
- Storage: Supabase pgvector with IVFFlat index
- Update strategy: incremental (only re-embed changed chunks)

### FR-07: Knowledge Extraction
- Concepts: extract key terms and definitions
- Formulas: detect mathematical expressions, convert to LaTeX
- Question banks: extract MCQs, fill-in-blank, short answer from PYQs
- Learning objectives: infer from headings and chapter summaries
- Prerequisites: identify topic dependency relationships
- Difficulty: estimate from question complexity, formula density, language level

### FR-08: Knowledge Organization
- Topic hierarchy: subject → chapter → topic → subtopic
- Knowledge graph: nodes = concepts, edges = relationships (prerequisite, related, part-of)
- Metadata index: document properties, tags, upload date, processing status
- Semantic index: vector embeddings for similarity search
- Full-text index: inverted index for keyword search

### FR-09: Hybrid Retrieval
- Dense retrieval: vector similarity search (top-k = 10)
- Sparse retrieval: keyword BM25 search (top-k = 10)
- Metadata filtering: filter by subject, chapter, document, date range, source confidence
- Graph traversal: follow prerequisite chains and related concepts
- Re-ranking: cross-encoder model (BAAI/bge-reranker) to re-rank combined results
- Fusion: Reciprocal Rank Fusion (RRF) to combine dense + sparse scores
- Final output: top 5 most relevant chunks with citations

### FR-10: Source Confidence Scoring
- Official exam board documents: 1.0 (highest)
- Government educational portals: 0.95
- NCERT / Open educational resources: 0.90
- Trusted publishers (Wiley, Pearson, etc.): 0.85
- Coaching institute materials: 0.70
- User-uploaded class notes: 0.65
- Community-generated content: 0.40
- Unverified internet sources: 0.20
- Cross-validation boost: +0.10 if corroborated by higher-confidence source

### FR-11: User Management Features
- Document CRUD: upload, view, delete, replace, reprocess
- Organization: folders, tags, favorites
- Search: full-text, semantic, filtered
- Export: download processed knowledge as JSON, Markdown, or Anki deck
- Sharing: share topics or documents with study groups (read-only or read-write)
- Versioning: keep document history, allow rollback

### FR-12: AI Grounding
- All AI responses must include citation markers [1], [2], etc.
- Citations link to specific document, page, and chunk
- Option to "show sources" in every response
- Option to restrict AI to specific documents or topics
- "No relevant content found" response when retrieval fails
- Confidence threshold: only cite sources with confidence > 0.50

### FR-13: Exam Auto-Setup
- Exam database: 100+ top exams (JEE, NEET, SAT, GRE, GMAT, CPA, CFA, etc.)
- For each exam: official website, syllabus URL, known PYQ repositories
- Web scraping: polite rate-limited crawling of official sites
- Fallback: search DuckDuckGo / Google for official resources
- User approval: present found resources, let user select which to import
- Processing: download → validate → process → index

---

## 6. Non-Functional Requirements

### NFR-01: Scalability
- Support 10,000 concurrent users
- Process 1,000 documents per hour
- Store 10 million chunks per tenant
- Vector search latency < 200ms p95
- Full-text search latency < 100ms p95
- API response time < 500ms p95 for simple queries

### NFR-02: Security
- TLS 1.3 for all data in transit
- AES-256 encryption for data at rest
- Document content encrypted with user-specific keys
- Zero-knowledge architecture: platform cannot read raw documents without user key
- RBAC: user, admin, system roles
- API key authentication for programmatic access
- Rate limiting: 100 req/min free, 1000 req/min pro, 10,000 req/min enterprise

### NFR-03: Privacy
- GDPR, CCPA, and India's DPDP Act compliance
- Right to data portability (export all data as JSON)
- Right to erasure (delete all user data within 30 days)
- No training of AI models on user documents without explicit opt-in
- Data residency: user can choose region (US, EU, India, etc.)
- Anonymous analytics only (no PII in logs)

### NFR-04: Performance
- Upload processing: < 5 min per 100-page PDF
- Chunking: < 1 min per 100 pages
- Embedding: < 2 min per 100 pages (batch-optimized)
- Indexing: < 1 min per 100 pages
- End-to-end: < 5 min per 100 pages
- Front-end: page load < 2s, search results < 500ms

### NFR-05: Reliability
- 99.9% uptime SLA
- Document processing: 99.5% success rate
- Automatic retry on transient failures (3 retries with exponential backoff)
- Dead letter queue for failed documents (manual review)
- Graceful degradation: if AI service is down, serve cached responses

### NFR-06: Cost Optimization
- Local-first defaults: Ollama (free), BAAI/BGE (free), Kokoro (free)
- Cloud AI only for users who opt-in or exceed free tier
- Object storage: R2 (cheaper than S3) with lifecycle policies
- Cache embeddings: never re-embed unchanged content
- Batch processing: process documents in off-peak hours when possible
- Tiered pricing: free (local only), pro (cloud AI), enterprise (dedicated)

### NFR-07: Fault Tolerance
- Microservices: each pipeline stage can fail independently without affecting others
- Circuit breaker: if OCR service is down, queue for retry
- Fallback: if local LLM fails, fallback to cloud LLM (if user has pro tier)
- Data redundancy: 3x replication for object storage, automated backups for PostgreSQL

### NFR-08: Disaster Recovery
- Daily automated backups of PostgreSQL to separate region
- Point-in-time recovery: 7 days retention
- Document storage: cross-region replication
- RPO: < 1 hour, RTO: < 4 hours
- Runbook for common failure scenarios

### NFR-09: Multi-Tenancy
- Strict tenant isolation at database level (RLS policies)
- Shared infrastructure with resource quotas per tenant
- No cross-tenant data leakage
- Per-tenant rate limits and usage quotas
- Per-tenant customization: supported languages, exam boards, etc.

### NFR-10: Compliance
- SOC 2 Type II (target within 12 months of launch)
- GDPR Article 32 (security of processing)
- Accessibility: WCAG 2.1 AA compliance
- Data retention: configurable (default 2 years after account deletion)

### NFR-11: Observability
- Structured logging (JSON) with correlation IDs
- Metrics: processing time, success rate, queue depth, cache hit rate
- Distributed tracing: OpenTelemetry with Jaeger
- Dashboards: Grafana for ops, custom analytics for product
- Alerts: PagerDuty for P0 issues, Slack for P1 issues
- Log retention: 30 days hot, 1 year cold (S3 Glacier)

### NFR-12: Audit Trails
- Log all user actions: upload, delete, search, share, AI query
- Log all admin actions: policy changes, manual data access
- Log all system actions: processing jobs, embedding generation, model updates
- Immutable audit logs (WORM storage)
- Retention: 7 years for compliance

---

## 7. Success Metrics & KPIs

| Metric | Target | Measurement Frequency |
|--------|--------|----------------------|
| Document upload success rate | > 99% | Daily |
| Average processing time (100 pages) | < 5 min | Per document |
| OCR accuracy (printed) | > 85% | Weekly sample |
| OCR accuracy (handwritten) | > 70% | Weekly sample |
| Retrieval precision@5 | > 80% | Weekly evaluation |
| AI response groundedness | 100% citations | Per response |
| User satisfaction (NPS) | > 50 | Monthly survey |
| Daily active users (DAU) | 10,000 | Daily |
| Documents processed per month | 100,000 | Monthly |
| Knowledge base coverage (top 100 exams) | 100% | Quarterly |
| Revenue (MRR) | $10,000 | Monthly |
| Churn rate | < 5% monthly | Monthly |
| Support ticket volume | < 1% of users | Weekly |

---

## 8. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| R1. OCR accuracy on poor-quality scans | High | Medium | Multi-engine OCR (Tesseract + Google Vision), manual review UI, user feedback loop |
| R2. Copyright issues with textbook uploads | Medium | High | DMCA compliance process, educational fair use policy, publisher partnerships |
| R3. Vector search costs at scale | Medium | High | IVFFlat → HNSW index, tiered storage, lazy loading |
| R4. AI hallucination despite grounding | Medium | High | Strict prompt templates, confidence thresholds, human-in-the-loop review for pro tier |
| R5. Exam auto-setup accuracy | Medium | Medium | Human-curated exam database, user feedback on found resources, manual override always available |
| R6. Multi-language support quality | Medium | Medium | Language-specific models, community contributions, gradual rollout |
| R7. Data privacy regulations | High | High | GDPR/CCPA compliance by design, data residency, legal review |
| R8. Competitor with deeper publisher integration | Low | High | Open ecosystem (any document), community features, AI differentiation |
| R9. Processing latency at scale | Medium | Medium | Async processing, queue-based architecture, horizontal scaling |
| R10. User resistance to AI answers | Low | Medium | Transparency (show sources), user control (manual override), gradual onboarding |

---

## 9. Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Core upload pipeline (PDF, DOCX, TXT)
- [ ] Basic OCR (Tesseract, printed text)
- [ ] Semantic chunking
- [ ] Embedding generation (BAAI/BGE)
- [ ] Simple vector search
- [ ] Basic topic extraction

### Phase 2: Intelligence (Weeks 3-4)
- [ ] Handwritten OCR
- [ ] Formula detection (MathPix)
- [ ] Table extraction
- [ ] Knowledge graph (prerequisites)
- [ ] Hybrid retrieval (dense + sparse)
- [ ] Source confidence scoring
- [ ] AI grounding with citations

### Phase 3: Auto-Setup (Weeks 5-6)
- [ ] Exam database (100+ exams)
- [ ] Web scraping for official resources
- [ ] Auto-download and process
- [ ] User approval workflow
- [ ] Source verification

### Phase 4: User Experience (Weeks 7-8)
- [ ] Document management UI
- [ ] Search UI (full-text + semantic)
- [ ] Knowledge base visualization
- [ ] Flashcard generation
- [ ] Quiz generation
- [ ] Revision plan integration

### Phase 5: Scale & Polish (Weeks 9-10)
- [ ] Multi-language support (10 languages)
- [ ] Image and PPTX support
- [ ] EPUB support
- [ ] ZIP folder upload
- [ ] Mobile PWA
- [ ] Performance optimization
- [ ] Security audit
- [ ] Compliance certification

### Phase 6: Ecosystem (Weeks 11-12)
- [ ] LMS integration (Canvas, Blackboard)
- [ ] API v2 for developers
- [ ] Study group collaboration
- [ ] Analytics dashboard
- [ ] Monetization (Stripe billing)

---

## 10. Acceptance Criteria

### AC-01: Upload & Process
- Given a 50-page PDF textbook
- When I upload it via drag-and-drop
- Then it appears in my document list within 10 seconds
- And processing completes within 3 minutes
- And I can see extracted topics, concepts, and formulas
- And each topic links back to the source page

### AC-02: Search
- Given a knowledge base with 10 documents
- When I search "thermodynamics first law"
- Then I see results from all documents containing that concept
- And results are ranked by relevance
- And each result shows a preview with the search term highlighted
- And I can filter by document or subject

### AC-03: Grounded AI Question
- Given a processed chemistry textbook
- When I ask "What is the ideal gas law?"
- Then the AI answers using only content from my textbook
- And the answer includes a citation marker [1]
- And clicking [1] shows the exact page and paragraph
- And the answer does not include information not in my textbook

### AC-04: Zero-Upload Setup
- Given I have no uploaded documents
- When I enter "JEE 2026, Physics, Chemistry, Mathematics"
- Then the system finds NCERT textbooks and official PYQs
- And shows me a list with confidence scores
- And I can approve which ones to import
- And approved documents are processed automatically

### AC-05: Flashcard Generation
- Given a processed biology chapter
- When I select "Generate Flashcards"
- Then I get 20+ flashcards with key terms and definitions
- And each flashcard links to the source paragraph
- And I can edit or delete any flashcard before saving

---

## 11. Dependencies

| Dependency | Status | Owner |
|-----------|--------|-------|
| Supabase project (PostgreSQL + pgvector) | ✅ Ready | DevOps |
| Cloudflare Worker (API gateway) | ✅ Ready | DevOps |
| Docling library | ✅ Ready | AI Team |
| BAAI/BGE embedding model | ✅ Ready | AI Team |
| Tesseract OCR | ✅ Ready | AI Team |
| MathPix API (formula OCR) | 🔄 API key needed | Product |
| Google Vision API (handwriting OCR) | 🔄 API key needed | Product |
| Publisher partnerships (copyright) | 🔄 In progress | Legal |

---

## 12. Open Questions

1. Should we offer OCR as a cloud-only feature or support local Tesseract as default?
2. What is the retention policy for processed document text (vs. raw PDF)?
3. Should we support real-time collaborative annotation on documents?
4. How do we handle documents in right-to-left languages (Arabic, Hebrew)?
5. What is the pricing for pro tier that includes cloud AI processing?

---

*End of PRD*
