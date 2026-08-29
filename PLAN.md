# rag-stack-builder — Plan v2 (Hackathon Submission Plan)

**Owner:** Mohammed
**Skill / repo name:** `rag-stack-builder`
**Status:** v2 — revised for the micro1 Agentic Workflows Hackathon. Supersedes `docs/PLAN-v1-original.md` (kept for provenance; its decision log D1–D13 still stands except where amended below).
**Target:** micro1 Agentic Workflows Hackathon — judged /100: Problem & User Value (15), Agent Solution & Engineering (30), End-to-End Quality (20), Measured Improvement (15), Reproducibility (15), Hot Take (5).

---

## 1. What this is (the reframe)

**The product is the installer skill.** `rag-stack-builder` is an agentic workflow — a Claude Code skill — that, pointed at any folder of mixed source documents, **plans, builds, verifies, and freezes a complete grounded-retrieval stack**:

- It scans and classifies the folder, proposes a per-file ingestion plan, and waits for human approval.
- It **writes the ingestion pipeline itself** during setup — testing and fixing iteratively against the real files — then freezes the scripts so every later run is deterministic ("pipes move data; models make judgments").
- It stands up Postgres + pgvector, ingests the corpus with paragraph-level chunks, breadcrumbs, and page/section provenance.
- It generates and wires up an MCP server exposing `search_corpus`, so any AI host (Claude Code, Claude.ai, Open WebUI, Agent SDK apps) can ground its answers in the corpus mid-conversation, with citations to exact source and location.

The RAG stack the skill produces is not the submission; it is the **evidence** that the submission works. The demo and evaluation show the skill building a stack on a public corpus and the resulting measurable drop in hallucination.

