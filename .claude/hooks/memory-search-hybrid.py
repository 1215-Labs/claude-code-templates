#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai>=1.58.0",
#     "psycopg[binary]>=3.2.0",
#     "pgvector>=0.3.0",
# ]
# ///
"""
Hybrid memory search: combines FTS5 keyword search with pgvector semantic search.

Bridges the last OpenClaw gap — vector search (semantic similarity via embeddings)
merged with existing BM25 keyword search at 0.7 vector / 0.3 keyword weighting.

Requires:
    DATABASE_URL  - PostgreSQL connection string with pgvector
                    (e.g. postgresql://postgres.xxx:pass@host:6543/postgres)
    OPENAI_API_KEY - For text-embedding-3-small embeddings

Usage:
    uv run memory-search-hybrid.py "query string"
    uv run memory-search-hybrid.py --index              # index memory files
    uv run memory-search-hybrid.py --keyword-only "q"   # FTS5 only (no DB needed)
    uv run memory-search-hybrid.py --vector-only "q"    # pgvector only
    uv run memory-search-hybrid.py --status              # show index stats
"""

import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MEMORY_DIRS = [
    ("global", Path.home() / ".claude" / "memory"),
    ("project", Path(".claude") / "memory"),
]

FTS_DB_PATH = Path(".claude") / "memory" / ".memory-search.db"

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMS = 1536
TABLE_NAME = "memory_embeddings"

# Hybrid weighting (OpenClaw recommendation)
VECTOR_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3

MAX_RESULTS = 8
CHUNK_SIZE = 800  # chars (~200 tokens) — larger than RAG pipeline's 400 for more context
CHUNK_OVERLAP = 100

# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------


def get_embedding(text: str) -> list[float]:
    """Generate embedding via OpenAI API."""
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts in a single API call."""
    if not texts:
        return []

    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    sorted_data = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in sorted_data]


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Character-based sliding window chunking."""
    text = text.replace("\r", "")
    if not text.strip():
        return []

    chunks = []
    step = max(1, chunk_size - overlap)
    for i in range(0, len(text), step):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def content_hash(text: str) -> str:
    """SHA-256 hash for change detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Database — pgvector
# ---------------------------------------------------------------------------


def get_pg_conn():
    """Connect to PostgreSQL with pgvector."""
    import psycopg
    from pgvector.psycopg import register_vector

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return None

    # psycopg uses postgresql:// not postgresql+asyncpg://
    db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    conn = psycopg.connect(db_url)
    conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    register_vector(conn)
    return conn


def ensure_table(conn) -> None:
    """Create memory_embeddings table if it doesn't exist."""
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id BIGSERIAL PRIMARY KEY,
            path TEXT NOT NULL,
            tier TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            embedding vector({EMBEDDING_DIMS}),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(path, chunk_index)
        )
    """)
    # Index for fast vector search
    conn.execute(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = '{TABLE_NAME}_embedding_idx'
            ) THEN
                CREATE INDEX {TABLE_NAME}_embedding_idx
                ON {TABLE_NAME} USING hnsw (embedding vector_cosine_ops);
            END IF;
        END
        $$;
    """)
    conn.commit()


def index_memory_files(conn) -> dict:
    """Index all memory markdown files into pgvector.

    Returns stats dict with counts.
    """
    ensure_table(conn)

    stats = {"files": 0, "chunks": 0, "skipped": 0, "errors": 0}

    for tier, mem_dir in MEMORY_DIRS:
        if not mem_dir.exists():
            continue

        for md_file in mem_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue

            try:
                text = md_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                stats["errors"] += 1
                continue

            if not text.strip():
                continue

            file_hash = content_hash(text)
            rel_path = str(md_file)

            # Check if already indexed with same hash
            existing = conn.execute(
                f"SELECT content_hash FROM {TABLE_NAME} WHERE path = %s AND chunk_index = 0 LIMIT 1",
                (rel_path,),
            ).fetchone()

            if existing and existing[0] == file_hash:
                stats["skipped"] += 1
                continue

            # Delete old chunks for this file
            conn.execute(f"DELETE FROM {TABLE_NAME} WHERE path = %s", (rel_path,))

            # Chunk and embed
            chunks = chunk_text(text)
            if not chunks:
                continue

            embeddings = get_embeddings_batch(chunks)

            for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                conn.execute(
                    f"""INSERT INTO {TABLE_NAME}
                        (path, tier, chunk_index, chunk_text, content_hash, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (path, chunk_index) DO UPDATE SET
                            chunk_text = EXCLUDED.chunk_text,
                            content_hash = EXCLUDED.content_hash,
                            embedding = EXCLUDED.embedding,
                            updated_at = NOW()
                    """,
                    (rel_path, tier, i, chunk, file_hash, emb),
                )

            stats["files"] += 1
            stats["chunks"] += len(chunks)
            print(f"  [{tier}] {md_file.name}: {len(chunks)} chunks")

    conn.commit()
    return stats


