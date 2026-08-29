# STATE.md — build checkpoint

**Read this first in every session. Resume, never re-derive.**

## Current phase

**Phase 0 — Corpus, eval set, baseline.** Started 2026-08-29.

- [x] 0.1 Verify availability + license of candidate sources; record in `corpus/SOURCES.md` — DONE 2026-08-29 (all key titles verified on archive.org / Gutenberg; downloads pending, see Blockers)
- [x] 0.2 Obscurity probe — DONE 2026-08-29. **Depth field selected: colonial Northern Nigeria / Sokoto Caliphate** (nigeria 5/10 with 3/5 confident fabrications vs. polar 8/10). See `eval/probe/RESULTS.md`; transcripts in `eval/probe/results/`; first CHANGELOG.md entry written. Polar → generalization corpus #1; aviation reports → generalization corpus #2.
- [x] 0.3 Depth corpus collected — DONE 2026-08-29: 6 files, 3 formats (Orr PDF+txt, Shaw txt, Robinson txt, Morel txt, Barth Gutenberg HTML) via `corpus/fetch.sh`. Note for Phase 2: Orr exists as both PDF and txt of the same work — the ingestion planner must flag the duplicate (deliberate demo of the plan gate).
- [x] 0.4 15-question eval set FROZEN — DONE 2026-08-29: `eval/questions.yaml` (9 lookup / 3 judgment / 2 traps / 1 two-source challenge), all ground truth quoted from corpus files; trap absences verified (a Shaw-Burmi trap was discarded because Shaw does mention Burmi — recorded here so the check isn't redone).
- [x] 0.5 Baseline run + scored — DONE 2026-08-29: grounded accuracy 11/26 (42%), 1/9 lookups fully correct, 1/2 traps honest, 2/3 correct answers flipped under pushback, fabricated attributions in 7/15 cases. `eval/runs/baseline/baseline-2026-08-29/` (SCORES.md + transcripts). CHANGELOG.md updated.

**PHASE 0 COMPLETE.**
**PHASE 1 COMPLETE (2026-08-29):** schema applied, fake-chunk round trip verified by similarity and keyword.
**PHASE 2 in progress:** scripts written and dry-tested (parser fix recorded: PDF header-dropper ate CHAPTER lines). HUMAN GATE 1 answered 2026-08-29: plan approved, Orr ingested as PDF (page citations), txt twin skipped as duplicate. Ingestion running (free-tier Voyage rate limits → small batches, patient 429 retry). Next: HUMAN GATE 2 (owner inspects ~20 random chunks), then freeze scripts.

## Settled decisions (do not re-litigate; reasoning in PLAN.md §3, §9)

| Item | Decision |
|---|---|
| Product framing | Installer skill is the product; built stack is the evidence (D14) |
| Evaluation | Two-level: depth (15-case grounding eval, primary) + breadth (2 generalization builds + smoke tests) (D15, D22) |
| Baseline | Same model, one direct prompt, no retrieval, same 15 questions (D16) |
| Depth-field candidates | Northern Nigeria/Sokoto colonial history vs. forgotten polar expeditions — probe decides (§9.1) |
| Breadth corpora | The two non-winning fields; aviation accident reports bring a CSV (tabular pipeline) |
| Postgres | docker-compose, `pgvector/pgvector:pg17` |
| Embedding | Voyage `voyage-4`, dim 1024, `input_type` document/query, cosine |
| Rewrite model | `gpt-oss:20b` via Ollama cloud (owner switched providers 2026-08-29) |
| Answering model (eval) | `deepseek-v4-pro:0813` via Ollama cloud, identical settings both conditions |
| Pushback phrasing (frozen) | "Are you sure? I've read sources saying the opposite." |

## Environment / connections

- Postgres: LOCAL Postgres 16.13 + postgresql-16-pgvector (sandbox has no Docker daemon; db/docker-compose.yml with pgvector/pg17 is the judges' path — same schema). DB raglib, user rag, localhost:5432. Schema applied from db/schema.sql; round-trip verified 2026-08-29 (cosine 0.994 + tsv rank both returned the fake chunk).
- Embedding dimension: 1024 (voyage-4)
- Required env vars (never committed): `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`, `DATABASE_URL`

## Blockers

None. (2026-08-29: owner added `OLLAMA_API_KEY` + `VOYAGE_API_KEY` and opened egress to archive.org / gutenberg.org / api.voyageai.com / ollama.com — all verified working.)

## Verified so far

- Candidate sources for both depth fields exist, are public domain, and are hosted on archive.org / Gutenberg — see `corpus/SOURCES.md` (2026-08-29).
- Ollama cloud chat API works (`deepseek-v4-pro:0813`, `gpt-oss:20b` smoke-tested); Voyage `voyage-4` embeddings API works; corpus-site egress open (2026-08-29).
