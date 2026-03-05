# Obsidian Ecosystem Hub — Vector Search Patterns

Exploration of pgvector infrastructure in `obsidian-ecosystem-hub` for potential reuse in the memory system's hybrid search.

## Infrastructure Overview

| Component | Details |
|-----------|---------|
| Database | PostgreSQL 16 with pgvector 0.8.1 |
| Hosting | Hostinger VPS (`148.230.95.154`), Docker container `postgres-vector` on port 5432 |
| Embedding model | OpenAI `text-embedding-3-small` (1536 dimensions) |
| Databases | `obsidian_agent`, `obsidian_brain`, `langfuse`, `flowise`, `property_monitor` |
| Services using it | obsidian-brain (GraphRAG), backend_rag_pipeline (indexer) |
| SSH access | `ssh obsidian-vps` (configured in `~/.ssh/config`) |

---

## Part 1: obsidian-brain Vector Patterns

Source: `/home/mdc159/projects/obsidian-ecosystem-hub/stack/obsidian-brain/`

### Database Setup

**File**: `app/core/database.py`

Async SQLAlchemy with pgvector extension loading:

```python
_engine = create_async_engine(
    settings.database.database_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

# pgvector extension loaded on connect:
await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
```

Session factory: `sessionmaker` with `AsyncSession`, `expire_on_commit=False`.

Connection string format (Supabase):
```
postgresql+asyncpg://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

### Embedding Generation

**File**: `app/core/embeddings.py`

Three embedding functions with increasing sophistication:

```python
# Single text
async def embed_text(text: str) -> list[float]:
    response = await client.embeddings.create(
        model=settings.openai.embedding_model,
        input=text,
    )
    return response.data[0].embedding

# Batch (single API call)
async def embed_texts(texts: list[str]) -> list[list[float]]:
    response = await client.embeddings.create(
        model=settings.openai.embedding_model,
        input=texts,
    )
    sorted_data = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in sorted_data]

# Batched with rate limiting (for large volumes)
async def embed_texts_batched(
    texts: list[str],
    batch_size: int = 100,
    delay_between_batches: float = 0.1,
) -> list[list[float]]:
    # Processes in chunks of batch_size with delays between
```

Retry logic via `tenacity`: 3 attempts, exponential backoff (2-10s wait).

### Vector Similarity Search

**File**: `app/core/database.py` (lines 104-139)

Calls a server-side PostgreSQL function:

```python
async def match_documents(
    query_embedding: list[float],
    match_count: int = 5,
    filter_metadata: dict | None = None,
) -> list[dict]:
    query = """
    SELECT * FROM match_documents(
        :query_embedding::vector(1536),
        :match_count,
        :filter_metadata::jsonb
    )
    """
    result = await session.execute(
        text(query),
        {
            "query_embedding": str(query_embedding),
            "match_count": match_count,
            "filter_metadata": str(filter_json).replace("'", '"'),
        },
    )
    return [dict(row._mapping) for row in result.fetchall()]
```

### Hybrid Search (GraphRAG)

**File**: `app/services/graph_rag.py` (lines 70-111)

Combines graph traversal + vector search:
- Graph results get base score of 0.8
- Vector results get cosine similarity score
- Results appearing in both searches get boosted
- Final ranking: sorted by combined score

```python
query_embedding = await embed_text(query)
vector_results = await match_documents(query_embedding, top_k)

for doc in vector_results:
    result["vector_notes"].append({
        "path": doc["metadata"].get("file_path", "unknown"),
        "title": doc["metadata"].get("file_title", "Unknown"),
        "similarity": doc["similarity"],
        "content_preview": doc["content"][:200] + "...",
    })
```

### Dependencies

```toml
"sqlalchemy[asyncio]>=2.0.0"
"asyncpg>=0.30.0"
"pgvector>=0.3.0"
"openai>=1.58.0"
"tenacity>=9.0.0"
```

---

## Part 2: RAG Pipeline Patterns

Source: `/home/mdc159/projects/obsidian-ecosystem-hub/stack/obsidian-ai-agent/backend_rag_pipeline/`

### File Watching -> Embedding Flow

**Timestamp-based change detection** with database state persistence:
- Polls filesystem every 60 seconds via `os.walk()` + `stat`
- Tracks `known_files` as JSONB `{file_path: modified_timestamp}` in `rag_pipeline_state` table
- Compares current filesystem scan against known_files to detect changes
- Excludes folders: `.obsidian`, `Templates`, `Workflows` (configurable)
- Supports both local filesystem and S3/MinIO modes

### Chunking Strategy

**File**: `backend_rag_pipeline/common/text_processor.py`

Character-based sliding window:

```python
def chunk_text(text: str, chunk_size: int = 400, overlap: int = 0) -> List[str]:
    # Clean text: replace \r with empty string
    # Iterate: range(0, len(text), chunk_size - overlap)
    # Extract: text[i : i + chunk_size]
    # Skip empty chunks
