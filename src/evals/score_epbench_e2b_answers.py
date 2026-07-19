#!/usr/bin/env python3
"""Score saved EPBench E2B answers with a local OpenAI-compatible judge."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
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


def read_qrels(path: Path) -> dict[str, list[str]]:
    qrels: dict[str, list[str]] = defaultdict(list)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            query_id, doc_id, score = line.rstrip("\n").split("\t")
            if float(score) > 0:
                qrels[query_id].append(doc_id)
    return dict(qrels)


def post_json(url: str, payload: dict[str, Any], timeout: int = 240) -> dict[str, Any]:
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


def retry_json(url: str, payload: dict[str, Any], timeout: int, retries: int, retry_base_delay: float) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            return post_json(url, payload, timeout)
        except Exception as exc:  # noqa: BLE001 - persist all local judge/API failure modes.
            last_error = exc
            if attempt > retries:
                break
            time.sleep(retry_base_delay * (2 ** (attempt - 1)))
    raise RuntimeError(str(last_error)) from last_error


def extract_json_object(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Judge did not return a JSON object: {text[:500]}")
    return json.loads(match.group(0))


def judge_answer(
    base_url: str,
    model: str,
    query: str,
    answer: str,
    gold_contexts: list[dict[str, str]],
    max_tokens: int,
    timeout: int,
    retries: int,
    retry_base_delay: float,
) -> dict[str, Any]:
    context = "\n\n".join(
        f"[gold_doc {index}: {doc['id']}]\n{doc['text']}" for index, doc in enumerate(gold_contexts, start=1)
    )
    prompt = f"""Query:
{query}

Gold relevant passage(s):
{context}

Candidate answer:
{answer}

Grade the candidate answer against the query using only the gold relevant passage(s).

Return only valid JSON with these keys:
- score: integer from 0 to 5
- grade: one of "pass", "partial", "fail"
- supported_items: list of answer items supported by the gold passage(s)
- unsupported_items: list of answer items not supported by the gold passage(s)
- missing_items: list of important requested protagonist/entity items missing from the answer
- explanation: one short sentence

