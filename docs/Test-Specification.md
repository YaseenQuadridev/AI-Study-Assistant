# Test Specification

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 2.1.0
**Date:** 2026-06-27
**Status:** Approved — Ready for Testing
**Product:** Adaptive Study Planner v4.1.0-ENTERPRISE
**Author:** QA & Engineering Team

---

## 1. Test Levels

```
Level 1: Unit Tests (pytest, jest)
  | Run: Every PR
  | Coverage: ≥ 80%
  | Time: < 2 min
  |
Level 2: Integration Tests (pytest integration/)
  | Run: Every PR
  | Coverage: 100% API endpoints
  | Time: < 5 min
  |
Level 3: AI Evaluation Tests (Ollama, benchmark dataset)
  | Run: Every PR
  | Coverage: MRR@10, Precision@5, Recall@10
  | Time: < 10 min
  |
Level 4: End-to-End Tests (Cypress)
  | Run: Every PR
  | Coverage: 100% critical user flows
  | Time: < 10 min
  |
Level 5: Performance Tests (k6)
  | Run: Nightly
  | Coverage: 200 concurrent users
  | Time: < 30 min
  |
Level 6: Security Tests (OWASP ZAP, Trivy)
  | Run: Every PR + weekly
  | Coverage: 0 critical/high vulnerabilities
  | Time: < 15 min
  |
Level 7: Stress Tests (k6)
  | Run: Weekly
  | Coverage: 50 concurrent uploads, 1000 queries
  | Time: < 60 min
  |
Level 8: Scalability Tests (simulated)
  | Run: Monthly
  | Coverage: 10K concurrent users
  | Time: < 2 hours
  |
Level 9: Disaster Recovery Tests
  | Run: Quarterly
  | Coverage: RPO < 1h, RTO < 4h
  | Time: < 4 hours
```

---

## 2. Test Strategy

### Philosophy
- **Test everything that matters.** If a bug would affect a student's learning, test it.
- **Automate everything possible.** Manual testing is for edge cases only.
- **Test at the right level.** Unit for logic, integration for APIs, E2E for user flows, AI evaluation for quality.
- **Fail fast.** If a test fails, the PR cannot merge.
- **Continuous improvement.** Test suite evolves with the product.

### Test Data
- **Synthetic documents:** Generated via reportlab, fpdf2, python-docx (deterministic, reproducible)
- **Benchmark datasets:** Real anonymized documents (100 docs, 10K pages, 50 subjects)
- **Synthetic queries:** LLM-generated from known content (500 queries, each with known relevant chunks)
- **Test data storage:** `tests/data/` with git-lfs, versioned per release

---

## 3. Test Categories

### 3.1 Upload Tests (Unit + Integration)

**Test Data:** 100 documents (all supported formats, sizes 1KB to 100MB)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| UP-001 | All supported formats | Verify all formats upload successfully | Clean test environment | 15 files (PDF, DOCX, PPTX, TXT, EPUB, JPG, PNG, TIFF, HEIC, ZIP) | All files accepted, status = "uploaded" | 100% success rate | pytest |
| UP-002 | Chunked upload resume | Verify interrupted uploads can resume | Slow connection simulation | 50MB file, interrupted at 50% | Upload resumes from 50%, completes | Resume works, no data loss | pytest |
| UP-003 | Folder upload ZIP | Verify ZIP extraction and processing | ZIP with 10 files | ZIP file (10 mixed formats) | All 10 files extracted, processed | 100% extraction success | pytest |
| UP-004 | Drag-drop multiple | Verify multi-file drag-drop | Browser test | 5 files dragged simultaneously | All 5 files uploaded | 100% success rate | Cypress |
| UP-005 | Upload progress tracking | Verify progress bar accuracy | Large file upload | 100MB file | Progress increments 0-100% | Progress monotonically increasing | Cypress |
| UP-006 | Duplicate detection SHA256 | Verify exact duplicate detection | Same file uploaded twice | Same PDF twice | Second upload flagged as duplicate | 100% duplicate detection | pytest |
| UP-007 | Duplicate detection perceptual hash | Verify similar image detection | Two similar images | Two screenshots of same page | Flagged as similar duplicate | 100% similarity detection | pytest |
| UP-008 | Oversized file rejection | Verify 100MB limit enforcement | Clean environment | 101MB file | Rejected with error code 413 | Error message clear, file not stored | pytest |
| UP-009 | Virus detection EICAR | Verify virus scan works | ClamAV running | EICAR test file | Rejected, quarantined, user notified | 100% virus detection | pytest |
| UP-010 | Invalid magic number | Verify file type validation | Clean environment | PNG renamed to .pdf | Rejected with error "invalid file type" | 100% rejection | pytest |
| UP-011 | Encrypted PDF rejection | Verify password-protected files rejected | Clean environment | Password-protected PDF | Rejected with error "encrypted file" | 100% rejection | pytest |
| UP-012 | Upload rate limiting | Verify rate limit enforcement | Free tier user | 101 uploads in 1 minute | 101st request rejected (429) | Rate limit enforced | k6 |
| UP-013 | Upload resume after 24h | Verify long-term resume capability | Chunked upload started 24h ago | Resume upload | Resumes from last chunk | No data loss | pytest |
| UP-014 | Parallel chunked uploads | Verify multiple chunks upload simultaneously | Clean environment | 10 chunks in parallel | All chunks uploaded | 100% success | pytest |
| UP-015 | ZIP with nested folders | Verify recursive ZIP extraction | ZIP with nested folders | Nested ZIP | All files extracted recursively | 100% extraction | pytest |

