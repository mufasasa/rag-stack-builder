# Trajectory: the installer agent's write → test → fix loop (Phase 2)

**Date:** 2026-08-29 · **Agent:** Claude Code building the ingestion pipeline
per SKILL.md Phase 2 · distilled from the session; the verbatim numbers below
are from the actual tool outputs (also reflected in commit c7c2a64).

## 1. Write

The agent wrote `ingest/parsers.py` (OCR-txt, Gutenberg-HTML, PDF parsers),
`chunker.py`, `embedder.py`, `db.py`, `ingest.py` (scan→classify→plan→run).

## 2. Test (dry run on the real corpus, before any DB writes)

```
orr_...1911.txt   pars=1466 chunks=230 chapters=22 words min/med/max=30/427/547
orr_...1911.pdf   pars= 881 chunks=236 chapters= 5 words min/med/max=33/394/680
barth_...html     pars=2018 chunks=848 chapters=51 ...
```

**Anomaly detected by the agent:** the PDF twin of the same book yielded 5
chapters where the txt yielded 22.

## 3. Diagnose

The agent grepped the PDF's extracted text for CHAPTER lines:

```
(17, 'CHAPTER I') (17, 'CHAPTER II') ... ← table of contents, pages 17-19
(21, 'CHAPTER I') (41, 'CHAPTER II') (75, 'CHAPTER III') ... ← real chapters
total CHAPTER lines: 42
```

All headings present in the text — so the loss was in the parser. Root cause:
the running-header dropper removed each page's first line when it looked like
a header, and on chapter-opening pages the first line IS "CHAPTER N". The TOC
then set the chapter counter to XVII and nothing ever reset it: 854 of 881
paragraphs were labeled "Chapter XVII — Page".

## 4. Fix (permanent, per the freeze discipline)

Two changes to `parsers.py`: (a) never header-drop a line matching the
CHAPTER regex; (b) an `expect_title` flag so only the ALL-CAPS line
*immediately after* a chapter marker becomes its title (stray caps lines and
the TOC's "PAGE" column are noise). Applied to both the PDF and txt parsers.

## 5. Re-verify

```
orr_...1911.pdf   chunks=241 chapters=21   ← was 5
Q2 GT chunk -> Making of Northern Nigeria › Chapter VI — Events … 1903 …
               | pages 150 - 152
```

The ground-truth passage for eval case Q2 now lands in a correctly-located
chunk with real page numbers — the citation shape the whole project exists to
produce. The scripts were frozen at HUMAN GATE 2 with this fix inside; the
second domain (polar) later ingested with **zero** parser changes.
