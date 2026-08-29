"""Paragraph-level chunking (PLAN.md §4.3): target 200–500 words, merge tiny
fragments, never split mid-paragraph, flush at chapter boundaries. Identical
parameters for every source in a domain — consistency beats cleverness."""

TARGET_MIN = 200
TARGET_MAX = 500
TINY = 30


def chunk_paragraphs(paragraphs: list, title: str) -> list:
    chunks, buf, words = [], [], 0

    def flush():
        nonlocal buf, words
        if not buf:
            return
        first = buf[0]
        breadcrumb = " › ".join(
            x for x in [title, first["chapter"], first["section"]] if x
        )
        pages = [p for par in buf for p in (par["page_start"], par["page_end"]) if p]
        chunks.append({
            "chapter": first["chapter"],
            "section": first["section"],
            "page_start": min(pages) if pages else None,
            "page_end": max(pages) if pages else None,
            "breadcrumb": breadcrumb,
            "text": "\n\n".join(par["text"] for par in buf),
        })
        buf, words = [], 0

    prev_key = None
    for par in paragraphs:
        n = len(par["text"].split())
        key = (par["chapter"], par["section"])
        if buf and key != prev_key and words >= TINY:
            flush()                     # chapter/section boundary
        if buf and words + n > TARGET_MAX and words >= TARGET_MIN:
            flush()
        buf.append(par)
        words += n
        prev_key = key
        if words >= TARGET_MIN and n > TARGET_MAX:
            flush()                     # oversized single paragraph stays whole
    flush()

    for i, c in enumerate(chunks):
        c["seq"] = i
    return chunks
