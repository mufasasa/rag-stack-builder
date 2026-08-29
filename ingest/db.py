"""Database access for ingestion. One transaction per source file: the source
row and all its chunks land atomically or not at all. file_hash dedupe."""
import os

import psycopg2

DEFAULT_URL = "postgresql://rag:ragdev@localhost:5432/raglib"


def connect():
    return psycopg2.connect(os.environ.get("DATABASE_URL", DEFAULT_URL))


def already_ingested(conn, file_hash: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM source WHERE file_hash=%s", (file_hash,))
        return cur.fetchone() is not None


def insert_source_with_chunks(conn, source: dict, chunks: list, embeddings: list) -> int:
    assert len(chunks) == len(embeddings)
    with conn:                      # atomic
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO source (domain,title,author,file_name,format,file_hash)
                   VALUES (%(domain)s,%(title)s,%(author)s,%(file_name)s,%(format)s,%(file_hash)s)
                   RETURNING id""",
                source,
            )
            sid = cur.fetchone()[0]
            for c, emb in zip(chunks, embeddings):
                cur.execute(
                    """INSERT INTO chunk
                       (source_id,domain,chapter,section,page_start,page_end,seq,
                        breadcrumb,text,tsv,embedding)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,
                               to_tsvector('english', %s), %s)""",
                    (sid, source["domain"], c["chapter"], c["section"],
                     c["page_start"], c["page_end"], c["seq"], c["breadcrumb"],
                     c["text"], c["text"], str(emb)),
                )
    return sid
