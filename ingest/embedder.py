"""Voyage AI embeddings (voyage-4, 1024-dim). Breadcrumb is prefixed to the
chunk text before embedding (located paragraphs retrieve better than orphans).
Batched; simple retry with backoff."""
import json
import os
import time
import urllib.request

MODEL = "voyage-4"
ENDPOINT = "https://api.voyageai.com/v1/embeddings"
BATCH = 96


def embed_texts(texts: list, input_type: str = "document") -> list:
    out = []
    for i in range(0, len(texts), BATCH):
        batch = texts[i:i + BATCH]
        body = {"input": batch, "model": MODEL, "input_type": input_type}
        for attempt in range(4):
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
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
    return out


def embed_chunks(chunks: list) -> list:
    return embed_texts([f'{c["breadcrumb"]}\n\n{c["text"]}' for c in chunks], "document")


def embed_query(query: str) -> list:
    return embed_texts([query], "query")[0]
