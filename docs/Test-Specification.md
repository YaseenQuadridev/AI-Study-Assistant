# Test Specification

## Universal Knowledge Ingestion & AI Knowledge Layer

**Version:** 1.0.0
**Date:** 2026-06-26
**Status:** Draft — Ready for Review
**Author:** QA Architecture Team

---

## 1. Testing Philosophy

Testing is not a phase — it is a continuous practice embedded in every stage of development. The Universal Knowledge Ingestion feature handles complex, non-deterministic AI components alongside deterministic infrastructure. This demands a multi-layered testing strategy that validates:

1. **Correctness:** Does the system do what it should?
2. **Robustness:** Does the system handle edge cases gracefully?
3. **Performance:** Does the system meet latency and throughput targets?
4. **Security:** Is the system protected against known attack vectors?
5. **AI Quality:** Does the AI produce accurate, grounded, useful outputs?

---

## 2. Test Pyramid

```
          ┌─────────────┐
          │  E2E Tests  │  ← 5% of tests (critical user flows)
          │  (Cypress)  │
          ├─────────────┤
          │  Integration │  ← 15% of tests (API endpoints, pipelines)
          │   Tests      │
          │  (pytest)    │
          ├─────────────┤
          │   Unit Tests  │  ← 80% of tests (functions, classes, modules)
          │  (pytest +   │
          │   jest)       │
          └─────────────┘
```

**Target Coverage:**
- Unit tests: 80% line coverage (minimum), 90% for critical paths
- Integration tests: 100% of API endpoints
- E2E tests: 100% of critical user flows
- AI evaluation tests: 100% of AI components with accuracy benchmarks

---

## 3. Unit Tests

### 3.1 File Validator (Python)

```python
class TestFileValidator:
    def test_valid_pdf_passes(self):
        result = FileValidator.validate(b"%PDF-1.4...", "test.pdf")
        assert result.is_valid is True
        assert result.mime_type == "application/pdf"

    def test_invalid_magic_number_rejected(self):
        result = FileValidator.validate(b"<html>...</html>", "virus.pdf")
        assert result.is_valid is False
        assert result.error == "INVALID_MAGIC_NUMBER"

    def test_oversized_file_rejected(self):
        large_file = b"x" * (101 * 1024 * 1024)  # 101MB
        result = FileValidator.validate(large_file, "large.pdf")
        assert result.is_valid is False
        assert result.error == "FILE_TOO_LARGE"

    def test_virus_detected(self):
        eicar_test = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        result = FileValidator.validate(eicar_test, "test.pdf")
        assert result.is_valid is False
        assert result.error == "VIRUS_DETECTED"

    def test_duplicate_detection(self):
        content = b"test content"
        hash1 = DuplicateDetector.compute_hash(content)
        hash2 = DuplicateDetector.compute_hash(content)
        assert hash1 == hash2
        assert DuplicateDetector.is_duplicate(hash1, user_id="user-1") is True
```

### 3.2 Semantic Chunker (Python)

```python
class TestSemanticChunker:
    def test_heading_aware_splitting(self):
        markdown = "# Chapter 1\n\nText here.\n\n# Chapter 2\n\nMore text."
        chunks = SemanticChunker.chunk(markdown, max_tokens=500, overlap=80)
        assert len(chunks) == 2
        assert chunks[0].heading == "# Chapter 1"
        assert chunks[1].heading == "# Chapter 2"

    def test_no_table_split(self):
        markdown = "| A | B |\n|---|---|\n| 1 | 2 |"
        chunks = SemanticChunker.chunk(markdown, max_tokens=50)
        assert len(chunks) == 1  # table kept intact
        assert "| A | B |" in chunks[0].text

    def test_overlap_tokens(self):
        markdown = "Paragraph one. " * 200 + "\n\nParagraph two. " * 200
        chunks = SemanticChunker.chunk(markdown, max_tokens=300, overlap=80)
        assert len(chunks) == 2
        # Verify overlap
        chunk1_end = chunks[0].text[-100:]
        chunk2_start = chunks[1].text[:100:]
        assert len(set(chunk1_end.split()) & set(chunk2_start.split())) > 0

    def test_chunk_size_range(self):
        markdown = "Word " * 1000
        chunks = SemanticChunker.chunk(markdown, max_tokens=300, overlap=80)
        for chunk in chunks:
            tokens = len(chunk.text.split())
            assert 300 <= tokens <= 450  # allow some flexibility
```

