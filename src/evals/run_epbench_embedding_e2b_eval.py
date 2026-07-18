#!/usr/bin/env python3
"""Run a resumable EPBench retrieval + E2B generation eval."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def read_qrels(path: Path) -> dict[str, dict[str, float]]:
    qrels: dict[str, dict[str, float]] = defaultdict(dict)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            query_id, doc_id, score = line.rstrip("\n").split("\t")
            qrels[query_id][doc_id] = float(score)
    return dict(qrels)


def post_json(url: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
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


def retry_json(
    url: str,
    payload: dict[str, Any],
    timeout: int,
    retries: int,
    base_delay: float,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            return post_json(url, payload, timeout)
        except Exception as exc:  # noqa: BLE001 - store all API failure modes durably.
            last_error = exc
            if attempt > retries:
                break
            time.sleep(base_delay * (2 ** (attempt - 1)))
    raise RuntimeError(str(last_error)) from last_error


def embed_one(
    base_url: str,
    model: str,
    text: str,
    timeout: int,
    retries: int,
    retry_base_delay: float,
) -> list[float]:
    result = retry_json(
        f"{base_url.rstrip('/')}/embeddings",
        {"model": model, "input": [text]},
        timeout,
        retries,
        retry_base_delay,
    )
    return result["data"][0]["embedding"]


def load_embedding_cache(path: Path) -> dict[str, list[float]]:
    return {row["cache_key"]: row["embedding"] for row in read_jsonl(path)}


def ensure_embeddings(
    cache_path: Path,
    items: list[tuple[str, str]],
    base_url: str,
    model: str,
    timeout: int,
    retries: int,
    retry_base_delay: float,
) -> dict[str, list[float]]:
    cache = load_embedding_cache(cache_path)
    for index, (cache_key, text) in enumerate(items, start=1):
        if cache_key in cache:
            continue
        embedding = embed_one(base_url, model, text, timeout, retries, retry_base_delay)
        cache[cache_key] = embedding
        append_jsonl(
            cache_path,
            {
                "cache_key": cache_key,
                "embedding": embedding,
                "embedded_at": datetime.now(timezone.utc).isoformat(),
                "model": model,
            },
        )
        if index % 25 == 0:
            print(json.dumps({"stage": "embedding", "cached": len(cache), "total": len(items)}, sort_keys=True))
    return cache


def format_retrieved_context(scored_rows: list[dict[str, Any]], corpus_by_id: dict[str, dict[str, Any]], limit: int) -> str:
    context_blocks: list[str] = []
    for rank, scored_row in enumerate(scored_rows[:limit], start=1):
        doc = corpus_by_id[scored_row["doc_id"]]
        context_blocks.append(
            f"[retrieved_rank {rank}; doc_id {doc['id']}; score {scored_row['score']:.6f}]\n{doc['text']}"
        )
    return "\n\n".join(context_blocks)


def chat_completion(
    base_url: str,
    model: str,
    query: str,
    context: str,
    max_tokens: int,
    timeout: int,
    retries: int,
    retry_base_delay: float,
) -> dict[str, Any]:
    payload = {
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
    }
    result = retry_json(
        f"{base_url.rstrip('/')}/chat/completions",
        payload,
        timeout,
        retries,
        retry_base_delay,
    )
    message = result["choices"][0]["message"]
    return {
        "answer": message.get("content") or "",
        "raw_message": message,
        "usage": result.get("usage", {}),
    }


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


def build_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "queries": len(rows),
        "hit_at_1": mean([1.0 if row["hit_at_1"] else 0.0 for row in rows]),
        "hit_at_3": mean([1.0 if row["hit_at_3"] else 0.0 for row in rows]),
        "hit_at_5": mean([1.0 if row["hit_at_5"] else 0.0 for row in rows]),
        "hit_at_10": mean([1.0 if row["hit_at_10"] else 0.0 for row in rows]),
        "recall_at_10": mean([row["recall_at_10"] for row in rows]),
        "mrr": mean([row["mrr"] for row in rows]),
        "ndcg_at_10": mean([row["ndcg_at_10"] for row in rows]),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
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
            for field in ("relevant_doc_ids", "top_10_doc_ids", "generation_context_doc_ids"):
                csv_row[field] = json.dumps(row[field], ensure_ascii=False)
            writer.writerow({field: csv_row[field] for field in fieldnames})


def write_progress(
    out_dir: Path,
    rows: list[dict[str, Any]],
    total_queries: int,
    started_at: str,
    start_time: float,
    consecutive_errors: int,
) -> None:
    write_json(
        out_dir / "progress.json",
        {
            "completed_queries": len(rows),
            "remaining_queries": max(total_queries - len(rows), 0),
            "total_queries": total_queries,
            "consecutive_errors": consecutive_errors,
            "started_at": started_at,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        },
    )


def read_query_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def selected_queries(
    all_queries: list[dict[str, Any]],
    limit: int | None,
    query_ids_file: Path | None,
) -> list[dict[str, Any]]:
    if query_ids_file is None:
        return all_queries if limit is None else all_queries[:limit]

    queries_by_id = {query["id"]: query for query in all_queries}
    query_ids = read_query_ids(query_ids_file)
    missing_query_ids = [query_id for query_id in query_ids if query_id not in queries_by_id]
    if missing_query_ids:
        raise ValueError(f"Query IDs not found in dataset: {missing_query_ids}")
    selected = [queries_by_id[query_id] for query_id in query_ids]
    return selected if limit is None else selected[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/epbench_episodic"))
    parser.add_argument("--out", type=Path, default=Path("evals/epbench_embedding_e2b_full"))
    parser.add_argument("--embedding-base-url", default="http://127.0.0.1:8083/v1")
    parser.add_argument("--embedding-model", default="embeddinggemma-300m")
    parser.add_argument("--chat-base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--chat-model", default="gemma-4-e2b")
    parser.add_argument("--limit", type=int, help="Optional query limit. Omit for all EPBench queries.")
    parser.add_argument("--query-ids-file", type=Path, help="Optional newline-delimited query IDs to evaluate.")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--generation-context-k", type=int)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--ctx-size", type=int, help="Context size of the chat server used for this run.")
    parser.add_argument("--reasoning", choices=("on", "off", "auto"), default="auto")
    parser.add_argument("--reasoning-budget", type=int, help="Reasoning token budget configured on the chat server.")
    parser.add_argument("--embedding-timeout", type=int, default=180)
    parser.add_argument("--chat-timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-base-delay", type=float, default=2.0)
    parser.add_argument("--max-consecutive-errors", type=int, default=10)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    generation_context_k = args.generation_context_k or args.top_k

    corpus = read_jsonl(args.dataset / "corpus.jsonl")
    corpus_by_id = {row["id"]: row for row in corpus}
    all_queries = read_jsonl(args.dataset / "queries.jsonl")
    queries = selected_queries(all_queries, args.limit, args.query_ids_file)
    qrels = read_qrels(args.dataset / "qrels.tsv")

    existing_rows_by_id = {row["query_id"]: row for row in read_jsonl(args.out / "results.jsonl")}
    existing_query_ids = set(existing_rows_by_id)
    errors_path = args.out / "errors.jsonl"

    embedding_items = [
        (f"corpus::{row['id']}", f"title: {row.get('title', '')}\ntext: {row['text']}")
        for row in corpus
    ] + [(f"query::{row['id']}", row["text"]) for row in queries]
    embedding_cache = ensure_embeddings(
        args.out / "embedding_cache.jsonl",
        embedding_items,
        args.embedding_base_url,
        args.embedding_model,
        args.embedding_timeout,
        args.retries,
        args.retry_base_delay,
    )
    corpus_embeddings = [l2_normalize(embedding_cache[f"corpus::{row['id']}"]) for row in corpus]

    def generate_row(query: dict[str, Any]) -> dict[str, Any]:
        query_embedding = l2_normalize(embedding_cache[f"query::{query['id']}"])
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
        completion = chat_completion(
            args.chat_base_url,
            args.chat_model,
            query["text"],
            generation_context,
            args.max_tokens,
            args.chat_timeout,
            args.retries,
            args.retry_base_delay,
        )
        return {
            "query_id": query["id"],
            "query_type": query.get("query_type", ""),
            "query_text": query["text"],
            "relevant_doc_ids": list(query_qrels),
            "top_doc_id": ranked_doc_ids[0],
            "top_score": scored[0]["score"],
            "top_10_doc_ids": ranked_doc_ids[: args.top_k],
            "generation_context_doc_ids": generation_context_doc_ids,
            "e2b_answer": completion["answer"],
            "chat_usage": completion["usage"],
            "raw_chat_message": completion["raw_message"],
            **grade,
        }

    pending_queries = [query for query in queries if query["id"] not in existing_query_ids]
    consecutive_errors = 0

    def persist_success(row: dict[str, Any]) -> None:
        append_jsonl(args.out / "results.jsonl", row)
        existing_rows_by_id[row["query_id"]] = row
        existing_query_ids.add(row["query_id"])
        if len(existing_rows_by_id) % 10 == 0 or len(existing_rows_by_id) == len(queries):
            print(
                json.dumps(
                    {
                        "stage": "generation",
                        "completed": len(existing_rows_by_id),
                        "total": len(queries),
                        "latest_query_id": row["query_id"],
                    },
                    sort_keys=True,
                )
            )

    def persist_failure(query: dict[str, Any], exc: Exception, error_count: int) -> None:
        append_jsonl(
            errors_path,
            {
                "failed_at": datetime.now(timezone.utc).isoformat(),
                "query_id": query["id"],
                "query_type": query.get("query_type", ""),
                "error": repr(exc),
                "consecutive_errors": error_count,
            },
        )

    if args.workers <= 1:
        for query in pending_queries:
            try:
                row = generate_row(query)
                persist_success(row)
                consecutive_errors = 0
            except Exception as exc:  # noqa: BLE001 - make failed rows resumable.
                consecutive_errors += 1
                persist_failure(query, exc, consecutive_errors)
                if consecutive_errors >= args.max_consecutive_errors:
                    break
            finally:
                write_progress(
                    args.out,
                    list(existing_rows_by_id.values()),
                    len(queries),
                    started_at,
                    start_time,
                    consecutive_errors,
                )
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_query = {executor.submit(generate_row, query): query for query in pending_queries}
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    row = future.result()
                    persist_success(row)
                    consecutive_errors = 0
                except Exception as exc:  # noqa: BLE001 - make failed rows resumable.
                    consecutive_errors += 1
                    persist_failure(query, exc, consecutive_errors)
                    if consecutive_errors >= args.max_consecutive_errors:
                        executor.shutdown(cancel_futures=True)
                        break
                finally:
                    write_progress(
                        args.out,
                        list(existing_rows_by_id.values()),
                        len(queries),
                        started_at,
                        start_time,
                        consecutive_errors,
                    )

    rows = [existing_rows_by_id[query["id"]] for query in queries if query["id"] in existing_rows_by_id]
    metrics = build_metrics(rows)
    manifest = {
        "run_type": "epbench_embedding_chat_resumable_eval",
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
        "ctx_size": args.ctx_size,
        "reasoning": args.reasoning,
        "reasoning_budget": args.reasoning_budget,
        "limit": args.limit,
        "query_ids_file": str(args.query_ids_file) if args.query_ids_file else None,
        "top_k": args.top_k,
        "generation_context_k": generation_context_k,
        "corpus_rows": len(corpus),
        "dataset_query_rows": len(all_queries),
        "query_rows_targeted": len(queries),
        "query_rows_completed": len(rows),
        "qrel_rows": sum(len(value) for value in qrels.values()),
        "workers": args.workers,
        "generation_context_policy": "inject top generation_context_k retrieved passages into the chat prompt",
        "deterministic_grade_scope": "retrieval only, via qrels.tsv",
        "durability": "embeddings and generation results are append-only jsonl; reruns skip completed query_id rows",
    }
    write_json(args.out / "metrics.json", metrics)
    write_json(args.out / "manifest.json", manifest)
    write_csv(args.out / "results.csv", rows)
    print(
        json.dumps(
            {
                "status": "complete" if len(rows) == len(queries) else "partial",
                "completed": len(rows),
                "target": len(queries),
                "metrics": metrics,
                "out": str(args.out),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
