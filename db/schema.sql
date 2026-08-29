-- rag-stack-builder schema (PLAN.md §4.2). Embedding dimension 1024 = voyage-4.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS source (
  id          bigserial PRIMARY KEY,
  domain      text NOT NULL,
  title       text NOT NULL,
  author      text,
  file_name   text,
  format      text,          -- pdf | epub | md | html | docx | txt | csv | xlsx | ...
  file_hash   text,          -- dedupe re-ingestion
  ingested_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chunk (
  id          bigserial PRIMARY KEY,
  source_id   bigint NOT NULL REFERENCES source(id),
  domain      text   NOT NULL,           -- denormalized for fast filtering
  chapter     text,
  section     text,
  page_start  int,
  page_end    int,
  seq         int    NOT NULL,           -- order within source
  breadcrumb  text   NOT NULL,           -- "Title › Ch. N Name › Section"
  text        text   NOT NULL,
  tsv         tsvector,
  embedding   vector(1024)
);

CREATE INDEX IF NOT EXISTS chunk_embedding_idx ON chunk
  USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunk_tsv_idx    ON chunk USING gin (tsv);
CREATE INDEX IF NOT EXISTS chunk_domain_idx ON chunk (domain);

-- RESERVED for v2 (do not build yet): entity, mention, entity_relation.