### 3.3 Scorer (Python)

```python
class TestScorer:
    def test_compute_score_basic(self):
        score = compute_score(S=0.5, P=0.9, D=0.8, U=0.5)
        expected = round(0.35*0.5 + 0.20*0.9 + 0.35*0.8 + 0.10*0.5, 4)
        assert score == expected

    def test_p_cap(self):
        score = compute_score(S=0, P=1.0, D=0, U=0)
        assert score == round(0.20*0.9 + 0.10*0.2, 4)

    def test_u_floor(self):
        score = compute_score(S=0, P=0, D=0, U=0)
        assert score == round(0.10*0.2, 4)

    def test_classify_priority(self):
        assert classify_priority(0.75) == "High"
        assert classify_priority(0.55) == "Medium"
        assert classify_priority(0.30) == "Low"
```

### 3.4 Services (Python)

```python
class TestServices:
    def test_load_app_state_default(self):
        state = load_app_state(Path("nonexistent.json"))
        assert state["topics"] == []
        assert state["current_day"] == 1

    def test_add_topic_new(self):
        state = default_state()
        topic = add_topic(state, "Math", "Calculus", 0.8, 0.9, 0.5)
        assert len(state["topics"]) == 1
        assert topic["name"] == "Calculus"
        assert topic["D"] == 0.8

    def test_add_topic_duplicate_updates(self):
        state = default_state()
        add_topic(state, "Math", "Calculus", 0.8, 0.9, 0.5)
        add_topic(state, "Math", "calculus", 0.7, 0.8, 0.6)
        assert len(state["topics"]) == 1
        assert state["topics"][0]["D"] == 0.7

    def test_log_study_session(self):
        state = default_state()
        add_topic(state, "Math", "Calculus", 0.8, 0.9, 0.5)
        log_study_session(state, "Calculus", True, True)
        assert state["topics"][0]["mistakes"] == 1
        assert state["topics"][0]["last_studied"] == 1

    def test_state_transaction_success(self):
        with state_transaction() as state:
            state["current_day"] = 99
        saved = load_app_state()
        assert saved["current_day"] == 99

    def test_state_transaction_exception_rollback(self):
        try:
            with state_transaction() as state:
                state["current_day"] = 77
                raise ValueError("test")
        except ValueError:
            pass
        saved = load_app_state()
        assert saved["current_day"] != 77
```

### 3.5 Flask API (Python)

```python
class TestFlaskAPI:
    def test_add_topic_valid(self, client):
        response = client.post("/add-topic", json={
            "name": "Calculus", "subject": "Math", "D": 0.8, "P": 0.9, "U": 0.5
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["ok"] is True
        assert data["data"]["name"] == "Calculus"

    def test_add_topic_missing_name(self, client):
        response = client.post("/add-topic", json={"D": 0.8})
        assert response.status_code == 400
        assert response.get_json()["error"] == "Topic name required"

    def test_add_topic_invalid_numeric(self, client):
        response = client.post("/add-topic", json={
            "name": "Test", "D": "abc"
        })
        assert response.status_code == 400
        assert "valid numbers" in response.get_json()["error"]

    def test_rate_limit(self, client):
        for _ in range(35):
            response = client.get("/health")
        assert response.status_code == 429

    def test_cors_headers(self, client):
        response = client.options("/")
        assert "Access-Control-Allow-Origin" in response.headers
```

