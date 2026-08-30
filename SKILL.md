---
name: rag-stack-builder
description: >-
  Build a citation-backed grounding stack from any folder of mixed documents.
  Use when the user points at a folder of sources (books, papers, articles,
  PDFs, HTML, text) and asks to "build a RAG stack", "build a knowledge base",
  "ground my AI in these documents", "make a searchable library", or to add a
  new domain to an existing library. Plans the ingestion, gets human approval,
  executes frozen per-format pipelines into Postgres+pgvector, and exposes
  retrieval as an MCP tool (search_corpus) with citations to source and
  page/chapter. Also use to re-run ingestion for new files in a known domain.
---

# rag-stack-builder — build a grounded, citation-backed library from a folder

You are executing a **phased build with verification gates**. The intelligence
in this skill was spent at design time; your job is to run the frozen
machinery, verify each phase, and stop at the human gates. Two principles
govern every step (PLAN.md §8):

1. **Pipes move data; models make judgments.** Never read the corpus files
   yourself; run the scripts that process them. If a weird file breaks a
   script, fix the script (permanently), never hand-process the file.
2. **Consistency beats cleverness.** Identical chunking across a domain beats
   per-document optimization.

## Conventions (all phases)

- Maintain `STATE.md` in the project root: current phase, verified facts,
  connection details, gate answers. **Read it first in every session; resume,
  never re-derive.** Postgres may need `service postgresql start` (or
  `docker compose up -d`) after a container recycle.
- Every phase ends with a verification step. Do not advance until it passes.
- Human gates are explicit stops: ask, wait, record the answer in STATE.md.
- Secrets live in `.env` (see `.env.example`); never commit them.

## Phase 1 — Database

HUMAN GATE (skip if STATE.md already records answers): where does Postgres run
(docker compose in `db/`, or an existing/local instance) and which embedding
model (dimension must match `db/schema.sql`, default `voyage-4` @ 1024)?

Then: apply `db/schema.sql`. Verify with a round trip: insert one fake chunk
with a dummy embedding, query it back BOTH by cosine similarity and by
tsvector keyword, then delete it. Record in STATE.md.

## Phase 2 — Ingestion (the intake desk)

The scripts in `ingest/` are **frozen templates** proven on two domains
(mixed OCR txt / Gutenberg HTML / scanned PDF). Start from them; adapt only
if verification fails, and any fix becomes permanent.

1. `python3 ingest/ingest.py plan <folder> --domain <name> --out <plan.json>`
   — read-only scan → classify → per-file plan with probes, duplicate warnings
   (same work in two formats must not be ingested twice), and skipped files
   with reasons. Never silently drop a file.
2. **HUMAN GATE 1:** show the plan; the owner approves or edits (set
   `"action": "skip"` per file). Prefer the PDF twin of a work when it has a
   text layer — page-number citations beat chapter-only.
3. `python3 ingest/ingest.py run <folder> --domain <name> --plan <plan.json>`
   — parse → chunk (200–500 words, never split mid-paragraph) → breadcrumb
   (prefixed to text before embedding) → batched embeddings → atomic per-file
   insert with sha256 dedupe. Embedding APIs rate-limit hard on free tiers:
   the embedder self-paces; expect ~10K tokens/min on free Voyage keys, so a
   book-sized corpus takes 1–2 hours. Run it in the background.
4. **HUMAN GATE 2:** sample ~20 random chunks across sources (SQL in
   REPRODUCE.md); the owner checks text cleanliness, breadcrumbs, page sanity.
   Fix-and-re-ingest until approved.

Known limits (do not re-discover): OCR-era typos in century-old scans are
source artifacts, not parser bugs; ~5% of OCR-txt chunks start mid-sentence;
tabular files (csv/xlsx) are routed away from the prose pipeline and their
strategy is decided only when a corpus actually contains them (PLAN.md D12).

## Phase 3 — Retrieval (the search counter)

`mcp_server/server.py` is the frozen single-file MCP server: `search_corpus
(query, domain, k)` + `list_domains` + `list_sources`, stdio transport,
config via `DATABASE_URL` / `VOYAGE_API_KEY`. Wire it into the host's MCP
config (see `.mcp.json`). Verify end-to-end: three questions whose answers
you have verified exist in the corpus must return the right passages with
correct citations (query through the host's MCP tools, not in-process).

## Phase 4 — Retrieval quality (already decided; do not re-litigate)

Hybrid retrieval (vector + OR-semantics keyword arm, RRF fusion) is the
default — it took ground-truth-chunk MRR from 0.733 to 0.900 on the depth
corpus. Server-side query rewriting was tried and REMOVED (it dilutes rank
fusion; CHANGELOG.md Iteration 3). If retrieval underperforms on a new
corpus, measure with `eval/rank_probe.py` (adapt the needles) before
changing anything.

## Phase 5 — Agent behavior

The grounding instruction ships in the server's `instructions` string, so
every MCP host inherits it: decompose judgment questions into sub-topic
searches, cite source + location per claim, and say plainly when the library
does not answer. Verify: one judgment question should trigger ≥2 distinct
search_corpus calls and a fully cited answer.

## Evaluating a new domain (optional but recommended)

Write ~5 smoke questions with ground truth QUOTED from the corpus files
(never from memory), run them through the tool, and check answers + citations.
For a full before/after protocol (baseline vs. grounded, pushback stability,
traps), follow `eval/run_eval.py` and PLAN.md §5.

## When this stack stops being enough

Upgrade triggers live in PLAN.md §7 (entity/mention graph layer, reranking,
Agent SDK wrapper, per-domain partial indexes). Earn complexity with evidence
— the fumbled-questions list decides, not intuition.
