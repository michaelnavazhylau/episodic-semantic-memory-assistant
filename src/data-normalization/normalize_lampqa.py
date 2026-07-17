#!/usr/bin/env python3
"""Normalize local LaMP-QA validation JSON into personalization files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count


def load_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("version https://git-lfs.github.com/spec/v1"):
        raise ValueError(f"{path} is still a Git LFS pointer, not JSON content")
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError(f"Expected a top-level list in {path}")
    return data


def normalize_lampqa(source: Path, out: Path, split: str) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)

    questions: list[dict[str, Any]] = []
    profiles: list[dict[str, Any]] = []
    manifest_categories: dict[str, dict[str, int]] = {}
    seen_question_ids: set[str] = set()
    seen_profile_ids: set[str] = set()

    split_paths = sorted(source.glob(f"*/{split}/{split}.json"))
    if not split_paths:
        raise FileNotFoundError(f"No LaMP-QA {split} files found under {source}")

    for path in split_paths:
        source_config = path.parts[-3]
        records = load_records(path)
        profile_count = 0

        for record in records:
            raw_question_id = record["id"]
            question_id = f"{source_config}::{raw_question_id}"
            if question_id in seen_question_ids:
                raise ValueError(f"Duplicate question ID after normalization: {question_id}")
            seen_question_ids.add(question_id)

            questions.append(
                {
                    "id": question_id,
                    "original_id": raw_question_id,
                    "question": record["question"],
                    "narrative": record.get("narrative", ""),
                    "category": record.get("category", ""),
                    "source_config": source_config,
                    "split": split,
                    "rubric_aspects": record.get("rubric_aspects", []),
                    "dataset": "LaMP-QA",
                    "task": "personalized_long_form_qa",
                }
            )

            for profile in record.get("profile", []):
                raw_profile_id = profile["id"]
                profile_id = f"{source_config}::{raw_profile_id}"
                if profile_id in seen_profile_ids:
                    raise ValueError(f"Duplicate profile ID after normalization: {profile_id}")
                seen_profile_ids.add(profile_id)
                profile_count += 1
                profiles.append(
                    {
                        "id": profile_id,
                        "original_id": raw_profile_id,
                        "question_id": question_id,
                        "text": profile["text"],
                        "category": profile.get("category", ""),
                        "source_config": source_config,
                        "split": split,
                        "dataset": "LaMP-QA",
                        "memory_type": "semantic_personal",
                    }
                )

        manifest_categories[source_config] = {
            "questions": len(records),
            "profiles": profile_count,
        }

    counts = {
        "questions": write_jsonl(out / "questions.jsonl", questions),
        "profiles": write_jsonl(out / "profiles.jsonl", profiles),
    }
    manifest = {
        "dataset": "LaMP-QA",
        "source": str(source),
        "split": split,
        "categories": manifest_categories,
        "outputs": counts,
        "id_policy": {
            "questions": "<source_config>::<original_id>",
            "profiles": "<source_config>::<original_id>",
        },
        "next_outputs": {
            "retrieved_contexts.jsonl": "created by profile retrieval over profiles.jsonl",
            "answers.jsonl": "created by generation after retrieval is validated",
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    manifest = normalize_lampqa(args.source, args.out, args.split)
    print(json.dumps(manifest["outputs"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
