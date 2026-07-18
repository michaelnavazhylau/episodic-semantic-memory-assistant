#!/usr/bin/env python3
"""Run a resumable LaMP-QA profile-retrieval + E2B generation eval."""

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
from typing import Any, Iterable


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


def retry_json(url: str, payload: dict[str, Any], timeout: int, retries: int, base_delay: float) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 2):
        try:
            return post_json(url, payload, timeout)
        except Exception as exc:  # noqa: BLE001 - persist all API failure modes.
            last_error = exc
            if attempt > retries:
                break
            time.sleep(base_delay * (2 ** (attempt - 1)))
    raise RuntimeError(str(last_error)) from last_error


def load_embedding_cache(path: Path) -> dict[str, list[float]]:
    return {row["cache_key"]: row["embedding"] for row in read_jsonl(path)}


def embed_one(
    cache: dict[str, list[float]],
    cache_path: Path,
    cache_key: str,
    text: str,
    base_url: str,
    model: str,
    timeout: int,
    retries: int,
    retry_base_delay: float,
) -> list[float]:
    if cache_key in cache:
        return cache[cache_key]
    result = retry_json(
        f"{base_url.rstrip('/')}/embeddings",
        {"model": model, "input": [text]},
        timeout,
        retries,
        retry_base_delay,
    )
    embedding = result["data"][0]["embedding"]
    cache[cache_key] = embedding
    append_jsonl(
        cache_path,
        {
            "cache_key": cache_key,
            "embedded_at": datetime.now(timezone.utc).isoformat(),
            "embedding": embedding,
            "model": model,
        },
    )
    return embedding


def l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        raise ValueError("Embedding vector has zero norm")
    return [value / norm for value in vector]


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def trim_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + " ..."


def build_query_text(question: dict[str, Any]) -> str:
    parts = [f"question: {question['question']}"]
    narrative = question.get("narrative") or ""
    if narrative:
        parts.append(f"narrative: {narrative}")
    category = question.get("category") or ""
    if category:
        parts.append(f"category: {category}")
    return "\n".join(parts)


def format_context(scored_profiles: list[dict[str, Any]], context_k: int, max_profile_chars: int, max_context_chars: int) -> str:
    blocks: list[str] = []
    total_chars = 0
    for rank, scored in enumerate(scored_profiles[:context_k], start=1):
        profile = scored["profile"]
        text = trim_text(profile["text"], max_profile_chars)
        block = (
            f"[rank {rank}; profile_id {profile['id']}; category {profile.get('category', '')}; "
            f"score {scored['score']:.6f}]\n{text}"
        )
        if blocks and total_chars + len(block) + 2 > max_context_chars:
            break
        blocks.append(block)
        total_chars += len(block) + 2
    return "\n\n".join(blocks)


def build_prompt(question: dict[str, Any], context: str) -> list[dict[str, str]]:
    narrative = question.get("narrative") or ""
    user_parts = [
        "Answer the current user question. Use the retrieved profile memories only when they help personalize or contextualize the answer.",
        "Do not mention retrieval, profile memories, grading rubrics, or that you are using a benchmark dataset.",
        "If the profile memories are unrelated, answer the current question directly.",
        "",
        f"Current question:\n{question['question']}",
    ]
    if narrative:
        user_parts.extend(["", f"Question context:\n{narrative}"])
    if context:
        user_parts.extend(["", f"Retrieved profile memories:\n{context}"])
    return [
        {
            "role": "system",
            "content": "You write concise, accurate long-form answers tailored to the user's apparent interests and prior profile.",
        },
        {"role": "user", "content": "\n".join(user_parts)},
    ]


def chat_completion(
    base_url: str,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    timeout: int,
    retries: int,
    retry_base_delay: float,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    return retry_json(f"{base_url.rstrip('/')}/chat/completions", payload, timeout, retries, retry_base_delay)


def write_progress(out: Path, started_at: str, start_time: float, total: int, completed: int, consecutive_errors: int) -> None:
    write_json(
        out / "progress.json",
        {
            "completed_questions": completed,
            "consecutive_errors": consecutive_errors,
            "elapsed_seconds": round(time.perf_counter() - start_time, 3),
            "remaining_questions": total - completed,
            "started_at": started_at,
            "total_questions": total,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )


def write_results_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "question_id",
        "source_config",
        "category",
        "profile_count",
        "retrieved_profile_ids",
        "retrieved_profile_scores",
        "question",
        "e2b_answer",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "question_id": row["question_id"],
                    "source_config": row["source_config"],
                    "category": row["category"],
                    "profile_count": row["profile_count"],
                    "retrieved_profile_ids": ",".join(row["retrieved_profile_ids"]),
                    "retrieved_profile_scores": ",".join(f"{score:.6f}" for score in row["retrieved_profile_scores"]),
                    "question": row["question"],
                    "e2b_answer": row["e2b_answer"],
                }
            )


