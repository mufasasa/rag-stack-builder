#!/usr/bin/env python3
"""Citation audit for this run: verify every load-bearing quoted claim in the
answers appears verbatim in the retrieval log stored with the transcript."""
import json

CHECKS = {
  "Q1": ["hoisted at Lokoja in place of the Company"],
  "Q3": ["eleven miles", "double ditch"],
  "Q5": ["amounted to about 10,000 men"],
  "Q6": ["bucklers"],
  "Q7": ["two thousand cowries"],
  "Q8": ["certainly not above the truth"],
  "Q9": ["407 miles"],
  "Q10": ["practically no defence"],
  "Q11": ["commerce and manufactures go hand in hand"],
  "Q12": ["strenuous spirit of heroism"],
  "Q14": ["basis for the discussion"],
}
failed = 0
for qid, needles in CHECKS.items():
    d = json.load(open(f"{qid}.json"))
    corpus_text = " ".join(h["text"] for h in (d.get("retrieval") or []))
    for n in needles:
        ok = n.lower() in corpus_text.lower()
        failed += (not ok)
        print(f"{qid}: {'FOUND' if ok else 'MISSING'}: \"{n}\"")
print("AUDIT", "PASSED" if not failed else f"FAILED ({failed})")
