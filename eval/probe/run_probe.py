#!/usr/bin/env python3
"""Obscurity probe runner (Phase 0.2).

Asks the baseline answering model each probe question with NO retrieval,
exactly as the eval baseline will be run (one direct prompt, basic
instructions). Saves full request/response transcripts to results/.

Usage: OLLAMA_API_KEY=... python3 run_probe.py [--model MODEL]
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.request

import yaml

HERE = pathlib.Path(__file__).parent
DEFAULT_MODEL = "deepseek-v4-pro:0813"
ENDPOINT = "https://ollama.com/api/chat"
SYSTEM_PROMPT = (
    "You are a knowledgeable assistant. Answer the question directly and "
    "concisely, stating specific facts (dates, names, numbers) where relevant."
)


def chat(model: str, question: str) -> dict:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "stream": False,
    }
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=DEFAULT_MODEL)
    args = ap.parse_args()

    questions = yaml.safe_load((HERE / "questions.yaml").read_text())
    outdir = HERE / "results"
    outdir.mkdir(exist_ok=True)

    for q in questions:
        outfile = outdir / f"{q['id']}.json"
        if outfile.exists():
            print(f"skip (exists): {q['id']}")
            continue
        print(f"asking {q['id']} ...", flush=True)
        resp = chat(args.model, q["question"])
        record = {
            "id": q["id"],
            "field": q["field"],
            "model": args.model,
            "system_prompt": SYSTEM_PROMPT,
            "question": q["question"],
            "ground_truth": q["ground_truth"],
            "evidence": q["evidence"],
            "response": resp,
        }
        outfile.write_text(json.dumps(record, indent=2))
        answer = resp.get("message", {}).get("content", "")
        print(f"  -> {answer[:160].replace(chr(10), ' ')}")

    print("done; transcripts in", outdir)


if __name__ == "__main__":
    sys.exit(main())
