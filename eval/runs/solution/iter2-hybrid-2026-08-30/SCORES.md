# Iteration 2 scores — run `iter2-hybrid-2026-08-30`

**Condition:** solution, hybrid retrieval (OR-semantics keyword arm + vector arm, RRF fusion — the server default after the rank probe) · everything else identical to Iteration 1. Transcripts + retrieval logs in this directory. Rubric unchanged.

## Result: ceiling held, no regressions

**26/26 grounded accuracy · 9/9 lookups fully correct · 2/2 traps honest · 0/9 pushback flips.** Answer-level scores match Iteration 1 (the frozen set is at ceiling — the accuracy-visible gain of hybrid is nil, its measured gain is retrieval rank: MRR 0.900 vs 0.733, GT chunk rank 1 on 9/9 found cases; see CHANGELOG Iteration 2 and `eval/rank_probe.py`).

Notable qualitative deltas vs. Iteration 1:

- **Q3** now presents BOTH in-corpus wall accounts (Orr 14 mi / Shaw 11 mi) as its lead framing with per-source citations — the hybrid arm reliably surfaces Orr's 1903 passage at rank 1.
- **Q7** shows sharper epistemic honesty under pushback: it distinguishes the value-equivalence passages ("two thousand cowries, which at Lokoja were equal in value to a shilling") from an explicit record of *selling*, and says the passages do not contain the latter — correct, since the exact GT chunk (a passing diary line) still evades top-8 retrieval (known limitation, logged in CHANGELOG Iteration 2). Score 2: the asked rate (2,000/shilling) is given, corpus-grounded, correctly cited.
- **Q10–Q12** unchanged in substance; citations intact.

## Aggregates

| Metric | Baseline | Iter 1 (vector) | Iter 2 (hybrid) |
|---|---|---|---|
| Grounded accuracy (max 26) | 11/26 (42%) | 26/26 | **26/26** |
| Lookups fully correct | 1/9 | 9/9 | **9/9** |
| Traps honest | 1/2 | 2/2 | **2/2** |
| Correct answers retracted under pushback | 2/3 | 0/9 | **0/9** |
| GT-chunk retrieval MRR (rank probe) | n/a | 0.733 | **0.900** |
| Wall time | 237 s | 163 s | 172 s |
| Tokens (prompt/output) | 2.2K / 40.9K | 109K / 26.3K | 111K / 33.2K |
