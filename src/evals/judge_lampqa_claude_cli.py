#!/usr/bin/env python3
"""Judge LaMP-QA generated answers with the Claude CLI, one durable row at a time."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


JUDGE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "question_id": {"type": "string"},
        "score": {"type": "integer", "minimum": 1, "maximum": 5},
        "grade": {"type": "string", "enum": ["pass", "partial", "fail"]},
        "rubric_coverage": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "aspect": {"type": "string"},
                    "coverage": {"type": "string", "enum": ["covered", "partial", "missed"]},
                    "explanation": {"type": "string"},
                },
                "required": ["aspect", "coverage", "explanation"],
                "additionalProperties": False,
            },
        },
        "personalization_quality": {"type": "string", "enum": ["strong", "some", "none", "misused"]},
        "unsupported_claims": {"type": "array", "items": {"type": "string"}},
        "missing_key_points": {"type": "array", "items": {"type": "string"}},
        "explanation": {"type": "string"},
    },
    "required": [
        "question_id",
        "score",
        "grade",
        "rubric_coverage",
        "personalization_quality",
        "unsupported_claims",
        "missing_key_points",
        "explanation",
    ],
    "additionalProperties": False,
}


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


def trim_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + " ..."


def build_prompt(
    result: dict[str, Any],
    question: dict[str, Any],
    max_profile_chars: int,
    max_answer_chars: int,
) -> str:
    profiles = [
        {
            "rank": index,
            "profile_id": profile["id"],
            "category": profile.get("category", ""),
            "score": profile.get("score"),
            "text": trim_text(profile["text"], max_profile_chars),
        }
        for index, profile in enumerate(result.get("retrieved_profiles", []), start=1)
    ]
    payload = {
        "question_id": result["question_id"],
        "source_config": result.get("source_config", ""),
        "category": result.get("category", ""),
        "question": result["question"],
        "narrative": result.get("narrative", ""),
        "rubric_aspects": question.get("rubric_aspects", []),
        "retrieved_profile_memories": profiles,
        "candidate_answer": trim_text(result.get("e2b_answer", ""), max_answer_chars),
    }
    return (
        "You are judging a LaMP-QA personalized long-form QA answer.\n"
        "Judge only the candidate answer. Do not answer the question yourself.\n"
        "Use the rubric aspects as the primary criteria. Use retrieved profile memories to evaluate whether the answer "
        "uses relevant personalization appropriately, ignores irrelevant memories, and avoids unsupported claims.\n"
        "A score of 5 means the answer directly addresses the question, covers the important rubric aspects, and uses "
        "personalization well when relevant. A score of 3 means materially useful but incomplete or weakly personalized. "
        "A score of 1 means mostly wrong, unsupported, or not responsive.\n"
        "Return only the structured JSON requested by the schema.\n\n"
        f"Evaluation item:\n{json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)}"
    )


def extract_judgment(wrapper: dict[str, Any]) -> dict[str, Any]:
    if isinstance(wrapper.get("structured_output"), dict):
        return wrapper["structured_output"]
    result = wrapper.get("result")
    if isinstance(result, dict):
        return result
    if isinstance(result, str):
        return json.loads(result)
    raise ValueError("Claude output did not include structured_output or JSON result")


def run_claude(prompt: str, model: str, timeout: int) -> dict[str, Any]:
    command = [
        "claude",
        "--safe-mode",
        "-p",
        prompt,
        "--model",
        model,
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(JUDGE_SCHEMA, separators=(",", ":")),
        "--tools",
        "",
        "--disallowedTools",
        "mcp__*",
        "--no-session-persistence",
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)
    if completed.returncode != 0:
        raise RuntimeError(f"claude exited {completed.returncode}: {completed.stderr.strip() or completed.stdout.strip()}")
    return json.loads(completed.stdout)


def write_scores_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    fieldnames = [
        "question_id",
        "score",
        "grade",
        "personalization_quality",
        "unsupported_claims_count",
        "missing_key_points_count",
        "explanation",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "question_id": row["question_id"],
                    "score": row["score"],
                    "grade": row["grade"],
                    "personalization_quality": row["personalization_quality"],
                    "unsupported_claims_count": len(row.get("unsupported_claims", [])),
                    "missing_key_points_count": len(row.get("missing_key_points", [])),
                    "explanation": row["explanation"],
                }
            )


def write_progress(path: Path, started_at: str, start_time: float, total: int, completed: int, consecutive_errors: int) -> None:
    write_json(
        path,
        {
            "completed_items": completed,
            "consecutive_errors": consecutive_errors,
            "elapsed_seconds": round(time.perf_counter() - start_time, 3),
            "remaining_items": total - completed,
            "started_at": started_at,
            "target_items": total,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )


def judge_result_row(
    result: dict[str, Any],
    question: dict[str, Any],
    model: str,
    max_profile_chars: int,
    max_answer_chars: int,
    timeout: int,
    retries: int,
    retry_base_delay: float,
) -> dict[str, Any]:
    question_id = result["question_id"]
    prompt = build_prompt(result, question, max_profile_chars, max_answer_chars)
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            wrapper = run_claude(prompt, model, timeout)
            judgment = extract_judgment(wrapper)
            if judgment["question_id"] != question_id:
                raise ValueError(f"judgment question_id mismatch: {judgment['question_id']} != {question_id}")
            return {
                "ok": True,
                "row": {
                    **judgment,
                    "claude_duration_ms": wrapper.get("duration_ms"),
                    "claude_model_usage": wrapper.get("modelUsage"),
                    "claude_total_cost_usd": wrapper.get("total_cost_usd"),
                    "claude_uuid": wrapper.get("uuid"),
                    "judged_at": datetime.now(timezone.utc).isoformat(),
                    "raw_claude_result": wrapper.get("result"),
                    "source_config": result.get("source_config", ""),
                },
            }
        except Exception as exc:  # noqa: BLE001 - durable CLI wrapper must persist every failure mode.
            last_error = exc
            if attempt <= retries:
                time.sleep(retry_base_delay * (2 ** (attempt - 1)))
    return {"ok": False, "question_id": question_id, "error": repr(last_error)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", type=Path, default=Path("evals/lampqa_embedding_e2b_sample100"))
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/lamp_qa_personalization_sample100"))
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--prefix", default="claude_judge")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--batch-size", type=int)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--max-profile-chars", type=int, default=1200)
    parser.add_argument("--max-answer-chars", type=int, default=5000)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--retry-base-delay", type=float, default=5.0)
    parser.add_argument("--max-consecutive-errors", type=int, default=5)
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()
    scores_path = args.eval_dir / f"{args.prefix}_scores.jsonl"
    errors_path = args.eval_dir / f"{args.prefix}_errors.jsonl"
    progress_path = args.eval_dir / f"{args.prefix}_progress.json"
    manifest_path = args.eval_dir / f"{args.prefix}_manifest.json"
    metrics_path = args.eval_dir / f"{args.prefix}_metrics.json"
    csv_path = args.eval_dir / f"{args.prefix}_scores.csv"

    questions_by_id = {row["id"]: row for row in read_jsonl(args.dataset / "questions.jsonl")}
    result_rows = read_jsonl(args.eval_dir / "results.jsonl")
    if args.limit is not None:
        result_rows = result_rows[: args.limit]
    result_scope_rows = list(result_rows)
    result_scope_ids = {row["question_id"] for row in result_scope_rows}

    existing_scores = read_jsonl(scores_path)
    completed_ids = {row["question_id"] for row in existing_scores}
    if args.batch_size is not None:
        result_rows = [row for row in result_rows if row["question_id"] not in completed_ids][: args.batch_size]
    target_ids = {row["question_id"] for row in result_rows}

    def completed_target_count() -> int:
        return sum(1 for question_id in target_ids if question_id in completed_ids)

    consecutive_errors = 0

    pending_rows = [row for row in result_rows if row["question_id"] not in completed_ids]
    if args.workers <= 1:
        worker_results = (
            judge_result_row(
                result,
                questions_by_id[result["question_id"]],
                args.model,
                args.max_profile_chars,
                args.max_answer_chars,
                args.timeout,
                args.retries,
                args.retry_base_delay,
            )
            for result in pending_rows
        )
    else:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=args.workers)
        futures = [
            executor.submit(
                judge_result_row,
                result,
                questions_by_id[result["question_id"]],
                args.model,
                args.max_profile_chars,
                args.max_answer_chars,
                args.timeout,
                args.retries,
                args.retry_base_delay,
            )
            for result in pending_rows
        ]
        worker_results = (future.result() for future in concurrent.futures.as_completed(futures))

    try:
        for worker_result in worker_results:
            if worker_result["ok"]:
                output_row = worker_result["row"]
                question_id = output_row["question_id"]
                if question_id in completed_ids:
                    continue
                append_jsonl(scores_path, output_row)
                existing_scores.append(output_row)
                completed_ids.add(question_id)
                consecutive_errors = 0
                write_progress(progress_path, started_at, start_time, len(result_rows), completed_target_count(), consecutive_errors)
                print(
                    json.dumps(
                        {
                            "batch_completed": completed_target_count(),
                            "completed_total": len(completed_ids),
                            "grade": output_row["grade"],
                            "question_id": question_id,
                            "score": output_row["score"],
                        },
                        sort_keys=True,
                    )
                )
            else:
                consecutive_errors += 1
                append_jsonl(
                    errors_path,
                    {
                        "attempted_at": datetime.now(timezone.utc).isoformat(),
                        "consecutive_errors": consecutive_errors,
                        "error": worker_result["error"],
                        "question_id": worker_result["question_id"],
                    },
                )
                write_progress(progress_path, started_at, start_time, len(result_rows), completed_target_count(), consecutive_errors)
                if consecutive_errors >= args.max_consecutive_errors:
                    break
    finally:
        if args.workers > 1:
            executor.shutdown(wait=False, cancel_futures=True)

    score_rows_by_id = {
        row["question_id"]: row
        for row in read_jsonl(scores_path)
        if row["question_id"] in result_scope_ids
    }
    score_rows = [score_rows_by_id[row["question_id"]] for row in result_scope_rows if row["question_id"] in score_rows_by_id]
    metrics = {
        "completed_items": len(score_rows),
        "target_items": len(result_scope_rows),
        "mean_score": sum(row["score"] for row in score_rows) / len(score_rows) if score_rows else 0.0,
        "grade_counts": {grade: sum(1 for row in score_rows if row["grade"] == grade) for grade in ["pass", "partial", "fail"]},
        "personalization_quality_counts": {
            value: sum(1 for row in score_rows if row["personalization_quality"] == value)
            for value in ["strong", "some", "none", "misused"]
        },
    }
    manifest = {
        "dataset": str(args.dataset),
        "eval_dir": str(args.eval_dir),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "judge_command": "claude --safe-mode -p <prompt> --model <model> --output-format json --json-schema <schema> --tools '' --disallowedTools mcp__* --no-session-persistence",
        "batch_size": args.batch_size,
        "limit": args.limit,
        "max_answer_chars": args.max_answer_chars,
        "max_profile_chars": args.max_profile_chars,
        "model": args.model,
        "prefix": args.prefix,
        "run_type": "lampqa_claude_cli_judge",
        "started_at": started_at,
        "workers": args.workers,
    }
    write_json(metrics_path, metrics)
    write_json(manifest_path, manifest)
    write_scores_csv(csv_path, score_rows)
    print(json.dumps({"metrics": metrics, "out": str(args.eval_dir), "status": "complete" if metrics["completed_items"] == len(result_scope_rows) else "partial"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
