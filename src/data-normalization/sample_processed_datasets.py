#!/usr/bin/env python3
"""Create reproducible samples from processed benchmark datasets."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
            count += 1
    return count


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def sample_rows(rows: list[dict[str, Any]], sample_size: int, seed: int) -> list[dict[str, Any]]:
    if sample_size > len(rows):
        raise ValueError(f"Cannot sample {sample_size} rows from {len(rows)} rows")
    rng = random.Random(seed)
    sampled = rng.sample(rows, sample_size)
    sampled_ids = {row["id"] for row in sampled}
    return [row for row in rows if row["id"] in sampled_ids]


def sample_lampqa(source: Path, out: Path, sample_size: int, seed: int) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    questions = read_jsonl(source / "questions.jsonl")
    profiles = read_jsonl(source / "profiles.jsonl")

    sampled_questions = sample_rows(questions, sample_size, seed)
    sampled_question_ids = {row["id"] for row in sampled_questions}
    sampled_profiles = [row for row in profiles if row["question_id"] in sampled_question_ids]

    profiles_by_question: dict[str, int] = defaultdict(int)
    for row in sampled_profiles:
        profiles_by_question[row["question_id"]] += 1

    counts = {
        "questions": write_jsonl(out / "questions.jsonl", sampled_questions),
        "profiles": write_jsonl(out / "profiles.jsonl", sampled_profiles),
    }
    manifest = {
        "dataset": "LaMP-QA",
        "sampled_from": str(source),
        "sample_size": sample_size,
        "seed": seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "outputs": counts,
        "profile_fanout": {
            "min": min(profiles_by_question.values()) if profiles_by_question else 0,
            "max": max(profiles_by_question.values()) if profiles_by_question else 0,
            "mean": sum(profiles_by_question.values()) / len(profiles_by_question) if profiles_by_question else 0,
        },
    }
    write_json(out / "manifest.json", manifest)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=("lampqa",), required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    manifest = sample_lampqa(args.source, args.out, args.sample_size, args.seed)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
