# rag-stack-builder — Full Plan & Handoff Document

**Owner:** Mohammed
**Skill / repo name:** `rag-stack-builder`
**Status:** Design finalized, ready to build (v1)
**Purpose of this document:** Complete context handoff for a Claude Code session that will build this system. It records how the idea started, how it evolved through design discussion, every decision made (with reasoning), and the exact v1 build specification.

---

## 1. One-sentence definition

A personal, domain-swappable knowledge library: point the skill at a folder of mixed source files — books, papers, articles, MD/text files, CSVs, and other formats — and it plans and executes ingestion into a Postgres+pgvector database, then exposes retrieval as an MCP tool so any AI host (Claude Code, Claude.ai, Open WebUI, Agent SDK apps) can search that library mid-conversation and answer with citations pointing to the exact source and location (page, section, or row).

**Primary goal:** reduce hallucination and improve decision quality by grounding LLM answers in a curated corpus, per domain, reusable across projects.

---

## 2. How it started

The project began as a much larger multi-agent orchestration idea:

- A conversational **orchestrator agent** that captures intent ("build a knowledge graph around this data").
- Input could be CSVs, documents, books, images, or codebases.
- The orchestrator would route to specialist agents: a **Geo agent** (deep knowledge of the Geo knowledge graph platform's ontology, would plan and delegate ingestion into Geo) or a **vector-DB agent** (plan chunking/embedding into a vector store), each handing off to ingestion sub-agents, with human-in-the-loop approval gates.
- The open question was the harness: build agents on a framework (LangChain/LangGraph, Google ADK), use the Claude Code skills + subagents pattern (as demonstrated by the last30days-skill on GitHub), or something else.

Key early conclusions that survived into the final design:

- **A skill is not an agent framework** — it is procedural knowledge loaded into a host agent's already-tuned harness. Skills borrow the host's subagent primitives.
- **The last30days lesson:** put deterministic work in scripts; reserve the model for judgment. Pure prompt-driven orchestration of data processing is slow, expensive, and inconsistent.
- **Staged approach:** prototype as skills in Claude Code (v1) → wrap with the Claude Agent SDK for headless/UI use (v2) → frameworks only if the system ever serves other users.
- The Claude Agent SDK loads filesystem skills via `setting_sources=["project"]` and (since June 15, 2026) runs on a separate monthly Agent SDK credit included with Pro/Max plans — so headless operation on the owner's Max subscription is viable for v2.

---

## 3. How it evolved (decision log)

Each decision below is settled. Do not re-litigate them during the build; they carry reasoning from extended discussion.

**D1 — Geo is out of v1 entirely.**
The owner decided v1 targets his own store only. Geo (a public knowledge graph he curates) may return later as an optional publish target for a distilled entity layer, but nothing in v1 depends on it.

**D2 — Vector store vs knowledge graph: not either/or.**
The owner's instinct — chunk books into paragraphs, embed them, extract mentioned entities, link entities to every paragraph that mentions them, link paragraphs to chapters/pages — is the established **lexical graph + domain graph hybrid** (GraphRAG-style). Vector search = fuzzy semantic recall; knowledge graph = identity + typed relationships + multi-hop traversal. They are layers of one artifact, not competing backends.

**D3 — But the graph layer is deferred to v2.**
Reasons: (a) entity resolution (merging aliases into one node) is the genuinely hard problem, and a bad graph injects irrelevant passages and actively degrades answers; (b) we don't yet know which failures are graph-shaped — run plain retrieval first and collect fumbled questions; (c) agentic retrieval (the model searching iteratively via a tool) covers much of what mention-links would provide, free. The v1 schema reserves space for `entity` and `mention` tables so adding the layer later disturbs nothing.

**D4 — Reframe: this is a domain-agnostic grounding system, not a book-graph product.**
The real vision: point the pipeline at any corpus (software engineering, astrophysics, anything), get a knowledge base, plug it into whatever you're working on. Classic RAG first, graph later.

**D5 — Honest calibration on what retrieval fixes.**
Two question types:
- *Type 1 (lookup):* the answer is written in the books. Retrieval nearly eliminates hallucination here — the model restates real text and cites it; the human can verify.
- *Type 2 (judgment):* e.g. "best architecture for a Twitter-like feed system." No book contains the answer; the books contain the ingredients. Retrieval hands the model the right ingredients so it reasons from real material instead of fuzzy memory — a real improvement, but the final synthesis is still the model's own reasoning and can still be wrong.
- Expected lift on Type 2 is largest for corpora the base model doesn't already know well (niche, recent, specialized, local material). For canonical textbooks the lift is precision + citability more than transformation.

**D6 — Storage: Postgres + pgvector, not Neo4j.**
The book graph is shallow (paragraph → entity → paragraph = 2 hops); nothing needs variable-length paths yet. Postgres is the owner's home stack; one database holds chunks, embeddings, metadata, and (later) edges; hybrid filtered search is a strength; no second operational surface, no store-sync problem. Neo4j triggers (later, if ever): need for graph algorithms (community detection, centrality), genuinely path-shaped queries, or measured traversal degradation. The neutral nodes-and-edges IR makes migration an export script.

**D7 — One database, many domains.**
A `domain` column on every chunk. ~25–35k chunks per fully loaded domain; even 20 domains ≈ 600k rows — trivial for Postgres/HNSW. Per-domain partial indexes or partitioning only if filtered-search slowdown is actually felt. Separate databases only for isolation needs (handing a domain to someone, separate backup policy) — none apply to v1.

**D8 — Retrieval is an MCP server, not a skill.**
A skill exists only inside a Claude Code session; retrieval must be available wherever prompting happens. One MCP server exposing `search_corpus(query, domain, k)` plugs into every host. Critically, retrieval-as-a-tool enables **agentic retrieval**: the model decides when to search, reformulates, searches multiple times, follows leads. A Type 2 question is secretly a bundle of Type 1 questions; tool-based retrieval lets the agent decompose it into focused lookups — the single biggest quality difference vs. bolting top-k chunks onto the prompt.

**D9 — Query reformulation ("reprompting") is in scope, at two layers.**
(1) Server-side: a cheap fast model expands each incoming query into 2–3 focused variants with synonyms/technical vocabulary; optionally HyDE (embed a hypothetical *answer* paragraph rather than the question — answers resemble book passages more than questions do). Server-side means every host benefits, even single-shot callers. (2) Agent-side: an instruction to decompose judgment questions into sub-topics and search each separately.

**D10 — Ingestion intelligence is build-time, not run-time.**
The agent (Claude Code) *writes* the ingestion scripts during setup — iteratively testing and fixing — then **freezes** them. Thereafter, ingesting a book means *running* `ingest.py`, not re-improvising. Reasons: (a) consistency — improvised per-run processing drifts chunk sizes and breadcrumb formats between books, silently degrading corpus-wide retrieval; (b) cost/speed — a script chunks a 400-page book in seconds; the model should never read the book, only route it through a pipe; (c) improvised processing is where silent corruption (dropped chapters, shifted page numbers) sneaks in. When a weird book breaks the script, the agent fixes the script and the fix becomes permanent.

**D11 — The entire v1 build is driven by ONE installer skill.**
A single skill whose SKILL.md is a phased build plan the agent executes end-to-end, with verification gates per phase, a `STATE.md` checkpoint file (builds span multiple sessions), and explicit human gates. The skill ships with no pre-written Python — generating and freezing the scripts is part of the build.

**D12 — Multi-format sources; the folder is the unit of ingestion.**
Not just books: papers, articles, MD/text files, HTML, DOCX, CSVs and other tabular files. The interaction model: the owner points the skill at a folder and asks it to plan the ingestion / build a RAG stack on top. The ingester therefore gains a **scan → classify → plan → approve → execute** flow: scan the folder, classify each file by format, produce a per-file ingestion plan (which pipeline, expected chunking), get human approval, then run the frozen per-format pipelines. Prose formats share the paragraph pipeline; **tabular files (CSV/XLSX) must NOT silently pass through the paragraph pipeline** — chunk-and-embed works poorly on tables. Route them separately: serialize rows into labeled sentences for embedding, and/or store them as tables and expose a second SQL-style lookup tool. The exact tabular strategy is a Phase 2 decision, but the routing split is settled.

**D13 — Packaging: a clone-and-run skill repo, with template copy-back.**
Distributed like last30days: a GitHub repo (`rag-stack-builder`) cloned into `.claude/skills/` (or any Agent Skills host). The repo contains SKILL.md (the phased build plan) and reference specs; running it generates all artifacts (schema, scripts, MCP server, STATE.md) inside the target project. After the first clean build, copy the frozen `ingest.py` and MCP server back into the repo's `templates/` folder, and change the skill instruction to "start from template, adapt only if verification fails" — every later setup gets faster and more reproducible while keeping the agent's ability to fix parser edge cases per corpus.

---

## 4. Current system definition (v1)

### 4.1 Components

1. **The library** — one Postgres database with pgvector. Paragraph-level chunks + embeddings + metadata (domain, book, chapter, section, page). Domains separated by a `domain` column.
2. **The intake desk** — an ingestion capability inside Claude Code: point it at a folder ("build a RAG stack on this folder as domain X"), it scans and classifies the files, presents a per-file ingestion plan for approval, then executes via frozen per-format scripts (`ingest.py` + parser helpers) produced during setup.
3. **The search counter** — a small MCP server exposing `search_corpus(query, domain, k)`: query rewriting → hybrid (vector + keyword) search filtered by domain → top passages returned **with citations** (book, chapter, page). Connected to Claude Code, Claude.ai projects, Open WebUI, and any future Agent SDK app.

### 4.2 Reference schema (starting point — agent may refine, not simplify away)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE source (
  id          bigserial PRIMARY KEY,
  domain      text NOT NULL,
  title       text NOT NULL,
  author      text,
  file_name   text,
  format      text,          -- pdf | epub | md | html | docx | txt | csv | xlsx | ...
  file_hash   text,          -- dedupe re-ingestion
  ingested_at timestamptz DEFAULT now()
);

