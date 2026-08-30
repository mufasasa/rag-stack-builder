# Video script (≤5 minutes) — shot list and narration

Deliverable 03. Record a screen capture following this sequence; narration
beats are written to be read aloud (~140 wpm ≈ 4:45 total). Everything shown
is committed in the repo — no staging needed.

## 0:00–0:40 — The problem and the baseline

*Show:* `eval/runs/baseline/baseline-2026-08-29/Q8.json` (or SCORES.md row Q8).
*Say:* "I asked a frontier-class model about a niche field — colonial Northern
Nigeria. It answered fluently. Then I pushed back once: 'Are you sure?' It
invented a verbatim quote from a book on my shelf and retracted its own
CORRECT answer. Across fifteen questions with ground truth quoted from real
sources, it scored forty-two percent, fabricated citations in seven cases,
and retracted two of its three correct answers under one generic challenge.
That's the baseline: one direct prompt, no retrieval."

## 0:40–1:30 — The product: an installer skill

*Show:* `SKILL.md` frontmatter, then `corpus/files/nigeria/` folder listing.
*Say:* "The fix is grounding the model in a curated library — but building a
retrieval stack per corpus is days of specialist work. So the product here is
an agent that builds it for you. rag-stack-builder is a Claude Code skill:
point it at a folder of mixed documents — scanned PDFs, OCR text, HTML — and
it plans the ingestion, waits for your approval, and runs frozen pipelines it
wrote and debugged itself."

## 1:30–2:30 — One realistic execution, start to finish

*Show (terminal):* `python3 ingest/ingest.py plan corpus/files/polar --domain polar`
— point at the per-file plan and the duplicate warning in the nigeria plan
(`corpus/nigeria.plan.json`). Then the run summary from
`eval/runs/smoke/polar-2026-08-30/SCORES.md`: 1,341 chunks, zero parser
changes.
*Say:* "Here's the flow on a second, unrelated domain — polar expedition
memoirs. Scan, classify, plan: every file accounted for, duplicates flagged
for a human decision, nothing silently dropped. I approve; it ingests —
paragraph chunks, location breadcrumbs, embeddings, atomic inserts. First
domain: two fix iterations. Second domain: zero changes, one approval, done.
The intelligence was spent once, then frozen."

## 2:30–3:20 — The grounded answer, live

*Show:* an MCP host calling `search_corpus`, then the solution transcript for
Q9 (`eval/runs/solution/iter2-hybrid-2026-08-30/Q9.json`) and the Phase 5
trajectory (`trajectories/phase5-agentic-decomposition.md`).
*Say:* "Retrieval is one MCP tool any host can use. Same model, same
questions, now with the library: one hundred percent grounded accuracy, every
claim cited to source and page. Pushed back, it quotes the source and holds —
zero retractions in nine. Ask it something the library can't answer and it
says so. And on judgment questions it decomposes into focused searches —
here, three sub-queries pulled complementary passages from four different
books."

## 3:20–4:10 — The changelog: what earned its place

*Show:* `CHANGELOG.md` — scroll from baseline row to Final.
*Say:* "Every layer had to prove itself on the same fifteen cases. Vector
retrieval took accuracy to ceiling. Hybrid search looked like a no-op — and
it WAS one: keyword matching with AND semantics returned zero rows on real
questions, invisible in answer scores, caught only by a retrieval-rank probe.
Fixed, it took the ground-truth chunk to rank one across the board — kept.
Query rewriting made ranks WORSE, so it's gone; the changelog keeps the
removal and what it taught us. The biggest single contribution: retrieval
plus verifiable citations. The removed experiment: rewriting."

## 4:10–4:45 — Final comparison and the hot take

*Show:* README.md measured-improvement table.
*Say:* "Forty-two percent to one hundred. Seven fabricated citations to zero,
audited quote by quote against the retrieval logs. Two of three correct
answers retracted, to zero of nine. The hot take: hallucination's scariest
form is fabricated receipts — and both the model's failure and one of our own
pipeline's failures were invisible until we built the layer that checks
receipts. Build that layer first. Everything here — code, corpus fetcher,
eval harness, transcripts — is in the repo, reproducible from a clean
machine."

## Recording notes

- Terminal font large; have `README.md`, `CHANGELOG.md`, the two Q8/Q9
  transcripts, and `SKILL.md` open in tabs before recording.
- The plan/run commands can be shown against the polar domain without
  re-embedding (the run will print "skip (already ingested, hash match)" —
  itself a nice dedupe demo).
- If time runs over, cut section 3's trajectory beat first.
