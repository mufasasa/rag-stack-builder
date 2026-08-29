# STATE.md — build checkpoint

**Read this first in every session. Resume, never re-derive.**

## Current phase

**Phase 0 — Corpus, eval set, baseline.** Started 2026-08-29.

- [x] 0.1 Verify availability + license of candidate sources; record in `corpus/SOURCES.md` — DONE 2026-08-29 (all key titles verified on archive.org / Gutenberg; downloads pending, see Blockers)
- [x] 0.2 Obscurity probe — DONE 2026-08-29. **Depth field selected: colonial Northern Nigeria / Sokoto Caliphate** (nigeria 5/10 with 3/5 confident fabrications vs. polar 8/10). See `eval/probe/RESULTS.md`; transcripts in `eval/probe/results/`; first CHANGELOG.md entry written. Polar → generalization corpus #1; aviation reports → generalization corpus #2.
- [ ] 0.3 Collect the full depth corpus (~8–15 mixed-format files; Orr + Shaw already fetched — add Robinson's Hausaland, Barth volumes, Lugard report(s), 1–2 more; verify each in corpus/SOURCES.md)
- [ ] 0.4 Write and freeze the 15-question eval set + ground truth (`eval/questions.yaml`)
- [ ] 0.5 Run and score the baseline; record in `CHANGELOG.md`

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

- Postgres: not yet provisioned (Phase 1)
- Embedding dimension: 1024 (voyage-4)
- Required env vars (never committed): `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`, `DATABASE_URL`

## Blockers

None. (2026-08-29: owner added `OLLAMA_API_KEY` + `VOYAGE_API_KEY` and opened egress to archive.org / gutenberg.org / api.voyageai.com / ollama.com — all verified working.)

## Verified so far

- Candidate sources for both depth fields exist, are public domain, and are hosted on archive.org / Gutenberg — see `corpus/SOURCES.md` (2026-08-29).
- Ollama cloud chat API works (`deepseek-v4-pro:0813`, `gpt-oss:20b` smoke-tested); Voyage `voyage-4` embeddings API works; corpus-site egress open (2026-08-29).
