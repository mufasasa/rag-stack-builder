# Obscurity probe — results and field selection

**Date:** 2026-08-29 · **Model:** `deepseek-v4-pro:0813` (Ollama cloud) · **Protocol:** one direct prompt, basic instructions, no retrieval — identical to the eval baseline condition. Full transcripts: `results/*.json`. Ground truth: quoted from downloaded source texts in `questions.yaml`.

## Scores

2 = correct on the asked specifics · 1 = partially correct · 0 = confidently wrong on the asked specifics. No answer abstained.

| ID | Field | Asked specifics | Model answer vs. source | Score |
|---|---|---|---|---|
| N1 | nigeria | Flag hoisting date/place/predecessor | 1 Jan 1900, Lokoja, Royal Niger Company — all correct | 2 |
| N2 | nigeria | 1903 Kano column composition + date | Date correct (29 Jan 1903); composition fabricated: "1,200 men … four 75-mm guns and four Maxim guns" vs. source's "some 24 British officers and 700 men of the West African Frontier Force" | 1 |
| N3 | nigeria | Kano wall perimeter/height/thickness | "11 miles … 30–50 ft … 15 ft thick" vs. source's "14 miles … 30 to 50 feet … about 40 feet thick at the base" — 2 of 3 specifics wrong, stated confidently | 0 |
| N4 | nigeria | Emir's whereabouts + horsemen count | "fled … roughly 300 horsemen" vs. source's "gone some four weeks previously … about 2000 horsemen" | 0 |
| N5 | nigeria | Ex-Sultan's death place/date | Burmi, July 1903 — correct (adds 27 July, consistent with source's "July 1903") | 2 |
| P1 | polar | Ninnis death date/cause/distance | 14 Dec 1912, crevasse, ~310 miles — matches source ("three hundred miles east") | 2 |
| P2 | polar | Ninnis's regiment | Royal Fusiliers — correct | 2 |
| P3 | polar | Lockwood farthest-north lat/long/flag | 83°24′ N, 40°46′ W, American flag — exact match | 2 |
| P4 | polar | Jeannette Havre departure + voyage length | "June 29, 1878 … 181 days" vs. source's "July 15, 1878 … a hundred and sixty-five days" — both specifics fabricated | 0 |
| P5 | polar | Why Aurora left five men | Search for Mawson's missing party — correct | 2 |

**Totals:** nigeria 5/10 (3 of 5 answers contain confident fabrications) · polar 8/10 (1 of 5).

## Verdict

**Depth corpus: colonial-era Northern Nigeria / Sokoto Caliphate.** The baseline model sits squarely in the hallucination sweet spot there: it never abstains, answers fluently, and fabricates specifics (force sizes, dimensions, counts) in 3 of 5 questions. The polar field is too well represented in the model's training (4/5 correct, including exact coordinates) and would understate the solution's measurable lift.

**Consequences (per PLAN.md §9):** the polar corpus (already fetched) becomes generalization-build corpus #1; historical aviation accident reports (with CSV data) become generalization-build corpus #2. P4-style errors show the polar smoke test will still be meaningful.

Also noted for the Hot Take file: the model's fabricated specifics are *plausibly shaped* (a real commander's name, realistic gun counts) — the failure mode is not ignorance but confident interpolation, which is invisible to a user without sources.
