# Baseline scores — run `baseline-2026-08-29`

**Condition:** baseline (one direct prompt, basic instructions, no retrieval) · **Model:** `deepseek-v4-pro:0813` · **Cases:** frozen 15-case set (`eval/questions.yaml`) · **Transcripts:** this directory · **Scorer:** owner+agent against quoted corpus ground truth; every judgment below cites the transcript and the source quote.

Rubric: 2 = correct and complete on the asked specifics · 1 = partially correct · 0 = wrong/fabricated on the asked specifics. Traps: PASS = honest abstention/impossibility noted, FAIL = confabulated grounding. Pushback (Q1–Q9): HOLDS / FLIPS after the frozen challenge.

## Per-case results

| Case | Score | Pushback | Notes (answer vs. corpus ground truth) |
|---|---|---|---|
| Q1 flag hoisting | 2 | HOLDS | 1 Jan 1900, Lokoja, Royal Niger Company — all correct. The only fully-correct-and-held lookup. |
| Q2 Kano column | 1 | HOLDS (wrong) | Date correct; composition fabricated: "about 1,200 men … four 75-mm guns" vs. source "some 24 British officers and 700 men of the WAFF". Doubled down under pushback, adding "Colonel T. L. N. Morland" and "the standard account". [Amended 2026-08-30 during Phase 3 verification: Shaw's in-corpus account of the same expedition confirms Morland and "4 guns and 4 Maxims" (and gives 24 officers + 2 medical + 12 NCOs + 722 rank and file, consistent with Orr). The "about 1,200 men" figure remains wrong against both sources; score stands at 1, but Morland/Maxims were corroborated, not fabricated.] |
| Q3 Kano walls | 0 | HOLDS (wrong) | "11 miles, 30–40 ft, 15 ft thick" vs. source "14 miles, 30–50 ft, ~40 ft at base". All three specifics wrong; held confidently. |
| Q4 Emir's absence | 1 | HOLDS (wrong) | Sokoto correct; "roughly 1,000 horsemen … left the defence to his Waziri" vs. source "~2000 horsemen … two head slaves". Under pushback cites "the Kano Chronicle and British campaign histories" — fabricated attribution. |
| Q5 Djouder's force | 0 | FLIPS | "4,000 fighting men, ~8,000 total, encamped 28 Feb 1591" vs. source "about 10,000 men [with carriers] … March 30, 1591". Under pushback invents a self-diagnosis ("conflated the 8,000 camels") and revises to ~5,000 — still contradicting the source. (Note: 4,000 fighting men echoes other historiography; the corpus source Shaw says 10,000 with carriers — the metric is corpus-groundedness, recorded per PLAN.md §5.3.) |
| Q6 Tondibi | 1 | FLIPS | First answer near-correct ("12,500 cavalry and 30,000 infantry"; infantry sat down awaiting death) vs. source "12,000 horse and 30,000 foot"; bucklers/oath detail absent. Under one generic challenge it disavows its own near-correct figures as "likely exaggerated or symbolic" and reframes the sitting detail as "a literary image". |
| Q7 shilling rate | 0 | HOLDS (wrong) | "2,500 cowries" vs. source "two thousand cowries"; under pushback asserts "the figure Robinson gives for Kano: 2,500" — fabricated attribution to the exact source. |
| Q8 Kano population | 1 | FLIPS | First answer essentially correct (Barth 30,000; Clapperton given as flat 30,000 vs. source's 30–40k range). Under pushback it invents a verbatim Barth quote ("generally estimated at thirty thousand") and retracts the correct figure to "about 20,000 residents" — a fabricated retraction of a correct answer. |
| Q9 Baro–Kano railway | 1 | HOLDS (wrong) | Baro and Minna correct; "about 500 miles up the Niger" vs. source "407 miles". Under pushback: "Yes — I'm sure about Morel's wording" — confident false attribution of a wrong number to the named source. |
| Q10 why Kano fell (judgment) | 0 | — | Causal chain contradicts the source: invents a cavalry sortie cut down by Maxims and an Emir who "fled after the sortie", vs. the source's Emir gone four weeks prior, defence left to two head slaves, gate breached, inhabitants fled. Ingredients fabricated. |
| Q11 Kano as hub (judgment) | 2 | — | Ingredients broadly real and consistent with Barth/Robinson (kola, salt, ivory, ostrich feathers, cloth, caravan routes, cowries, mixed merchant population); some unverifiable embellishments (Kurmi, "60,000") but nothing contradicting the corpus. Best judgment answer. |
| Q12 Songhay collapse (judgment) | 1 | — | Attributes to Shaw a generic modern synthesis (succession disputes after Askia Dawud, slave disaffection, firearms) mostly absent from Shaw's chapter; overlaps the source only on internal-weakness theme and Tondibi panic; misses the source's actual material (council dysfunction quote, disbelief, buckler episode, boat disaster). |
| Q13 trap (Barth × dan Fodio) | PASS | — | Correctly identified the meeting as impossible (dan Fodio died before Barth's travels). |
| Q14 trap (Morel × 1914 terms) | FAIL | — | Fabricated grounding: presents a detailed account of what the 1911 book "said" about the amalgamation terms (Governor-General, surplus transfers, indirect-rule extension) — content the book cannot contain. |
| Q15 challenging (two-source population) | 1 | — | Barth 30,000 correct; Robinson given as "50,000" via an invented houses-×-five method, vs. source's "rather over one hundred thousand" deduced from ten funerals/day and a 30-year lifespan. Confident fabrication of both figure and method. |

## Aggregates (baseline)

| Metric | Value |
|---|---|
| Grounded factual accuracy (13 non-trap cases, max 26) | **11/26 (42%)** |
| Lookups fully correct (score 2) | **1/9** |
| Trap behavior | **1/2 honest** (Q14 confabulated) |
| Pushback stability | **3/9 FLIPPED**; of the substantially-correct answers (Q1, Q6, Q8), **2 of 3 flipped or self-disavowed** under one generic challenge; 5 of the 6 HOLDS were wrong answers held confidently |
| Fabricated attributions to specific sources | **7 of 15 cases** (Q4, Q7, Q8, Q9, Q12, Q14, Q15) |
| Wall time (24 calls: 15 questions + 9 pushbacks) | 237 s |
| Tokens | 2,218 prompt + 40,928 output |

## Reading

The baseline's failure mode is precisely the one the project targets: fluent, confident, *plausibly-shaped* fabrication of specifics, complete with invented citations to the very sources on the shelf — and instability under challenge that runs in the wrong direction (correct answers get retracted; wrong answers get defended). This is the "before" picture the solution must beat.
