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


@server.tool()
def search_corpus(query: str, domain: str, k: int = 8) -> list:
    """Semantic search over the document library. Returns the k most relevant
    passages with citations (source title, chapter, pages, breadcrumb) and a
    similarity score. Search per sub-topic rather than pasting whole questions."""
    emb = str(_embed_query(query))
    rows = _q(
        """SELECT s.title, c.chapter, c.page_start, c.page_end, c.breadcrumb,
                  c.text, 1 - (c.embedding <=> %s::vector) AS score
           FROM chunk c JOIN source s ON s.id = c.source_id
           WHERE c.domain = %s
           ORDER BY c.embedding <=> %s::vector
           LIMIT %s""",
        (emb, domain, emb, k),
    )
    return [
        {
            "text": r[5],
            "citation": {
                "source": r[0], "chapter": r[1],
                "page_start": r[2], "page_end": r[3], "breadcrumb": r[4],
            },
            "score": round(float(r[6]), 4),
        }
        for r in rows
    ]


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