### 3.2 Validation Tests (Unit)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| VAL-001 | File type detection libmagic | Verify magic number detection | python-magic installed | 15 files (all formats) | Correct MIME type for all | 100% accuracy | pytest |
| VAL-002 | Encoding detection UTF-8 | Verify UTF-8 detection | chardet installed | UTF-8 text file | Detected as UTF-8 | 100% accuracy | pytest |
| VAL-003 | Encoding detection Latin-1 | Verify Latin-1 detection | chardet installed | Latin-1 text file | Detected as ISO-8859-1 | 100% accuracy | pytest |
| VAL-004 | Language detection English | Verify English detection | fastText model | English text | Detected as English | 100% accuracy | pytest |
| VAL-005 | Language detection Spanish | Verify Spanish detection | fastText model | Spanish text | Detected as Spanish | 100% accuracy | pytest |
| VAL-006 | Language detection Hindi | Verify Hindi detection | fastText model | Hindi text | Detected as Hindi | 100% accuracy | pytest |
| VAL-007 | Corrupted file rejection | Verify corrupted file detection | Clean environment | Corrupted PDF | Rejected with error | 100% rejection | pytest |
| VAL-008 | Empty file rejection | Verify empty file detection | Clean environment | 0-byte file | Rejected with error | 100% rejection | pytest |
| VAL-009 | Password protected rejection | Verify encrypted file detection | Clean environment | Encrypted PDF | Rejected with error | 100% rejection | pytest |
| VAL-010 | Executable embedded in PDF | Verify executable content detection | Clean environment | PDF with embedded JS | Rejected with security warning | 100% detection | pytest |

### 3.3 OCR Accuracy Tests (Unit + Integration)

**Test Data:** 50 documents (20 printed, 15 handwritten, 10 mixed, 5 formula-heavy)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| OCR-001 | Printed text accuracy | Verify Tesseract on printed text | Tesseract 5.x | 20 printed PDFs | Extracted text | WER < 15% | pytest |
| OCR-002 | Handwritten accuracy | Verify Google Vision on handwriting | Google Vision API | 15 handwritten images | Extracted text | WER < 30% | pytest |
| OCR-003 | Formula extraction | Verify MathPix on formulas | MathPix API | 5 formula-heavy pages | LaTeX formulas | Accuracy > 80% | pytest |
| OCR-004 | Multilingual English | Verify English OCR | Tesseract 5.x | English document | Extracted text | WER < 15% | pytest |
| OCR-005 | Multilingual Spanish | Verify Spanish OCR | Tesseract 5.x | Spanish document | Extracted text | WER < 15% | pytest |
| OCR-006 | Multilingual Hindi | Verify Hindi OCR | Tesseract 5.x + lang pack | Hindi document | Extracted text | WER < 20% | pytest |
| OCR-007 | Multilingual Mandarin | Verify Mandarin OCR | Tesseract 5.x + chi_sim | Mandarin document | Extracted text | WER < 20% | pytest |
| OCR-008 | Multilingual Arabic | Verify Arabic OCR | Tesseract 5.x + ara | Arabic document | Extracted text | WER < 20% | pytest |
| OCR-009 | Low confidence flagging | Verify low confidence detection | Clean environment | Blurry scan | Flagged (< 60% confidence) | 100% flagging | pytest |
| OCR-010 | Table preservation | Verify table structure preservation | Tesseract 5.x | Table-heavy page | Markdown table | Structure preserved | pytest |
| OCR-011 | Engine selection logic | Verify automatic engine selection | Multi-engine config | Handwritten image | Google Vision selected | Correct selection | pytest |
| OCR-012 | Fallback to Google Vision | Verify Tesseract fallback | Tesseract fails (< 60%) | Poor quality scan | Google Vision used | Fallback works | pytest |
| OCR-013 | MathPix formula extraction | Verify formula LaTeX conversion | MathPix API | Formula image | LaTeX output | Accuracy > 80% | pytest |
| OCR-014 | Benchmark suite | Run full OCR benchmark | 50-document dataset | All 50 documents | Accuracy report | Printed > 85%, Handwritten > 70%, Formula > 80% | pytest |

### 3.4 Parsing Tests (Unit + Integration)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| PAR-001 | Docling heading preservation | Verify heading hierarchy | Docling installed | PDF with h1, h2, h3 | Markdown with ##, ###, #### | All headings preserved | pytest |
| PAR-002 | Docling table to markdown | Verify table extraction | Docling installed | PDF with table | Markdown table | Structure preserved | pytest |
| PAR-003 | Docling formula to LaTeX | Verify formula preservation | Docling installed | PDF with formula | LaTeX in Markdown | Formula preserved | pytest |
| PAR-004 | Docling image extraction | Verify image detection | Docling installed | PDF with images | Image locations + captions | All images detected | pytest |
| PAR-005 | Docling citation preservation | Verify citation links | Docling installed | PDF with citations | Citation links preserved | Links preserved | pytest |
| PAR-006 | PDF structure parsing | Verify PDF structure | Docling installed | Complex PDF | Structured Markdown | Hierarchy correct | pytest |
| PAR-007 | DOCX structure parsing | Verify DOCX structure | python-docx | DOCX with headings | Structured Markdown | Headings preserved | pytest |
| PAR-008 | PPTX slides parsing | Verify PPTX parsing | python-pptx | PPTX with 10 slides | Per-slide Markdown | All slides parsed | pytest |
| PAR-009 | EPUB chapters parsing | Verify EPUB parsing | ebooklib | EPUB with 5 chapters | Per-chapter Markdown | All chapters parsed | pytest |
| PAR-010 | Text cleaning headers | Verify header removal | TextCleaner | PDF with headers | Clean text (no headers) | Headers removed | pytest |
| PAR-011 | Text cleaning watermarks | Verify watermark removal | TextCleaner | PDF with watermarks | Clean text (no watermarks) | Watermarks removed | pytest |
| PAR-012 | Text cleaning whitespace | Verify whitespace normalization | TextCleaner | PDF with extra whitespace | Normalized whitespace | Collapsed correctly | pytest |

