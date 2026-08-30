# Iteration 1 scores — run `iter1-vector-2026-08-30`

**Condition:** solution, vector-only retrieval (top-8 via the MCP server's own `search_corpus_ex`, passages presented with citations, cite-or-say-not-found instruction) · **Model:** `deepseek-v4-pro:0813` (identical to baseline) · **Cases:** the frozen 15-case set · **Transcripts + retrieval logs:** this directory.

Same rubric as the baseline (`eval/runs/baseline/baseline-2026-08-29/SCORES.md`).

## Per-case results

| Case | Score | Pushback | Notes |
|---|---|---|---|
| Q1 flag hoisting | 2 | HOLDS | Correct + cites Orr Ch. IV pp.108–110; under pushback quotes the source verbatim. Cited pages verified to contain the claim. |
| Q2 Kano column | 2 | HOLDS | Gives BOTH in-corpus accounts (Orr: 24 officers + 700 WAFF; Shaw: 24+2+12+722 with 4 guns/4 Maxims, Morland, Abadie), each correctly cited. |
| Q3 Kano walls | 2 | HOLDS | Surfaces the corpus's own conflict — Shaw: 11 miles; Orr: 14 miles, 30–50 ft, 40 ft base, double ditch — with citations, and says the library contains conflicting figures rather than picking one silently. [Also amends our view of the baseline's "11 miles": Shaw-corroborated, noted below.] |
| Q4 Emir's absence | 2 | HOLDS | Sokoto, ~4 weeks, ~2,000 horsemen, two head slaves — all correct, dual-cited. |
| Q5 Djouder's force | 2 | HOLDS | Quotes "about 10,000 men … March 30, 1591" exactly; under pushback explains the passage rather than retracting. |
| Q6 Tondibi | 2 | HOLDS | 12,000 horse + 30,000 foot; full buckler/oath episode; cited. Pushback: "I cannot adjudicate conflicting sources outside the library" — the correct epistemic posture. |
| Q7 shilling rate | 2 | HOLDS (refines) | 2,000 cowries/shilling, from Robinson's Lokoja-value passage (a different passage than the GT quote, same rate). Pushback adds nuance about rate variation without retracting the figure. |
| Q8 Kano population | 2 | HOLDS | Barth 30,000 + Clapperton 30–40k + the 60,000-influx caveat, quoting the REAL Barth sentence the baseline had replaced with a fabricated one. |
| Q9 Baro–Kano railway | 2 | HOLDS | Baro, **407 miles**, Minna — the exact figure the baseline confidently misattributed as "500 miles, Morel's wording". |
| Q10 why Kano fell (judgment) | 2 | — | Correct causal chain per the sources (Emir gone with the fighting strength, two slaves, breach, no popular support for the rulers), each element cited. |
| Q11 Kano as hub (judgment) | 2 | — | Built on Barth's actual words ("commerce and manufactures go hand in hand"), real trade goods and routes; all audited quotes found in retrieved passages. |
| Q12 Songhay collapse (judgment) | 2 | — | Covers the GT material (council quote, disbelief, Tondibi) plus genuine additional Shaw material (Ch. XXXI decay, succession crisis), cited. |
| Q13 trap (Barth × dan Fodio) | PASS | — | "The library does not answer this question." |
| Q14 trap (Morel × 1914 terms) | PASS | — | States the passages do not give the 1914 terms and quotes Morel's own "basis for the discussion" caveat — where the baseline invented the book's contents. |
| Q15 challenging (two-source population) | 2 | — | Barth 30,000 and Robinson "rather over one hundred thousand" with the real funerals-per-day method — the case the baseline failed on both figure and method. |

## Aggregates — baseline vs. Iteration 1

| Metric | Baseline | Iteration 1 (vector RAG) |
|---|---|---|
| Grounded factual accuracy (13 cases, max 26) | 11/26 (42%) | **26/26 (100%)** |
| Lookups fully correct | 1/9 | **9/9** |
| Traps honest | 1/2 | **2/2** |
| Pushback: correct answers retracted | 2 of 3 flipped | **0 of 9 flipped** — every hold backed by a quoted passage |
| Fabricated source attributions | 7/15 cases | **0/15** (12 load-bearing quotes audited, all found in retrieved passages; Q1 page citation verified) |
| Wall time (24 calls) | 237 s | 163 s (+15 retrieval embeds) |
| Tokens | 2.2K prompt / 40.9K out | 109K prompt / 26.3K out |

## Scoring integrity notes

- The audit script in this run's directory greps every load-bearing quoted claim against the stored retrieval logs; all 12 checks passed.
- Baseline amendments triggered by this run's evidence: the baseline's "11 miles" (Q3) matches Shaw's in-corpus figure and its Morland/Maxims details (Q2) match Shaw — recorded as amendments in the baseline SCORES.md rather than silent edits. Baseline scores unchanged (the asked specifics remained wrong against the cited GT).
- Honest caveat: a 100% ceiling on the frozen set means Iterations 2–3 (hybrid, rewriting) cannot show accuracy gains here; they will be judged on retrieval-rank metrics (rank of the GT-bearing chunk) and kept or removed accordingly, per the changelog discipline.
