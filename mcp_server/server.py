#!/usr/bin/env python3
"""The search counter (PLAN.md §4.4) — MCP server over the library.

Phase 3 "dumb version": vector-only search with citations. Hybrid search and
query rewriting arrive as Phase 4 layers, each proven by the eval before it
stays. Single file, stdio transport.

Config via environment: DATABASE_URL, VOYAGE_API_KEY.
Run: python3 server.py     (or wire into a host's MCP config, see .mcp.json)
"""
import json
import os
import time
import urllib.request

import psycopg2
from mcp.server.mcpserver import MCPServer

DB_URL = os.environ.get("DATABASE_URL", "postgresql://rag:ragdev@localhost:5432/raglib")
VOYAGE_MODEL = "voyage-4"
VOYAGE_ENDPOINT = "https://api.voyageai.com/v1/embeddings"

server = MCPServer(
    "rag-stack-library",
    instructions=(
        "Search a curated, citation-backed document library. For design or "
        "judgment questions, decompose into sub-topics and call search_corpus "
        "separately for each. Cite source + location (page/chapter) for every "
        "claim drawn from retrieval. If retrieval returns nothing relevant, say "
        "so rather than answering from memory as if grounded."
    ),
)


def _embed_query(query: str) -> list:
    body = {"input": [query], "model": VOYAGE_MODEL, "input_type": "query"}
    attempt = 0
    while True:
        try:
            req = urllib.request.Request(
                VOYAGE_ENDPOINT,
                data=json.dumps(body).encode(),
                headers={
                    "Authorization": f"Bearer {os.environ['VOYAGE_API_KEY']}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())["data"][0]["embedding"]
        except urllib.error.HTTPError as exc:
            attempt += 1
            if exc.code == 429 and attempt <= 10:
                time.sleep(21)
                continue
            raise


def _q(sql: str, params: tuple) -> list:
    with psycopg2.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


# --- Phase 4 layers (each proven by the eval before becoming the default) ---
REWRITE_MODEL = "gpt-oss:20b"
OLLAMA_ENDPOINT = "https://ollama.com/api/chat"
# hybrid became the default after the Iteration 2 rank probe (MRR 0.900 vs
# 0.733 vector-only); rewriting was REMOVED after the same probe showed it
# degrades ranks (0.783) — see CHANGELOG.md Iterations 2-3.
DEFAULT_MODE = os.environ.get("RAG_MODE", "hybrid")          # vector | hybrid
DEFAULT_REWRITE = os.environ.get("RAG_REWRITE", "off") == "on"

_SELECT = """SELECT c.id, s.title, c.chapter, c.page_start, c.page_end,
                    c.breadcrumb, c.text"""


def _vector_arm(emb: str, domain: str, k: int) -> list:
    return _q(
        _SELECT + """
           FROM chunk c JOIN source s ON s.id = c.source_id
           WHERE c.domain = %s
           ORDER BY c.embedding <=> %s::vector LIMIT %s""",
        (domain, emb, k),
    )


def _keyword_arm(query: str, domain: str, k: int) -> list:
    # OR the parsed terms: websearch_to_tsquery ANDs every word, which returns
    # zero rows for question-length queries (found in the Iteration 2 rank
    # probe — the AND-semantics arm was a silent no-op). ts_rank still rewards
    # chunks matching more terms, so OR + rank ≈ best-coverage matching.
    return _q(
        _SELECT + """
           FROM chunk c JOIN source s ON s.id = c.source_id
           CROSS JOIN LATERAL (
               SELECT replace(websearch_to_tsquery('english', %s)::text,
                              ' & ', ' | ')::tsquery AS tq) t
           WHERE c.domain = %s AND c.tsv @@ t.tq
           ORDER BY ts_rank(c.tsv, t.tq) DESC
           LIMIT %s""",
        (query, domain, k),
    )


def _rrf_merge(ranked_lists: list, k: int, c: int = 60) -> list:
    """Reciprocal rank fusion across any number of ranked row lists."""
    scores, best = {}, {}
    for rows in ranked_lists:
        for rank, row in enumerate(rows):
            cid = row[0]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (c + rank + 1)
            best.setdefault(cid, row)
    top = sorted(scores, key=scores.get, reverse=True)[:k]
    return [(best[cid], scores[cid]) for cid in top]


def _rewrite_query(query: str) -> list:
    """Cheap fast model expands the query into 2-3 focused variants."""
    body = {
        "model": REWRITE_MODEL,
        "messages": [
            {"role": "system", "content":
                "Rewrite the user's search query into 2-3 alternative search "
                "queries using synonyms, related technical/historical "
                "vocabulary, and more specific phrasings. Output ONLY the "
                "queries, one per line, no numbering."},
            {"role": "user", "content": query},
        ],
        "stream": False,
    }
    try:
        req = urllib.request.Request(
            OLLAMA_ENDPOINT, data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {os.environ['OLLAMA_API_KEY']}",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            text = json.loads(resp.read())["message"]["content"]
        variants = [ln.strip() for ln in text.split("\n") if ln.strip()][:3]
        return [query] + variants
    except Exception:
        return [query]                      # rewriting must never break search


def search_corpus_ex(query: str, domain: str, k: int = 8,
                     mode: str = None, rewrite: bool = None) -> list:
    """Full retrieval pipeline with explicit layer control (used by the eval
    harness to prove each layer; the MCP tool calls it with the defaults)."""
    mode = mode or DEFAULT_MODE
    rewrite = DEFAULT_REWRITE if rewrite is None else rewrite
    queries = _rewrite_query(query) if rewrite else [query]

    arms = []
    for q_text in queries:
        emb = str(_embed_query(q_text))
        arms.append(_vector_arm(emb, domain, k))
        if mode == "hybrid":
            arms.append(_keyword_arm(q_text, domain, k))
    merged = _rrf_merge(arms, k)
    return [
        {
            "text": row[6],
            "citation": {"source": row[1], "chapter": row[2],
                         "page_start": row[3], "page_end": row[4],
                         "breadcrumb": row[5]},
            "score": round(score, 4),
        }
        for row, score in merged
    ]


@server.tool()
def search_corpus(query: str, domain: str, k: int = 8) -> list:
    """Search the document library. Returns the k most relevant passages with
    citations (source title, chapter, pages, breadcrumb) and a relevance score.
    Search per sub-topic rather than pasting whole questions."""
    return search_corpus_ex(query, domain, k)


@server.tool()
def list_domains() -> list:
    """List the domains available in the library."""
    return [
        {"domain": r[0], "sources": r[1], "chunks": r[2]}
        for r in _q(
            """SELECT c.domain, COUNT(DISTINCT c.source_id), COUNT(*)
               FROM chunk c GROUP BY c.domain ORDER BY c.domain""", ())
    ]


@server.tool()
def list_sources(domain: str) -> list:
    """List the sources ingested for a domain."""
    return [
        {"title": r[0], "format": r[1], "file_name": r[2], "chunks": r[3]}
        for r in _q(
            """SELECT s.title, s.format, s.file_name, COUNT(c.id)
               FROM source s LEFT JOIN chunk c ON c.source_id = s.id
               WHERE s.domain = %s GROUP BY s.id ORDER BY s.title""",
            (domain,))
    ]


if __name__ == "__main__":
    server.run(transport="stdio")