Rubric:
5 = complete or near-complete, no unsupported items, follows the requested list-only format.
4 = mostly correct, minor omission or harmless extra.
3 = partially correct but has notable omissions or unsupported items.
2 = some correct content but poor coverage or format.
1 = minimal relevant content.
0 = empty, unrelated, or unsupported.
"""
    result = retry_json(
        f"{base_url.rstrip('/')}/chat/completions",
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a strict benchmark grader. Return only JSON, with no markdown.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
        },
        timeout,
        retries,
        retry_base_delay,
    )
    content = result["choices"][0]["message"].get("content", "")
    parsed = extract_json_object(content)
    parsed["raw_judge_content"] = content
    return parsed


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def build_metrics(scored_rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [row["answer_score"] for row in scored_rows]
    return {
        "answers": len(scored_rows),
        "mean_answer_score": mean(scores),
        "pass_count": sum(1 for row in scored_rows if row["answer_grade"] == "pass"),
        "partial_count": sum(1 for row in scored_rows if row["answer_grade"] == "partial"),
        "fail_count": sum(1 for row in scored_rows if row["answer_grade"] == "fail"),
        "score_distribution": {str(score): scores.count(score) for score in range(6)},
    }


def write_scores_csv(path: Path, scored_rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "query_id",
            "query_type",
            "answer_score",
            "answer_grade",
            "top_doc_id",
            "gold_doc_ids",
            "supported_items",
            "unsupported_items",
            "missing_items",
            "explanation",
            "e2b_answer",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in scored_rows:
            csv_row = dict(row)
            for field in ("gold_doc_ids", "supported_items", "unsupported_items", "missing_items"):
                csv_row[field] = json.dumps(csv_row[field], ensure_ascii=False)
            writer.writerow({field: csv_row[field] for field in fieldnames})


def write_progress(
    path: Path,
    scored_rows: list[dict[str, Any]],
    total_answers: int,
    skipped_answers: int,
    started_at: str,
    start_time: float,
    consecutive_errors: int,
) -> None:
    write_json(
        path,
        {
            "completed_answers": len(scored_rows),
            "skipped_answers": skipped_answers,
            "remaining_answers": max(total_answers - skipped_answers - len(scored_rows), 0),
            "total_answers": total_answers,
            "consecutive_errors": consecutive_errors,
            "started_at": started_at,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", type=Path, default=Path("evals/epbench_embedding_e2b_smoke"))
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/epbench_episodic"))
    parser.add_argument("--chat-base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--chat-model", default="gemma-4-e2b")
    parser.add_argument("--prefix", default="e2b_answer")
    parser.add_argument("--skip-scores-jsonl", type=Path, action="append", default=[])
    parser.add_argument("--limit", type=int, help="Optional result-row limit before skip filtering.")
    parser.add_argument("--max-tokens", type=int, default=768)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-base-delay", type=float, default=2.0)
    parser.add_argument("--max-consecutive-errors", type=int, default=10)
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()

    result_rows = read_jsonl(args.eval_dir / "results.jsonl")
    if args.limit is not None:
        result_rows = result_rows[: args.limit]
    corpus = {row["id"]: row for row in read_jsonl(args.dataset / "corpus.jsonl")}
    qrels = read_qrels(args.dataset / "qrels.tsv")

    jsonl_path = args.eval_dir / f"{args.prefix}_scores.jsonl"
    csv_path = args.eval_dir / f"{args.prefix}_scores.csv"
    metrics_path = args.eval_dir / f"{args.prefix}_metrics.json"
    manifest_path = args.eval_dir / f"{args.prefix}_score_manifest.json"
    errors_path = args.eval_dir / f"{args.prefix}_errors.jsonl"
    progress_path = args.eval_dir / f"{args.prefix}_progress.json"

    skip_query_ids: set[str] = set()
    for skip_path in args.skip_scores_jsonl:
        skip_query_ids.update(row["query_id"] for row in read_jsonl(skip_path))
    scored_by_query_id = {row["query_id"]: row for row in read_jsonl(jsonl_path)}
    consecutive_errors = 0
    for row in result_rows:
        if row["query_id"] in skip_query_ids or row["query_id"] in scored_by_query_id:
            continue
        try:
            gold_contexts = [corpus[doc_id] for doc_id in qrels[row["query_id"]]]
            judge = judge_answer(
                args.chat_base_url,
                args.chat_model,
                row["query_text"],
                row["e2b_answer"],
                gold_contexts,
                args.max_tokens,
                args.timeout,
                args.retries,
                args.retry_base_delay,
            )
            scored_row = {
                "query_id": row["query_id"],
                "query_type": row.get("query_type", ""),
                "top_doc_id": row["top_doc_id"],
                "gold_doc_ids": qrels[row["query_id"]],
                "e2b_answer": row["e2b_answer"],
                "answer_score": int(judge["score"]),
                "answer_grade": judge["grade"],
                "supported_items": judge.get("supported_items", []),
                "unsupported_items": judge.get("unsupported_items", []),
                "missing_items": judge.get("missing_items", []),
                "explanation": judge.get("explanation", ""),
                "raw_judge_content": judge["raw_judge_content"],
            }
            append_jsonl(jsonl_path, scored_row)
            scored_by_query_id[row["query_id"]] = scored_row
            consecutive_errors = 0
            if len(scored_by_query_id) % 10 == 0:
                print(
                    json.dumps(
                        {
                            "stage": "e2b_judge",
                            "completed": len(scored_by_query_id),
                            "skipped": len(skip_query_ids),
                            "total": len(result_rows),
                            "latest_query_id": row["query_id"],
                        },
                        sort_keys=True,
                    )
                )
        except Exception as exc:  # noqa: BLE001 - make failed judge rows resumable.
            consecutive_errors += 1
            append_jsonl(
                errors_path,
                {
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                    "query_id": row["query_id"],
                    "query_type": row.get("query_type", ""),
                    "error": repr(exc),
                    "consecutive_errors": consecutive_errors,
                },
            )
            if consecutive_errors >= args.max_consecutive_errors:
                break
        finally:
            write_progress(
                progress_path,
                list(scored_by_query_id.values()),
                len(result_rows),
                len(skip_query_ids),
                started_at,
                start_time,
                consecutive_errors,
            )

    scored_rows = [scored_by_query_id[row["query_id"]] for row in result_rows if row["query_id"] in scored_by_query_id]
    metrics = build_metrics(scored_rows)
    manifest = {
        "run_type": "epbench_e2b_answer_scoring",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        "eval_dir": str(args.eval_dir),
        "dataset": str(args.dataset),
        "judge_base_url": args.chat_base_url,
        "judge_model": args.chat_model,
        "judge_temperature": 0,
        "judge_max_tokens": args.max_tokens,
        "score_scope": "LLM-as-judge generation score against all gold qrel passages",
        "answers_targeted": len(result_rows),
        "answers_skipped": len(skip_query_ids),
        "answers_scored": len(scored_rows),
        "skip_scores_jsonl": [str(path) for path in args.skip_scores_jsonl],
        "durability": "judge scores are append-only jsonl; reruns skip completed query_id rows",
    }

    write_json(metrics_path, metrics)
    write_json(manifest_path, manifest)
    write_scores_csv(csv_path, scored_rows)

    expected_to_score = len([row for row in result_rows if row["query_id"] not in skip_query_ids])
    print(
        json.dumps(
            {
                "status": "complete" if len(scored_rows) == expected_to_score else "partial",
                "completed": len(scored_rows),
                "skipped": len(skip_query_ids),
                "target": len(result_rows),
                "metrics": metrics,
                "out": str(args.eval_dir),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
