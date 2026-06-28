-- 001_full_schema.sql — Complete Phase 4 Enterprise database schema

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- documents table (expanded)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    filename TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    r2_path TEXT,
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

CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_sha256 ON documents(sha256_hash);
CREATE INDEX IF NOT EXISTS idx_documents_subject ON documents(subject);
CREATE INDEX IF NOT EXISTS idx_documents_source_confidence ON documents(source_confidence);

-- chunks table (with pgvector)
CREATE TABLE IF NOT EXISTS chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
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

CREATE INDEX IF NOT EXISTS idx_chunks_user_id ON chunks(user_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_chunks_text_search ON chunks USING GIN (to_tsvector('english', text));
CREATE INDEX IF NOT EXISTS idx_chunks_heading ON chunks(heading);

-- concepts table
CREATE TABLE IF NOT EXISTS concepts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    definition TEXT,
    subject TEXT,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES chunks(id) ON DELETE CASCADE,
    confidence REAL DEFAULT 0.5,
    source_type TEXT DEFAULT 'extracted',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_concepts_user_id ON concepts(user_id);
CREATE INDEX IF NOT EXISTS idx_concepts_name ON concepts(name);
CREATE INDEX IF NOT EXISTS idx_concepts_document_id ON concepts(document_id);

-- formulas table
CREATE TABLE IF NOT EXISTS formulas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    latex TEXT NOT NULL,
    context TEXT,
    subject TEXT,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES chunks(id) ON DELETE CASCADE,
    confidence REAL DEFAULT 0.5,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_formulas_user_id ON formulas(user_id);
CREATE INDEX IF NOT EXISTS idx_formulas_latex ON formulas(latex);

-- questions table
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    question_type TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    options TEXT[],
    difficulty REAL DEFAULT 0.5,
    subject TEXT,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES chunks(id) ON DELETE CASCADE,
    confidence REAL DEFAULT 0.5,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_questions_user_id ON questions(user_id);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);

-- knowledge_edges table (graph)
CREATE TABLE IF NOT EXISTS knowledge_edges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,
    relationship TEXT NOT NULL CHECK (relationship IN ('prerequisite', 'related', 'part-of', 'covers', 'example-of')),
    confidence REAL NOT NULL DEFAULT 0.5,
    source_document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, source_node, target_node, relationship)
);

CREATE INDEX IF NOT EXISTS idx_knowledge_edges_user_id ON knowledge_edges(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_source ON knowledge_edges(source_node);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_target ON knowledge_edges(target_node);
CREATE INDEX IF NOT EXISTS idx_knowledge_edges_relationship ON knowledge_edges(relationship);

-- ocr_results table
CREATE TABLE IF NOT EXISTS ocr_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    text TEXT,
    confidence REAL DEFAULT 0,
    engine TEXT DEFAULT 'tesseract',
    needs_review BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ocr_results_document_id ON ocr_results(document_id);
CREATE INDEX IF NOT EXISTS idx_ocr_results_confidence ON ocr_results(confidence);

-- ai_queries table (grounding audit)
CREATE TABLE IF NOT EXISTS ai_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    query TEXT NOT NULL,
    response TEXT,
    citations JSONB DEFAULT '[]',
    grounding_score REAL DEFAULT 0,
    retrieval_time_ms INTEGER,
    generation_time_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ai_queries_user_id ON ai_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_queries_created_at ON ai_queries(created_at);

-- study_groups table
CREATE TABLE IF NOT EXISTS study_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    created_by UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- group_members table
CREATE TABLE IF NOT EXISTS group_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id UUID REFERENCES study_groups(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('admin', 'moderator', 'member')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- shared_topics table
CREATE TABLE IF NOT EXISTS shared_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_name TEXT NOT NULL,
    shared_by UUID NOT NULL,
    group_id UUID REFERENCES study_groups(id) ON DELETE CASCADE,
    permission TEXT NOT NULL DEFAULT 'read' CHECK (permission IN ('read', 'write')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
