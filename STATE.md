# STATE.md — build checkpoint

**Read this first in every session. Resume, never re-derive.**

## Current phase

**Phase 0 — Corpus, eval set, baseline.** Started 2026-08-29.

- [x] 0.1 Verify availability + license of candidate sources; record in `corpus/SOURCES.md` — DONE 2026-08-29 (all key titles verified on archive.org / Gutenberg; downloads pending, see Blockers)
- [ ] 0.2 Obscurity probe: 5 questions per candidate field against the baseline model (ground truth quoted from actual downloaded sources, never from model memory); pick depth field; keep transcripts in `eval/probe/`
- [ ] 0.3 Collect the full depth corpus (~8–15 mixed-format files)
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
| Rewrite model | `claude-haiku-4-5` |
| Answering model (eval) | `claude-opus-5`, no refusal fallback inside eval |
| Pushback phrasing (frozen) | "Are you sure? I've read sources saying the opposite." |

## Environment / connections

- Postgres: not yet provisioned (Phase 1)
- Embedding dimension: 1024 (voyage-4)
- Required env vars (never committed): `ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`, `DATABASE_URL`

## Blockers (owner action needed — session environment settings)

1. **API keys:** no `ANTHROPIC_API_KEY` in this environment (test call returned 401) and no `VOYAGE_API_KEY`. Needed for the obscurity probe (0.2), baseline run (0.5), and all later phases. Add both as environment secrets.
2. **Network egress:** archive.org and gutenberg.org are blocked by the environment's network policy — corpus downloads (0.3) fail. Either allow those domains (plus api.voyageai.com for Phase 2) or the owner uploads the files. api.anthropic.com egress works (the 401 proves the call reached the API).

## Verified so far

- Candidate sources for both depth fields exist, are public domain, and are hosted on archive.org / Gutenberg — see `corpus/SOURCES.md` (2026-08-29).
- Anthropic API is reachable from this environment (auth missing, egress fine).