### 3.5 Embedding Validation (Unit)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| EMB-001 | Dimension 1024 | Verify BAAI dimension | BAAI model loaded | "Hello world" | Vector of length 1024 | 100% accuracy | pytest |
| EMB-002 | L2 normalization | Verify normalization | BAAI model loaded | Any text | Vector with norm = 1.0 | |norm| - 1.0| < 0.001 | pytest |
| EMB-003 | Batch size 32 | Verify batch processing | BAAI model loaded | 32 chunks | 32 embeddings | All 32 processed | pytest |
| EMB-004 | Cosine similarity related | Verify semantic similarity | BAAI model loaded | Two related chunks | High cosine similarity | similarity > 0.7 | pytest |
| EMB-005 | Cache hit | Verify Redis cache | Redis running | Same chunk twice | Second from cache | Cache hit recorded | pytest |
| EMB-006 | Cache miss | Verify cache miss | Redis running | New chunk | Computed from model | Cache miss recorded | pytest |
| EMB-007 | Incremental update | Verify partial re-embedding | Redis + PostgreSQL | Changed chunk only | Only changed chunk re-embedded | Old embeddings unchanged | pytest |
| EMB-008 | OpenAI fallback | Verify OpenAI provider | OpenAI API key | "Hello world" | Vector of length 1536 | 100% accuracy | pytest |
| EMB-009 | CPU speed benchmark | Verify CPU performance | BAAI model loaded | 100 chunks | Processing time | < 2s per batch | pytest |
| EMB-010 | GPU speed benchmark | Verify GPU performance | CUDA + BAAI model | 100 chunks | Processing time | < 0.5s per batch | pytest |

### 3.6 Chunking Validation (Unit)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| CHK-001 | Heading respected | Verify heading boundaries | Chunker configured | Document with headings | Chunks start at headings | 100% heading respect | pytest |
| CHK-002 | No table split | Verify table preservation | Chunker configured | Document with table | Table in single chunk | No table splits | pytest |
| CHK-003 | No formula split | Verify formula preservation | Chunker configured | Document with formula | Formula in single chunk | No formula splits | pytest |
| CHK-004 | No code block split | Verify code block preservation | Chunker configured | Document with code block | Code block in single chunk | No code splits | pytest |
| CHK-005 | Overlap 80 tokens | Verify overlap | Chunker configured | Long document | Overlapping text between chunks | Overlap = 80 tokens | pytest |
| CHK-006 | Size range 300-800 | Verify chunk size | Chunker configured | 10 documents | Chunk sizes | All chunks in [300, 800] | pytest |
| CHK-007 | Metadata preservation | Verify metadata | Chunker configured | Document with metadata | Chunks with metadata | Metadata present | pytest |
| CHK-008 | Parent-child relationships | Verify hierarchy | Chunker configured | Hierarchical document | Parent-child links | Hierarchy correct | pytest |
| CHK-009 | Adaptive size | Verify adaptive chunking | Chunker configured | Formula-heavy + prose | Different chunk sizes | Formula chunks smaller | pytest |
| CHK-010 | Hierarchical levels | Verify level assignment | Chunker configured | Document with 4 levels | Chunks with level 1-4 | Levels correct | pytest |
| CHK-011 | Benchmark MRR | Verify retrieval quality | Chunker + Search | 500 queries | MRR@10 score | MRR@10 > 0.6 | pytest |

### 3.7 Retrieval Precision Tests (Integration)

**Test Data:** 500 queries (100 definition, 100 problem, 100 comparison, 100 summary, 100 synonym)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| RET-001 | Precision@5 definition | Verify definition query precision | 500 queries dataset | Definition queries | Top 5 results | Precision > 80% | pytest |
| RET-002 | Precision@5 problem | Verify problem query precision | 500 queries dataset | Problem queries | Top 5 results | Precision > 80% | pytest |
| RET-003 | Precision@5 comparison | Verify comparison query precision | 500 queries dataset | Comparison queries | Top 5 results | Precision > 80% | pytest |
| RET-004 | Precision@5 hybrid vs dense | Compare hybrid vs dense-only | Same queries | All queries | Precision scores | Hybrid > Dense by 10% | pytest |
| RET-005 | Precision@5 hybrid vs sparse | Compare hybrid vs sparse-only | Same queries | All queries | Precision scores | Hybrid > Sparse by 10% | pytest |
| RET-006 | Precision@5 with metadata | Verify metadata filtering | Same queries | Queries + subject filter | Precision scores | Precision > 80% | pytest |
| RET-007 | Precision@5 with graph | Verify graph expansion | Same queries | Queries + graph traversal | Precision scores | Precision > 80% | pytest |
| RET-008 | Precision@5 with re-ranking | Verify re-ranking boost | Same queries | Queries + re-ranker | Precision scores | Precision > 85% | pytest |
| RET-009 | Benchmark precision | Run full precision benchmark | 500 queries | All queries | Precision report | Precision@5 > 80% | pytest |

### 3.8 Retrieval Recall Tests (Integration)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| REC-001 | Recall@10 definition | Verify definition recall | 500 queries dataset | Definition queries | Top 10 results | Recall > 50% | pytest |
| REC-002 | Recall@10 problem | Verify problem recall | 500 queries dataset | Problem queries | Top 10 results | Recall > 50% | pytest |
| REC-003 | Recall@10 synonym | Verify synonym recall | 500 queries dataset | Synonym queries | Top 10 results | Recall > 50% | pytest |
| REC-004 | Recall@10 multilingual | Verify multilingual recall | 500 queries dataset | Multilingual queries | Top 10 results | Recall > 50% | pytest |
| REC-005 | Benchmark recall | Run full recall benchmark | 500 queries | All queries | Recall report | Recall@10 > 50% | pytest |

### 3.9 Hallucination Tests (AI Evaluation)

**Test Data:** 200 questions with known answers from knowledge base

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| HAL-001 | No hallucination 100 questions | Verify 0 hallucinations | 200 questions | 100 questions | AI responses | 0 unsupported claims | pytest + Ollama |
| HAL-002 | No hallucination off-topic | Verify off-topic handling | 200 questions | 50 off-topic questions | "I don't know" | 100% "I don't know" | pytest + Ollama |
| HAL-003 | No hallucination partial context | Verify partial context | 200 questions | 50 partial context | Responses with caveats | 0 unsupported claims | pytest + Ollama |
| HAL-004 | No hallucination multiple docs | Verify multi-document context | 200 questions | 50 multi-doc questions | Responses with citations | 0 unsupported claims | pytest + Ollama |
| HAL-005 | Benchmark hallucination | Run full hallucination benchmark | 200 questions | All questions | Hallucination report | 0 hallucinations | pytest + Ollama |

