# Product Requirements Document

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 2.1.0
**Date:** 2026-06-27
**Status:** Approved — Phase 4 Enterprise Active
**Product:** Adaptive Study Planner v4.1.0-ENTERPRISE
**Author:** Product & Engineering Team

---

## 1. Vision

Every student has a unique set of study materials: textbooks, class notes, formula sheets, previous year question papers, and handwritten annotations. These documents are the single most trusted source of knowledge for exam preparation. Yet, no existing study platform treats a student's own documents as first-class citizens in the learning experience.

**The Universal Knowledge Ingestion & AI Knowledge Layer transforms any educational document into a structured, searchable, AI-ready knowledge base.** Students upload their materials. The system extracts, organizes, embeds, and connects every concept. From that point forward, every AI interaction — every quiz, every explanation, every revision plan — is grounded in the student's own trusted sources, not generic internet content.

> **"Your knowledge. Your exam. Your AI."**

### New Product Vision: Personalized AI Learning Platform

Beyond a simple AI tutor, the Adaptive Study Planner becomes a **Personalized AI Learning Platform** that:

* Builds a personal knowledge base for every student from their own materials or auto-discovered official resources.
* Understands the structure, concepts, formulas, and relationships within every uploaded document.
* Automatically collects trusted study resources when the student has no materials to upload.
* Organizes knowledge into a structured graph of subjects, chapters, concepts, topics, and prerequisites.
* Performs Hybrid Retrieval (dense + sparse + metadata + graph) before every AI response.
* Grounds all AI responses in trusted, cited sources with confidence scores.
* Generates personalized learning experiences — flashcards, quizzes, summaries, study plans, and video lessons — derived from the student's own knowledge base.
* Supports both individual learning and collaborative study groups with shared knowledge.
* Provides enterprise-grade security, privacy, scalability, and observability for institutional deployments.

The platform is not an "AI Study Assistant." It is an **Adaptive Learning Operating System** where the student's knowledge is the core asset, and AI is a capability, not the product.

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
| **O7. Build personal knowledge graph for every student** | > 90% of documents have extracted concepts | Knowledge graph coverage |
| **O8. Enable prerequisite-aware study planning** | 100% of topics linked to prerequisites | Prerequisite chain completeness |
| **O9. Support automatic resource discovery** | 80% of exams have official resources found | Auto-discovery success rate |
| **O10. Generate personalized learning materials** | 100% of AI-generated content cites sources | Citation coverage |
| **O11. Support collaborative study groups** | Shared knowledge bases with permission levels | Collaboration feature adoption |
| **O12. Achieve enterprise-grade reliability** | 99.9% uptime, 99.5% processing success | SLA compliance |

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

### Persona 5: Dr. Sharma — University Professor (New)
- 45 years old, teaches undergraduate physics
- Wants to create a shared knowledge base for his class
- Uploads lecture notes, problem sets, reference materials
- Wants to: share topics with students, track prerequisite completion
- Struggles with: distributing consistent study materials across 200 students

### Persona 6: Ravi — Coaching Institute Admin (New)
- 35 years old, manages a coaching center with 500 students
- Has proprietary study materials, mock tests, PYQ banks
- Wants to: create institutional knowledge base, track student progress
- Struggles with: scaling personalized study plans for hundreds of students

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
- [ ] **Resume interrupted uploads**
- [ ] **Detect duplicate documents by content hash**

### US-02: OCR on Scanned Notes
**As a** student with handwritten notes, **I want to** upload scanned images, **so that** the AI can read and search my handwriting.

**Acceptance Criteria:**
- [ ] Support JPG, PNG, TIFF, HEIC
- [ ] OCR accuracy > 85% for printed text
- [ ] OCR accuracy > 70% for clear handwriting
- [ ] Preserve text layout (columns, tables)
- [ ] Support multilingual OCR (English, Spanish, Hindi, Chinese, Arabic)
- [ ] **Flag low-confidence results for manual review**
- [ ] **Support formula OCR (MathPix → LaTeX)**

### US-03: Zero-Upload Exam Setup
**As a** student with no materials, **I want to** enter my exam details, **so that** the AI finds official resources for me.

**Acceptance Criteria:**
- [ ] Collect: exam name, board, country, year, subjects, language, target score, exam date
- [ ] Auto-search official websites for syllabus PDFs
- [ ] Auto-search for official PYQs
- [ ] Present found resources for user approval
- [ ] Download and process approved resources automatically
- [ ] Show confidence score for each auto-found source
- [ ] **Support 100+ top exams (JEE, NEET, SAT, GRE, GMAT, CPA, CFA, etc.)**
- [ ] **Rate-limited polite crawling of official sites**

### US-04: View Knowledge Base
**As a** student, **I want to** see what topics the AI extracted from my documents, **so that** I can verify correctness.

**Acceptance Criteria:**
- [ ] Show topic hierarchy (subject → chapter → topic → subtopic)
- [ ] Show source document for each topic
- [ ] Show extracted concepts, definitions, formulas
- [ ] Allow editing topic names and hierarchy
- [ ] Show processing status per document (pending / processing / ready / error)
- [ ] **Show knowledge graph visualization (concepts + relationships)**
- [ ] **Show prerequisite chains for each topic**

### US-05: Search Knowledge Base
**As a** student, **I want to** search "integration by parts" across all my documents, **so that** I find every occurrence quickly.

**Acceptance Criteria:**
- [ ] Support full-text search across all documents
- [ ] Support semantic search ("find similar to this concept")
- [ ] Filter by document, subject, chapter, date range
- [ ] Show snippet previews with highlighting
- [ ] Rank results by relevance and source confidence
- [ ] **Support concept-based search (find related concepts)**
- [ ] **Show confidence badges per result (green/yellow/red)**

### US-06: Ask Grounded Questions
**As a** student, **I want to** ask "What are the main causes of WWI?" and get an answer only from my uploaded textbook, **so that** I don't learn content not in my syllabus.

**Acceptance Criteria:**
- [ ] Every AI response cites specific source document(s)
- [ ] Option to restrict search to specific documents or topics
- [ ] Show confidence score for each cited source
- [ ] "I don't know" response when no relevant content found
- [ ] No hallucination of content not in knowledge base
- [ ] **Clickable citations [1], [2] linking to exact page and chunk**
- [ ] **Citation verification: verify cited chunks exist in retrieved results**