CREATE TABLE chunk (
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
  tsv         tsvector,                  -- keyword search
  embedding   vector(1024)               -- dimension per chosen model
);

CREATE INDEX chunk_embedding_idx ON chunk
  USING hnsw (embedding vector_cosine_ops);
CREATE INDEX chunk_tsv_idx    ON chunk USING gin (tsv);
CREATE INDEX chunk_domain_idx ON chunk (domain);

-- RESERVED for v2 (do not build yet):
-- entity(id, domain, name, type, aliases text[])
-- mention(chunk_id, entity_id)
-- entity_relation(from_id, to_id, type)
```

Embedding is stored on the chunk row; the breadcrumb is **prefixed to the text before embedding** (located paragraphs retrieve far better than orphaned ones).

### 4.3 Ingestion pipeline spec (what the frozen scripts must do)

**Step 0 — Scan & plan (per folder run):**
Scan the target folder recursively; classify each file by format; produce an ingestion plan listing, per file: detected format, chosen pipeline, expected structure (chapters vs sections vs rows), and any files it cannot handle. HUMAN GATE: owner approves/edits the plan before execution.

**Prose pipeline** (pdf, epub, md, html, docx, txt — books, papers, articles, notes):
1. Parse → structured text with the richest location tracking the format offers (chapter/section/page for books and PDFs; heading hierarchy for MD/HTML; section for papers).
2. Chunk at paragraph level (target ~200–500 words; merge tiny fragments; never split mid-paragraph; consistent parameters across ALL sources in a domain).
3. Build breadcrumb per chunk ("Title › Ch./Heading › Subsection"); prefix it to the text for embedding.
4. Embed via the chosen embedding API (batched).
5. Insert source row + chunk rows atomically; populate `tsv`; skip files whose `file_hash` already exists.
6. Print a summary: chunks created, pages/sections covered, anomalies (empty chapters, parse warnings, skipped files).

**Tabular pipeline** (csv, xlsx) — routing settled, strategy is a Phase 2 decision:
- Never send raw tables through the prose pipeline.
- Option A: serialize each row into a labeled sentence ("Column: value; …") with a breadcrumb of file + row number, then embed like prose.
- Option B: load into Postgres as real tables and expose a separate SQL-lookup MCP tool for precise queries.
- A and B can coexist; pick based on what the first real tabular files are actually used for.

**Unknown/unsupported formats:** list them in the plan as skipped with a reason; never silently drop a file.

### 4.4 MCP server spec

Tool: `search_corpus(query: str, domain: str, k: int = 8)`
Pipeline inside the tool:
1. **Rewrite:** cheap model expands the query into 2–3 focused variants (synonyms, technical vocabulary). Optional HyDE variant for judgment-style queries.
2. **Hybrid search:** for each variant, vector similarity (`embedding <=> $v`) + keyword (`tsv @@ query`) within `WHERE domain = $domain`; merge and dedupe (reciprocal rank fusion is fine).
3. **Return:** top-k chunks, each with `text`, `breadcrumb`, `book`, `chapter`, `page_start`, `page_end`, and similarity score.
Also expose `list_domains()` and `list_sources(domain)` as trivial helper tools.
Config: Postgres connection string + embedding API key via environment variables. Keep the server small — single file if possible, stdio transport for local hosts.

### 4.5 Agent-side instruction (to be added wherever the tool is used)

> For design/judgment questions, decompose into sub-topics and call search_corpus separately for each before answering. Cite book + page for every claim drawn from retrieval. If retrieval returns nothing relevant, say so rather than answering from memory as if grounded.

### 4.6 Quality stack summary (Type 2 path)

Decomposition (agent) → query rewriting + HyDE (server) → hybrid search (Postgres) → cited synthesis. Each layer is small; together they are most of the distance between naive RAG and a grounded-feeling system.

---

## 5. The installer skill — build phases

The new Claude Code session's job is to create this skill and then execute it. SKILL.md structure:

**Conventions (all phases):**
- Maintain `STATE.md` in the project root: current phase, what's verified, connection details, embedding model + dimension, script versions. Every session starts by reading it; resume, never re-derive.
- Every phase ends with a verification step. Do not advance until it passes.
- Human gates are explicit stops: ask, wait, record the answer in STATE.md.

**Phase 1 — Database.**
HUMAN GATE: where does Postgres run (existing instance / new local / container)? Which embedding model (determines vector dimension)?
Then: install pgvector, create schema (§4.2), insert one fake chunk with a dummy embedding, query it back by similarity and by keyword.
Verify: round-trip query returns the row.

**Phase 2 — Ingestion scripts (agent writes, then freezes).**
Write `ingest.py` + parser helpers per §4.3, including the folder scan → classify → plan step. Test on a SMALL MIXED folder: one book (PDF/EPUB), one paper or article, one MD file. (Tabular strategy is decided here too if the owner's first corpus includes CSVs; otherwise defer per D12.)
HUMAN GATE 1: owner approves the generated ingestion plan for the test folder.
HUMAN GATE 2: owner inspects ~20 random chunks across the different formats (clean text? correct breadcrumbs? sane locations?) and approves.
Fix iteratively until approved, then freeze — later changes only to fix a broken parse, and fixes are permanent.
Verify: test folder fully ingested; summary matches the files' real structure.

**Phase 3 — MCP server, dumb version.**
Vector-only search + citations, per §4.4 minus rewriting/hybrid. Wire into Claude Code's MCP config.
Verify: end-to-end — ask three questions the test book definitely answers; correct passages with correct citations come back.

**Phase 4 — Quality layers.**
Add keyword+vector hybrid with rank fusion, then server-side query rewriting (and HyDE for judgment queries).
Verify: run 5 judgment-style questions before/after; retrieval relevance visibly improves (record the before/after in STATE.md).

**Phase 5 — Agent instruction.**
Add §4.5 instruction to the relevant CLAUDE.md / project instructions / skill so every host using the tool decomposes and cites.
Verify: a judgment question triggers multiple distinct search_corpus calls and a cited answer.

**Phase 6 — First real domain + evaluation.**
Point the skill at a full domain folder (10–20 mixed files: books, papers, articles, notes). Owner uses it for real work for 1–2 weeks, keeping a running list of fumbled questions in `EVAL.md`.
This list — not theory — decides v2 priorities.

---

## 6. Explicitly OUT of v1

- Geo integration (D1) — possible v2+ publish target for a distilled entity layer.
- Entity/mention/relation graph layer (D3) — schema space reserved.
- Reranking stage (retrieve-30-rerank-to-5) — add when corpora grow.
- Agent SDK wrapper, Open WebUI custom app, cron/headless runs — v2.
- Any orchestration framework (LangChain/LangGraph/ADK) — only if other users ever come aboard (then API-key auth, isolation, cost controls).
- Neo4j — only on the D6 triggers.

## 7. Upgrade triggers (when v1 stops being enough)

- Fumbled questions cluster around "gather everything across all books about X" → build the entity/mention layer (v2 graph).
- Owner wants the library from cron jobs or a custom chat UI → wrap with Claude Agent SDK (`setting_sources=["project"]`, runs on the Max plan's Agent SDK monthly credit).
- Other people become users → frameworks + API keys conversation reopens.
- Filtered vector search measurably slows as unrelated domains grow → per-domain partial HNSW indexes or partitioning.

## 8. Design principles (carry these into every build decision)

1. **Pipes move data; models make judgments.** Never have the model read a book; have it fix the pipe that processes books.
2. **Consistency beats cleverness in ingestion.** Identical chunking across a domain > per-book optimization.
3. **Citations are the anti-hallucination mechanism.** Every retrieved claim traceable to its source + location (page, heading, or row).
4. **Neutral IR (chunks / entities / links with provenance)** keeps every storage and backend choice reversible.
5. **Earn complexity with evidence.** The fumbled-questions list in EVAL.md, not intuition, schedules v2.

## 9. Open items for the human (answer during Phase 1 gates)

- Postgres location (existing instance vs new container).
- Embedding model choice (sets `vector(N)` dimension; consider cost per ~30k chunks/domain and multilingual needs).
- Cheap model for server-side query rewriting (small/fast; called on every search).
- First test folder (small, mixed formats) and first full domain folder to ingest.
- Whether the first corpus includes tabular files (decides if the CSV strategy — D12 Option A/B — is chosen in Phase 2 or deferred).