### 3.6 Frontend Utils (JavaScript)

```javascript
// tests/unit/app.test.js
import { clearChildren, makeEl, setStatus } from '../app.js';

describe('clearChildren', () => {
  test('removes all children', () => {
    const parent = document.createElement('div');
    parent.appendChild(document.createElement('span'));
    parent.appendChild(document.createElement('p'));
    clearChildren(parent);
    expect(parent.childNodes.length).toBe(0);
  });
});

describe('makeEl', () => {
  test('creates element with text', () => {
    const el = makeEl('div', 'test-class', 'hello');
    expect(el.tagName).toBe('DIV');
    expect(el.className).toBe('test-class');
    expect(el.textContent).toBe('hello');
  });

  test('does not use innerHTML', () => {
    const el = makeEl('div', '', '<script>alert(1)</script>');
    expect(el.textContent).toBe('<script>alert(1)</script>');
    expect(el.innerHTML).not.toContain('<script>');
  });
});
```

---

## 4. Integration Tests

### 4.1 Upload → Processing Pipeline

```python
def test_upload_and_process_pdf():
    """E2E test: upload PDF → validate → store in R2 → trigger processing → verify status"""
    # 1. Upload PDF
    with open("test_data/sample_textbook.pdf", "rb") as f:
        response = client.post("/upload", data={"files": (f, "textbook.pdf")})
    assert response.status_code == 202
    upload_id = response.get_json()["upload_id"]

    # 2. Poll status
    for _ in range(60):  # wait up to 5 minutes
        status = client.get(f"/documents/{upload_id}/status")
        if status.get_json()["data"]["status"] == "ready":
            break
        time.sleep(5)
    assert status.get_json()["data"]["status"] == "ready"

    # 3. Verify chunks exist
    chunks = client.get(f"/documents/{upload_id}/chunks")
    assert chunks.get_json()["ok"] is True
    assert len(chunks.get_json()["data"]) > 0

    # 4. Verify embeddings exist
    chunk = chunks.get_json()["data"][0]
    assert chunk["embedding"] is not None
    assert len(chunk["embedding"]) == 1024
```

### 4.2 Retrieval Pipeline

```python
def test_hybrid_retrieval():
    """Test full hybrid retrieval: dense + sparse + re-rank + fusion"""
    # Seed test data
    test_chunks = [
        {"text": "The ideal gas law is PV = nRT", "embedding": [...], "heading": "Gas Laws"},
        {"text": "Newton's second law: F = ma", "embedding": [...], "heading": "Mechanics"},
    ]
    # Insert into pgvector
    # ...

    # Query
    response = client.post("/retrieve", json={"query": "ideal gas law"})
    data = response.get_json()
    assert data["ok"] is True
    assert len(data["data"]["results"]) > 0

    # Verify top result is about gas laws
    top = data["data"]["results"][0]
    assert "PV = nRT" in top["text"]
    assert top["score"] > 0.5

    # Verify latency
    assert data["data"]["search_time_ms"] < 200
```

### 4.3 AI Grounding

```python
def test_ai_answer_grounded():
    """Test that AI answers cite only existing chunks"""
    # Upload test document
    # ...

    # Ask question
    response = client.post("/ask", json={
        "question": "What is the ideal gas law?",
        "context": {"restrict_documents": [doc_id]}
    })
    data = response.get_json()
    assert data["ok"] is True

    # Verify citations exist
    for citation in data["data"]["citations"]:
        chunk = db.query(f"SELECT * FROM chunks WHERE id = '{citation['chunk_id']}'")
        assert chunk is not None
        assert citation["confidence"] > 0.5

    # Verify no hallucination
    answer = data["data"]["answer"]
    # Check that answer content is in retrieved chunks
    chunks_text = " ".join([c["text"] for c in data["data"]["citations"]])
    # Semantic check: answer should be derived from chunks
    assert len(answer) > 0
```