```

Configuration (`config.json`):
```json
"text_processing": {
    "default_chunk_size": 400,
    "default_chunk_overlap": 0
}
```

- 400 chars = ~100 tokens (at ~4 chars/token)
- No heading-aware or sentence-boundary detection
- Markdown hashtag extraction: `r"(?<!#)#([a-zA-Z0-9][\w-]*)"`

### Embedding Storage Schema

**File**: `alembic/versions/2ee8b9d62dd1_add_rag_tables.py`

Four tables:

#### `documents` — Primary vector storage
```sql
CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    content TEXT,                    -- Chunk text
    metadata JSONB,                  -- file_id, file_url, file_title, chunk_index, tags
    embedding vector(1536)           -- pgvector (OpenAI text-embedding-3-small)
);
```

Metadata JSONB structure:
```json
{
    "file_id": "file_path or S3 key",
    "file_url": "file://... or s3://...",
    "file_title": "filename.md",
    "mime_type": "text/markdown",
    "chunk_index": 0,
    "tags": ["tag1", "tag2"]
}
```

#### `document_metadata` — Per-file metadata
```sql
CREATE TABLE document_metadata (
    id TEXT PRIMARY KEY,             -- file_id (file path)
    title TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    schema TEXT,                     -- CSV column names
    tags JSONB DEFAULT '[]'::jsonb
);

CREATE INDEX idx_document_metadata_tags ON document_metadata USING GIN (tags);
```

#### `rag_pipeline_state` — Cross-restart persistence
```sql
CREATE TABLE rag_pipeline_state (
    pipeline_id TEXT PRIMARY KEY,
    pipeline_type TEXT NOT NULL,
    last_check_time TIMESTAMP,
    known_files JSONB,               -- {file_path: modified_timestamp}
    last_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Vector Search Function (PostgreSQL RPC)

```sql
CREATE OR REPLACE FUNCTION match_documents (
    query_embedding vector(1536),
    match_count int DEFAULT NULL,
    filter jsonb DEFAULT '{}'
) RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        id, content, metadata,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE metadata @> filter
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

- `<=>` is pgvector's **cosine distance** operator (0 = identical, 2 = opposite)
- Similarity = `1 - distance` → range [0, 1]
- JSONB `@>` operator for tag-based filtering with GIN index
- **RLS enabled** on all tables — requires service role key

### Batch Embedding

**File**: `backend_rag_pipeline/common/text_processor.py` (lines 120-140)

```python
def create_embeddings(texts: List[str]) -> List[List[float]]:
    response = openai_client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL_CHOICE"),
        input=texts  # Single API call for all chunks in a file
    )
    return [item.embedding for item in response.data]
```

- Single API call per file (all chunks at once)
- No rate limiting, retries, or caching in the pipeline (unlike obsidian-brain)
- Per-file processing: chunk -> embed -> insert in one transaction

### Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/db
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_API_KEY=sk-...
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
RAG_PIPELINE_ID=memory-files-pipeline
```

---

## Performance Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| File scan (100 files) | ~500ms | os.walk + stat calls |
| Chunking (10KB text) | ~5ms | String slicing |
| Embedding (25 chunks) | ~300-500ms | OpenAI API latency |
| DB insert (25 chunks) | ~50-100ms | Single transaction |
| Vector search | ~50-200ms | Without HNSW index |
| Total per-file processing | ~1-2s | Dominated by API call |

---

## Patterns to Reuse for Memory Hybrid Search

### What to adopt

1. **`match_documents()` PostgreSQL RPC function** — Already exists on Supabase, use the same pattern
2. **Raw SQL with `sqlalchemy.text()`** — No ORM models needed, keeps it simple
3. **OpenAI `text-embedding-3-small`** — Same model, consistent 1536-dim vectors
4. **JSONB metadata** — Store `file_path`, `chunk_index`, `source` (global/project)
5. **Cosine distance `<=>` operator** — Standard pgvector similarity metric

### What to adapt

1. **Separate table** — Use `memory_embeddings` instead of `documents` to avoid polluting obsidian data
2. **Chunk size** — Memory files are small; consider 800 chars for more context per chunk
3. **Content-hash caching** — Skip re-embedding unchanged files (memory files change rarely)
4. **Sync approach** — UV single-file script (not a Docker service) that indexes on search
5. **Hybrid weighting** — 0.7 vector / 0.3 keyword per OpenClaw's recommended ratio

### What NOT to adopt

1. **File watching service** — Overkill for memory dirs; reindex on demand
2. **PydanticAI tool interface** — We need a CLI script, not an agent tool
3. **Alembic migrations** — Direct `CREATE TABLE IF NOT EXISTS` for a single table
4. **S3/MinIO support** — Memory files are always local

### Connection Details

```
Host: 148.230.95.154 (Hostinger VPS, ssh alias: obsidian-vps)
Port: 5432 (direct, requires SSH tunnel from WSL)
Driver: postgresql:// (psycopg) or postgresql+asyncpg:// (asyncpg)
Auth: postgres / obsidian-brain-2024 (from /root/stack/.env on VPS)
Extension: pgvector 0.8.1 installed in obsidian_agent and obsidian_brain databases
```

**SSH tunnel for local access:**
```bash
ssh -f -N -L 15432:localhost:5432 obsidian-vps
DATABASE_URL="postgresql://postgres:obsidian-brain-2024@localhost:15432/obsidian_brain"
```

Note: The Supabase cloud instance (`wilpayvbjaimkrskwowb.supabase.co`) is for the **Karaoke project**, not the obsidian/memory system. The `OPENAI_API_KEY` is available in the WSL environment.