**Verification Method:**
```python
def verify_no_hallucination(response, context_chunks):
    claims = extract_claims(response)  # NLP claim extraction
    for claim in claims:
        if not claim_in_context(claim, context_chunks):
            return False, claim
    return True, None
```

### 3.10 Grounding Tests (AI Evaluation)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| GRD-001 | Citation present | Verify citations in all responses | 200 questions | All questions | Responses with [1], [2] | 100% citations present | pytest + Ollama |
| GRD-002 | Citation verified | Verify citations link to chunks | 200 questions | All questions | Verified citations | 100% citations verified | pytest + Ollama |
| GRD-003 | Confidence above threshold | Verify confidence > 0.50 | 200 questions | All questions | Confidence scores | All > 0.50 | pytest + Ollama |
| GRD-004 | Context only | Verify no external knowledge | 200 questions | All questions | Responses | No external claims | pytest + Ollama |
| GRD-005 | I don't know off-topic | Verify off-topic refusal | 200 questions | 50 off-topic | "I don't know" | 100% refusal | pytest + Ollama |
| GRD-006 | I don't know insufficient | Verify insufficient context | 200 questions | 50 insufficient | "I don't know" | 100% refusal | pytest + Ollama |
| GRD-007 | Benchmark grounding | Run full grounding benchmark | 200 questions | All questions | Grounding report | 100% grounding score | pytest + Ollama |

### 3.11 Citation Tests (Unit + Integration)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| CIT-001 | Format correct | Verify citation format | Citation service | Response with [1] | Formatted citation | Format correct | pytest |
| CIT-002 | Index sequential | Verify citation numbering | Citation service | Response with [1], [3] | Sequential [1], [2] | Sequential | pytest |
| CIT-003 | Links to existing chunk | Verify chunk linkage | Citation service + DB | Response with [1] | Chunk exists | Chunk verified | pytest |
| CIT-004 | Confidence above 0.50 | Verify confidence threshold | Citation service | Response with [1] | Confidence > 0.50 | All > 0.50 | pytest |
| CIT-005 | Source document visible | Verify source visibility | Citation service | Response with [1] | Source name shown | Source visible | pytest |
| CIT-006 | Page number correct | Verify page accuracy | Citation service | Response with [1] | Correct page | Page correct | pytest |
| CIT-007 | Verification passes | Verify invented citation detection | Citation service | Response with fake [1] | Flagged as invented | 100% detection | pytest |
| CIT-008 | Multiple sources ordered | Verify source ranking | Citation service | Multiple sources | Ordered by confidence | Highest first | pytest |
| CIT-009 | Invented citation fails | Verify fake citation rejection | Citation service | Fake citation | Verification fails | 100% rejection | pytest |
| CIT-010 | Wrong chunk fails | Verify wrong chunk detection | Citation service | Wrong chunk reference | Verification fails | 100% detection | pytest |

### 3.12 Source Ranking Tests (Integration)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| SRC-001 | Official above community | Verify ranking | Source ranking | Official + community sources | Official ranked higher | Official > Community | pytest |
| SRC-002 | NCERT above coaching | Verify NCERT ranking | Source ranking | NCERT + coaching | NCERT ranked higher | NCERT > Coaching | pytest |
| SRC-003 | Cross-validation boost | Verify boost | Source ranking | Same fact in 2 sources | Boosted confidence | Boost > 0.10 | pytest |
| SRC-004 | User override | Verify manual override | Source ranking | User-adjusted score | Adjusted score used | Override respected | pytest |
| SRC-005 | Confidence filtering | Verify threshold | Source ranking | Sources < 0.50 | Filtered out | All results > 0.50 | pytest |
| SRC-006 | Badge colors | Verify badge system | Source ranking | Sources 0.2-1.0 | Green/yellow/red | Correct colors | Cypress |

### 3.13 Duplicate Detection Tests (Unit + Integration)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| DUP-001 | SHA256 same file | Verify exact duplicate | Duplicate detector | Same file twice | Flagged duplicate | 100% detection | pytest |
| DUP-002 | SHA256 different files | Verify no false positive | Duplicate detector | Different files | Not flagged | 0% false positive | pytest |
| DUP-003 | Perceptual hash similar | Verify image similarity | Duplicate detector | Similar images | Flagged similar | 100% detection | pytest |
| DUP-004 | Perceptual hash different | Verify no image false positive | Duplicate detector | Different images | Not flagged | 0% false positive | pytest |
| DUP-005 | Cross-document duplicate | Verify cross-document detection | Duplicate detector | Same content in 2 docs | Flagged | 100% detection | pytest |
| DUP-006 | Replace vs keep both | Verify user choice | Duplicate detector | Duplicate + user choice | Correct action | Choice respected | pytest |
| DUP-007 | Version incremental | Verify version tracking | Duplicate detector | Updated document | Version incremented | Version correct | pytest |

### 3.14 Knowledge Graph Tests (Integration)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| KGR-001 | Prerequisite traversal | Verify chain traversal | Graph with 5 nodes | "Thermodynamics" | Prerequisites list | Chain correct | pytest |
| KGR-002 | Related concepts | Verify related edges | Graph with 10 nodes | "Integration" | Related concepts | Related found | pytest |
| KGR-003 | Part-of relationships | Verify part-of edges | Graph with hierarchy | "Calculus" | Sub-topics | Sub-topics found | pytest |
| KGR-004 | Concept gap detection | Verify gap analysis | Graph with missing edges | Target topic | Missing prerequisites | Gaps detected | pytest |
| KGR-005 | Learning path optimization | Verify shortest path | Graph with 20 nodes | Start + target | Optimized path | Path optimal | pytest |
| KGR-006 | Graph visualization data | Verify data format | Graph with 10 nodes | Graph query | JSON format | Valid JSON | pytest |
| KGR-007 | Query latency | Verify speed | Graph with 10K edges | Prerequisite query | Response time | < 100ms | pytest |
| KGR-008 | Consistency after reprocessing | Verify consistency | Graph + reprocessing | Reprocessed document | Updated graph | Consistent | pytest |

