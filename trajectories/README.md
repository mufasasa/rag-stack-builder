# Agent trajectories — index

Representative trajectories for every agent role in this project (hackathon
deliverable 04). The build was executed by Claude Code driving the repo's
tooling; each entry shows instructions → actions → tool responses → outcome.

| Trajectory | What it shows |
|---|---|
| `phase5-agentic-decomposition.md` | The retrieval agent at work over real MCP: a judgment question decomposed into 3 focused `search_corpus` calls, complementary passages from 4 sources, fully cited synthesis with a corpus-boundary disclaimer. |
| `build-parser-fix.md` | The installer agent's write→test→fix loop on the frozen pipeline: the PDF running-header bug (17 chapters collapsed to 5), diagnosis, fix, re-verification — the "agent fixes the pipe, not the file" principle live. |
| `../eval/probe/results/*.json` | The baseline model's raw probe transcripts (10 questions, both candidate fields) — the evidence behind the corpus-field decision. |
| `../eval/runs/baseline/baseline-2026-08-29/*.json` | Baseline exam: 15 cases + 9 pushbacks, full request/response records including the fabricated-quote retraction (Q8) and the confident wrong holds. |
| `../eval/runs/solution/iter1-vector-2026-08-30/*.json` | Grounded exam, same cases: each transcript includes the retrieval log (what the tool returned) so every citation is auditable (`audit_quotes.py`). |
| `../eval/runs/solution/iter2-hybrid-2026-08-30/*.json` | Same, under the hybrid default that survived the rank probe. |

Human checkpoints (gates) and their recorded answers are in `../STATE.md`;
retries and failures (Voyage 429 walls, the twice-restarted ingestion, the
hybrid no-op discovery) are preserved in the commit history and CHANGELOG.
