"""Per-format parsers. Each parser yields paragraph dicts:
   {"chapter": str|None, "section": str|None, "page_start": int|None,
    "page_end": int|None, "text": str}
Formats covered in v1: OCR txt (archive.org djvu), Gutenberg HTML, scanned PDF
with OCR text layer (pypdf). EPUB/DOCX/MD arrive when a corpus needs them.
"""
import re
from collections import Counter

from bs4 import BeautifulSoup
from pypdf import PdfReader

CHAPTER_RE = re.compile(r"^\s*CHAPTER\s+([IVXLC]+|[0-9]+)\b[.\s]*(.*)$", re.IGNORECASE)


def _dehyphenate(text: str) -> str:
    return re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)


def _clean_ocr_spaces(text: str) -> str:
    return re.sub(r"[ \t]{2,}", " ", text)


def _is_noise_line(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if len(s) <= 3:                       # stray page numbers / marks
        return True
    if re.fullmatch(r"[0-9ivxlc.\s]+", s, re.IGNORECASE):
        return True
    return False


def parse_txt_ocr(path: str) -> list:
    """archive.org djvu OCR text: blank-line paragraphs, CHAPTER headings,
    running headers dropped by frequency. No reliable page numbers."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    raw = _dehyphenate(raw)
    blocks = re.split(r"\n\s*\n", raw)

    # running headers repeat many times (e.g. book title in caps) — count them
    shorts = Counter(
        b.strip() for b in blocks if 0 < len(b.strip()) < 60 and b.strip().isupper()
    )
    headers = {s for s, n in shorts.items() if n >= 3}

    paragraphs, chapter, expect_title = [], None, False
    for block in blocks:
        text = _clean_ocr_spaces(" ".join(block.split("\n"))).strip()
        if not text or text in headers:
            continue
        m = CHAPTER_RE.match(text)
        if m:
            chapter = f"Chapter {m.group(1).upper()}"
            rest = m.group(2).strip(" .")
            if rest and len(rest) < 80:
                chapter += f" — {rest.title()}"
                expect_title = False
            else:
                expect_title = True
            continue
        # the ALL-CAPS block directly after a chapter marker is its title;
        # other stray caps blocks (running headers, TOC columns) are noise
        if text.isupper() and len(text) < 80:
            if expect_title and chapter and text.upper() != "PAGE":
                chapter += f" — {text.title()}"
            expect_title = False
            continue
        expect_title = False
        if _is_noise_line(text):
            continue
        paragraphs.append(
            {"chapter": chapter, "section": None, "page_start": None,
             "page_end": None, "text": text}
        )
    return paragraphs


def parse_html_gutenberg(path: str) -> list:
    """Project Gutenberg HTML: h1-h4 headings become chapter/section; <p> are
    paragraphs; PG header/footer boilerplate stripped (per corpus/SOURCES.md
    license note the PG branding is removed and the source URL recorded)."""
    soup = BeautifulSoup(open(path, encoding="utf-8", errors="replace").read(), "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    paragraphs, chapter, section, in_body = [], None, None, True
    for el in soup.find_all(["h1", "h2", "h3", "h4", "p"]):
        text = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
        if not text:
            continue
        upper = text.upper()
        if "START OF THE PROJECT GUTENBERG" in upper:
            in_body, chapter, section = True, None, None
            paragraphs = []          # everything before the marker was front matter
            continue
        if "END OF THE PROJECT GUTENBERG" in upper:
            break
        if el.name in ("h1", "h2"):
            chapter, section = text[:120], None
            continue
        if el.name in ("h3", "h4"):
            section = text[:120]
            continue
        if in_body and len(text) > 1:
            paragraphs.append(
                {"chapter": chapter, "section": section, "page_start": None,
                 "page_end": None, "text": text}
            )
    return paragraphs


def parse_pdf(path: str) -> list:
    """Scanned PDF with OCR text layer. Real page numbers (PDF index, 1-based).
    Paragraph reconstruction heuristic: a paragraph ends when a line ends with
    terminal punctuation and is notably short (print's last-line signature)."""
    reader = PdfReader(path)
    paragraphs, chapter = [], None
    for pageno, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        lines = [ln.rstrip() for ln in text.split("\n")]
        # drop running header: first line, short, mostly caps/digits — but a
        # chapter-opening page has "CHAPTER N" as its first line: never drop that
        if (lines and len(lines[0]) < 60 and not CHAPTER_RE.match(lines[0].strip())
                and re.fullmatch(r"[A-Z0-9 .,'\-]+", lines[0] or " ")):
            lines = lines[1:]

        buf, expect_title = [], False
        for ln in lines:
            s = ln.strip()
            if _is_noise_line(s):
                continue
            m = CHAPTER_RE.match(s)
            if m:
                if buf:
                    paragraphs.append(_pdf_par(buf, chapter, pageno))
                    buf = []
                chapter = f"Chapter {m.group(1).upper()}"
                expect_title = True
                continue
            if s.isupper() and len(s) < 70:
                # the ALL-CAPS line directly after a chapter marker is its title;
                # any other stray caps line (running header, TOC column) is noise
                if expect_title and s.upper() != "PAGE":
                    chapter += f" — {s.title()}"
                expect_title = False
                continue
            expect_title = False
            buf.append(s)
            if re.search(r"[.!?][\"']?$", s) and len(s) < 45:
                paragraphs.append(_pdf_par(buf, chapter, pageno))
                buf = []
        if buf:
            paragraphs.append(_pdf_par(buf, chapter, pageno))
    return [p for p in paragraphs if p["text"]]


def _pdf_par(lines: list, chapter, pageno: int) -> dict:
    text = _clean_ocr_spaces(_dehyphenate("\n".join(lines)).replace("\n", " ")).strip()
    return {"chapter": chapter, "section": None, "page_start": pageno,
            "page_end": pageno, "text": text}


PARSERS = {
    "txt": parse_txt_ocr,
    "html": parse_html_gutenberg,
    "pdf": parse_pdf,
}