def read_question_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def select_questions(questions: list[dict[str, Any]], question_ids_file: Path | None) -> list[dict[str, Any]]:
    if question_ids_file is None:
        return questions
    questions_by_id = {question["id"]: question for question in questions}
    question_ids = read_question_ids(question_ids_file)
    missing_question_ids = [question_id for question_id in question_ids if question_id not in questions_by_id]
    if missing_question_ids:
        raise ValueError(f"Question IDs not found in dataset: {missing_question_ids}")
    return [questions_by_id[question_id] for question_id in question_ids]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/lamp_qa_personalization_sample100"))
    parser.add_argument("--out", type=Path, default=Path("evals/lampqa_embedding_e2b_sample100"))
    parser.add_argument("--embedding-base-url", default="http://127.0.0.1:8083/v1")
    parser.add_argument("--embedding-model", default="embeddinggemma-300m")
    parser.add_argument("--chat-base-url", default="http://127.0.0.1:8081/v1")
    parser.add_argument("--chat-model", default="gemma-4-e2b")
    parser.add_argument("--question-ids-file", type=Path, help="Optional newline-delimited question IDs to evaluate.")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--generation-context-k", type=int, default=8)
    parser.add_argument("--embedding-max-chars", type=int, default=2000)
    parser.add_argument("--max-profile-chars", type=int, default=1200)
    parser.add_argument("--max-context-chars", type=int, default=9000)
    parser.add_argument("--max-tokens", type=int, default=384)
    parser.add_argument("--ctx-size", type=int, help="Context size of the chat server used for this run.")
    parser.add_argument("--reasoning", choices=("on", "off", "auto"), default="auto")
    parser.add_argument("--reasoning-budget", type=int, help="Reasoning token budget configured on the chat server.")
    parser.add_argument("--embedding-timeout", type=int, default=180)
    parser.add_argument("--chat-timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-base-delay", type=float, default=2.0)
    parser.add_argument("--max-consecutive-errors", type=int, default=10)
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)

    all_questions = read_jsonl(args.dataset / "questions.jsonl")
    questions = select_questions(all_questions, args.question_ids_file)
    profiles = read_jsonl(args.dataset / "profiles.jsonl")
    profiles_by_question: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for profile in profiles:
        profiles_by_question[profile["question_id"]].append(profile)

    existing_rows_by_id = {row["question_id"]: row for row in read_jsonl(args.out / "results.jsonl")}
    embedding_cache_path = args.out / "embedding_cache.jsonl"
    embedding_cache = load_embedding_cache(embedding_cache_path)

    consecutive_errors = 0
    for question in questions:
        question_id = question["id"]
        if question_id in existing_rows_by_id:
            continue
        try:
            question_embedding = l2_normalize(
                embed_one(
                    embedding_cache,
                    embedding_cache_path,
                    f"question::{question_id}::question+narrative::max_chars={args.embedding_max_chars}",
                    trim_text(build_query_text(question), args.embedding_max_chars),
                    args.embedding_base_url,
                    args.embedding_model,
                    args.embedding_timeout,
                    args.retries,
                    args.retry_base_delay,
                )
            )

            scored_profiles: list[dict[str, Any]] = []
            for profile in profiles_by_question.get(question_id, []):
                profile_text = trim_text(profile["text"], args.embedding_max_chars)
                profile_embedding = l2_normalize(
                    embed_one(
                        embedding_cache,
                        embedding_cache_path,
                        f"profile::{profile['id']}::max_chars={args.embedding_max_chars}",
                        profile_text,
                        args.embedding_base_url,
                        args.embedding_model,
                        args.embedding_timeout,
                        args.retries,
                        args.retry_base_delay,
                    )
                )
                scored_profiles.append({"profile": profile, "score": dot(question_embedding, profile_embedding)})

            scored_profiles.sort(key=lambda row: row["score"], reverse=True)
            context = format_context(
                scored_profiles,
                args.generation_context_k,
                args.max_profile_chars,
                args.max_context_chars,
            )
            used_profiles = scored_profiles[: args.generation_context_k]
            messages = build_prompt(question, context)
            response = chat_completion(
                args.chat_base_url,
                args.chat_model,
                messages,
                args.max_tokens,
                args.chat_timeout,
                args.retries,
                args.retry_base_delay,
            )
            raw_chat_message = response["choices"][0]["message"]
            answer = raw_chat_message.get("content", "")
            result_row = {
                "answered_at": datetime.now(timezone.utc).isoformat(),
                "category": question.get("category", ""),
                "chat_usage": response.get("usage", {}),
                "dataset": "LaMP-QA",
                "e2b_answer": answer,
                "generation_context_k": args.generation_context_k,
                "messages": messages,
                "narrative": question.get("narrative", ""),
                "profile_count": len(scored_profiles),
                "question": question["question"],
                "question_id": question_id,
                "retrieved_profile_ids": [row["profile"]["id"] for row in used_profiles],
                "retrieved_profile_scores": [row["score"] for row in used_profiles],
                "retrieved_profiles": [
                    {
                        "category": row["profile"].get("category", ""),
                        "id": row["profile"]["id"],
                        "score": row["score"],
                        "text": row["profile"]["text"],
                    }
                    for row in used_profiles
                ],
                "raw_chat_message": raw_chat_message,
                "source_config": question.get("source_config", ""),
                "top_k": args.top_k,
            }
            append_jsonl(args.out / "results.jsonl", result_row)
            existing_rows_by_id[question_id] = result_row
            consecutive_errors = 0
            completed = len(existing_rows_by_id)
            write_progress(args.out, started_at, start_time, len(questions), completed, consecutive_errors)
            if completed % 10 == 0:
                print(
                    json.dumps(
                        {
                            "completed": completed,
                            "latest_question_id": question_id,
                            "stage": "lampqa_generation",
                            "total": len(questions),
                        },
                        sort_keys=True,
                    )
                )
        except Exception as exc:  # noqa: BLE001 - durable eval must persist all row failures.
            consecutive_errors += 1
            append_jsonl(
                args.out / "errors.jsonl",
                {
                    "consecutive_errors": consecutive_errors,
                    "error": repr(exc),
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                    "question_id": question_id,
                },
            )
            write_progress(args.out, started_at, start_time, len(questions), len(existing_rows_by_id), consecutive_errors)
            if consecutive_errors >= args.max_consecutive_errors:
                break

    rows = list(existing_rows_by_id.values())
    metrics = {
        "questions": len(rows),
        "target_questions": len(questions),
        "profile_rows": len(profiles),
        "mean_profile_count": sum(row["profile_count"] for row in rows) / len(rows) if rows else 0.0,
    }
    write_json(args.out / "metrics.json", metrics)
    write_results_csv(args.out / "results.csv", rows)
    manifest = {
        "chat_base_url": args.chat_base_url,
        "chat_model": args.chat_model,
        "dataset": str(args.dataset),
        "durability": "embeddings and generation results are append-only jsonl; reruns skip completed question_id rows",
        "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        "embedding_base_url": args.embedding_base_url,
        "embedding_max_chars": args.embedding_max_chars,
        "embedding_model": args.embedding_model,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "generation_context_k": args.generation_context_k,
        "ctx_size": args.ctx_size,
        "max_context_chars": args.max_context_chars,
        "max_profile_chars": args.max_profile_chars,
        "max_tokens": args.max_tokens,
        "output_dir": str(args.out),
        "profile_rows": len(profiles),
        "question_rows_completed": len(rows),
        "question_rows_targeted": len(questions),
        "dataset_question_rows": len(all_questions),
        "question_ids_file": str(args.question_ids_file) if args.question_ids_file else None,
        "reasoning": args.reasoning,
        "reasoning_budget": args.reasoning_budget,
        "retrieval_policy": "rank only profiles linked to the current LaMP-QA question_id",
        "run_type": "lampqa_embedding_chat_resumable_generation",
        "started_at": started_at,
        "temperature": 0,
        "top_k": args.top_k,
    }
    write_json(args.out / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "completed": len(rows),
                "metrics": metrics,
                "out": str(args.out),
                "status": "complete" if len(rows) == len(questions) else "partial",
                "target": len(questions),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
