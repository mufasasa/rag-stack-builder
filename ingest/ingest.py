#!/usr/bin/env python3
"""The intake desk (PLAN.md §4.3): scan → classify → plan → [HUMAN GATE] → run.

  python3 ingest.py plan <folder> --domain <name> [--out plan.json]
  python3 ingest.py run  <folder> --domain <name> --plan plan.json

`plan` is read-only: it scans the folder, classifies every file, probes its
structure, flags duplicates and unsupported formats, and writes plan.json for
the owner to approve/edit (set "action": "skip" to exclude a file).
`run` executes ONLY an approved plan: parse → chunk → breadcrumb → embed →
atomic insert, skipping file_hash duplicates, and prints a summary.
Never silently drop a file: everything appears in the plan with a reason.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

from parsers import PARSERS, parse_pdf  # noqa: F401
import chunker
import embedder
import db

SUPPORTED = {"txt": "prose-txt-ocr", "html": "prose-html", "pdf": "prose-pdf",
             "md": "prose-md (not yet implemented)", "epub": "prose-epub (not yet implemented)",
             "csv": "tabular (deferred, D12)", "xlsx": "tabular (deferred, D12)"}
IMPLEMENTED = {"txt", "html", "pdf"}


def file_hash(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def title_from_name(path: pathlib.Path) -> str:
    stem = re.sub(r"_(gutenberg|v?\d{4}|v\d+)", "", path.stem)
    return stem.replace("_", " ").title()


def probe(path: pathlib.Path, fmt: str) -> dict:
    try:
        if fmt == "pdf":
            from pypdf import PdfReader
            r = PdfReader(str(path))
            sample = (r.pages[len(r.pages) // 2].extract_text() or "").strip()
            return {"pages": len(r.pages), "text_layer": bool(sample),
                    "note": "OCR text layer present" if sample else "NO TEXT LAYER — needs OCR"}
        if fmt == "txt":
            text = open(path, encoding="utf-8", errors="replace").read()
            chapters = len(re.findall(r"^\s*CHAPTER\s+[IVXLC0-9]+", text, re.M | re.I))
            return {"bytes": len(text), "chapter_headings": chapters}
        if fmt == "html":
            text = open(path, encoding="utf-8", errors="replace").read()
            return {"bytes": len(text),
                    "headings": len(re.findall(r"<h[12]", text, re.I)),
                    "paragraph_tags": len(re.findall(r"<p[ >]", text, re.I))}
    except Exception as exc:  # a probe failure is plan information, not a crash
        return {"error": str(exc)}
    return {}


def cmd_plan(args) -> int:
    folder = pathlib.Path(args.folder)
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    entries = []
    for p in files:
        fmt = p.suffix.lstrip(".").lower()
        e = {"path": str(p.relative_to(folder)), "format": fmt,
             "title": title_from_name(p), "sha256": file_hash(p)}
        if fmt in IMPLEMENTED:
            e.update(action="ingest", pipeline=SUPPORTED[fmt], probe=probe(p, fmt))
        elif fmt in SUPPORTED:
            e.update(action="skip", pipeline=SUPPORTED[fmt],
                     reason=f"pipeline for .{fmt} not implemented in v1")
        else:
            e.update(action="skip", pipeline=None, reason=f"unsupported format .{fmt}")
        entries.append(e)

    # duplicate-work detection: same leading stem tokens in different formats
    by_stem = {}
    for e in entries:
        stem = "_".join(pathlib.Path(e["path"]).stem.split("_")[:2])
        by_stem.setdefault(stem, []).append(e)
    for stem, group in by_stem.items():
        if len(group) > 1:
            for e in group:
                e.setdefault("warnings", []).append(
                    f"possible duplicate of the same work as: "
                    + ", ".join(x["path"] for x in group if x is not e)
                    + " — ingesting both would double-count this text; keep ONE"
                )

    plan = {"domain": args.domain, "folder": str(folder), "files": entries}
    out = pathlib.Path(args.out)
    out.write_text(json.dumps(plan, indent=2))

    print(f"INGESTION PLAN — domain '{args.domain}', folder {folder}\n")
    for e in entries:
        line = f"  [{e['action']:6}] {e['path']}  ({e.get('pipeline') or 'n/a'})"
        if e.get("reason"):
            line += f"  reason: {e['reason']}"
        print(line)
        if e.get("probe"):
            print(f"           probe: {e['probe']}")
        for w in e.get("warnings", []):
            print(f"           WARNING: {w}")
    print(f"\nplan written to {out} — review, edit actions if needed, then run:")
    print(f"  python3 ingest.py run {folder} --domain {args.domain} --plan {out}")
    return 0


def cmd_run(args) -> int:
    folder = pathlib.Path(args.folder)
    plan = json.loads(pathlib.Path(args.plan).read_text())
    if plan["domain"] != args.domain:
        print(f"plan domain {plan['domain']!r} != --domain {args.domain!r}", file=sys.stderr)
        return 2
    conn = db.connect()
    totals = {"ingested": 0, "chunks": 0, "skipped_plan": 0, "skipped_dupe": 0}
    for e in plan["files"]:
        path = folder / e["path"]
        if e["action"] != "ingest":
            totals["skipped_plan"] += 1
            print(f"skip (plan: {e.get('reason','excluded')}): {e['path']}")
            continue
        if db.already_ingested(conn, e["sha256"]):
            totals["skipped_dupe"] += 1
            print(f"skip (already ingested, hash match): {e['path']}")
            continue
        print(f"ingesting {e['path']} ...", flush=True)
        paragraphs = PARSERS[e["format"]](str(path))
        chunks = chunker.chunk_paragraphs(paragraphs, e["title"])
        if not chunks:
            print(f"  ANOMALY: parser produced 0 chunks — investigate before re-running")
            continue
        embeddings = embedder.embed_chunks(chunks)
        source = {"domain": args.domain, "title": e["title"], "author": None,
                  "file_name": e["path"], "format": e["format"], "file_hash": e["sha256"]}
        sid = db.insert_source_with_chunks(conn, source, chunks, embeddings)
        totals["ingested"] += 1
        totals["chunks"] += len(chunks)
        chapters = len({c["chapter"] for c in chunks if c["chapter"]})
        pages = [c["page_end"] for c in chunks if c["page_end"]]
        print(f"  source id {sid}: {len(chunks)} chunks, {chapters} chapters"
              + (f", pages up to {max(pages)}" if pages else ", no page tracking (OCR txt)"))
    conn.close()
    print(f"\nSUMMARY: {totals}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("plan"); p1.add_argument("folder"); p1.add_argument("--domain", required=True)
    p1.add_argument("--out", default="plan.json"); p1.set_defaults(fn=cmd_plan)
    p2 = sub.add_parser("run"); p2.add_argument("folder"); p2.add_argument("--domain", required=True)
    p2.add_argument("--plan", required=True); p2.set_defaults(fn=cmd_run)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