### 3.15 Zero-Upload Setup Tests (E2E)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| ZUP-001 | Auto setup JEE 2026 | Verify JEE resource discovery | Web scraper | JEE 2026, PCM | Found resources | > 3 resources | pytest |
| ZUP-002 | Auto setup NEET 2026 | Verify NEET resource discovery | Web scraper | NEET 2026, PCB | Found resources | > 3 resources | pytest |
| ZUP-003 | Auto setup SAT 2026 | Verify SAT resource discovery | Web scraper | SAT 2026 | Found resources | > 3 resources | pytest |
| ZUP-004 | Resource ranking | Verify ranking | Web scraper | Mixed sources | Ranked list | Official > Community | pytest |
| ZUP-005 | User approval workflow | Verify approval | Web scraper + UI | Found resources | Approval UI | Workflow works | Cypress |
| ZUP-006 | Rejection handling | Verify rejection | Web scraper + UI | Rejected resources | Not processed | Rejected skipped | pytest |
| ZUP-007 | Processing after approval | Verify auto-processing | Approved resources | Approved resources | Status = "ready" | Processing complete | pytest |
| ZUP-008 | Rate limiting | Verify scraper rate limits | Web scraper | 100 requests | Rate limited | Max 1 req/sec | pytest |

### 3.16 Export Tests (Integration)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| EXP-001 | JSON valid | Verify JSON export | Knowledge base | Export JSON | Valid JSON file | Valid JSON | pytest |
| EXP-002 | Markdown valid | Verify Markdown export | Knowledge base | Export Markdown | Valid Markdown | Valid Markdown | pytest |
| EXP-003 | Anki valid | Verify Anki export | Knowledge base | Export Anki | Valid .apkg file | Valid Anki | pytest |
| EXP-004 | PDF valid | Verify PDF export | Knowledge base | Export PDF | Valid PDF file | Valid PDF | pytest |
| EXP-005 | Includes citations | Verify citations in export | Knowledge base | Export | Citations included | All citations present | pytest |
| EXP-006 | Includes metadata | Verify metadata in export | Knowledge base | Export | Metadata included | All metadata present | pytest |
| EXP-007 | Large knowledge base | Verify large export | 1000 topics | Export | Complete export | All data exported | pytest |

### 3.17 Collaboration Tests (Integration)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| COL-001 | Share read-only | Verify read-only sharing | 2 users + topic | Share read-only | Viewer sees topic | Viewer can read | pytest |
| COL-002 | Share read-write | Verify read-write sharing | 2 users + topic | Share read-write | Editor can edit | Editor can write | pytest |
| COL-003 | Group study session | Verify group session | Study group | Group session | Session created | Session works | pytest |
| COL-004 | Shared document visibility | Verify visibility | Shared document | 2 users | Both see document | Visibility correct | pytest |
| COL-005 | Permission revocation | Verify revocation | Shared topic | Revoke permission | Access removed | Immediate revocation | pytest |
| COL-006 | Realtime cursor | Verify cursor sync | 2 users editing | Simultaneous edit | Cursor positions sync | Cursor sync | Cypress |

### 3.18 Existing Tests (Preserved from v2.0.0)

All existing tests from v2.0.0 are preserved:
- 3.1-3.6: Unit, Integration, E2E, AI, Security, Regression (original content)
- 4.1-4.5: Performance, Load, Scalability, Stress, Penetration (original content)
- 5.1-5.2: Accessibility, Localization (original content)
- 6.1-6.2: Disaster Recovery, Telegram Backup (original content)
- 7.1-7.2: Acceptance, Regression (original content)
- 8.1-8.2: Test Data, Automation (original content)
- 9.1-9.2: Exit Criteria, Continuous Improvement (original content)

---

## 4. Performance Tests (Expanded)

| Test ID | Name | Objective | Preconditions | Inputs | Expected Output | Success Criteria | Automation |
|---------|------|-----------|---------------|--------|-----------------|------------------|------------|
| PERF-001 | Processing 100 pages | Verify processing speed | Clean environment | 100-page PDF | Processing time | < 5 min | pytest |
| PERF-002 | Processing 50 pages | Verify processing speed | Clean environment | 50-page PDF | Processing time | < 3 min | pytest |
| PERF-003 | Chunking 100 pages | Verify chunking speed | Clean environment | 100-page PDF | Chunking time | < 1 min | pytest |
| PERF-004 | Embedding 100 pages | Verify embedding speed | Clean environment | 100-page PDF | Embedding time | < 2 min | pytest |
| PERF-005 | Vector search p95 | Verify vector search latency | 1M vectors | 100 queries | Latency distribution | p95 < 200ms | k6 |
| PERF-006 | Full-text search p95 | Verify full-text latency | 1M documents | 100 queries | Latency distribution | p95 < 100ms | k6 |
| PERF-007 | API response p95 | Verify API latency | Production-like | 1000 requests | Latency distribution | p95 < 500ms | k6 |
| PERF-008 | Retrieval end-to-end p95 | Verify full retrieval | Production-like | 500 queries | Latency distribution | p95 < 200ms | k6 |
| PERF-009 | AI response latency | Verify AI generation | LLM running | 100 questions | Response time | < 2s | pytest |
| PERF-010 | Audio generation latency | Verify TTS speed | Kokoro running | 100 words | Audio generation | < 1s per 10 words | pytest |
| PERF-011 | OCR per page | Verify OCR speed | Tesseract running | 100 pages | OCR time | Printed < 2s, Handwritten < 5s | pytest |
| PERF-012 | Graph query latency | Verify graph speed | 10K edges | 100 queries | Query time | < 100ms | pytest |
| PERF-013 | Cache hit latency | Verify cache speed | Redis running | 1000 cached queries | Response time | < 50ms | k6 |
| PERF-014 | Concurrent uploads | Verify upload throughput | 10 workers | 100 files | Upload time | < 10 min | k6 |
| PERF-015 | Concurrent searches | Verify search throughput | 10 workers | 1000 queries | Query time | < 5 min | k6 |