def vector_search(conn, query: str, limit: int = MAX_RESULTS) -> list[dict]:
    """Semantic search via pgvector cosine similarity."""
    query_embedding = get_embedding(query)

    results = conn.execute(
        f"""
        SELECT path, tier, chunk_index, chunk_text,
               1 - (embedding <=> %s::vector) AS similarity
        FROM {TABLE_NAME}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (query_embedding, query_embedding, limit),
    ).fetchall()

    return [
        {
            "path": r[0],
            "tier": r[1],
            "chunk_index": r[2],
            "snippet": r[3][:200],
            "score": float(r[4]),
            "source": "vector",
        }
        for r in results
    ]


# ---------------------------------------------------------------------------
# FTS5 keyword search (delegates to existing memory-search.py)
# ---------------------------------------------------------------------------


def keyword_search(query: str, limit: int = MAX_RESULTS) -> list[dict]:
    """FTS5 keyword search via the existing memory-search sidecar."""
    FTS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(FTS_DB_PATH))

    # Ensure FTS5 table exists
    conn.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts "
        "USING fts5(tier, path, content, tokenize='porter unicode61')"
    )

    # Reindex (fast for small memory dirs)
    conn.execute("DELETE FROM memory_fts")
    for tier, mem_dir in MEMORY_DIRS:
        if not mem_dir.exists():
            continue
        for md_file in mem_dir.rglob("*.md"):
            if md_file.name.startswith("."):
                continue
            try:
                content = md_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if not content.strip():
                continue
            conn.execute(
                "INSERT INTO memory_fts(tier, path, content) VALUES (?, ?, ?)",
                (tier, str(md_file), content),
            )
    conn.commit()

    # Search
    fts_query = query.strip()
    if not fts_query:
        conn.close()
        return []

    try:
        rows = conn.execute(
            "SELECT tier, path, snippet(memory_fts, 2, '', '', '...', 32), rank "
            "FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
            (fts_query, limit),
        ).fetchall()
    except sqlite3.OperationalError:
        safe_query = '"' + fts_query.replace('"', '""') + '"'
        rows = conn.execute(
            "SELECT tier, path, snippet(memory_fts, 2, '', '', '...', 32), rank "
            "FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
            (safe_query, limit),
        ).fetchall()

    conn.close()

    if not rows:
        return []

    # Normalize FTS5 ranks to 0-1 range (rank is negative, lower = better)
    min_rank = min(r[3] for r in rows)
    max_rank = max(r[3] for r in rows)
    rank_range = max_rank - min_rank if max_rank != min_rank else 1.0

    return [
        {
            "path": r[1],
            "tier": r[0],
            "chunk_index": -1,
            "snippet": r[2],
            "score": 1.0 - ((r[3] - min_rank) / rank_range),  # normalize to [0, 1]
            "source": "keyword",
        }
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Hybrid merge
# ---------------------------------------------------------------------------


def hybrid_search(query: str, limit: int = MAX_RESULTS) -> list[dict]:
    """Merge vector + keyword results with weighted scoring.

    Uses 0.7 vector / 0.3 keyword weighting per OpenClaw recommendation.
    """
    # Get results from both sources
    pg_conn = get_pg_conn()
    if pg_conn is None:
        print("WARNING: DATABASE_URL not set, falling back to keyword-only search", file=sys.stderr)
        results = keyword_search(query, limit)
        for r in results:
            r["sources"] = ["keyword"]
            r["vector_score"] = 0.0
            r["keyword_score"] = r["score"]
            r["hybrid_score"] = r["score"]
        return results

    try:
        ensure_table(pg_conn)
        v_results = vector_search(pg_conn, query, limit * 2)
    except Exception as e:
        print(f"WARNING: Vector search failed ({e}), falling back to keyword-only", file=sys.stderr)
        v_results = []
        pg_conn.close()
        if not v_results:
            results = keyword_search(query, limit)
            for r in results:
                r["sources"] = ["keyword"]
                r["vector_score"] = 0.0
                r["keyword_score"] = r["score"]
                r["hybrid_score"] = r["score"]
            return results
    else:
        pg_conn.close()

    k_results = keyword_search(query, limit * 2)

    # Build a merged result set keyed by file path
    merged: dict[str, dict] = {}

    for r in v_results:
        key = r["path"]
        if key not in merged:
            merged[key] = {
                "path": r["path"],
                "tier": r["tier"],
                "snippet": r["snippet"],
                "vector_score": r["score"],
                "keyword_score": 0.0,
                "sources": ["vector"],
            }
        else:
            # Keep highest vector score for this file
            merged[key]["vector_score"] = max(merged[key]["vector_score"], r["score"])
            if "vector" not in merged[key]["sources"]:
                merged[key]["sources"].append("vector")

    for r in k_results:
        key = r["path"]
        if key not in merged:
            merged[key] = {
                "path": r["path"],
                "tier": r["tier"],
                "snippet": r["snippet"],
                "vector_score": 0.0,
                "keyword_score": r["score"],
                "sources": ["keyword"],
            }
        else:
            merged[key]["keyword_score"] = max(merged[key].get("keyword_score", 0.0), r["score"])
            if "keyword" not in merged[key]["sources"]:
                merged[key]["sources"].append("keyword")
            # Prefer keyword snippet if we don't have a vector one
            if not merged[key].get("snippet"):
                merged[key]["snippet"] = r["snippet"]

    # Calculate hybrid score
    for item in merged.values():
        item["hybrid_score"] = (
            VECTOR_WEIGHT * item["vector_score"]
            + KEYWORD_WEIGHT * item["keyword_score"]
        )

    # Sort by hybrid score descending
    ranked = sorted(merged.values(), key=lambda x: x["hybrid_score"], reverse=True)
    return ranked[:limit]


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------


def show_status() -> None:
    """Show index stats for both FTS5 and pgvector."""
    print("=== Memory Search Index Status ===\n")

    # FTS5
    if FTS_DB_PATH.exists():
        conn = sqlite3.connect(str(FTS_DB_PATH))
        try:
            count = conn.execute("SELECT COUNT(*) FROM memory_fts").fetchone()[0]
            print(f"FTS5 (keyword): {count} documents indexed")
            print(f"  DB: {FTS_DB_PATH} ({FTS_DB_PATH.stat().st_size // 1024} KB)")
        except sqlite3.OperationalError:
            print("FTS5 (keyword): not initialized")
        conn.close()
    else:
        print("FTS5 (keyword): not initialized")

    # pgvector
    pg_conn = get_pg_conn()
    if pg_conn:
        try:
            ensure_table(pg_conn)
            count = pg_conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
            files = pg_conn.execute(f"SELECT COUNT(DISTINCT path) FROM {TABLE_NAME}").fetchone()[0]
            print(f"\npgvector (semantic): {count} chunks from {files} files")

            # Show per-tier breakdown
            tiers = pg_conn.execute(
                f"SELECT tier, COUNT(DISTINCT path), COUNT(*) FROM {TABLE_NAME} GROUP BY tier"
            ).fetchall()
            for tier, file_count, chunk_count in tiers:
                print(f"  [{tier}] {file_count} files, {chunk_count} chunks")

        except Exception as e:
            print(f"\npgvector (semantic): error - {e}")
        pg_conn.close()
    else:
        print("\npgvector (semantic): DATABASE_URL not set")

    # Memory dirs
    print("\nMemory directories:")
    total_files = 0
    for tier, mem_dir in MEMORY_DIRS:
        if mem_dir.exists():
            md_files = list(mem_dir.rglob("*.md"))
            md_files = [f for f in md_files if not f.name.startswith(".")]
            total_files += len(md_files)
            print(f"  [{tier}] {mem_dir}: {len(md_files)} .md files")
        else:
            print(f"  [{tier}] {mem_dir}: not found")
    print(f"\nTotal: {total_files} memory files")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    args = sys.argv[1:]

    if not args:
        print(__doc__.strip(), file=sys.stderr)
        return 1

    if args[0] == "--status":
        show_status()
        return 0

    if args[0] == "--index":
        pg_conn = get_pg_conn()
        if not pg_conn:
            print("ERROR: DATABASE_URL not set", file=sys.stderr)
            return 1
        print("Indexing memory files into pgvector...")
        stats = index_memory_files(pg_conn)
        pg_conn.close()
        print(f"\nDone: {stats['files']} files, {stats['chunks']} chunks "
              f"({stats['skipped']} skipped, {stats['errors']} errors)")
        return 0

    if args[0] == "--keyword-only":
        query = " ".join(args[1:])
        if not query:
            print("Usage: memory-search-hybrid.py --keyword-only <query>", file=sys.stderr)
            return 1
        results = keyword_search(query)
        for r in results:
            print(f"### [{r['tier']}] {r['path']}  (score: {r['score']:.3f})")
            print(r["snippet"])
            print()
        return 0

    if args[0] == "--vector-only":
        query = " ".join(args[1:])
        if not query:
            print("Usage: memory-search-hybrid.py --vector-only <query>", file=sys.stderr)
            return 1
        pg_conn = get_pg_conn()
        if not pg_conn:
            print("ERROR: DATABASE_URL not set", file=sys.stderr)
            return 1
        ensure_table(pg_conn)
        results = vector_search(pg_conn, query)
        pg_conn.close()
        for r in results:
            print(f"### [{r['tier']}] {r['path']}  (similarity: {r['score']:.3f})")
            print(r["snippet"])
            print()
        return 0

    # Default: hybrid search
    query = " ".join(args)
    results = hybrid_search(query)

    if not results:
        print(f"No results for: {query}")
        return 0

    for r in results:
        sources = "+".join(r["sources"])
        print(f"### [{r['tier']}] {r['path']}  (hybrid: {r['hybrid_score']:.3f}  [{sources}])")
        if r.get("vector_score", 0) > 0:
            print(f"    vector={r['vector_score']:.3f}  keyword={r['keyword_score']:.3f}")
        print(r["snippet"])
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
