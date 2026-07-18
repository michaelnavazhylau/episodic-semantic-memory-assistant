#!/usr/bin/env python3
"""Run a deterministic 10-query EPBench retrieval smoke test."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def read_qrels(path: Path) -> dict[str, dict[str, float]]:
    qrels: dict[str, dict[str, float]] = defaultdict(dict)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            query_id, doc_id, score = line.rstrip("\n").split("\t")
            qrels[query_id][doc_id] = float(score)
    return dict(qrels)


def post_json(url: str, payload: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body}") from exc


def embed_texts(base_url: str, model: str, texts: list[str], batch_size: int) -> list[list[float]]:
    embeddings: list[list[float]] = []
    endpoint = f"{base_url.rstrip('/')}/embeddings"
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        payload = {"model": model, "input": batch}
        result = post_json(endpoint, payload)
        data = sorted(result["data"], key=lambda item: item["index"])
        embeddings.extend(item["embedding"] for item in data)
    return embeddings


def l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        raise ValueError("Embedding vector has zero norm")
    return [value / norm for value in vector]


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def dcg(doc_ids: list[str], qrel: dict[str, float]) -> float:
    total = 0.0
    for index, doc_id in enumerate(doc_ids, start=1):
        gain = qrel.get(doc_id, 0.0)
        if gain:
            total += gain / math.log2(index + 1)
    return total


def grade_query(ranked_doc_ids: list[str], qrel: dict[str, float], k: int) -> dict[str, Any]:
    relevant_doc_ids = set(qrel)
    top_k = ranked_doc_ids[:k]
    hits = [doc_id for doc_id in top_k if doc_id in relevant_doc_ids]
    first_relevant_rank = next(
        (index for index, doc_id in enumerate(ranked_doc_ids, start=1) if doc_id in relevant_doc_ids),
        None,
    )
    ideal_doc_ids = sorted(qrel, key=lambda doc_id: qrel[doc_id], reverse=True)[:k]
    ideal_dcg = dcg(ideal_doc_ids, qrel)
    ndcg_at_k = dcg(top_k, qrel) / ideal_dcg if ideal_dcg else 0.0
    return {
        "hit_at_1": ranked_doc_ids[0] in relevant_doc_ids,
        "hit_at_3": bool(set(ranked_doc_ids[:3]) & relevant_doc_ids),
        "hit_at_5": bool(set(ranked_doc_ids[:5]) & relevant_doc_ids),
        "hit_at_10": bool(hits),
        "recall_at_10": len(hits) / len(relevant_doc_ids) if relevant_doc_ids else 0.0,
        "mrr": 1 / first_relevant_rank if first_relevant_rank else 0.0,
        "ndcg_at_10": ndcg_at_k,
        "first_relevant_rank": first_relevant_rank,
        "grade": "pass" if hits else "fail",
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/epbench_episodic"))
    parser.add_argument("--out", type=Path, default=Path("evals/epbench_smoke"))
    parser.add_argument("--base-url", default="http://127.0.0.1:8083/v1")
    parser.add_argument("--model", default="embeddinggemma-300m")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)

    corpus = read_jsonl(args.dataset / "corpus.jsonl")
    queries = read_jsonl(args.dataset / "queries.jsonl")[: args.limit]
    qrels = read_qrels(args.dataset / "qrels.tsv")

    corpus_texts = [f"title: {row.get('title', '')}\ntext: {row['text']}" for row in corpus]
    query_texts = [row["text"] for row in queries]

    corpus_embeddings = [l2_normalize(vector) for vector in embed_texts(args.base_url, args.model, corpus_texts, args.batch_size)]
    query_embeddings = [l2_normalize(vector) for vector in embed_texts(args.base_url, args.model, query_texts, args.batch_size)]

    result_rows: list[dict[str, Any]] = []
    for query, query_embedding in zip(queries, query_embeddings):
        scored = sorted(
            (
                {
                    "doc_id": doc["id"],
                    "score": dot(query_embedding, doc_embedding),
                }
                for doc, doc_embedding in zip(corpus, corpus_embeddings)
            ),
            key=lambda row: row["score"],
            reverse=True,
        )
        ranked_doc_ids = [row["doc_id"] for row in scored]
        query_qrels = qrels.get(query["id"], {})
        grade = grade_query(ranked_doc_ids, query_qrels, args.top_k)
        result_rows.append(
            {
                "query_id": query["id"],
                "query_type": query.get("query_type", ""),
                "query_text": query["text"],
                "relevant_doc_ids": list(query_qrels),
                "top_doc_id": ranked_doc_ids[0],
                "top_score": scored[0]["score"],
                "top_10_doc_ids": ranked_doc_ids[: args.top_k],
                **grade,
            }
        )

    metrics = {
        "queries": len(result_rows),
        "hit_at_1": mean([1.0 if row["hit_at_1"] else 0.0 for row in result_rows]),
        "hit_at_3": mean([1.0 if row["hit_at_3"] else 0.0 for row in result_rows]),
        "hit_at_5": mean([1.0 if row["hit_at_5"] else 0.0 for row in result_rows]),
        "hit_at_10": mean([1.0 if row["hit_at_10"] else 0.0 for row in result_rows]),
        "recall_at_10": mean([row["recall_at_10"] for row in result_rows]),
        "mrr": mean([row["mrr"] for row in result_rows]),
        "ndcg_at_10": mean([row["ndcg_at_10"] for row in result_rows]),
    }
    manifest = {
        "run_type": "epbench_10_query_smoke",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        "dataset": str(args.dataset),
        "output_dir": str(args.out),
        "embedding_base_url": args.base_url,
        "embedding_model": args.model,
        "limit": args.limit,
        "top_k": args.top_k,
        "corpus_rows": len(corpus),
        "query_rows_scored": len(queries),
        "scoring": "cosine similarity over L2-normalized local embeddings",
    }

    (args.out / "results.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in result_rows),
        encoding="utf-8",
    )
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    with (args.out / "results.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "query_id",
            "query_type",
            "grade",
            "hit_at_1",
            "hit_at_3",
            "hit_at_5",
            "hit_at_10",
            "recall_at_10",
            "mrr",
            "ndcg_at_10",
            "first_relevant_rank",
            "top_doc_id",
            "top_score",
            "relevant_doc_ids",
            "top_10_doc_ids",
            "query_text",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in result_rows:
            csv_row = dict(row)
            csv_row["relevant_doc_ids"] = json.dumps(row["relevant_doc_ids"])
            csv_row["top_10_doc_ids"] = json.dumps(row["top_10_doc_ids"])
            writer.writerow(csv_row)

    print(json.dumps({"status": "ok", "metrics": metrics, "out": str(args.out)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