---

## 5. Load Tests (k6, Expanded)

```javascript
// k6 load test configuration
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up
    { duration: '5m', target: 50 },   // Steady state
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Steady state
    { duration: '2m', target: 200 },  // Ramp up
    { duration: '5m', target: 200 },  // Steady state
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.post('https://api.adaptive-study-planner.com/api/v3/search', {
    query: 'thermodynamics first law',
  });
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

| Test ID | Name | Objective | Target | Duration | Thresholds | Automation |
|---------|------|-----------|--------|----------|------------|------------|
| LOAD-001 | Search load 200 users | Verify search capacity | 200 concurrent | 21 min | p95 < 500ms, error < 1% | k6 |
| LOAD-002 | Upload load 50 concurrent | Verify upload capacity | 50 concurrent | 21 min | p95 < 2000ms, error < 1% | k6 |
| LOAD-003 | Ask load 200 users | Verify Q&A capacity | 200 concurrent | 21 min | p95 < 2000ms, error < 1% | k6 |
| LOAD-004 | Dashboard load 100 users | Verify dashboard capacity | 100 concurrent | 21 min | p95 < 1000ms, error < 1% | k6 |
| LOAD-005 | Graph query load 100 users | Verify graph capacity | 100 concurrent | 21 min | p95 < 500ms, error < 1% | k6 |
| LOAD-006 | Document processing 10 parallel | Verify processing throughput | 10 parallel | 30 min | All complete, error < 1% | k6 |
| LOAD-007 | Mixed workload | Verify mixed load | 200 users, mixed | 30 min | All thresholds met | k6 |

---

## 6. Stress Tests (New)

| Test ID | Name | Objective | Target | Duration | Success Criteria | Automation |
|---------|------|-----------|--------|----------|------------------|------------|
| STR-001 | 50 concurrent uploads | Verify upload stress | 50 concurrent | 10 min | < 5% error | k6 |
| STR-002 | 1000 concurrent searches | Verify search stress | 1000 concurrent | 10 min | < 10% error | k6 |
| STR-003 | 100 concurrent asks | Verify Q&A stress | 100 concurrent | 10 min | < 5% error | k6 |
| STR-004 | Connection pool saturation | Verify DB resilience | 1000 connections | 10 min | Graceful degradation | k6 |
| STR-005 | Memory usage 1000 chunks | Verify memory limits | 1000 chunks | 10 min | No OOM | pytest |
| STR-006 | Vector index 1M vectors | Verify index performance | 1M vectors | 10 min | p95 < 500ms | pytest |
| STR-007 | Full-text index 1M docs | Verify text index | 1M documents | 10 min | p95 < 200ms | pytest |
| STR-008 | Cache eviction | Verify cache behavior | Memory pressure | 10 min | Graceful eviction | pytest |

---

## 7. Scalability Tests (New)

| Test ID | Name | Objective | Target | Duration | Success Criteria | Automation |
|---------|------|-----------|--------|----------|------------------|------------|
| SCL-001 | 10K concurrent users | Verify user scale | 10K simulated | 1 hour | < 5% error | k6 |
| SCL-002 | 1000 documents/hour | Verify processing scale | 1000 docs/hour | 1 hour | 99% success | k6 |
| SCL-003 | 10M chunks per tenant | Verify data scale | 10M chunks | 1 hour | Queries < 500ms | pytest |
| SCL-004 | Horizontal scaling Workers | Verify auto-scale | Traffic spike | 1 hour | Auto-scale works | k6 |
| SCL-005 | Read replica routing | Verify replica usage | Read-heavy load | 1 hour | Replicas used | k6 |
| SCL-006 | Connection pooling 1000 | Verify pool scale | 1000 clients | 1 hour | No connection errors | k6 |

---

## 8. Disaster Recovery Tests (New)

| Test ID | Name | Objective | Preconditions | Steps | Success Criteria | Automation |
|---------|------|-----------|---------------|-------|----------------|------------|
| DR-001 | Daily backup | Verify backup completion | PostgreSQL running | Trigger backup | Backup completes | pytest |
| DR-002 | Cross-region replication | Verify replication sync | R2 cross-region | Upload file, check replica | File in replica | pytest |
| DR-003 | Point-in-time recovery | Verify PITR | PostgreSQL WAL | Restore to 1 hour ago | Data restored | pytest |
| DR-004 | RPO under 1 hour | Verify data loss | Production load | Measure max data loss | < 1 hour | pytest |
| DR-005 | RTO under 4 hours | Verify recovery time | Simulated failure | Restore from backup | < 4 hours | Manual |
| DR-006 | Telegram backup | Verify Telegram upload | Telegram bot | Upload document | Document in Telegram | pytest |
| DR-007 | Telegram recovery | Verify Telegram restore | Telegram backup | Trigger recovery | File restored | Manual |
| DR-008 | Migration reversibility | Verify rollback | Migration script | Apply + rollback | Schema unchanged | pytest |
| DR-009 | Feature flag rollback | Verify feature disable | LaunchDarkly | Disable feature | Feature disabled | pytest |

---

## 9. Telegram Backup Tests (New)

| Test ID | Name | Objective | Preconditions | Steps | Success Criteria | Automation |
|---------|------|-----------|---------------|-------|----------------|------------|
| TEL-001 | Upload document | Verify Telegram upload | Bot active | Upload PDF to Telegram | Document in channel | pytest |
| TEL-002 | Download document | Verify Telegram download | Uploaded document | Download from Telegram | File matches original | pytest |
| TEL-003 | Backup integrity | Verify SHA-256 match | Uploaded document | Compare checksums | Checksums match | pytest |
| TEL-004 | Recovery flow | Verify full recovery | Backup exists | Trigger recovery | File restored to R2 | Manual |
| TEL-005 | File size limit | Verify 2GB limit | Bot active | Upload 2.1GB file | Rejected or split | pytest |
| TEL-006 | Backup encryption | Verify encryption | Optional feature | Encrypt before upload | Encrypted upload | pytest |
| TEL-007 | Backup scheduling | Verify scheduled backup | Cron job | Schedule daily backup | Backup runs daily | pytest |

---

## 10. Acceptance Tests (Expanded)

### AC-01: Upload & Process (Existing — Updated)
Given a 50-page PDF textbook
When I upload it via drag-and-drop
Then it appears in my document list within 10 seconds
And processing completes within 3 minutes
And I can see extracted topics, concepts, and formulas
And each topic links back to the source page
**And I can see the knowledge graph preview**
**And I can browse the topic hierarchy**
**And I can see prerequisite chains**

### AC-02: Search (Existing — Updated)
Given a knowledge base with 10 documents
When I search "thermodynamics first law"
Then I see results from all documents containing that concept
And results are ranked by relevance
And each result shows a preview with the search term highlighted
And I can filter by document or subject
**And I can filter by source confidence (high/medium/low)**
**And results show confidence badges per source**
**And I can expand related concepts**

### AC-03: Grounded AI Question (Existing — Updated)
Given a processed chemistry textbook
When I ask "What is the ideal gas law?"
Then the AI answers using only content from my textbook
And the answer includes a citation marker [1]
And clicking [1] shows the exact page and paragraph
And the answer does not include information not in my textbook
**And the citation confidence is > 0.50**
**And the citation is verified against the database**
**And the response time is < 2 seconds**
**And the evidence trace is available**

### AC-04: Zero-Upload Setup (Existing — Updated)
Given I have no uploaded documents
When I enter "JEE 2026, Physics, Chemistry, Mathematics"
Then the system finds NCERT textbooks and official PYQs
And shows me a list with confidence scores
And I can approve which ones to import
And approved documents are processed automatically
**And the system shows a processing progress bar**
**And I receive a notification when complete**
**And official resources are ranked above community sources**

### AC-05: Flashcard Generation (Existing — Updated)
Given a processed biology chapter
When I select "Generate Flashcards"
Then I get 20+ flashcards with key terms and definitions
And each flashcard links to the source paragraph
And I can edit or delete any flashcard before saving
**And flashcards include source citations**
**And I can export to Anki format**
**And formula flashcards render LaTeX correctly**

### AC-06: Knowledge Graph Visualization (New)
Given a processed physics textbook with 30 concepts
When I navigate to the Knowledge Graph view
Then I see an interactive graph with concept nodes
And edges show prerequisite relationships
And I can click a concept to see its definition and source
And the graph renders within 2 seconds
And I can zoom and pan the graph
And prerequisite chains are highlighted

### AC-07: Zero-Upload Auto-Setup (New)
Given I have no uploaded documents
When I enter exam details (JEE 2026, CBSE, India, PCM)
Then the system searches official sources within 60 seconds
And presents at least 3 resources with confidence scores
And official resources are ranked above community sources
And I can approve/reject each resource individually
And approved resources are processed within 5 minutes
And I receive a completion notification with summary
And the knowledge base is ready for search and Q&A

### AC-08: Citation Verification (New)
Given a knowledge base with 5 processed documents
When I ask "Explain Newton's second law"
Then the AI response includes at least one citation [1]
And clicking [1] opens the source document at the correct page
And the citation confidence is displayed (> 0.50)
And the citation is verified in the database
And the evidence trace is available (claim → chunk → document → page)
And there are no invented citations

### AC-09: Export Knowledge Base (New)
Given a knowledge base with 50 topics and 200 concepts
When I export as JSON
Then I receive a valid JSON file with all topics, concepts, and relationships
And the export includes source citations
And the export completes within 10 seconds
When I export as Anki deck
Then I receive a valid .apkg file with flashcards and tags
And the export includes source citations on each card
And the export includes knowledge graph relationships

### AC-10: Collaborative Sharing (New)
Given a user with a processed mathematics document
When they share a topic with read-write permission to a study group
Then group members can see the topic in their knowledge base
And group members can add comments to the topic
And the owner receives a notification when someone comments
And the owner can revoke sharing at any time
And revoked members lose access immediately
And all actions are logged in the audit trail

---

## 11. Regression Tests (Expanded)

| Test ID | Name | Objective | Automation |
|---------|------|-----------|------------|
| REG-001 | Scoring formula | Verify existing scoring formula unchanged | pytest |
| REG-002 | Plan generation | Verify existing plan generation unchanged | pytest |
| REG-003 | Knowledge extraction | Verify extraction quality unchanged | pytest + Ollama |
| REG-004 | Retrieval ranking | Verify ranking order unchanged | pytest |
| REG-005 | Embedding similarity | Verify embedding quality unchanged | pytest |
| REG-006 | Chunking quality | Verify chunking quality unchanged | pytest |
| REG-007 | Grounding policy | Verify grounding policy unchanged | pytest + Ollama |
| REG-008 | Citation format | Verify citation format unchanged | pytest |
| REG-009 | API backward compatibility | Verify API v3 unchanged | pytest |
| REG-010 | Database schema migration | Verify schema migration safety | pytest |

---

## 12. Test Data Strategy

### Synthetic Document Generation
```python
# Generate test PDFs
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def generate_test_pdf(filename, pages, headings, formulas, tables):
    c = canvas.Canvas(filename, pagesize=letter)
    for page in range(pages):
        if page in headings:
            c.drawString(100, 750, f"Heading: {headings[page]}")
        if page in formulas:
            c.drawString(100, 700, f"Formula: {formulas[page]}")
        if page in tables:
            c.drawString(100, 650, f"Table: {tables[page]}")
        c.drawString(100, 600, f"Page {page + 1} content...")
        c.showPage()
    c.save()
