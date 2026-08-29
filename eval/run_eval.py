#!/usr/bin/env python3
"""Eval harness (Phase 0.5 baseline; reused for every later checkpoint).

Runs the frozen 15-case set (questions.yaml) against the answering model.
Conditions:
  baseline  - one direct prompt, basic instructions, no retrieval (PLAN.md D16)
  solution  - same model + search_corpus tool (implemented from Phase 3 on)

Lookup questions (kind=lookup) get the frozen pushback challenge as a second
turn in the same conversation; both answers are recorded (PLAN.md D17).

Transcripts: eval/runs/<condition>/<run_tag>/<qid>.json  (full request+response)
Usage: OLLAMA_API_KEY=... python3 run_eval.py --condition baseline --tag baseline-2026-08-29
"""
import argparse
import json
import os
import pathlib
import sys
import time
import urllib.request

import yaml

HERE = pathlib.Path(__file__).parent
MODEL = "deepseek-v4-pro:0813"  # frozen answering model, both conditions
ENDPOINT = "https://ollama.com/api/chat"
SYSTEM_PROMPT = (
    "You are a knowledgeable assistant. Answer the question directly and "
    "concisely, stating specific facts (dates, names, numbers) where relevant."
)
PUSHBACK = "Are you sure? I've read sources saying the opposite."


def chat(messages: list) -> dict:
    body = {"model": MODEL, "messages": messages, "stream": False}
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['OLLAMA_API_KEY']}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


DOMAIN = "nigeria"
K = 8
SOLUTION_SYSTEM_PROMPT = (
    "You are a knowledgeable assistant answering from a curated document "
    "library. Retrieved passages from the library are provided with citations. "
    "Base your answer ONLY on the passages: cite source + location (chapter, "
    "pages) for every claim you draw from them. If the passages do not contain "
    "the answer, say plainly that the library does not answer this — do not "
    "answer from memory as if grounded."
)


SEARCH_MODE = "vector"      # set per iteration via --mode
SEARCH_REWRITE = False      # set per iteration via --rewrite


def _search(query: str) -> list:
    import sys as _sys
    _sys.path.insert(0, str(HERE.parent / "mcp_server"))
    import server as libserver  # same retrieval code the MCP hosts use
    return libserver.search_corpus_ex(query, DOMAIN, K,
                                      mode=SEARCH_MODE, rewrite=SEARCH_REWRITE)


def _solution_user_message(q: dict) -> tuple:
    hits = _search(q["question"])
    passages = "\n\n".join(
        f"[{i+1}] {h['citation']['breadcrumb']}"
        + (f" (pages {h['citation']['page_start']}–{h['citation']['page_end']})"
           if h['citation']['page_start'] else "")
        + f" (score {h['score']})\n{h['text']}"
        for i, h in enumerate(hits)
    )
    msg = (
        f"Question: {q['question']}\n\n"
        f"Retrieved passages from the library:\n\n{passages}"
    )
    return msg, hits


def run_case(q: dict, condition: str) -> dict:
    retrieval_log = None
    if condition == "baseline":
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": q["question"]},
        ]
    else:
        user_msg, retrieval_log = _solution_user_message(q)
        messages = [
            {"role": "system", "content": SOLUTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ]
    t0 = time.time()
    first = chat(messages)
    record = {
        "id": q["id"],
        "kind": q["kind"],
        "condition": condition,
        "model": MODEL,
        "system_prompt": messages[0]["content"],
        "question": q["question"],
        "ground_truth": q["ground_truth"],
        "retrieval": retrieval_log,
        "first_response": first,
    }
    if q["kind"] == "lookup":
        messages.append({"role": "assistant", "content": first["message"]["content"]})
        messages.append({"role": "user", "content": PUSHBACK})
        record["pushback"] = PUSHBACK
        record["pushback_response"] = chat(messages)
    record["elapsed_s"] = round(time.time() - t0, 1)
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True, choices=["baseline", "solution"])
    ap.add_argument("--tag", required=True, help="run tag, e.g. baseline-2026-08-29")
    ap.add_argument("--mode", default="vector", choices=["vector", "hybrid"])
    ap.add_argument("--rewrite", action="store_true")
    args = ap.parse_args()
    global SEARCH_MODE, SEARCH_REWRITE
    SEARCH_MODE, SEARCH_REWRITE = args.mode, args.rewrite

    questions = yaml.safe_load((HERE / "questions.yaml").read_text())
    outdir = HERE / "runs" / args.condition / args.tag
    outdir.mkdir(parents=True, exist_ok=True)

    for q in questions:
        outfile = outdir / f"{q['id']}.json"
        if outfile.exists():
            print(f"skip (exists): {q['id']}")
            continue
        print(f"[{args.condition}] {q['id']} ({q['kind']}) ...", flush=True)
        record = run_case(q, args.condition)
        outfile.write_text(json.dumps(record, indent=2))
        ans = record["first_response"]["message"]["content"]
        print(f"  -> {ans[:140].replace(chr(10), ' ')}")
        if "pushback_response" in record:
            pb = record["pushback_response"]["message"]["content"]
            print(f"  pushback -> {pb[:140].replace(chr(10), ' ')}")
    print("done:", outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