### 4.4 RLS Isolation

```python
def test_rls_user_isolation():
    """Verify User A cannot see User B's documents"""
    # Create two users
    user_a_token = create_user("user_a@example.com")
    user_b_token = create_user("user_b@example.com")

    # User A uploads document
    client_a = authenticated_client(user_a_token)
    client_a.post("/upload", data={"files": open("test.pdf", "rb")})

    # User B tries to access User A's document
    client_b = authenticated_client(user_b_token)
    response = client_b.get("/documents")
    docs = response.get_json()["data"]
    assert len(docs) == 0  # No cross-tenant leakage
```

---

## 5. End-to-End Tests

### 5.1 Critical User Flows (Cypress)

```javascript
// tests/e2e/upload-and-ask.cy.js
describe('Upload and Ask Flow', () => {
  it('uploads a PDF and asks a grounded question', () => {
    // Login
    cy.visit('/login');
    cy.get('[data-testid=email]').type('test@example.com');
    cy.get('[data-testid=password]').type('password123');
    cy.get('[data-testid=login-btn]').click();

    // Upload PDF
    cy.visit('/upload');
    cy.get('[data-testid=dropzone]').attachFile('sample_textbook.pdf');
    cy.get('[data-testid=upload-btn]').click();
    cy.get('[data-testid=status]').should('contain', 'Processing');
    cy.get('[data-testid=status]', { timeout: 300000 }).should('contain', 'Ready');

    // Ask question
    cy.visit('/ask');
    cy.get('[data-testid=question-input]').type('What is the ideal gas law?');
    cy.get('[data-testid=ask-btn]').click();

    // Verify answer
    cy.get('[data-testid=answer]', { timeout: 10000 }).should('be.visible');
    cy.get('[data-testid=citation]').should('have.length.at.least', 1);
    cy.get('[data-testid=citation]').first().click();
    cy.get('[data-testid=source-preview]').should('contain', 'PV = nRT');
  });
});

// tests/e2e/exam-auto-setup.cy.js
describe('Exam Auto-Setup Flow', () => {
  it('sets up JEE 2026 automatically', () => {
    cy.visit('/setup');
    cy.get('[data-testid=exam-name]').type('JEE');
    cy.get('[data-testid=board]').select('CBSE');
    cy.get('[data-testid=year]').type('2026');
    cy.get('[data-testid=subject-physics]').check();
    cy.get('[data-testid=subject-chemistry]').check();
    cy.get('[data-testid=subject-mathematics]').check();
    cy.get('[data-testid=submit-btn]').click();

    // Verify found resources
    cy.get('[data-testid=resource]', { timeout: 60000 }).should('have.length.at.least', 3);
    cy.get('[data-testid=resource-confidence]').first().should('contain', 'Official');

    // Approve resources
    cy.get('[data-testid=approve-all]').click();
    cy.get('[data-testid=processing-status]').should('contain', 'Processing');
    cy.get('[data-testid=processing-status]', { timeout: 300000 }).should('contain', 'Complete');
  });
});
```

---

## 6. Performance Tests

### 6.1 Document Processing Latency

```python
def test_processing_latency_100_pages():
    """Benchmark: process 100-page PDF in < 5 minutes"""
    start = time.time()
    response = client.post("/upload", data={"files": open("100_pages.pdf", "rb")})
    upload_id = response.get_json()["upload_id"]

    # Poll until ready
    for _ in range(60):
        status = client.get(f"/documents/{upload_id}/status")
        if status.get_json()["data"]["status"] == "ready":
            break
        time.sleep(5)

    elapsed = time.time() - start
    assert elapsed < 300, f"Processing took {elapsed}s, expected < 300s"
```

### 6.2 Vector Search Latency