### US-07: Generate Flashcards from Documents
**As a** student, **I want to** select a chapter and generate flashcards, **so that** I can review key concepts efficiently.

**Acceptance Criteria:**
- [ ] Extract key terms, definitions, formulas from selected content
- [ ] Generate question-answer pairs
- [ ] Allow manual editing before saving
- [ ] Support image-based flashcards (diagrams, formulas)
- [ ] Export to Anki format
- [ ] **Include source citation on each flashcard**
- [ ] **Support formula-based flashcards (LaTeX rendering)**

### US-08: Generate Quizzes from Documents
**As a** student, **I want to** generate a 10-question quiz from my PYQs, **so that** I can test my understanding.

**Acceptance Criteria:**
- [ ] Extract questions from uploaded question banks
- [ ] Generate new questions from content (not just extract)
- [ ] Support MCQ, true/false, fill-in-the-blank, short answer
- [ ] Track performance per topic
- [ ] Show explanation with source citation
- [ ] **Support difficulty-based question selection**
- [ ] **Track prerequisite completion before advancing**

### US-09: Generate Revision Plan from Documents
**As a** student, **I want to** generate a daily study plan based on my document content, **so that** I prioritize what's in my syllabus.

**Acceptance Criteria:**
- [ ] Extract topic difficulty from document analysis
- [ ] Extract past paper frequency from PYQs
- [ ] Integrate with existing planner scoring (D, P, U, S)
- [ ] Show which documents each plan item comes from
- [ ] Allow manual override of auto-generated priorities
- [ ] **Prerequisite-aware planning (can't study Integration without Algebra)**
- [ ] **Concept gap analysis ("You're missing prerequisites for 3 topics")**

### US-10: Reprocess Documents
**As a** student, **I want to** re-upload a corrected version of my notes and have the AI reprocess it, **so that** my knowledge base stays accurate.

**Acceptance Criteria:**
- [ ] Detect duplicate documents by content hash
- [ ] Offer "replace existing" or "keep both" options
- [ ] Preserve manual edits (topic names, hierarchy) where possible
- [ ] Show diff of changes between versions
- [ ] Incremental reprocessing (only changed sections)
- [ ] **Version history with rollback capability**
- [ ] **Preserve knowledge graph relationships during reprocessing**

### US-11: Chunked Upload (New)
**As a** student with a slow connection, **I want to** resume interrupted uploads, **so that** I don't lose progress on large files.

**Acceptance Criteria:**
- [ ] Support chunked upload (split large files into segments)
- [ ] Resume from last successful chunk on interruption
- [ ] Show progress per chunk
- [ ] Support files up to 100MB per file, 1GB per batch
- [ ] **Auto-retry failed chunks (3x with exponential backoff)**

### US-12: View Knowledge Graph (New)
**As a** student, **I want to** see a visual map of concepts and their relationships, **so that** I understand how topics connect.

**Acceptance Criteria:**
- [ ] Show nodes for concepts, topics, formulas
- [ ] Show edges for prerequisites, related concepts, part-of relationships
- [ ] Allow zooming and panning
- [ ] Click a node to see definition and source
- [ ] **Highlight prerequisite chains for selected topic**
- [ ] **Show learning path optimization (shortest path to readiness)**

### US-13: Browse Topic Hierarchy (New)
**As a** student, **I want to** browse my knowledge base as a tree (subject → chapter → topic → subtopic), **so that** I can navigate systematically.

**Acceptance Criteria:**
- [ ] Show expandable tree view
- [ ] Show concept count per topic
- [ ] Show formula count per topic
- [ ] Show question count per topic
- [ ] **Link each topic to source documents and pages**
- [ ] **Show difficulty score per topic**

### US-14: Search by Concept (New)
**As a** student, **I want to** search by concept name (not just keyword), **so that** I find related ideas even with different wording.

**Acceptance Criteria:**
- [ ] Search by concept name returns exact and related concepts
- [ ] Show semantic similarity score
- [ ] Show prerequisite and related concepts
- [ ] **Support query expansion (synonyms, related terms)**
- [ ] **Show concept definitions in search results**

### US-15: Citation Verification (New)
**As a** student, **I want to** verify that every AI citation links to a real source, **so that** I trust the AI's answers.

**Acceptance Criteria:**
- [ ] Every citation [n] links to a specific chunk in the database
- [ ] Clicking citation shows source document, page, and snippet
- [ ] Citation confidence score > 0.50
- [ ] **Flag unverified citations for review**
- [ ] **Show evidence trace (claim → chunk → document → page)**

### US-16: Generate Study Plan from Knowledge Base (New)
**As a** student, **I want to** the AI to generate a study plan using my knowledge base topics, **so that** I study what matters for my exam.

**Acceptance Criteria:**
- [ ] Plan includes topics from uploaded documents
- [ ] Plan considers difficulty, past-paper frequency, prerequisites
- [ ] Plan shows source document for each topic
- [ ] **Prerequisite completion tracked before advancing**
- [ ] **Concept gap analysis highlights missing prerequisites**
- [ ] **Auto-adjust plan when new documents are uploaded**

### US-17: Export Knowledge Base (New)
**As a** student, **I want to** export my knowledge base as JSON, Markdown, or Anki deck, **so that** I can study offline or share with friends.

**Acceptance Criteria:**
- [ ] Export all topics, concepts, definitions, formulas
- [ ] Export as JSON (structured data)
- [ ] Export as Markdown (human-readable)
- [ ] Export as Anki deck (.apkg)
- [ ] **Include source citations in exports**
- [ ] **Include knowledge graph relationships in JSON export**

### US-18: Share Topics with Study Group (New)
**As a** student, **I want to** share specific topics or documents with my study group, **so that** we can collaborate.

**Acceptance Criteria:**
- [ ] Share read-only or read-write permissions
- [ ] Group members see shared topics in their knowledge base
- [ ] **Track who shared what and when**
- [ ] **Allow comments and annotations on shared content**
- [ ] **Revoke sharing at any time**

### US-19: Track Prerequisite Completion (New)
**As a** student, **I want to** see which prerequisites I've completed and which are missing, **so that** I don't study advanced topics prematurely.

**Acceptance Criteria:**
- [ ] Show prerequisite chain for each topic
- [ ] Mark prerequisites as completed based on study sessions
- [ ] **Alert when attempting to study topic with incomplete prerequisites**
- [ ] **Suggest prerequisite review before advancing**
- [ ] **Show progress bar for prerequisite completion**

### US-20: Receive AI Tutor Explanation (New)
**As a** student, **I want to** ask "Explain the ideal gas law with an example from my textbook," **so that** I get a personalized explanation grounded in my own materials.

**Acceptance Criteria:**
- [ ] AI uses only content from my knowledge base
- [ ] Explanation includes specific example from my documents
- [ ] Citation markers [1] link to source page
- [ ] **Show confidence score for the explanation**
- [ ] **Offer alternative explanations from different source documents**

---

## 5. Functional Requirements

### FR-01: File Upload
- Support PDF, DOCX, PPTX, TXT, EPUB, JPG, PNG, TIFF, HEIC, ZIP
- Max file size: 100MB per file, 1GB total per upload batch
- ZIP auto-extract and process contents recursively
- Virus scan all uploads (ClamAV or cloud-native)
- Reject encrypted/password-protected PDFs with clear error
- **Chunked upload support for resumable large file uploads**
- **Duplicate detection via SHA-256 + perceptual hash (pHash)**

### FR-02: Document Validation
- Verify file magic numbers (not just extensions)
- Detect corrupted files before processing
- Extract basic metadata: filename, size, page count, creation date
- Check for duplicate content (perceptual hash + content hash)
- Flag suspicious files (e.g., executable content embedded in PDF)
- **Encoding detection (chardet / charset-normalizer)**
- **Language detection (langdetect / fastText) for 10+ languages**
- **File integrity verification (checksum comparison)**

### FR-03: OCR Pipeline
- Printed text: Tesseract 5.x or cloud OCR (Google Vision / AWS Textract)
- Handwritten text: Google Vision Handwriting API or custom model
- Mathematical formulas: MathPix or LaTeX OCR
- Diagrams: Detect and extract as images with captions
- Tables: Detect structure and convert to markdown/HTML tables
- Languages: English, Spanish, Hindi, Mandarin, Arabic, French, German, Portuguese, Russian, Japanese
- Confidence threshold: reject OCR results below 60% confidence; flag for manual review
- **Multi-engine selection: automatic engine selection based on document type, text clarity, language, user tier**
- **OCR confidence logging per page for quality tracking**

### FR-04: Text Extraction & Cleaning
- Extract text while preserving document structure (headings, lists, paragraphs)
- Remove headers, footers, page numbers
- Remove watermarks (detect and exclude repeated text)
- Normalize whitespace and line breaks
- Preserve mathematical formulas as LaTeX
- Preserve code blocks with language detection
- Detect and preserve citations/references
- **Table extraction as Markdown tables with preserved structure**
- **Image extraction with auto-generated captions**
- **Citation link preservation (document → source → page)**

### FR-05: Semantic Chunking
- Chunk size: 300-800 tokens (configurable)
- Overlap: 80 tokens between chunks
- Respect document boundaries: never split headings, tables, formulas, or code blocks
- Create hierarchical chunks: document → chapter → section → paragraph
- Metadata per chunk: source doc, page number, heading, topic, subject
- **Parent/child relationships: track chunk hierarchy for context assembly**
- **Adaptive chunk size based on content density (formulas vs prose)**
- **Chunk-level quality scoring (completeness, coherence)**

### FR-06: Embedding Generation
- Model: BAAI/bge-large-en-v1.5 (default) or OpenAI text-embedding-3-small (optional)
- Batch size: 32 chunks per batch
- Dimension: 1024 (BAAI) or 1536 (OpenAI)
- Normalization: L2 normalize all vectors
- Storage: Supabase pgvector with IVFFlat index
- Update strategy: incremental (only re-embed changed chunks)
- **Embedding cache in Redis (24h TTL, key = hash of chunk text)**
- **GPU acceleration support (CUDA for BAAI)**
- **Embedding model hot-swapping (config-based provider change)**

### FR-07: Knowledge Extraction
- Concepts: extract key terms and definitions
- Formulas: detect mathematical expressions, convert to LaTeX
- Question banks: extract MCQs, fill-in-blank, short answer from PYQs
- Learning objectives: infer from headings and chapter summaries
- Prerequisites: identify topic dependency relationships
- Difficulty: estimate from question complexity, formula density, language level
- **Chapter detection: automatic heading hierarchy extraction**
- **Topic classification: subject/topic auto-tagging**
- **Example extraction: worked examples and problem sets**
- **Metadata extraction: author, publisher, edition, source type**

### FR-08: Knowledge Organization
- Topic hierarchy: subject → chapter → topic → subtopic
- Knowledge graph: nodes = concepts, edges = relationships (prerequisite, related, part-of)
- Metadata index: document properties, tags, upload date, processing status
- Semantic index: vector embeddings for similarity search
- Full-text index: inverted index for keyword search
- **Concept catalog: flat list of all extracted concepts with definitions**
- **Formula gallery: searchable catalog of all extracted formulas**
- **Question bank index: searchable question database with difficulty tags**
- **Prerequisite chain index: fast lookup of prerequisite relationships**

### FR-09: Hybrid Retrieval
- Dense retrieval: vector similarity search (top-k = 10)
- Sparse retrieval: keyword BM25 search (top-k = 10)
- Metadata filtering: filter by subject, chapter, document, date range, source confidence
- Graph traversal: follow prerequisite chains and related concepts
- Re-ranking: cross-encoder model (BAAI/bge-reranker) to re-rank combined results
- Fusion: Reciprocal Rank Fusion (RRF) to combine dense + sparse scores
- Final output: top 5 most relevant chunks with citations
- **Intent detection: classify query type (definition, problem, comparison, summary)**
- **Query planning: select retrieval strategy based on intent**
- **Query cache: Redis cache for frequent queries (1h TTL)**
- **Query expansion: synonym expansion, spell correction, HyDE (optional)**

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
- **User override: manual confidence adjustment for user documents**
- **Cross-document validation: boost confidence when multiple sources agree**
- **Source type auto-detection from document metadata and URL patterns**

### FR-11: User Management Features
- Document CRUD: upload, view, delete, replace, reprocess
- Organization: folders, tags, favorites
- Search: full-text, semantic, filtered
- Export: download processed knowledge as JSON, Markdown, or Anki deck
- Sharing: share topics or documents with study groups (read-only or read-write)
- Versioning: keep document history, allow rollback
- **Study groups: create, join, manage group membership**
- **Collaborative annotation: comments and highlights on shared documents**
- **Permission levels: owner, editor, viewer, admin**

### FR-12: AI Grounding
- All AI responses must include citation markers [1], [2], etc.
- Citations link to specific document, page, and chunk
- Option to "show sources" in every response
- Option to restrict AI to specific documents or topics
- "No relevant content found" response when retrieval fails
- Confidence threshold: only cite sources with confidence > 0.50
- **Citation verification: verify every cited chunk exists in retrieved results**
- **Evidence trace: show claim → chunk → document → page → confidence**
- **"I don't know" policy: strict refusal when context is insufficient**
- **Grounding audit: log every AI response with citation verification result**

### FR-13: Exam Auto-Setup
- Exam database: 100+ top exams (JEE, NEET, SAT, GRE, GMAT, CPA, CFA, etc.)
- For each exam: official website, syllabus URL, known PYQ repositories
- Web scraping: polite rate-limited crawling of official sites
- Fallback: search DuckDuckGo / Google for official resources
- User approval: present found resources, let user select which to import
- Processing: download → validate → process → index
- **Resource ranking: official > publisher > community (confidence-based)**
- **Rate limiting: max 1 request per second per domain**
- **User-agent rotation and respect for robots.txt**
- **Source verification: verify downloaded files match expected content type**

### FR-14: Document Versioning and Rollback (New)
- Track all versions of uploaded documents
- Store version history in object storage
- Show diff between versions (added/removed/changed topics)
- Rollback to any previous version
- Preserve manual edits during rollback where possible
- **Incremental reprocessing: only reprocess changed sections**
- **Version metadata: upload date, change summary, user notes**

### FR-15: Knowledge Graph Visualization (New)
- Generate interactive graph from extracted concepts and relationships
- Support zoom, pan, and node selection
- Color-code nodes by subject and confidence
- Show edge labels (prerequisite, related, part-of)
- **Export graph as SVG or PNG**
- **Filter graph by subject, document, or confidence threshold**

### FR-16: Prerequisite-Aware Study Planning (New)
- Extract prerequisite chains from knowledge graph
- Block study of topics with incomplete prerequisites
- Suggest prerequisite review before advancing
- Show prerequisite completion progress
- **Auto-detect prerequisite relationships from document content**
- **Learning path optimization: shortest path to exam readiness**

### FR-17: Auto-Resource Discovery (New)
- Search official exam websites for syllabus PDFs
- Search known PYQ repositories
- Search government educational portals
- Rank found resources by source confidence
- Present resources with confidence scores for user approval
- Download and auto-process approved resources
- **Fallback to DuckDuckGo/Google search if official sites fail**
- **Cache discovered resources to avoid repeated searches**

### FR-18: Citation Verification and Formatting (New)
- Extract citation markers [1], [2] from LLM output
- Verify each citation against retrieved chunks
- Format citations with source name, page, confidence
- Handle missing citations gracefully
- **Flag invented citations (citations not in retrieved results)**
- **Support multiple citation formats (numeric, author-date)**
- **Generate citation summary table per response**

### FR-19: Content Export (New)
- Export knowledge base as JSON (structured data with relationships)
- Export as Markdown (human-readable with headings)
- Export as Anki deck (.apkg with tags and source citations)
- Export as PDF (formatted study guide)
- **Include source citations in all exports**
- **Include knowledge graph relationships in JSON export**
- **Support selective export (by subject, topic, or document)**

### FR-20: Collaborative Annotation (New)
- Add comments to specific chunks or documents
- Add highlights to text passages
- Share annotations with study group members
- **Threaded discussions on annotations**
- **Annotation permissions (private, group, public)**
- **Notification when someone comments on your annotation**

---

## 6. Non-Functional Requirements

### NFR-01: Scalability
- Support 10,000 concurrent users
- Process 1,000 documents per hour
- Store 10 million chunks per tenant
- Vector search latency < 200ms p95
- Full-text search latency < 100ms p95
- API response time < 500ms p95 for simple queries
- **Graph query latency < 100ms for < 3 hops**
- **Support 100 concurrent document uploads**

### NFR-02: Security
- TLS 1.3 for all data in transit
- AES-256 encryption for data at rest
- Document content encrypted with user-specific keys
- Zero-knowledge architecture: platform cannot read raw documents without user key
- RBAC: user, admin, system, enterprise roles
- API key authentication for programmatic access
- Rate limiting: 100 req/min free, 1,000 req/min pro, 10,000 req/min enterprise
- **SAML 2.0 / LDAP integration for enterprise SSO**
- **API key scopes: read, write, admin**
- **Field-level encryption for sensitive metadata**

### NFR-03: Privacy
- GDPR, CCPA, and India's DPDP Act compliance
- Right to data portability (export all data as JSON)
- Right to erasure (delete all user data within 30 days)
- No training of AI models on user documents without explicit opt-in
- Data residency: user can choose region (US, EU, India, etc.)
- Anonymous analytics only (no PII in logs)
- **Privacy impact assessment for new features**
- **Data minimization: only collect necessary data**

### NFR-04: Performance
- Upload processing: < 5 min per 100-page PDF
- Chunking: < 1 min per 100 pages
- Embedding: < 2 min per 100 pages (batch-optimized)
- Indexing: < 1 min per 100 pages
- End-to-end: < 5 min per 100 pages
- Front-end: page load < 2s, search results < 500ms
- **OCR: < 2s per page (printed), < 5s per page (handwritten)**
- **Knowledge graph query: < 100ms for < 3 hops**
- **AI response generation: < 2s (including retrieval + generation)**

### NFR-05: Reliability
- 99.9% uptime SLA
- Document processing: 99.5% success rate
- Automatic retry on transient failures (3 retries with exponential backoff)
- Dead letter queue for failed documents (manual review)
- Graceful degradation: if AI service is down, serve cached responses
- **Circuit breaker pattern for external services (OCR, LLM, embedding)**
- **Health checks for all services every 30 seconds**
- **Auto-restart failed services within 60 seconds**

### NFR-06: Cost Optimization
- Local-first defaults: Ollama (free), BAAI/BGE (free), Kokoro (free)
- Cloud AI only for users who opt-in or exceed free tier
- Object storage: R2 (cheaper than S3) with lifecycle policies
- Cache embeddings: never re-embed unchanged content
- Batch processing: process documents in off-peak hours when possible
- Tiered pricing: free (local only), pro (cloud AI), enterprise (dedicated)
- **Telegram cold storage for free backup (optional)**
- **Lazy loading for large knowledge bases**
- **CDN caching for static assets (30-day TTL)**

### NFR-07: Fault Tolerance
- Microservices: each pipeline stage can fail independently without affecting others
- Circuit breaker: if OCR service is down, queue for retry
- Fallback: if local LLM fails, fallback to cloud LLM (if user has pro tier)
- Data redundancy: 3x replication for object storage, automated backups for PostgreSQL
- **Fallback chain: vLLM → OpenAI → Ollama → cached response**
- **Graceful degradation: if embedding fails, skip semantic search, use keyword only**
- **If graph DB is down, skip graph traversal, use dense + sparse only**

### NFR-08: Disaster Recovery
- Daily automated backups of PostgreSQL to separate region
- Point-in-time recovery: 7 days retention
- Document storage: cross-region replication
- RPO: < 1 hour, RTO: < 4 hours
- Runbook for common failure scenarios
- **Telegram cold storage as last-resort backup**
- **Backup verification: daily restore test on staging**
- **Documented rollback procedures for all deployments**

### NFR-09: Multi-Tenancy
- Strict tenant isolation at database level (RLS policies)
- Shared infrastructure with resource quotas per tenant
- No cross-tenant data leakage
- Per-tenant rate limits and usage quotas
- Per-tenant customization: supported languages, exam boards, etc.
- **Per-tenant embedding model selection**
- **Per-tenant knowledge graph customization**
- **Enterprise tenant isolation (schema-level if required)**

### NFR-10: Compliance
- SOC 2 Type II (target within 12 months of launch)
- GDPR Article 32 (security of processing)
- Accessibility: WCAG 2.1 AA compliance
- Data retention: configurable (default 2 years after account deletion)
- **ISO 27001 compliance roadmap**
- **HIPAA compliance for medical education (if applicable)**
- **Regular penetration testing (quarterly)**

### NFR-11: Observability
- Structured logging (JSON) with correlation IDs
- Metrics: processing time, success rate, queue depth, cache hit rate
- Distributed tracing: OpenTelemetry with Jaeger
- Dashboards: Grafana for ops, custom analytics for product
- Alerts: PagerDuty for P0 issues, Slack for P1 issues
- Log retention: 30 days hot, 1 year cold (S3 Glacier)
- **Custom metrics: retrieval precision@5, hallucination rate, citation accuracy**
- **User-facing analytics: study time, topic coverage, progress trends**

### NFR-12: Audit Trails
- Log all user actions: upload, delete, search, share, AI query
- Log all admin actions: policy changes, manual data access
- Log all system actions: processing jobs, embedding generation, model updates
- Immutable audit logs (WORM storage)
- Retention: 7 years for compliance
- **AI grounding audit: log every AI response with retrieval results and citations**
- **Data access audit: log all database queries with user_id and timestamp**
- **Export audit logs for compliance reporting**

---

## 7. Knowledge Management Requirements

### KM-01: Topic Hierarchy
- Automatic extraction of heading hierarchy from documents
- Subject → Chapter → Topic → Subtopic tree structure
- Manual editing of topic names and hierarchy
- Topic merge and split operations
- **Topic aliases (synonym mapping)**
- **Topic difficulty scoring (auto + manual override)**

### KM-02: Concept Catalog
- Extract key terms and definitions from all documents
- Deduplicate concepts across documents
- Link concepts to source chunks and documents
- **Concept confidence scoring (extraction confidence)**
- **Concept relationship inference (related concepts, prerequisites)**
- **Concept gap analysis (missing concepts for exam readiness)**

### KM-03: Formula Gallery
- Detect and catalog all mathematical formulas
- Convert to LaTeX for rendering
- Link formulas to source documents and examples
- **Formula search (by LaTeX, by name, by variable)**
- **Formula prerequisite mapping (e.g., calculus formulas require algebra)**
- **Formula usage examples extraction**

### KM-04: Question Bank
- Extract MCQs, fill-in-blank, short answer from PYQs
- Tag questions by topic, difficulty, and source
- **Question similarity detection (avoid duplicates)**
- **Question performance tracking (correct/incorrect per user)**
- **Question difficulty auto-adjustment based on user performance**

### KM-05: Prerequisite Chains
- Automatically detect prerequisite relationships
- Build prerequisite chains for each topic
- **Prerequisite cycle detection (prevent circular dependencies)**
- **Prerequisite gap analysis (missing prerequisites for target topics)**
- **Learning path optimization (shortest path to exam readiness)**

---

## 8. Upload Workflow

```
User drops files into web app
  ↓
Client-side validation (file type, size preview)
  ↓
POST /api/v3/upload (multipart/form-data, JWT)
  ↓
Cloudflare Worker validates JWT, rate limit
  ↓
Upload Service:
  1. Validate file (magic numbers, size, virus scan)
  2. Check for duplicates (SHA-256 + pHash)
  3. Generate chunked upload URL if file > 10MB
  4. Stream to R2: users/{user_id}/documents/{document_id}/original.{ext}
  5. Insert document record (status: "uploaded")
  6. Trigger Processing Pipeline (async webhook)
  7. Return 202 Accepted with upload_id
  ↓
Processing Pipeline (background):
  Stage 1: Validation → Virus Scan → Encoding Detection → Language Detection
  Stage 2: OCR (if scanned/image) → Text Extraction
  Stage 3: Parsing (Docling) → Structured Markdown
  Stage 4: Cleaning (headers, footers, watermarks removed)
  Stage 5: Metadata Extraction (topics, chapters, concepts, formulas, questions)
  Stage 6: Difficulty Classification
  Stage 7: Duplicate Removal (across documents)
  Stage 8: Semantic Chunking (heading-aware, 300-800 tokens, 80 overlap)
  Stage 9: Embeddings (BAAI/BGE, 1024-dim, L2 normalized, batch 32)
  Stage 10: Knowledge Graph Construction (concepts → prerequisites → relationships)
  Stage 11: Vector Index (pgvector IVFFlat / HNSW)
  Stage 12: Full-Text Index (PostgreSQL GIN tsvector)
  Stage 13: Metadata Index (document properties, tags, status)
  Stage 14: Status = "ready"
  ↓
Web App polls GET /api/v3/documents/:id/status
  ↓
When status = "ready", show:
  "Processing complete! X topics, Y concepts, Z formulas extracted."
  + Knowledge graph preview
  + Topic hierarchy tree
```

**Failure Paths:**
- Transient errors: retry 3x with exponential backoff (1s, 2s, 4s)
- Permanent errors: move to dead letter queue, notify user
- Low OCR confidence: flag for manual review, mark "ready_with_warnings"
- Virus detected: reject, quarantine, notify user
- Duplicate detected: offer "replace existing" or "keep both"

---

## 9. Automatic Resource Discovery Workflow

```
User enters exam details (name, board, country, year, subjects, language, target score, exam date)
  ↓
Web Resource Collector:
  1. Query exam database (100+ exams) for metadata
  2. If exam known:
     a. Search official website for syllabus PDF
     b. Search known PYQ repositories
     c. Search government educational portals
  3. If exam unknown:
     a. DuckDuckGo search: "{exam} {year} official syllabus PDF"
     b. DuckDuckGo search: "{exam} {year} previous year questions"
     c. Google search fallback (if DuckDuckGo fails)
  4. Rank found resources by source confidence:
     - Official exam board: 1.00
     - Government portal: 0.95
     - NCERT: 0.90
     - Trusted publisher: 0.85
     - Coaching: 0.70
  5. Present ranked resources to user with confidence scores
  6. User approves/rejects each resource
  7. Approved resources: download → validate → process → index
  8. Show processing progress for approved resources
  9. Notify: "Auto-setup complete! X resources imported."
```

**Constraints:**
- Polite crawling: max 1 request per second per domain
- Respect robots.txt
- User-agent rotation
- Rate limiting to avoid IP bans
- Cache discovered resources for 24 hours
- Fallback to manual upload if no official resources found

---

## 10. AI Grounding Requirements

### GR-01: Strict Context Adherence
- AI must answer using ONLY the retrieved context
- No external knowledge, no hallucination, no inference beyond context
- If context is insufficient, respond: "I don't have enough information in your knowledge base."

### GR-02: Citation Requirements
- Every factual claim must cite a source [n]
- Citations must link to specific chunks in the database
- Citation confidence must be > 0.50
- Citation format: [n] Source Name, Page X, Confidence Y

### GR-03: Citation Verification
- Verify every [n] in the LLM output against retrieved chunks
- Flag invented citations (not in retrieved results)
- Reject responses with unverified citations
- Log verification results for audit

### GR-04: Evidence Trace
- For every claim, trace: claim → chunk → document → page → confidence
- Show evidence trace on citation click
- Include snippet preview in citation popup

### GR-05: "I Don't Know" Policy
- If no relevant chunks retrieved, respond with "I don't know"
- Suggest alternative searches or document uploads
- Never guess or generate plausible-sounding but unverified answers
- Log all "I don't know" responses for knowledge gap analysis

### GR-06: Confidence Thresholds
- Only cite sources with confidence > 0.50
- High-confidence sources (> 0.85) should dominate citations
- Low-confidence sources (< 0.50) should be excluded from context
- User can override confidence threshold per query

### GR-07: Grounding Audit
- Log every AI query with: question, retrieved chunks, LLM response, citations, verification result
- Grounding score: % of claims with verified citations
- Target: 100% grounding score on all responses
- Monthly audit report for compliance

---

## 11. Security Requirements

### SEC-01: Transport Security
- TLS 1.3 for all API endpoints
- Certificate pinning for mobile apps
- HSTS headers on all responses

### SEC-02: Data Encryption
- AES-256 for data at rest (R2, PostgreSQL)
- Field-level encryption for sensitive PII
- Document content encrypted with user-specific keys (zero-knowledge)
- Key rotation policy (90 days)

### SEC-03: Authentication
- JWT (RS256, 1-hour expiry) for session auth
- OAuth 2.0 (Google, GitHub) for social login
- SAML 2.0 / LDAP for enterprise SSO
- API keys with scopes (read, write, admin) for programmatic access
- Multi-factor authentication (TOTP) for enterprise accounts

### SEC-04: Authorization
- RBAC: user, admin, system, enterprise roles
- Row-Level Security (RLS) on all database tables
- Resource-level permissions (owner, editor, viewer)
- Group-level permissions (admin, moderator, member)
- API key scopes enforced at gateway level

### SEC-05: Rate Limiting & DDoS Protection
- Cloudflare WAF for DDoS protection
- Per-IP rate limit: 100 req/min (free), 1,000 (pro), 10,000 (enterprise)
- Per-user rate limit: token bucket algorithm
- Per-tenant quota enforcement
- CAPTCHA after 3 failed login attempts

### SEC-06: Input Validation
- All user inputs validated against schemas
- SQL injection prevention (parameterized queries only)
- XSS prevention (no innerHTML with user data, textContent only)
- File upload validation (magic numbers, size limits, virus scan)
- JSON schema validation for all API requests

### SEC-07: Audit & Compliance
- Immutable audit logs (WORM storage)
- 7-year retention for compliance
- Log all user actions, admin actions, system actions
- Quarterly penetration testing
- Annual SOC 2 Type II audit

---

## 12. Privacy Requirements

### PRIV-01: Data Minimization
- Collect only necessary data for platform functionality
- No collection of browsing history outside platform
- No tracking pixels or third-party analytics without consent

### PRIV-02: Consent Management
- Explicit opt-in for AI model training on user data
- Granular consent for data sharing (none by default)
- Consent revocation mechanism (30-day deletion)
- Cookie consent banner for non-essential cookies

### PRIV-03: Data Portability
- Export all user data as JSON (complete knowledge base)
- Export study history, performance data, preferences
- Export in machine-readable format within 30 days of request

### PRIV-04: Right to Erasure
- Delete all user data within 30 days of request
- Cascade delete: documents → chunks → embeddings → concepts → knowledge_edges
- Purge from backups within 90 days
- Certificate of deletion upon request

### PRIV-05: Data Residency
- User-selectable region: US, EU, India, Singapore
- Data stored and processed in selected region only
- No cross-border data transfer without explicit consent
- GDPR Article 44 compliance for international transfers

### PRIV-06: Children's Privacy
- COPPA compliance for users under 13
- Parental consent required for accounts under 16
- No data sale to third parties (ever)
- Minimal data collection for minor accounts

---

## 13. Success Metrics & KPIs

| Metric | Target | Measurement Frequency |
|--------|--------|----------------------|
| Document upload success rate | > 99% | Daily |
| Average processing time (100 pages) | < 5 min | Per document |
| OCR accuracy (printed) | > 85% | Weekly sample |
| OCR accuracy (handwritten) | > 70% | Weekly sample |
| Retrieval precision@5 | > 80% | Weekly evaluation |
| AI response groundedness | 100% citations | Per response |
| **Citation verification accuracy** | **100%** | **Per response** |
| **Hallucination rate** | **0%** | **Weekly evaluation** |
| **Knowledge graph coverage** | **> 90%** | **Monthly** |
| **Prerequisite chain accuracy** | **> 80%** | **Monthly** |
| **Auto-discovery success rate** | **> 80%** | **Per exam** |
| User satisfaction (NPS) | > 50 | Monthly survey |
| Daily active users (DAU) | 10,000 | Daily |
| Documents processed per month | 100,000 | Monthly |
| Knowledge base coverage (top 100 exams) | 100% | Quarterly |
| Revenue (MRR) | $10,000 | Monthly |
| Churn rate | < 5% monthly | Monthly |
| Support ticket volume | < 1% of users | Weekly |
| **Uptime SLA** | **99.9%** | **Daily** |
| **Processing success rate** | **99.5%** | **Daily** |
| **API p95 latency** | **< 500ms** | **Daily** |
| **Citation accuracy** | **100%** | **Per response** |

---

## 14. Risks

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
| **R11. Knowledge graph accuracy** | **Medium** | **High** | **Human validation of extracted relationships, user feedback loop, confidence thresholds** |
| **R12. Prerequisite detection errors** | **Medium** | **Medium** | **Conservative prerequisite assignment, user override, multiple source validation** |
| **R13. Citation verification failures** | **Low** | **High** | **Automated verification, fallback to manual review, strict "I don't know" policy** |
| **R14. Auto-discovery legal issues** | **Medium** | **High** | **Robots.txt compliance, rate limiting, fair use policy, DMCA process** |
| **R15. Enterprise SSO integration complexity** | **Medium** | **Medium** | **SAML library abstraction, tested IdP integrations, fallback to local auth** |
| **R16. Telegram backup reliability** | **Low** | **Medium** | **Telegram is optional, not primary; primary backups use R2 cross-region** |
| **R17. Graph database migration complexity** | **Medium** | **Medium** | **PostgreSQL CTEs sufficient for Phase 3; ArangoDB evaluated in Phase 4 with migration script** |
| **R18. Embedding model drift** | **Low** | **Medium** | **Model versioning, benchmark evaluation before upgrades, incremental re-embedding** |

---

## 15. Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Core upload pipeline (PDF, DOCX, TXT)
- [ ] Basic OCR (Tesseract, printed text)
- [ ] Semantic chunking
- [ ] Embedding generation (BAAI/BGE)
- [ ] Simple vector search
- [ ] Basic topic extraction
- [ ] **Document validation (magic numbers, virus scan)**
- [ ] **Duplicate detection**

### Phase 2: Intelligence (Weeks 3-4)
- [ ] Handwritten OCR
- [ ] Formula detection (MathPix)
- [ ] Table extraction
- [ ] Knowledge graph (prerequisites)
- [ ] Hybrid retrieval (dense + sparse)
- [ ] Source confidence scoring
- [ ] AI grounding with citations
- [ ] **Concept extraction (LLM-based)**
- [ ] **Difficulty classification**
- [ ] **Prerequisite detection**

### Phase 3: Auto-Setup (Weeks 5-6)
- [ ] Exam database (100+ exams)
- [ ] Web scraping for official resources
- [ ] Auto-download and process
- [ ] User approval workflow
- [ ] Source verification
- [ ] **Resource ranking by confidence**
- [ ] **Rate-limited polite crawling**
- [ ] **Fallback search (DuckDuckGo/Google)**

### Phase 4: User Experience (Weeks 7-8)
- [ ] Document management UI
- [ ] Search UI (full-text + semantic)
- [ ] Knowledge base visualization
- [ ] Flashcard generation
- [ ] Quiz generation
- [ ] Revision plan integration
- [ ] **Knowledge graph visualization (D3.js)**
- [ ] **Topic hierarchy browser**
- [ ] **Concept search**
- [ ] **Prerequisite tracking UI**

### Phase 5: Scale & Polish (Weeks 9-10)
- [ ] Multi-language support (10 languages)
- [ ] Image and PPTX support
- [ ] EPUB support
- [ ] ZIP folder upload
- [ ] Mobile PWA
- [ ] Performance optimization
- [ ] Security audit
- [ ] Compliance certification
- [ ] **Chunked upload (resume)**
- [ ] **Collaborative annotations**
- [ ] **Export (JSON, Markdown, Anki, PDF)**

### Phase 6: Ecosystem (Weeks 11-12)
- [ ] LMS integration (Canvas, Blackboard)
- [ ] API v2 for developers
- [ ] Study group collaboration
- [ ] Analytics dashboard
- [ ] Monetization (Stripe billing)
- [ ] **Enterprise SSO (SAML/LDAP)**
- [ ] **API v2 with rate limiting and scopes**
- [ ] **Telegram cold storage integration**
- [ ] **Monitoring & alerting (Sentry, Grafana)**

---

## 16. Acceptance Criteria

### AC-01: Upload & Process
- Given a 50-page PDF textbook
- When I upload it via drag-and-drop
- Then it appears in my document list within 10 seconds
- And processing completes within 3 minutes
- And I can see extracted topics, concepts, and formulas
- And each topic links back to the source page
- **And I can see the knowledge graph preview**
- **And I can browse the topic hierarchy**

### AC-02: Search
- Given a knowledge base with 10 documents
- When I search "thermodynamics first law"
- Then I see results from all documents containing that concept
- And results are ranked by relevance
- And each result shows a preview with the search term highlighted
- And I can filter by document or subject
- **And I can filter by source confidence (high/medium/low)**
- **And results show confidence badges per source**

### AC-03: Grounded AI Question
- Given a processed chemistry textbook
- When I ask "What is the ideal gas law?"
- Then the AI answers using only content from my textbook
- And the answer includes a citation marker [1]
- And clicking [1] shows the exact page and paragraph
- And the answer does not include information not in my textbook
- **And the citation confidence is > 0.50**
- **And the citation is verified against the database**
- **And the response time is < 2 seconds**

### AC-04: Zero-Upload Setup
- Given I have no uploaded documents
- When I enter "JEE 2026, Physics, Chemistry, Mathematics"
- Then the system finds NCERT textbooks and official PYQs
- And shows me a list with confidence scores
- And I can approve which ones to import
- And approved documents are processed automatically
- **And the system shows a processing progress bar**
- **And I receive a notification when complete**

### AC-05: Flashcard Generation
- Given a processed biology chapter
- When I select "Generate Flashcards"
- Then I get 20+ flashcards with key terms and definitions
- And each flashcard links to the source paragraph
- And I can edit or delete any flashcard before saving
- **And flashcards include source citations**
- **And I can export to Anki format**

### AC-06: Knowledge Graph Visualization (New)
- Given a processed physics textbook with 30 concepts
- When I navigate to the Knowledge Graph view
- Then I see an interactive graph with concept nodes
- And edges show prerequisite relationships
- And I can click a concept to see its definition and source
- And the graph renders within 2 seconds
- And I can zoom and pan the graph

### AC-07: Zero-Upload Auto-Setup (New)
- Given I have no uploaded documents
- When I enter exam details (JEE 2026, CBSE, India, PCM)
- Then the system searches official sources within 60 seconds
- And presents at least 3 resources with confidence scores
- And official resources are ranked above community sources
- And I can approve/reject each resource individually
- And approved resources are processed within 5 minutes
- And I receive a completion notification with summary

### AC-08: Citation Verification (New)
- Given a knowledge base with 5 processed documents
- When I ask "Explain Newton's second law"
- Then the AI response includes at least one citation [1]
- And clicking [1] opens the source document at the correct page
- And the citation confidence is displayed (> 0.50)
- And the citation is verified in the database
- And the evidence trace is available (claim → chunk → document → page)

### AC-09: Export Knowledge Base (New)
- Given a knowledge base with 50 topics and 200 concepts
- When I export as JSON
- Then I receive a valid JSON file with all topics, concepts, and relationships
- And the export includes source citations
- And the export completes within 10 seconds
- When I export as Anki deck
- Then I receive a valid .apkg file with flashcards and tags
- And the export includes source citations on each card

### AC-10: Collaborative Sharing (New)
- Given a user with a processed mathematics document
- When they share a topic with read-write permission to a study group
- Then group members can see the topic in their knowledge base
- And group members can add comments to the topic
- And the owner receives a notification when someone comments
- And the owner can revoke sharing at any time
- And revoked members lose access immediately

---

## 17. Cross-Document Traceability

| PRD Section | Engineering Spec | ADR | AI Dev Spec | Test Spec |
|-------------|------------------|-----|-------------|-----------|
| FR-01: Upload | 2.1, 5.1 | — | E-015 | 3.7, 10 |
| FR-02: Validation | 2.2, 5.1 | — | E-016 | 3.8, 8.1 |
| FR-03: OCR | 2.3, 7.1 | ADR-015 | E-017 | 3.9, 9.2 |
| FR-04: Parsing | 2.4, 7.1 | ADR-001 | E-018 | 3.10, 9.3 |
| FR-05: Chunking | 2.6, 7.1 | ADR-011 | E-019 | 3.12, 9.4 |
| FR-06: Embedding | 2.7, 7.1 | ADR-016 | E-020 | 3.11, 9.5 |
| FR-07: Extraction | 2.5, 7.1 | — | E-019 | 3.5, 9.6 |
| FR-08: Organization | 2.8, 6.2 | ADR-012 | E-021 | 3.20, 9.6 |
| FR-09: Hybrid Retrieval | 2.9, 7.2 | ADR-009 | E-022 | 3.13, 3.14, 9.1 |
| FR-10: Source Confidence | 2.10 | ADR-013 | E-024 | 3.18, 9.7 |
| FR-11: User Management | 2.5, 2.11 | — | E-025 | 3.21, 3.23 |
| FR-12: AI Grounding | 2.10, 7.2 | ADR-018 | E-024 | 3.15, 3.16, 9.8 |
| FR-13: Auto-Setup | 3.3 | — | E-023 | 3.21, 10 |
| FR-14: Versioning | 2.5 | — | E-015 | 3.19 |
| FR-15: Graph Viz | 2.8 | ADR-012 | E-021 | 3.20 |
| FR-16: Prerequisites | 2.8 | ADR-012 | E-021 | 3.20 |
| FR-17: Auto-Discovery | 3.3 | — | E-023 | 3.21 |
| FR-18: Citation | 2.10 | ADR-018 | E-024 | 3.17, 9.8 |
| FR-19: Export | 2.5 | — | E-025 | 3.22 |
| FR-20: Collaboration | 2.11 | — | E-025 | 3.23 |
| Security (12) | 8, 9 | — | E-014 | 8 |
| Privacy (12) | 8 | — | — | 8 |
| NFR (12) | 10, 11, 12 | — | E-026 | 6, 7 |

---

*End of PRD*
