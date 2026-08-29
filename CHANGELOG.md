# Improvement Changelog

Every meaningful experiment gets an entry: what we tried and why, the evidence
(same evaluation method wherever possible), and the decision or learning.
Format per the challenge brief. Baseline and iteration rows are appended as the
phases complete (PLAN.md §5.5).

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Pre-baseline: obscurity probe (Phase 0.2, 2026-08-29) | Before building anything, tested which candidate corpus field puts the baseline model (`deepseek-v4-pro:0813`, no retrieval) in the hallucination sweet spot — confident errors rather than abstention or mastery. 5 specifics-dense questions per field, ground truth quoted from the actual public-domain sources. | Nigeria field: 5/10, confident fabrications in 3/5 answers (invented force compositions, wall dimensions, horsemen counts). Polar field: 8/10, 1/5 fabricated. Zero abstentions in either field. `eval/probe/RESULTS.md`, transcripts in `eval/probe/results/`. | Selected colonial-era Northern Nigeria / Sokoto Caliphate as the depth corpus; polar becomes generalization corpus #1. Learning: the failure mode is confident interpolation of plausible-shaped specifics, not ignorance — exactly what citations are meant to expose. |