```python
def test_vector_search_latency():
    """Benchmark: 1000 queries, p95 < 200ms"""
    queries = ["thermodynamics", "integration", "organic chemistry", ...]  # 1000 queries
    latencies = []
    for q in queries:
        start = time.perf_counter()
        client.post("/retrieve", json={"query": q})
        latencies.append((time.perf_counter() - start) * 1000)

    p95 = np.percentile(latencies, 95)
    assert p95 < 200, f"p95 latency: {p95}ms"
```

### 6.3 Concurrent Uploads

```python
def test_concurrent_uploads():
    """Stress test: 50 concurrent uploads"""
    import concurrent.futures

    def upload():
        with open("test.pdf", "rb") as f:
            return client.post("/upload", data={"files": f})

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(upload) for _ in range(50)]
        results = [f.result() for f in futures]

    success_count = sum(1 for r in results if r.status_code == 202)
    assert success_count >= 45, f"Only {success_count}/50 uploads succeeded"
```

---

## 7. Load Tests

### 7.1 API Load Test (k6)

```javascript
// tests/load/search-load.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 200 },   // Ramp up to 200 users
    { duration: '5m', target: 200 },   // Stay at 200 users
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],     // Error rate < 1%
  },
};

export default function () {
  const payload = JSON.stringify({ query: 'ideal gas law' });
  const headers = { 'Content-Type': 'application/json' };

  const res = http.post('https://api.adaptive-study-planner.com/retrieve', payload, { headers });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
    'has results': (r) => JSON.parse(r.body).data.results.length > 0,
  });

  sleep(1);
}
```

### 7.2 Upload Load Test (k6)

```javascript
// tests/load/upload-load.js
import http from 'k6/http';
import { check } from 'k6';
import { FormData } from 'https://jslib.k6.io/formdata/0.0.2/index.js';

export const options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '5m', target: 10 },
    { duration: '1m', target: 0 },
  ],
};

export default function () {
  const fd = new FormData();
  fd.append('files', http.file(open('test.pdf', 'b'), 'test.pdf'));

  const res = http.post('https://api.adaptive-study-planner.com/upload', {
    headers: { 'Content-Type': 'multipart/form-data; boundary=' + fd.boundary },
    body: fd.body,
  });

  check(res, {
    'status is 202': (r) => r.status === 202,
    'has upload_id': (r) => JSON.parse(r.body).upload_id !== undefined,
  });
}
```

---

## 8. Security Tests

### 8.1 XSS Prevention

```javascript
// tests/security/xss.test.js
describe('XSS Prevention', () => {
  it('rejects HTML injection in topic names', () => {
    const payload = {
      name: '<script>alert("xss")</script>',
      subject: 'Math',
      D: 0.5, P: 0.5, U: 0.5
    };
    const response = client.post('/add-topic', json=payload);
    const data = response.get_json();
    // Topic name should be stored as plain text, not executed
    assert '<script>' not in data['data']['name']
    assert data['data']['name'] == '<script>alert("xss")</script>'  // stored as text
  });

  it('does not render innerHTML with user data', () => {
    // Upload document with malicious filename
    // Verify frontend uses textContent, not innerHTML
  });
});
```

### 8.2 SQL Injection Prevention

```python
def test_sql_injection_in_search():
    """Verify SQL injection attempts are sanitized"""
    malicious_queries = [
        "'; DROP TABLE chunks; --",
        "1' OR '1'='1",
        "test' UNION SELECT * FROM users --",
    ]
    for query in malicious_queries:
        response = client.post("/retrieve", json={"query": query})
        # Should return 200 with empty results or error, not crash
        assert response.status_code in [200, 400]
        # Verify database is intact
        chunks = db.execute("SELECT COUNT(*) FROM chunks")
        assert chunks[0][0] > 0
```

### 8.3 RLS Bypass Attempts

