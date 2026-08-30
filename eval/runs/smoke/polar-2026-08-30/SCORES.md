# Polar generalization build — smoke test scores

**Build (installer-level metrics, D22):** 3 files planned → approved (1 human
gate) → ingested with **zero parser changes and zero errors** on the frozen
scripts; 1,341 chunks across 3 sources; wall time 90 min (17:03–18:33 UTC,
entirely embedding-rate-bound on the free Voyage tier — the compute itself is
minutes). Compare build #1 (nigeria): 2 gates, 2 fix iterations (PDF
header-dropper, embedder pacing), spread over a day of rate-limit restarts.
The frozen-template payoff is exactly as designed (PLAN.md D10/D13).

**Smoke test (5 questions, ground truth quoted from the polar sources during
the Phase 0 probe):** run through the identical solution pipeline
(hybrid retrieval, domain='polar', cite-or-say-not-found).

| Case | Result |
|---|---|
| S1 Ninnis's death | ✓ 14 Dec 1912, crevasse, 300 miles east — cited |
| S2 Ninnis's regiment | ✓ Royal Fusiliers — quotes the source line |
| S3 Lockwood farthest north | ✓ 83°24′N 40°46′W, "the American flag (Mrs. Greely's)" — cited |
| S4 Jeannette Havre departure | ✓ **15 July 1878, 165 days** — the case the ungrounded model fabricated in the probe ("June 29… 181 days") |
| S5 Aurora leaves five men | ✓ search for Mawson's missing party — cited |

**5/5 correct with citations.** Transcripts with retrieval logs: this
directory.