```

### Synthetic Query Generation
```python
# Generate queries from known content
from openai import OpenAI

def generate_queries(chunk_text, num_queries=5):
    prompt = f"Generate {num_queries} questions that can be answered from this text: {chunk_text}"
    # Use Ollama for local generation
    return ["What is...?", "Explain...", "How does...?", ...]
```

### Benchmark Dataset
- 100 real anonymized documents (10K pages, 50 subjects)
- 500 synthetic queries with known relevant chunks
- 200 questions with known correct answers
- 50 off-topic questions for "I don't know" testing
- 50 partially-answered questions for caveat testing

---

## 13. Automation Strategy

| Test Type | Frequency | Tool | CI Integration | Parallel |
|-----------|-----------|------|---------------|----------|
| Unit | Every PR | pytest, jest | GitHub Actions | Yes |
| Integration | Every PR | pytest integration/ | GitHub Actions | Yes |
| AI Evaluation | Every PR | pytest + Ollama | GitHub Actions | Yes |
| E2E | Every PR | Cypress | GitHub Actions | Yes |
| Security | Every PR | bandit, safety, Trivy, OWASP ZAP | GitHub Actions | Yes |
| Performance | Nightly | k6 | GitHub Actions (scheduled) | Yes |
| Load | Weekly | k6 | GitHub Actions (scheduled) | Yes |
| Stress | Weekly | k6 | GitHub Actions (scheduled) | Yes |
| Scalability | Monthly | k6 + simulated | GitHub Actions (scheduled) | No |
| Disaster Recovery | Quarterly | Manual + pytest | Manual | No |
| Regression | Every release | pytest + Cypress | GitHub Actions | Yes |

---

## 14. Exit Criteria

### Functional Quality
- [ ] Unit test coverage ≥ 80%
- [ ] Integration tests: 100% API endpoints
- [ ] E2E tests: 100% critical user flows
- [ ] Security: 0 critical/high vulnerabilities
- [ ] AI evaluation: MRR@10 > 0.6, Precision@5 > 0.7, Recall@10 > 0.5
- [ ] OCR: Printed > 85%, Handwritten > 70%, Formula > 80%
- [ ] **Citation accuracy: 100% verified**
- [ ] **Hallucination count: 0 on test set**
- [ ] **Grounding score: 100%**
- [ ] **Source ranking accuracy: > 90%**
- [ ] **Duplicate detection: > 95%**
- [ ] **Graph query latency: < 100ms**

### Performance & Scale
- [ ] Load test: 200 concurrent users, < 1% error
- [ ] Scalability: 10K concurrent users simulated
- [ ] API p95 latency: < 500ms
- [ ] Retrieval p95 latency: < 200ms
- [ ] AI response latency: < 2s
- [ ] Processing latency: < 5 min per 100 pages

### Reliability & Recovery
- [ ] DR: RPO < 1h, RTO < 4h
- [ ] Backup verification: daily restore test passes
- [ ] Telegram backup: upload and download verified
- [ ] Circuit breaker: all fallback chains tested
- [ ] Graceful degradation: tested for all critical services

### Compliance & Accessibility
- [ ] Accessibility: WCAG 2.1 AA
- [ ] Privacy: GDPR/CCPA/DPDP compliance verified
- [ ] Audit trail: all actions logged and immutable
- [ ] Encryption: data at rest and in transit verified

---

## 15. Cross-Document Traceability

| Test Section | PRD Requirement | Engineering Spec | ADR | AI Dev Spec |
|-------------|-----------------|------------------|-----|-------------|
| 3.1 Upload Tests | FR-01 | 2.1 | — | E-015 |
| 3.2 Validation Tests | FR-02 | 2.2 | — | E-016 |
| 3.3 OCR Tests | FR-03 | 2.3 | ADR-015 | E-017 |
| 3.4 Parsing Tests | FR-04 | 2.4 | ADR-001 | E-018 |
| 3.5 Embedding Tests | FR-06 | 2.7 | ADR-016 | E-020 |
| 3.6 Chunking Tests | FR-05 | 2.6 | ADR-011 | E-019 |
| 3.7 Retrieval Precision | FR-09 | 2.9 | ADR-009 | E-022 |
| 3.8 Retrieval Recall | FR-09 | 2.9 | ADR-009 | E-022 |
| 3.9 Hallucination Tests | FR-12 | 2.10 | ADR-018 | E-024 |
| 3.10 Grounding Tests | FR-12 | 2.10 | ADR-018 | E-024 |
| 3.11 Citation Tests | FR-12 | 2.10 | ADR-018 | E-024 |
| 3.12 Source Ranking | FR-10 | 2.10 | ADR-013 | E-024 |
| 3.13 Duplicate Tests | FR-01 | 2.1 | — | E-015 |
| 3.14 Graph Tests | FR-08 | 2.8 | ADR-012 | E-021 |
| 3.15 Zero-Upload Tests | FR-13 | 3.3 | — | E-023 |
| 3.16 Export Tests | FR-19 | 2.5 | — | E-025 |
| 3.17 Collaboration Tests | FR-20 | 2.11 | — | E-025 |
| 4 Performance Tests | NFR-04 | 10 | — | E-026 |
| 5 Load Tests | NFR-01 | 10 | — | E-026 |
| 6 Stress Tests | NFR-05 | 12 | — | E-026 |
| 7 Scalability Tests | NFR-01 | 10 | — | E-026 |
| 8 DR Tests | NFR-08 | 13 | ADR-014 | — |
| 9 Telegram Tests | NFR-08 | 6.5 | ADR-014 | — |
| 10 Acceptance Tests | AC-01-10 | 3 | — | All epics |
| 11 Regression Tests | All | All | All | All |

---

*End of Test Specification*
