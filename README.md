# rag-stack-builder

**An agent that turns any folder of documents into a citation-backed grounding
library for AI — and proves it with a before/after exam.**

Submission for the micro1 Agentic Workflows Hackathon.

---

## Who has this problem, and what's the bottleneck?

Anyone doing sustained knowledge work with an LLM inside a domain the model
only half-knows — niche, regional, historical, or specialized material. The
owner's own experience prompted this project: in such domains, frontier models
answer fluently and wrongly, and worse, **fold under pushback** — challenge a
correct answer and the model apologizes and reverses it.

Our baseline measurement made the problem concrete (details below): asked 15
questions about colonial-era Northern Nigeria, a strong open frontier-class
model **fabricated specifics in most lookups, invented verbatim quotes from
the exact books on our shelf, retracted 2 of its 3 correct answers under a
single generic challenge — and confidently defended 5 wrong ones.**

The known fix is retrieval over a curated corpus. The bottleneck is that
building a good retrieval stack per corpus — parsers for messy real files,
consistent chunking, hybrid search, citations to page level, host wiring — is
days of specialist work, so nobody does it for their personal projects.

## What we built: the installer skill is the product

`rag-stack-builder` is an [Agent Skill](SKILL.md) for Claude Code. Point it at
a folder and it:

1. **Scans and classifies** every file (PDF/HTML/OCR-text/…), produces a
   per-file ingestion plan — flagging duplicates and unsupported files with
   reasons — and **stops for human approval**;
2. **Runs frozen per-format pipelines** (written and battle-tested by the
   agent during this project, then frozen): paragraph chunking with location
   breadcrumbs, batched embeddings, atomic inserts into Postgres+pgvector;
3. **Exposes retrieval as a single-file MCP server** — `search_corpus(query,
   domain, k)` with hybrid vector+keyword search and citations down to page
   numbers — usable from Claude Code, Claude.ai, or any MCP host. The
   decompose-and-cite agent instruction ships inside the server, so every
   host inherits grounded behavior.

The stack this skill builds during the demo is the evidence that the skill
works — measured by the evaluation below.

## Measured improvement (the exam)

Frozen 15-case set (9 lookups, 3 judgment, 2 traps whose answers are NOT in
the corpus, 1 two-source challenge) over a 5-source public-domain corpus;
ground truth quoted verbatim from the sources. Same model
(`deepseek-v4-pro:0813`), same questions, same scripted pushback ("Are you
sure? I've read sources saying the opposite.") in both conditions. Protocol:
[PLAN.md §5](PLAN.md); transcripts and per-case scoring: `eval/runs/`.

| Metric | Baseline (no retrieval) | Final (built stack) |
|---|---|---|
| Grounded factual accuracy (13 cases, max 26) | 11/26 (42%) | **26/26 (100%)** |
| Lookups fully correct | 1/9 | **9/9** |
| Traps answered honestly | 1/2 | **2/2** |
| Correct answers retracted under pushback | 2 of 3 | **0 of 9** |
| Fabricated attributions to named sources | 7 of 15 cases | **0** (12/12 quote audit vs. retrieval logs) |
| Ground-truth chunk retrieval MRR | — | 0.733 (vector) → **0.900** (hybrid) |
| Human time per answer verified | manual source-diving | citation → page, seconds |
| Model cost per full eval run | ~43K tokens | ~144K tokens |

The pushback inversion is the headline: ungrounded, the model retracts true
answers and defends false ones; grounded, it quotes the source back and holds
— 0 flips in 9. Twice it surfaced the corpus's own internal conflicts (two
books disagree on Kano's wall perimeter) with a citation for each side.

## Improvement Changelog

The full labeled changelog — baseline → vector RAG → hybrid (kept, with the
silent-no-op bug it exposed) → query rewriting (**removed**, with evidence) →
agent-side decomposition — lives in [CHANGELOG.md](CHANGELOG.md). Every row
carries its numbers and links to transcripts.

## Main failure mode

Retrieval recall of *low-salience, single-line facts*: one lookup's exact
ground-truth sentence (a passing diary line about selling a shilling for
cowries) never surfaced in the top-8 under any retrieval config — the system
answered correctly only because a more prominent passage carried the same
fact, and under pushback it correctly confessed the distinction. A fact that
exists only once, in passing, in a low-signal chunk is still hard to
guarantee. (Logged in CHANGELOG Iteration 2; candidate v2 fix: reranking.)

## Hot take

**Hallucination's scariest form is not wrong facts — it's fabricated
receipts, and you can't see it without an eval that checks the receipts.**
Our ungrounded baseline didn't just err; it invented verbatim quotes from the
very books on our shelf and cited real page-shaped locations. And our own
pipeline had the mirror-image lesson: the hybrid-search layer silently
contributed *nothing* for a full iteration (AND-semantics keyword matching
returned zero rows on question-length queries) while answer-level scores —
already at ceiling — showed nothing wrong. Both failures were invisible at
the level people usually measure, and obvious one level down. Build the
receipt-checking layer first: quote audits against retrieval logs, and
retrieval-rank probes per layer. That is what we'd carry into every agent we
build next.

## What existed before vs. what we added

**Pre-existing:** Claude Code, Postgres + pgvector, Voyage AI embeddings,
Ollama cloud models, the MCP Python SDK, public-domain corpus texts
(Internet Archive / Project Gutenberg), and the owner's design document
(archived unmodified at `docs/PLAN-v1-original.md`).
**Added during the hackathon:** everything else in this repository — the
skill, pipelines, server, schema, eval harness, all evaluation data and
documents.

## Repository map

| Path | What it is |
|---|---|
| `SKILL.md` | The installer skill (the product) |
| `PLAN.md` | Full design + decision log + eval protocol |
| `CHANGELOG.md` | The improvement changelog (brief deliverable) |
| `REPRODUCE.md` | Clean-environment reproduction guide |
| `ingest/`, `mcp_server/`, `db/` | The frozen stack templates |
| `eval/` | Frozen question set, harness, rank probe, all runs + scores |
| `corpus/` | Source manifest, licenses, fetch script (files not committed) |
| `trajectories/` | Representative agent trajectories |
| `STATE.md` | Build checkpoint log (gates, verifications, decisions) |

## Run it

See [REPRODUCE.md](REPRODUCE.md) — clean-environment setup, exact commands
for baseline, solution, and eval, expected outputs, runtime and cost.
