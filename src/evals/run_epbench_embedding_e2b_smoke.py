#!/usr/bin/env python3
"""Run a 10-query EPBench retrieval + E2B generation smoke test."""

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
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_qrels(path: Path) -> dict[str, dict[str, float]]:
    qrels: dict[str, dict[str, float]] = defaultdict(dict)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            query_id, doc_id, score = line.rstrip("\n").split("\t")
            qrels[query_id][doc_id] = float(score)
    return dict(qrels)


def post_json(url: str, payload: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
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
    endpoint = f"{base_url.rstrip('/')}/embeddings"
    vectors: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        result = post_json(endpoint, {"model": model, "input": batch})
        vectors.extend(item["embedding"] for item in sorted(result["data"], key=lambda item: item["index"]))
    return vectors


def format_retrieved_context(scored_rows: list[dict[str, Any]], corpus_by_id: dict[str, dict[str, Any]], limit: int) -> str:
    context_blocks: list[str] = []
    for rank, scored_row in enumerate(scored_rows[:limit], start=1):
        doc = corpus_by_id[scored_row["doc_id"]]
        context_blocks.append(
            f"[retrieved_rank {rank}; doc_id {doc['id']}; score {scored_row['score']:.6f}]\n{doc['text']}"
        )
    return "\n\n".join(context_blocks)


def chat_completion(base_url: str, model: str, query: str, context: str, max_tokens: int) -> str:
    endpoint = f"{base_url.rstrip('/')}/chat/completions"
    result = post_json(
        endpoint,
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Answer the user's EPBench query using only the retrieved context passages. "
                        "Use every retrieved passage that is relevant to the query, and ignore retrieved "
                        "passages that are not relevant. Be concise. If the query asks for a list, return "
                        "only the list."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Retrieved context:\n{context}\n\nQuery:\n{query}",
                },
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
        },
        timeout=240,
    )
    return result["choices"][0]["message"]["content"]


def l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        raise ValueError("Embedding vector has zero norm")
    return [value / norm for value in vector]


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def dcg(doc_ids: list[str], qrel: dict[str, float]) -> float:
    return sum(qrel.get(doc_id, 0.0) / math.log2(index + 1) for index, doc_id in enumerate(doc_ids, start=1))


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
    return {
        "hit_at_1": ranked_doc_ids[0] in relevant_doc_ids,
        "hit_at_3": bool(set(ranked_doc_ids[:3]) & relevant_doc_ids),
        "hit_at_5": bool(set(ranked_doc_ids[:5]) & relevant_doc_ids),
        "hit_at_10": bool(hits),
        "recall_at_10": len(hits) / len(relevant_doc_ids) if relevant_doc_ids else 0.0,
        "mrr": 1 / first_relevant_rank if first_relevant_rank else 0.0,
        "ndcg_at_10": dcg(top_k, qrel) / ideal_dcg if ideal_dcg else 0.0,
        "first_relevant_rank": first_relevant_rank,
        "retrieval_grade": "pass" if hits else "fail",
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/epbench_episodic"))
    parser.add_argument("--out", type=Path, default=Path("evals/epbench_embedding_e2b_smoke"))
    parser.add_argument("--embedding-base-url", default="http://127.0.0.1:8083/v1")
    parser.add_argument("--embedding-model", default="embeddinggemma-300m")
    parser.add_argument("--chat-base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--chat-model", default="gemma-4-e2b")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--generation-context-k", type=int)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-tokens", type=int, default=96)
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    generation_context_k = args.generation_context_k or args.top_k

    corpus = read_jsonl(args.dataset / "corpus.jsonl")
    corpus_by_id = {row["id"]: row for row in corpus}
    queries = read_jsonl(args.dataset / "queries.jsonl")[: args.limit]
    qrels = read_qrels(args.dataset / "qrels.tsv")

    corpus_texts = [f"title: {row.get('title', '')}\ntext: {row['text']}" for row in corpus]
    query_texts = [row["text"] for row in queries]
    corpus_embeddings = [l2_normalize(vector) for vector in embed_texts(args.embedding_base_url, args.embedding_model, corpus_texts, args.batch_size)]
    query_embeddings = [l2_normalize(vector) for vector in embed_texts(args.embedding_base_url, args.embedding_model, query_texts, args.batch_size)]

    rows: list[dict[str, Any]] = []
    for query, query_embedding in zip(queries, query_embeddings):
        scored = sorted(
            (
                {"doc_id": doc["id"], "score": dot(query_embedding, doc_embedding)}
                for doc, doc_embedding in zip(corpus, corpus_embeddings)
            ),
            key=lambda row: row["score"],
            reverse=True,
        )
        ranked_doc_ids = [row["doc_id"] for row in scored]
        query_qrels = qrels.get(query["id"], {})
        grade = grade_query(ranked_doc_ids, query_qrels, args.top_k)
        generation_context_doc_ids = ranked_doc_ids[:generation_context_k]
        generation_context = format_retrieved_context(scored, corpus_by_id, generation_context_k)
        answer = chat_completion(args.chat_base_url, args.chat_model, query["text"], generation_context, args.max_tokens)
        rows.append(
            {
                "query_id": query["id"],
                "query_type": query.get("query_type", ""),
                "query_text": query["text"],
                "relevant_doc_ids": list(query_qrels),
                "top_doc_id": ranked_doc_ids[0],
                "top_score": scored[0]["score"],
                "top_10_doc_ids": ranked_doc_ids[: args.top_k],
                "generation_context_doc_ids": generation_context_doc_ids,
                "e2b_answer": answer,
                **grade,
            }
        )

    metrics = {
        "queries": len(rows),
        "hit_at_1": mean([1.0 if row["hit_at_1"] else 0.0 for row in rows]),
        "hit_at_3": mean([1.0 if row["hit_at_3"] else 0.0 for row in rows]),
        "hit_at_5": mean([1.0 if row["hit_at_5"] else 0.0 for row in rows]),
        "hit_at_10": mean([1.0 if row["hit_at_10"] else 0.0 for row in rows]),
        "recall_at_10": mean([row["recall_at_10"] for row in rows]),
        "mrr": mean([row["mrr"] for row in rows]),
        "ndcg_at_10": mean([row["ndcg_at_10"] for row in rows]),
    }
    manifest = {
        "run_type": "epbench_embedding_e2b_10_query_smoke",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        "dataset": str(args.dataset),
        "output_dir": str(args.out),
        "embedding_base_url": args.embedding_base_url,
        "embedding_model": args.embedding_model,
        "chat_base_url": args.chat_base_url,
        "chat_model": args.chat_model,
        "temperature": 0,
        "max_tokens": args.max_tokens,
        "limit": args.limit,
        "top_k": args.top_k,
        "generation_context_k": generation_context_k,
        "corpus_rows": len(corpus),
        "query_rows_scored": len(queries),
        "generation_context_policy": "inject top generation_context_k retrieved passages into the chat prompt",
        "deterministic_grade_scope": "retrieval only, via qrels.tsv",
    }

    (args.out / "results.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    with (args.out / "results.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "query_id",
            "query_type",
            "retrieval_grade",
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
            "generation_context_doc_ids",
            "query_text",
            "e2b_answer",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["relevant_doc_ids"] = json.dumps(row["relevant_doc_ids"])
            csv_row["top_10_doc_ids"] = json.dumps(row["top_10_doc_ids"])
            csv_row["generation_context_doc_ids"] = json.dumps(row["generation_context_doc_ids"])
            writer.writerow(csv_row)

    print(json.dumps({"status": "ok", "metrics": metrics, "out": str(args.out)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
