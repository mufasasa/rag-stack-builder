# Corpus sources — verification log

All works below were published before 1930 and are in the public domain in the US.
Verified via web search on 2026-08-29 (existence + hosting). Download is pending:
this session's network egress policy currently blocks archive.org and gutenberg.org
(see STATE.md → Blockers).

## Candidate field 1 — Colonial-era Northern Nigeria / Sokoto Caliphate

| Work | Author, year | Verified location | Formats |
|---|---|---|---|
| The Making of Northern Nigeria | Charles W. J. Orr, 1911 | https://archive.org/details/makingofnorthern00orrc (PDF: /download/makingofnorthern00orrc/makingofnorthern00orrc.pdf) | PDF, OCR txt |
| A Tropical Dependency | Flora L. Shaw (Lady Lugard), 1905 | https://archive.org/details/tropicaldependen00luga (also .../tropicaldependen00shaw) | PDF, OCR txt (djvu.txt confirmed) |
| Travels and Discoveries in North and Central Africa | Heinrich Barth, 1857–59 (1890 ed. also available) | https://archive.org/details/travelsdiscoveri00bartuoft (multi-volume scans; also Gutenberg #73138) | PDF, OCR txt, Gutenberg HTML/txt |

| Hausaland, or Fifteen Hundred Miles through the Central Soudan | C. H. Robinson, 1896 | https://archive.org/details/hausaland00robi | OCR txt (fetched) |
| Nigeria: Its Peoples and Its Problems | E. D. Morel, 1911 | https://archive.org/details/nigeriaitspeople00more | OCR txt (fetched) |
| Travels and Discoveries (Gutenberg HTML edition) | Heinrich Barth | https://www.gutenberg.org/ebooks/73138 | HTML (fetched) |

Lugard's Colonial Office annual reports were searched for on archive.org but no
standalone digitized volume surfaced under his name; the corpus (6 files, 3 formats)
is sufficient without them. The depth corpus is FROZEN as of 2026-08-29 — the eval
set (eval/questions.yaml) is written against exactly these files.

## Candidate field 2 — Forgotten 19th-century polar expeditions

| Work | Author, year | Verified location | Formats |
|---|---|---|---|
| The Home of the Blizzard | Douglas Mawson, 1915 | Project Gutenberg #6137 — https://www.gutenberg.org/ebooks/6137 | Gutenberg HTML, txt, EPUB |
| The Voyage of the Jeannette (ship and ice journals of G. W. De Long) | ed. Emma De Long, 1884 | https://archive.org/details/voyageofjeannett01delo (vol. 2 also on archive.org) | PDF, OCR txt |
| Three Years of Arctic Service (Lady Franklin Bay Expedition) | Adolphus W. Greely, 1886 | https://archive.org/details/threeyearsofarct00greeuoft (vol. 1), .../threeyearsofarct02greeuoft (vol. 2) | PDF, OCR txt |
| Our Lost Explorers (Jeannette narrative by survivors) | Raymond L. Newcomb, 1882 | https://archive.org/details/ourlostexplorers01newc | PDF, OCR txt |

## Breadth corpus candidate (generalization build) — historical aviation accident investigations

Pre-NTSB Civil Aeronautics Board reports and older NTSB reports (US government works,
public domain); NTSB accident database available as CSV (natural tabular-pipeline test).
To be verified when Phase 6a corpus collection starts.

## License notes

- Internet Archive scans of pre-1930 publications: public domain (no license restriction on the underlying text).
- Project Gutenberg: public domain in the US; the Project Gutenberg trademark license applies only if the PG header/branding is kept — we strip headers on ingestion and record the source URL here instead.
- CAB/NTSB reports: US federal government works, 17 U.S.C. § 105, public domain.
