#!/usr/bin/env python3
"""Validate processed LaMP-QA personalization files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
    return rows


def unique_ids(rows: list[dict[str, Any]], label: str) -> set[str]:
    ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise ValueError(f"{label} row {index} has missing or invalid id")
        if row_id in ids:
            raise ValueError(f"{label} has duplicate id: {row_id}")
        ids.add(row_id)
    return ids


def validate(dataset_dir: Path) -> dict[str, Any]:
    questions_path = dataset_dir / "questions.jsonl"
    profiles_path = dataset_dir / "profiles.jsonl"
    for path in (questions_path, profiles_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

    questions = read_jsonl(questions_path)
    profiles = read_jsonl(profiles_path)
    question_ids = unique_ids(questions, "questions")
    unique_ids(profiles, "profiles")

    missing_profile_question_ids = sorted(
        {
            row.get("question_id")
            for row in profiles
            if not isinstance(row.get("question_id"), str) or row["question_id"] not in question_ids
        }
    )
    if missing_profile_question_ids:
        raise ValueError(f"profiles reference {len(missing_profile_question_ids)} missing question IDs")

    profile_counts = Counter(row["question_id"] for row in profiles)
    questions_without_profiles = sorted(question_id for question_id in question_ids if profile_counts[question_id] == 0)
    if questions_without_profiles:
        raise ValueError(f"{len(questions_without_profiles)} questions have no profiles")

    source_configs = Counter(row.get("source_config", "") for row in questions)
    return {
        "questions": len(questions),
        "profiles": len(profiles),
        "source_configs": dict(sorted(source_configs.items())),
        "min_profiles_per_question": min(profile_counts.values()),
        "max_profiles_per_question": max(profile_counts.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_dir", type=Path)
    args = parser.parse_args()

    counts = validate(args.dataset_dir)
    print(json.dumps({"status": "ok", "counts": counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