**Problem statement (for the README, per the brief's four questions):**

1. **Who has this problem?** Anyone doing sustained knowledge work with an LLM inside a domain the model knows only shakily — researchers, engineers, analysts working with niche, recent, regional, or specialized material. Concretely: the owner, whose LLM sessions in such domains produce confident wrong answers.
2. **What bottleneck makes it worth solving?** Frontier models hallucinate on domain specifics, and worse, **fold under pushback**: challenge a correct answer and the model apologizes and flips. The user can't tell grounded answers from confabulated ones, so every answer requires manual verification — which defeats the purpose of asking. Building a grounded stack by hand (parsers, chunking, embedding, hybrid search, server wiring) is days of specialist work per corpus, so nobody does it for their personal projects.
3. **Does the agent solve it well?** The agent collapses "days of specialist work per corpus" into one supervised session: it plans the ingestion, writes and repairs the parsers against the actual files, verifies each phase, and freezes the result. Purposeful agentic choices throughout: agent-authored-then-frozen scripts (consistency + cost), human approval gates (controlled consequential actions), verification gates per phase, and agentic retrieval at query time (the model decomposes questions and searches iteratively). Measured by the evaluation protocol in §5.
4. **Can another person reproduce the result?** Yes — public corpus shipped/fetchable, docker-compose Postgres, pinned dependencies, exact commands for baseline, solution, and eval, plus a deterministic fallback path (the frozen scripts in `templates/`) for judges who don't run Claude Code. See §7.

---

## 2. Rubric alignment map

| Criterion (pts) | Where this plan earns it |
|---|---|
| Problem & User Value (15) | §1 problem statement; hallucination + pushback-flipping is concrete, personally observed, and demonstrated live in the eval. |
| Agent Solution & Engineering (30) | Installer-skill architecture (§4, §6): agent-written frozen pipelines, plan→approve→execute ingestion, verification gates, agentic retrieval, MCP portability. Every design choice traces to a reason in the decision log. |
| End-to-End Quality (20) | One realistic execution end-to-end: point skill at folder → approved plan → built stack → cited answers. Polished README, clean cited output a person would sign. |
| Measured Improvement (15) | §5: fixed 15-case eval set, fair no-retrieval baseline, eval re-run after every quality layer; changelog rows carry the numbers. |
| Reproducibility (15) | §7: clean-environment repro guide, public corpus, pinned versions, exact commands, expected outputs, runtime + cost. |
| Hot Take (5) | Candidate insights collected in `CHANGELOG.md` as they occur; leading candidate: what grounding does to answer *stability under challenge*, not just accuracy. |

---

## 3. Decision log

### Carried from v1 (see `docs/PLAN-v1-original.md` for full reasoning)

- **D1** Geo integration out of v1.
- **D2/D3** Lexical-graph hybrid is the long-term shape; graph layer deferred; schema reserves `entity`/`mention`/`entity_relation`.
- **D4** Domain-agnostic grounding system, not a book-graph product.
- **D5** Honest calibration: Type 1 (lookup) questions ≈ eliminated hallucination; Type 2 (judgment) questions get better ingredients, synthesis still the model's own.
- **D6** Postgres + pgvector, not Neo4j.
- **D7** One database, many domains (`domain` column).
- **D8** Retrieval is an MCP server, not a skill; agentic retrieval is the point.
- **D9** Query reformulation at two layers (server-side rewriting/HyDE + agent-side decomposition).
- **D10** Ingestion intelligence is build-time: agent writes scripts, then freezes them.
- **D11** One installer skill drives the whole build, with STATE.md checkpoints and human gates.
- **D12** Multi-format; folder is the unit; tabular routed away from the prose pipeline.
- **D13** Clone-and-run skill repo with template copy-back.

### New in v2 (hackathon alignment)

**D14 — The installer skill is the product; the stack is the evidence.**
The submission narrative, demo, and video center on the skill executing a build. Judges reproduce by running the skill (primary path) or the frozen scripts (fallback path). This is the innovation claim: not "another RAG stack" but "an agent that manufactures grounded-retrieval stacks from raw folders."

**D15 — Evidence-first: the eval set exists before the stack does.**
The eval corpus, question set, and scoring rubric are fixed in Phase 0, before any building. The same eval runs at every checkpoint (baseline → vector-only → hybrid → rewriting → agent instruction → final). **The phase evals ARE the improvement changelog** — each quality layer becomes a changelog row with before/after numbers. Experiments that don't move the numbers get recorded and removed, as the brief asks.

**D16 — Baseline definition.**
The baseline is: **the same model, same settings, one direct prompt with basic instructions, no retrieval tool**, answering the same 15 questions. This matches the brief's first suggested baseline form ("one direct prompt with basic instructions") and is fair: identical model, identical questions, identical scoring; the only delta is the solution's retrieval stack. Any resource difference (the solution also spends embedding + rewrite-model tokens) is disclosed in the results.

**D17 — Metric suite.**
- **Primary metric: grounded factual accuracy** — per-question score against ground truth extracted from the corpus (2 = correct + complete on specifics, 1 = partially correct, 0 = wrong or fabricated), summed over the case set.
- **Secondary: citation correctness** — for the solution only: does the cited source + location actually contain the claim? (n/a for baseline, which cannot cite.)
- **Secondary: false-grounding / abstention** — on trap questions whose answers are NOT in the corpus (and not reliably in the model), does the system say "not found" rather than confabulate? Scored for both baseline and solution.
- **Secondary (headline candidate): pushback stability** — after each factual answer, a scripted identical challenge: *"Are you sure? I've read sources saying the opposite."* Score: does the answer survive (holds with justification) or flip (retracts/reverses a previously correct answer)? Baseline flip-rate vs. grounded flip-rate. This operationalizes the owner's founding observation.
- **Brief-format extras:** human time per task (find + verify an answer manually in the corpus vs. via the tool) and cost per task (tokens + embedding spend), reported in the brief's three-row table.

**D18 — The eval corpus must be public, obscure-in-the-sweet-spot, and dense with specifics.**
- *Public/openly licensed:* judges must legally receive or fetch it (ground rules 7 & 10); the owner's personal library of copyrighted books is for private use after the hackathon, never in the submission.
- *Sweet-spot obscurity:* too famous → baseline already correct, no measurable lift; too unknown → the model honestly abstains, which is not hallucination, and the gap shrinks. The target is a field where the model has **partial, confident-but-shaky knowledge** — it attempts answers and errs on specifics.
- *Dense with specifics:* dates, figures, names, section numbers, parameter values — the things models confabulate most measurably.
- *Empirically verified, not guessed:* Phase 0 includes an **obscurity probe** — ask the baseline model ~5 probe questions from each candidate field; select the field where it confidently errs rather than abstains or aces. The probe transcripts are kept as evidence.
- *Mixed formats:* the chosen corpus should include at least a PDF, an HTML/MD source, and a plain-text source, to exercise the multi-format pipeline (a CSV if naturally available; otherwise tabular stays deferred per D12).

**D19 — Phase 6 is replaced; Phase 7 is added.**
v1's "owner uses it for 1–2 weeks collecting fumbled questions" does not fit a hackathon and provides no baseline. Replaced by a final full-protocol evaluation + changelog write-up (new Phase 6) and a deliverables phase (new Phase 7: reproduction guide, trajectories, video). The long-run EVAL.md fumbled-questions practice remains the **post-hackathon** v2-prioritization mechanism, unchanged.

**D20 — Reproducibility artifacts are first-class.**
`docker-compose.yml` for Postgres+pgvector; pinned Python dependencies; `.env.example` (no secrets in repo — ground rule 8); a `REPRODUCE.md` written for a stranger in a clean environment with exact commands for setup, ingest, baseline run, solution run, and eval scoring, plus expected outputs, approximate runtime, and cost. Two reproduction paths: (a) primary — run the installer skill in Claude Code and watch it build; (b) fallback — run the frozen scripts directly, no Claude Code required, reaching the same stack and eval numbers.

**D21 — Trajectories are captured from day one.**
Representative Claude Code transcripts are saved for: (1) the skill executing a build phase (including a parser-fix iteration), (2) the scan→classify→plan→approve ingestion flow, (3) agentic retrieval answering an eval question with multiple `search_corpus` calls, (4) a human gate in action. Stored under `trajectories/` with a short index explaining what each shows.

---

## 4. System definition (v1 stack — carried, unchanged in essentials)

### 4.1 Components

1. **The installer skill** — SKILL.md phased build plan + `templates/` (frozen artifacts copied back after first clean build, per D13). This is the repo.
2. **The library** — Postgres + pgvector; paragraph chunks + embeddings + metadata (domain, source, chapter/section, pages); domains separated by a `domain` column.
3. **The intake desk** — frozen `ingest.py` + parser helpers implementing scan → classify → plan → **human approval** → execute, per-format pipelines.
4. **The search counter** — single-file MCP server (stdio) exposing `search_corpus(query, domain, k)` plus `list_domains()` / `list_sources(domain)`.

### 4.2 Reference schema (agent may refine, not simplify away)

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

Breadcrumb is **prefixed to chunk text before embedding** (located paragraphs retrieve better than orphaned ones).

### 4.3 Ingestion pipeline spec (what the frozen scripts must do)

**Step 0 — Scan & plan (per folder run):** recursive scan; classify by format; emit per-file plan (format, pipeline, expected structure, unhandled files with reasons — never silently drop). **HUMAN GATE** before execution.

**Prose pipeline** (pdf, epub, md, html, docx, txt): parse with richest location tracking the format offers → paragraph-level chunks (~200–500 words, merge tiny fragments, never split mid-paragraph, identical parameters across the domain) → breadcrumb built and prefixed → batched embedding → atomic insert (source + chunks, `tsv` populated, `file_hash` dedupe) → printed summary (chunks, coverage, anomalies).

**Tabular pipeline** (csv, xlsx): never through the prose pipeline. Option A (row → labeled sentence + breadcrumb, embed) and/or Option B (real tables + SQL-lookup tool) — decided only if the chosen eval corpus contains tabular files; otherwise deferred.

### 4.4 MCP server spec

Tool `search_corpus(query, domain, k=8)`:
1. **Rewrite:** cheap fast model expands query into 2–3 focused variants (synonyms, technical vocabulary); optional HyDE for judgment queries.
2. **Hybrid search:** per variant, vector (`embedding <=> $v`) + keyword (`tsv @@ query`) within `WHERE domain = $domain`; merge with reciprocal rank fusion; dedupe.
3. **Return:** top-k chunks with `text`, `breadcrumb`, `book`, `chapter`, `page_start`, `page_end`, score.

Config via environment variables (connection string, API keys). Single file if possible; stdio transport.

### 4.5 Agent-side instruction (added wherever the tool is used)

> For design/judgment questions, decompose into sub-topics and call search_corpus separately for each before answering. Cite source + location for every claim drawn from retrieval. If retrieval returns nothing relevant, say so rather than answering from memory as if grounded.

---

## 5. Evaluation & Evidence (new — this section wins or loses 30 points)

### 5.1 Corpus selection (Phase 0, Human Gate 0)

Selection criteria per D18: public/openly licensed · sweet-spot obscurity (verified by the obscurity probe) · dense with specifics · mixed formats · small enough to ingest in minutes, big enough that retrieval is non-trivial (~8–15 files).

Candidate fields to probe (owner picks the shortlist; probe picks the winner):

- **A. Niche historical domain with public-domain sources** (e.g., a regional/colonial-era history with digitized books on Internet Archive / Project Gutenberg). Models typically have partial, confidently wrong knowledge; dense in names/dates. Strong hallucination bait.
- **B. Niche public regulatory/technical documents** (e.g., a smaller country's public regulations, public standards circulars, aviation/maritime notices). Extremely dense specifics; verifiably public.
- **C. Post-cutoff recent technical material** (2026 releases, specs, RFCs). Guaranteed knowledge gap, but risk the model abstains instead of hallucinating — probe decides.
- **D. Obscure open-source project documentation** (a small real project the model half-knows).

### 5.2 Question set (fixed in Phase 0, frozen before building)

**15 cases**, written against the corpus with ground-truth answers + source locations recorded in `eval/questions.yaml`:

- **9 × Type 1 (lookup):** answer verifiably written in the corpus; specifics-heavy.
- **3 × Type 2 (judgment):** answer requires synthesizing multiple passages; scored on whether the ingredients used are real and cited (per D5, synthesis quality itself is noted, not the primary score).
- **2 × traps:** plausible questions whose answers are NOT in the corpus — measure false grounding / honest abstention.
- **1 × challenging case** (required by the brief): deliberately hard — e.g., an answer split across two sources, or one that contradicts the model's prior; what it reveals is written up.

**Pushback protocol:** for the 9 lookup cases (both baseline and solution), the answer is followed by the identical scripted challenge: *"Are you sure? I've read sources saying the opposite."* Outcome recorded as HOLDS / FLIPS.

### 5.3 Scoring rubric

| Dimension | Applied to | Scale |
|---|---|---|
| Factual accuracy (primary) | all 13 non-trap cases | 2 correct / 1 partial / 0 wrong-or-fabricated |
| Citation correctness | solution only, per cited claim | cited location contains claim: yes/no |
| Trap behavior | 2 trap cases | abstains honestly / confabulates |
| Pushback stability | 9 lookup cases | HOLDS / FLIPS |
| Human time per task | sampled | minutes to obtain + verify answer |
| Cost per task | all | tokens + embedding spend |

Scoring notes are written per case with the evidence quote; every claimed number in the report links to a transcript (ground rule 9).

### 5.4 Protocol fairness

Same model, same settings, same 15 questions, same scoring rubric for baseline and solution. Runs scripted where possible (a small `eval/run_eval.py` harness driving both conditions) so re-runs are cheap and judges can repeat them. Disclosed differences: the solution additionally consumes embedding + rewrite-model tokens (reported under cost per task).

### 5.5 Eval checkpoints = changelog rows

| Stage | What changes | Eval run |
|---|---|---|
| Baseline | direct prompt, no retrieval | full 15 + pushback |
| Iteration 1 (Phase 3) | vector-only `search_corpus` + citations | full |
| Iteration 2 (Phase 4a) | + keyword hybrid, rank fusion | full |
| Iteration 3 (Phase 4b) | + server-side rewriting (+ HyDE) | full |
| Iteration 4 (Phase 5) | + agent-side decomposition instruction | full |
| Final | everything that survived | full 15 + pushback + time/cost table |

Each row in `CHANGELOG.md`: what we tried and why → numbers → kept / revised / removed → learning. Layers that don't move the numbers are removed and the removal recorded (the brief explicitly rewards this).

---

## 6. Build phases (revised)

**Conventions (all phases):** `STATE.md` in the project root (current phase, verified facts, connection details, model + dimension, script versions); every session starts by reading it. Every phase ends with a verification step — do not advance until it passes. Human gates are explicit stops recorded in STATE.md. `CHANGELOG.md` is appended at every eval checkpoint. Trajectory transcripts saved per D21.

**Phase 0 — Corpus, eval set, baseline. (NEW — nothing is built before this.)**
HUMAN GATE 0: owner shortlists candidate fields (§5.1). Then: obscurity probe → field selected with evidence; corpus files collected with license notes (`corpus/SOURCES.md`); 15 questions + ground truth written and frozen; **baseline run executed and scored**.
Verify: baseline numbers recorded in CHANGELOG.md; corpus redistributable or fetchable by script.

**Phase 1 — Database.**
HUMAN GATE: Postgres location (docker-compose default), embedding model (sets vector dimension).
Then: compose file, pgvector, schema, fake-chunk round-trip by similarity and keyword.
Verify: round-trip query returns the row.

**Phase 2 — Ingestion scripts (agent writes, then freezes).**
Write `ingest.py` + parser helpers per §4.3 including scan→classify→plan. Test on the eval corpus itself (it is the small mixed folder).
HUMAN GATE 1: owner approves the generated ingestion plan.
HUMAN GATE 2: owner inspects ~20 random chunks across formats (clean text? correct breadcrumbs? sane locations?) and approves.
Fix iteratively until approved, then freeze; later changes only to repair a broken parse, permanently.
Verify: corpus fully ingested; summary matches the files' real structure.

**Phase 3 — MCP server, dumb version.** Vector-only + citations; wire into Claude Code MCP config.
Verify: three known-answer questions return correct passages with correct citations. **Then: full eval run → changelog Iteration 1.**

**Phase 4 — Quality layers, each proven separately.**
4a: hybrid + rank fusion → **full eval → Iteration 2.**
4b: server-side rewriting (+ HyDE) → **full eval → Iteration 3.**
A layer that doesn't improve the numbers is removed and the removal recorded.

**Phase 5 — Agent instruction.** Add §4.5 to the host instructions.
Verify: a judgment question triggers multiple distinct `search_corpus` calls and a cited answer. **Full eval → Iteration 4.**

**Phase 6 — Final evaluation + report. (REPLACES v1's 1–2-week usage period.)**
Full protocol including pushback and time/cost table; final vs. baseline comparison; complete CHANGELOG.md with the removed-experiment entries; main failure mode + hot take drafted from what actually happened.

**Phase 7 — Deliverables. (NEW)**
- `README.md`: intended user, bottleneck, value; labeled Improvement Changelog; main failure mode + hot take.
- `REPRODUCE.md`: clean-environment guide, exact commands (setup / ingest / baseline / solution / eval), data requirements, expected output, versions, runtime, cost. Both reproduction paths (skill-driven and frozen-script fallback).
- `trajectories/`: the four representative transcripts (D21) + index.
- Video (≤5 min): problem + baseline → one realistic execution start-to-finish → final comparison → changelog walkthrough → biggest-contribution change + one removed experiment. Script drafted from the changelog.

---

## 7. Ground-rules compliance checklist

| # | Rule | How we comply |
|---|---|---|
| 1–2 | Known tools; declare pre-existing vs. added | Pre-existing: Claude Code, Postgres, pgvector, embedding APIs, MCP SDK, v1 plan document (archived in `docs/`). Added: everything in this repo. |
| 3 | Licenses & ToS | Corpus license notes in `corpus/SOURCES.md`; standard OSS deps. |
| 4–5 | Consequential actions controlled; human reviewer | Ingestion runs only after explicit human approval of the plan; all writes are to a local sandboxed database; human gates at every phase. |
| 6–7 | Legal/ethical; shareable data | Public/openly licensed corpus only (D18); no personal data. |
| 8 | No credentials in submission | `.env.example` pattern; secrets never committed. |
| 9 | Claims tied to evidence | Every eval number links to a stored transcript; scoring notes quote the evidence. |
| 10 | Judges can reproduce | §5.4 scripted harness + `REPRODUCE.md` + fallback path (D20). |

---

## 8. Explicitly OUT of the hackathon scope (carried from v1 §6, plus)

- Geo integration; entity/mention/relation graph layer (schema space reserved); reranking stage; Agent SDK wrapper / Open WebUI app / cron; orchestration frameworks; Neo4j — all per v1.
- The owner's private copyrighted library — post-hackathon use only.
- The 1–2-week fumbled-questions period (`EVAL.md`) — post-hackathon v2-prioritization mechanism.
- Tabular strategy decision — only if the chosen corpus naturally contains CSV/XLSX.

## 9. Open items for the owner (Gate 0 and Phase 1 gates)

1. **Corpus field shortlist** (§5.1 A–D or your own) — the obscurity probe makes the final pick, but the shortlist is yours. Everything downstream (questions, demo, video) depends on this.
2. **Postgres location** — proposed default: docker-compose (best for reproducibility); confirm or override.
3. **Embedding model** — sets `vector(N)`; consider cost and availability for judges reproducing.
4. **Cheap rewrite model** — small/fast, called on every search.
5. Confirm the pushback challenge phrasing (§5.2) or supply your own — it must stay identical across all runs.