```python
def test_rls_bypass_attempts():
    """Verify RLS cannot be bypassed"""
    # Create user A and user B
    user_a = create_user("a@example.com")
    user_b = create_user("b@example.com")

    # User A uploads document
    client_a = authenticated_client(user_a)
    client_a.post("/upload", data={"files": open("test.pdf", "rb")})

    # Attempts to bypass RLS:
    # 1. Direct SQL injection to change user_id
    # 2. Query with different user_id in payload
    # 3. Try to access via knowledge graph traversal
    # All should fail

    # Attempt 1: SQL injection in query filter
    response = client_a.post("/retrieve", json={
        "query": "test",
        "filters": {"user_id": "' OR '1'='1"}  # injection attempt
    })
    assert response.status_code == 400  # or 200 with no extra results
```

### 8.4 Rate Limiting

```python
def test_rate_limit_enforcement():
    """Verify rate limits are enforced"""
    # Send 110 requests in 1 minute
    for i in range(110):
        response = client.get("/health")
        if i < 100:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
            assert "Rate limit" in response.get_json()["error"]
```

---

## 9. AI Evaluation Tests

### 9.1 Retrieval Quality (MRR@10, Precision@5, Recall@10)

```python
def test_retrieval_quality():
    """Evaluate retrieval quality on benchmark dataset"""
    # Load test dataset (query + relevant chunks)
    test_queries = load_json("test_data/retrieval_benchmark.json")

    metrics = {"mrr": [], "precision@5": [], "recall@10": []}
    for item in test_queries:
        query = item["query"]
        relevant = set(item["relevant_chunk_ids"])

        response = client.post("/retrieve", json={"query": query, "k": 10})
        results = response.get_json()["data"]["results"]
        retrieved = [r["chunk_id"] for r in results]

        # MRR@10
        rr = 0
        for i, rid in enumerate(retrieved[:10]):
            if rid in relevant:
                rr = 1 / (i + 1)
                break
        metrics["mrr"].append(rr)

        # Precision@5
        p5 = len(set(retrieved[:5]) & relevant) / 5
        metrics["precision@5"].append(p5)

        # Recall@10
        r10 = len(set(retrieved[:10]) & relevant) / len(relevant)
        metrics["recall@10"].append(r10)

    assert np.mean(metrics["mrr"]) > 0.6
    assert np.mean(metrics["precision@5"]) > 0.7
    assert np.mean(metrics["recall@10"]) > 0.5
```

### 9.2 OCR Accuracy

```python
def test_ocr_accuracy():
    """Evaluate OCR accuracy on benchmark dataset"""
    test_docs = load_json("test_data/ocr_benchmark.json")

    for doc in test_docs:
        image = load_image(doc["image_path"])
        ground_truth = doc["text"]

        ocr_result = OCRPipeline.process(image, doc_type=doc["type"])

        if doc["type"] == "printed":
            wer = word_error_rate(ocr_result, ground_truth)
            assert wer < 0.15, f"WER: {wer}"
        elif doc["type"] == "handwritten":
            wer = word_error_rate(ocr_result, ground_truth)
            assert wer < 0.30, f"WER: {wer}"
```

### 9.3 AI Grounding (No Hallucination)

```python
def test_ai_no_hallucination():
    """Verify AI never hallucinates on test set"""
    test_questions = load_json("test_data/grounding_benchmark.json")

    hallucination_count = 0
    for item in test_questions:
        response = client.post("/ask", json={
            "question": item["question"],
            "context": {"restrict_documents": item["document_ids"]}
        })
        answer = response.get_json()["data"]["answer"]
        citations = response.get_json()["data"]["citations"]

        # Check if any claim in answer is not supported by citations
        for claim in extract_claims(answer):
            if not is_supported_by(claim, citations):
                hallucination_count += 1

    assert hallucination_count == 0, f"{hallucination_count} hallucinations found"
```

### 9.4 Concept Extraction Accuracy

