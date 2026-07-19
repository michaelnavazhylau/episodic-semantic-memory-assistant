#!/usr/bin/env python3
"""Score saved EPBench answers with an OpenRouter-hosted judge."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class OpenRouterError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, body: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body or ""


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def read_qrels(path: Path) -> dict[str, list[str]]:
    qrels: dict[str, list[str]] = defaultdict(list)
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            query_id, doc_id, score = line.rstrip("\n").split("\t")
            if float(score) > 0:
                qrels[query_id].append(doc_id)
    return dict(qrels)


def post_openrouter_json(
    base_url: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: int = 300,
) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost/episodic-semantic-memory-assistant",
            "X-Title": "episodic-semantic-memory-assistant",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise OpenRouterError(f"HTTP {exc.code} from OpenRouter: {body}", exc.code, body) from exc


def retry_openrouter_json(
    base_url: str,
    api_key: str,
    payload: dict[str, Any],
    timeout: int,
    retries: int,
    retry_base_delay: float,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            return post_openrouter_json(base_url, api_key, payload, timeout)
        except OpenRouterError as exc:
            last_error = exc
            if exc.status_code == 429:
                break
            if attempt > retries:
                break
            time.sleep(retry_base_delay * (2 ** (attempt - 1)))
        except Exception as exc:  # noqa: BLE001 - persist all judge/API failure modes.
            last_error = exc
            if attempt > retries:
                break
            time.sleep(retry_base_delay * (2 ** (attempt - 1)))
    raise RuntimeError(str(last_error)) from last_error


def extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Judge did not return a JSON object: {text[:500]}")
    return json.loads(match.group(0))


def judge_answer(
    base_url: str,
    api_key: str,
    model: str,
    query: str,
    answer: str,
    gold_contexts: list[dict[str, str]],
    max_tokens: int,
    reasoning_enabled: bool,
    retries: int,
    retry_base_delay: float,
    timeout: int,
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
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a strict benchmark grader. Return only JSON, with no markdown."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    payload["reasoning"] = {"enabled": reasoning_enabled}

    result = retry_openrouter_json(base_url, api_key, payload, timeout, retries, retry_base_delay)
    if "choices" not in result:
        raise RuntimeError(f"OpenRouter response did not include choices: {json.dumps(result)[:1000]}")
    message = result["choices"][0]["message"]
    content = message.get("content") or ""
    parsed = extract_json_object(content)
    parsed["raw_judge_content"] = content
    parsed["reasoning_details_present"] = bool(message.get("reasoning_details"))
    return parsed


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


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
            "reasoning_details_present",
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
    started_at: str,
    start_time: float,
    consecutive_errors: int,
) -> None:
    write_json(
        path,
        {
            "completed_answers": len(scored_rows),
            "remaining_answers": max(total_answers - len(scored_rows), 0),
            "total_answers": total_answers,
            "consecutive_errors": consecutive_errors,
            "started_at": started_at,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        },
    )


def extract_rate_limit_reset(error_text: str) -> str | None:
    match = re.search(r'"X-RateLimit-Reset"\s*:\s*"(\d+)"', error_text)
    if not match:
        return None
    reset_ms = int(match.group(1))
    return datetime.fromtimestamp(reset_ms / 1000, timezone.utc).isoformat()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", type=Path, default=Path("evals/epbench_embedding_e2b_smoke"))
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/epbench_episodic"))
    parser.add_argument("--dotenv", type=Path, default=Path(".env"))
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--judge-model", default="nvidia/nemotron-3-ultra-550b-a55b:free")
    parser.add_argument("--prefix", default="nemotron_answer")
    parser.add_argument("--max-tokens", type=int, default=768)
    parser.add_argument("--reasoning", choices=("on", "off"), default="on")
    parser.add_argument("--limit", type=int, help="Optional answer limit. Omit for all saved answers.")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-base-delay", type=float, default=3.0)
    parser.add_argument("--max-consecutive-errors", type=int, default=10)
    args = parser.parse_args()

    load_dotenv(args.dotenv)
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set in the environment or .env")

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
    rate_limit_path = args.eval_dir / f"{args.prefix}_rate_limit.json"

    scored_by_query_id = {row["query_id"]: row for row in read_jsonl(jsonl_path)}
    consecutive_errors = 0
    for row in result_rows:
        if row["query_id"] in scored_by_query_id:
            continue
        try:
            gold_contexts = [corpus[doc_id] for doc_id in qrels[row["query_id"]]]
            judge = judge_answer(
                args.base_url,
                api_key,
                args.judge_model,
                row["query_text"],
                row["e2b_answer"],
                gold_contexts,
                args.max_tokens,
                args.reasoning == "on",
                args.retries,
                args.retry_base_delay,
                args.timeout,
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
                "reasoning_details_present": judge["reasoning_details_present"],
            }
            append_jsonl(jsonl_path, scored_row)
            scored_by_query_id[row["query_id"]] = scored_row
            consecutive_errors = 0
            if len(scored_by_query_id) % 10 == 0 or len(scored_by_query_id) == len(result_rows):
                print(
                    json.dumps(
                        {
                            "stage": "judge",
                            "completed": len(scored_by_query_id),
                            "total": len(result_rows),
                            "latest_query_id": row["query_id"],
                        },
                        sort_keys=True,
                    )
                )
        except Exception as exc:  # noqa: BLE001 - make failed judge rows resumable.
            consecutive_errors += 1
            error_text = repr(exc)
            append_jsonl(
                errors_path,
                {
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                    "query_id": row["query_id"],
                    "query_type": row.get("query_type", ""),
                    "error": error_text,
                    "consecutive_errors": consecutive_errors,
                },
            )
            if "HTTP 429 from OpenRouter" in error_text:
                write_json(
                    rate_limit_path,
                    {
                        "blocked_at": datetime.now(timezone.utc).isoformat(),
                        "blocked_query_id": row["query_id"],
                        "reason": "OpenRouter rate limit",
                        "reset_at": extract_rate_limit_reset(error_text),
                        "resume_command": (
                            "UV_CACHE_DIR=.uv-cache uv run python "
                            "src/evals/score_epbench_answers_openrouter.py "
                            f"--eval-dir {args.eval_dir} --dataset {args.dataset} "
                            f"--judge-model {args.judge_model} --reasoning {args.reasoning} "
                            f"--max-tokens {args.max_tokens} --prefix {args.prefix}"
                        ),
                    },
                )
                break
            if consecutive_errors >= args.max_consecutive_errors:
                break
        finally:
            write_progress(
                progress_path,
                list(scored_by_query_id.values()),
                len(result_rows),
                started_at,
                start_time,
                consecutive_errors,
            )

    scored_rows = [scored_by_query_id[row["query_id"]] for row in result_rows if row["query_id"] in scored_by_query_id]
    metrics = build_metrics(scored_rows)
    manifest = {
        "run_type": "epbench_openrouter_answer_scoring",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        "eval_dir": str(args.eval_dir),
        "dataset": str(args.dataset),
        "judge_base_url": args.base_url,
        "judge_model": args.judge_model,
        "judge_temperature": 0,
        "judge_max_tokens": args.max_tokens,
        "judge_reasoning_enabled": args.reasoning == "on",
        "score_scope": "OpenRouter LLM-as-judge generation score against all gold qrel passages",
        "answers_targeted": len(result_rows),
        "answers_scored": len(scored_rows),
        "durability": "judge scores are append-only jsonl; reruns skip completed query_id rows",
    }

    write_json(metrics_path, metrics)
    write_json(manifest_path, manifest)
    write_scores_csv(csv_path, scored_rows)

    print(
        json.dumps(
            {
                "status": "complete" if len(scored_rows) == len(result_rows) else "partial",
                "completed": len(scored_rows),
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
