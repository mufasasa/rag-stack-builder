"""Voyage AI embeddings (voyage-4, 1024-dim). Breadcrumb is prefixed to the
chunk text before embedding (located paragraphs retrieve better than orphans).
Batched; simple retry with backoff."""
import json
import os
import time
import urllib.request

MODEL = "voyage-4"
ENDPOINT = "https://api.voyageai.com/v1/embeddings"
# Free-tier Voyage keys enforce low RPM/TPM caps; keep batches small and treat
# 429 as "wait and retry", not an error. ~16 chunks ≈ 9K tokens per request.
BATCH = 16
MAX_429_RETRIES = 40
RETRY_WAIT_S = 25


def embed_texts(texts: list, input_type: str = "document") -> list:
    out = []
    total = (len(texts) + BATCH - 1) // BATCH
    for i in range(0, len(texts), BATCH):
        batch = texts[i:i + BATCH]
        body = {"input": batch, "model": MODEL, "input_type": input_type}
        attempt = 0
        while True:
            try:
                req = urllib.request.Request(
                    ENDPOINT,
                    data=json.dumps(body).encode(),
                    headers={
                        "Authorization": f"Bearer {os.environ['VOYAGE_API_KEY']}",
                        "Content-Type": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read())
                out.extend(d["embedding"] for d in sorted(data["data"], key=lambda d: d["index"]))
                break
            except urllib.error.HTTPError as exc:
                attempt += 1
                if exc.code == 429 and attempt <= MAX_429_RETRIES:
                    time.sleep(RETRY_WAIT_S)
                    continue
                raise
            except Exception:
                attempt += 1
                if attempt > 4:
                    raise
                time.sleep(2 ** attempt)
        if (i // BATCH) % 10 == 0:
            print(f"    embedded batch {i // BATCH + 1}/{total}", flush=True)
    return out


def embed_chunks(chunks: list) -> list:
    return embed_texts([f'{c["breadcrumb"]}\n\n{c["text"]}' for c in chunks], "document")


def embed_query(query: str) -> list:
    return embed_texts([query], "query")[0]