```python
def test_concept_extraction_accuracy():
    """Evaluate concept extraction on benchmark dataset"""
    test_docs = load_json("test_data/concept_extraction_benchmark.json")

    for doc in test_docs:
        extracted = KnowledgeExtractor.extract_concepts(doc["text"])
        ground_truth = set(doc["concepts"])
        extracted_set = set(extracted)

        precision = len(extracted_set & ground_truth) / len(extracted_set)
        recall = len(extracted_set & ground_truth) / len(ground_truth)
        f1 = 2 * precision * recall / (precision + recall)

        assert f1 > 0.70, f"F1: {f1}"
```

---

## 10. Upload Validation Tests

### 10.1 File Format Validation

```python
def test_all_supported_formats():
    """Test upload for all supported formats"""
    formats = {
        "pdf": (b"%PDF-1.4\n...", "test.pdf"),
        "docx": (b"PK\x03\x04...", "test.docx"),
        "txt": (b"Hello world", "test.txt"),
        "epub": (b"PK\x03\x04...", "test.epub"),
        "jpg": (b"\xff\xd8\xff...", "test.jpg"),
        "png": (b"\x89PNG\r\n\x1a\n...", "test.png"),
        "zip": (b"PK\x03\x04...", "test.zip"),
    }

    for fmt, (content, filename) in formats.items():
        response = client.post("/upload", data={"files": (content, filename)})
        assert response.status_code == 202, f"Failed for {fmt}"
```

### 10.2 Edge Cases

```python
def test_edge_cases():
    """Test edge cases for upload"""
    edge_cases = [
        ("", "empty.pdf"),                           # Empty file
        (b"x" * 101 * 1024 * 1024, "large.pdf"),      # 101MB file
        (b"%PDF-1.4\n...", "virus.exe"),              # Wrong extension
        (b"<html>not a pdf</html>", "fake.pdf"),       # Fake PDF
        (b"\x00" * 1000, "nulls.pdf"),                # Null bytes
        (b"%PDF-1.4\n" + b"x" * 1024, "corrupt.pdf"), # Corrupt PDF
    ]

    for content, filename in edge_cases:
        response = client.post("/upload", data={"files": (content, filename)})
        assert response.status_code in [400, 413, 202], f"Unexpected status for {filename}"
```

---

## 11. Regression Tests

### 11.1 Scoring Formula Regression

```python
def test_scoring_formula_regression():
    """Ensure scoring formula never changes unexpectedly"""
    # Known inputs with expected outputs
    test_cases = [
        ((0.5, 0.9, 0.8, 0.5), 0.6650),
        ((0.0, 1.0, 0.0, 0.0), 0.2200),
        ((1.0, 0.9, 1.0, 1.0), 0.9550),
    ]

    for (S, P, D, U), expected in test_cases:
        actual = compute_score(S, P, D, U)
        assert abs(actual - expected) < 0.0001, f"Expected {expected}, got {actual}"
```

### 11.2 Plan Generation Regression

```python
def test_plan_generation_regression():
    """Ensure plan generation logic remains consistent"""
    state = load_state("test_data/regression_state.json")
    plan = get_plan(state)

    # Compare to known good output
    expected_plan = load_json("test_data/expected_plan.json")
    assert len(plan["plan"]) == len(expected_plan["plan"])
    for i, (actual, expected) in enumerate(zip(plan["plan"], expected_plan["plan"])):
        assert actual["topic"]["name"] == expected["topic"]["name"]
        assert actual["estimated_minutes"] == expected["estimated_minutes"]
```

---

## 12. Test Data Strategy

### 12.1 Test Data Sources

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| OCR Benchmark | Internal collection (50 docs) | 50 docs | OCR accuracy testing |
| Retrieval Benchmark | Internal + synthetic | 500 queries | Retrieval quality |
| Grounding Benchmark | Internal + synthetic | 200 Q&A pairs | AI hallucination testing |
| Concept Extraction | Internal + LLM-generated | 100 docs | Knowledge extraction |
| Security Test Cases | OWASP + internal | 50 cases | Security testing |
| Load Test Data | Synthetic | 10,000 queries | Load testing |
| Regression State | Production snapshot (anonymized) | 1 state | Regression testing |

