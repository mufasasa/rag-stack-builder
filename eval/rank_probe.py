#!/usr/bin/env python3
"""Retrieval-rank probe: for each lookup case, the rank (1-based, within top-8)
of the first chunk containing the ground-truth evidence, under each retrieval
config. This is the metric that judges Iterations 2-3 once answer accuracy is
at ceiling (see CHANGELOG Iteration 1 caveat)."""
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "mcp_server"))
import server  # noqa: E402

# distinctive substring of each case's GT evidence as it appears in chunk text
NEEDLES = {
    "Q1": "hoisted at Lokoja",
    "Q2": "700 men of the West African Frontier Force",
    "Q3": "40 feet thick at the base",
    "Q4": "two head slaves",
    "Q5": "amounted to about 10,000 men",
    "Q6": "throwing their bucklers",
    "Q7": "shilling for two thousand cowries",
    "Q8": "certainly not above the truth",
    "Q9": "407 miles up the Niger",
    "Q15": "rather over one hundred thousand",
}
CONFIGS = [("vector", "vector", False), ("hybrid", "hybrid", False),
           ("hybrid+rewrite", "hybrid", True)]


def main() -> int:
    questions = {q["id"]: q for q in yaml.safe_load((HERE / "questions.yaml").read_text())}
    print(f"{'case':5} " + " ".join(f"{name:>15}" for name, _, _ in CONFIGS))
    totals = {name: [] for name, _, _ in CONFIGS}
    for qid, needle in NEEDLES.items():
        row = [f"{qid:5}"]
        for name, mode, rewrite in CONFIGS:
            hits = server.search_corpus_ex(questions[qid]["question"], "nigeria",
                                           8, mode=mode, rewrite=rewrite)
            rank = next((i + 1 for i, h in enumerate(hits)
                         if needle.lower() in h["text"].lower()), None)
            totals[name].append(rank)
            row.append(f"{('miss' if rank is None else 'rank ' + str(rank)):>15}")
        print(" ".join(row))
    print()
    for name, ranks in totals.items():
        found = [r for r in ranks if r]
        mrr = sum(1.0 / r for r in found) / len(ranks)
        print(f"{name:>15}: found {len(found)}/{len(ranks)} in top-8, MRR {mrr:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
