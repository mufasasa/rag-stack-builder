# Reproduction guide (clean environment)

Everything below was verified in the build environment (Ubuntu 24.04,
Python 3.11). Approximate total cost to reproduce the main result: **< $5 in
model tokens** (Ollama cloud) + **free-tier Voyage embeddings** (the corpus is
~1.06M tokens; a free key embeds it in ~2 h at 10K tokens/min — a paid key
does it in minutes). Total wall time excluding embedding waits: ~30 minutes.

## 0. Requirements

- Python 3.11+, `pip install -r requirements.txt`
- Docker (for Postgres) — or a local Postgres 16/17 with the pgvector
  extension (`postgresql-16-pgvector`), which is what the original build used
  because its sandbox had no Docker daemon. Either path, same schema.
- API keys (free signup): `VOYAGE_API_KEY` (voyageai.com),
  `OLLAMA_API_KEY` (ollama.com). Copy `.env.example` → `.env`, fill in,
  `export $(cat .env | xargs)`.

## 1. Database

```bash
cd db && docker compose up -d          # pgvector/pgvector:pg17
docker compose exec -T db psql -U rag -d raglib < schema.sql
# local-Postgres alternative: create role rag + db raglib, CREATE EXTENSION
# vector, then: psql $DATABASE_URL -f db/schema.sql
```

Verify (round trip): insert any row with a dummy `vector(1024)` embedding and
confirm it returns by `ORDER BY embedding <=> ...` and by
`tsv @@ plainto_tsquery(...)`.

## 2. Corpus (public domain; not committed — fetch it)

```bash
./corpus/fetch.sh        # downloads all sources from archive.org / Gutenberg
```

Sources, editions, and license notes: `corpus/SOURCES.md`.

## 3. Build the library (the installer flow)

```bash
cd ingest
python3 ingest.py plan ../corpus/files/nigeria --domain nigeria --out ../corpus/nigeria.plan.json
# HUMAN GATE: review the plan. To match the submission exactly, set
# "action": "skip" on orr_making_of_northern_nigeria_1911.txt (duplicate of
# the PDF twin) — the committed corpus/nigeria.plan.json already records this.
python3 ingest.py run  ../corpus/files/nigeria --domain nigeria --plan ../corpus/nigeria.plan.json
```

Expected: 5 sources, **1,924 chunks** (Barth 848, Shaw 421, Orr 241 with page
numbers, Morel 227, Robinson 187). Free-tier embedding takes ~2 h
(self-paced under the 10K tokens/min cap); run it in the background.

Chunk-inspection gate (what the owner approved), sample query:

```sql
SELECT c.id, s.title, c.breadcrumb, c.page_start, left(c.text, 200)
FROM chunk c JOIN source s ON s.id = c.source_id
WHERE c.domain = 'nigeria' ORDER BY md5(c.id::text || 'gate2seed') LIMIT 20;
```

## 4. Retrieval server

```bash
python3 mcp_server/server.py     # stdio MCP server; or use .mcp.json in a host
```

Smoke test (in-process, same code path):

```bash
python3 -c "import sys; sys.path.insert(0,'mcp_server'); import server; \
print(server.search_corpus_ex('column left Zaria for Kano January 1903','nigeria',2))"
```

Expected: the top passage is Orr's Chapter VI chunk (pages 150–152) containing
"some 24 British officers and 700 men of the West African Frontier Force".

## 5. The evaluation (main result)

```bash
cd eval
python3 run_eval.py --condition baseline --tag baseline-repro          # 15 cases + 9 pushbacks, ~4 min
python3 run_eval.py --condition solution --tag solution-repro --mode hybrid
python3 rank_probe.py                                                  # retrieval-rank metric
```

Transcripts land in `eval/runs/<condition>/<tag>/`. Score against
`eval/questions.yaml` ground truth using the rubric in
`eval/runs/baseline/baseline-2026-08-29/SCORES.md`; audit solution citations
with `eval/runs/solution/iter1-vector-2026-08-30/audit_quotes.py`.

Expected result shape (our runs, committed): baseline ≈ 11/26 with pushback
flips and fabricated attributions; solution 26/26, zero flips, zero
fabricated attributions; rank probe ≈ vector MRR 0.733 / hybrid 0.900.
Exact model outputs vary run to run — the committed transcripts are the runs
scored in the report. Model: `deepseek-v4-pro:0813` via `https://ollama.com`.

## 6. Generalization build (breadth evidence)

```bash
cd ingest
python3 ingest.py plan ../corpus/files/polar --domain polar --out ../corpus/polar.plan.json
python3 ingest.py run  ../corpus/files/polar --domain polar --plan ../corpus/polar.plan.json
```

Then the 5-question polar smoke test: `eval/polar_smoke.yaml` (ground truth
quoted from the polar sources) through `search_corpus(..., domain='polar')`.

## Versions

Pinned in `requirements.txt` (psycopg2-binary 2.9.12, beautifulsoup4 4.15.0,
pypdf 6.16.2, PyYAML 6.0.1, mcp 2.1.1). Postgres 16.13 + pgvector (build) /
pgvector:pg17 image (compose). Embeddings: `voyage-4`, 1024-dim, cosine.