### 12.2 Data Generation

- **Synthetic documents:** Generate PDFs with known text using Python libraries (reportlab, fpdf2)
- **Synthetic queries:** Use LLM to generate questions from known document content
- **Synthetic embeddings:** Generate random vectors with known similarity patterns
- **Anonymized production data:** Strip PII, shuffle identifiers, use for regression

### 12.3 Data Storage

- Test data stored in `tests/data/` directory (git-lfs for large files)
- Benchmark datasets versioned separately (semantic versioning)
- Production data anonymization pipeline: strip PII → shuffle IDs → add noise

---

## 13. Automation Strategy

### 13.1 CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt
      - run: pip install -r requirements-test.txt
      - run: pytest tests/unit/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v4

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env: { POSTGRES_PASSWORD: postgres }
      redis:
        image: redis:7-alpine
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/integration/ -v

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: cypress-io/github-action@v6
        with:
          start: python scoring_test/flask_app.py
          wait-on: http://localhost:5000/health

  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install bandit safety
      - run: bandit -r src/ -f json -o bandit-report.json
      - run: safety check -r requirements.txt

  ai-evaluation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest tests/ai/ -v --tb=short
```

### 13.2 Test Schedule

| Test Type | Trigger | Frequency | Environment |
|-----------|---------|-----------|-------------|
| Unit tests | Every push | Continuous | Local / CI |
| Integration tests | Every PR | Continuous | CI (Docker) |
| E2E tests | Every PR | Continuous | CI (Staging) |
| Security tests | Every PR | Continuous | CI |
| AI evaluation | Every PR | Continuous | CI (with Ollama) |
| Performance tests | Nightly | Daily | Staging |
| Load tests | Weekly | Weekly | Staging |
| Regression tests | Before release | Per release | Staging |

---

## 14. Exit Criteria

### 14.1 Release Readiness Checklist

- [ ] Unit test coverage ≥ 80% (measured by codecov)
- [ ] Integration tests: 100% API endpoints pass
- [ ] E2E tests: 100% critical user flows pass
- [ ] Security tests: 0 critical vulnerabilities, 0 high vulnerabilities
- [ ] AI evaluation: MRR@10 > 0.6, Precision@5 > 0.7, Recall@10 > 0.5
- [ ] OCR accuracy: Printed > 85%, Handwritten > 70%
- [ ] Performance: p95 latency < 500ms for all APIs
- [ ] Load tests: 200 concurrent users, < 1% error rate
- [ ] Accessibility: WCAG 2.1 AA compliance (axe-core audit)
- [ ] Documentation: API docs updated, runbooks updated, ADRs updated
- [ ] Monitoring: dashboards configured, alerts tested
- [ ] Rollback plan: database migrations reversible, feature flags ready

### 14.2 Go / No-Go Decision

| Criteria | Threshold | Actual | Status |
|----------|-----------|--------|--------|
| Unit test coverage | ≥ 80% | TBD | Pending |
| Integration test pass rate | 100% | TBD | Pending |
| E2E test pass rate | 100% | TBD | Pending |
| Security vulnerabilities (critical/high) | 0 | TBD | Pending |
| MRR@10 | > 0.6 | TBD | Pending |
| Precision@5 | > 0.7 | TBD | Pending |
| OCR printed accuracy | > 85% | TBD | Pending |
| OCR handwritten accuracy | > 70% | TBD | Pending |
| API p95 latency | < 500ms | TBD | Pending |
| Load test error rate | < 1% | TBD | Pending |

**Go / No-Go Meeting:** Scheduled 2 days before release. All stakeholders (Engineering, QA, Product, Security) must sign off.

---

*End of Test Specification*
