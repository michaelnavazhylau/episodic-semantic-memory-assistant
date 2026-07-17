#!/usr/bin/env python3
"""Normalize local LMEB parquet retrieval datasets into JSONL/TSV files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import pyarrow.parquet as pq


EPBENCH_QUERY_TYPES = (
    "Entities",
    "Event_contents",
    "Full_event_details",
    "Other_entities",
    "Spaces",
    "Times",
)


def read_parquet_rows(path: Path) -> list[dict[str, Any]]:
    return pq.read_table(path).to_pylist()


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
            count += 1
    return count


def write_qrels(path: Path, rows: Iterable[tuple[str, str, int | float]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for query_id, corpus_id, score in rows:
            handle.write(f"{query_id}\t{corpus_id}\t{score}\n")
            count += 1
    return count


def single_parquet_file(directory: Path) -> Path:
    files = sorted(directory.glob("*.parquet"))
    if len(files) != 1:
        raise ValueError(f"Expected exactly one parquet file in {directory}, found {len(files)}")
    return files[0]


def normalize_epbench(source: Path, out: Path, variant: str) -> dict[str, Any]:
    variant_dir = source / variant
    if not variant_dir.is_dir():
        raise FileNotFoundError(f"Missing EPBench variant directory: {variant_dir}")

    out.mkdir(parents=True, exist_ok=True)

    corpus_by_id: dict[str, dict[str, Any]] = {}
    queries: list[dict[str, Any]] = []
    qrels: list[tuple[str, str, int | float]] = []
    per_query_type: dict[str, dict[str, int]] = {}

    for query_type in EPBENCH_QUERY_TYPES:
        corpus_dir = variant_dir / f"{query_type}-corpus"
        queries_dir = variant_dir / f"{query_type}-queries"
        qrels_dir = variant_dir / f"{query_type}-qrels"
        for directory in (corpus_dir, queries_dir, qrels_dir):
            if not directory.is_dir():
                raise FileNotFoundError(f"Missing EPBench directory: {directory}")

        corpus_rows = read_parquet_rows(single_parquet_file(corpus_dir))
        query_rows = read_parquet_rows(single_parquet_file(queries_dir))
        qrel_rows = read_parquet_rows(single_parquet_file(qrels_dir))

        for row in corpus_rows:
            normalized_id = f"{variant}::{row['id']}"
            normalized = {
                "id": normalized_id,
                "original_id": row["id"],
                "title": row.get("title") or "",
                "text": row["text"],
                "dataset": "EPBench",
                "memory_type": "episodic",
                "variant": variant,
            }
            existing = corpus_by_id.get(normalized_id)
            if existing and (existing["text"] != normalized["text"] or existing["title"] != normalized["title"]):
                raise ValueError(f"Conflicting corpus rows for {normalized_id}")
            corpus_by_id[normalized_id] = normalized

        for row in query_rows:
            queries.append(
                {
                    "id": f"{variant}::{query_type}::{row['id']}",
                    "original_id": row["id"],
                    "text": row["text"],
                    "dataset": "EPBench",
                    "target_memory_type": "episodic",
                    "variant": variant,
                    "query_type": query_type,
                }
            )

        for row in qrel_rows:
            qrels.append(
                (
                    f"{variant}::{query_type}::{row['query-id']}",
                    f"{variant}::{row['corpus-id']}",
                    row["score"],
                )
            )

        per_query_type[query_type] = {
            "corpus_rows_seen": len(corpus_rows),
            "queries": len(query_rows),
            "qrels": len(qrel_rows),
        }

    counts = {
        "corpus": write_jsonl(out / "corpus.jsonl", corpus_by_id.values()),
        "queries": write_jsonl(out / "queries.jsonl", queries),
        "qrels": write_qrels(out / "qrels.tsv", qrels),
    }
    manifest = {
        "dataset": "EPBench",
        "memory_type": "episodic",
        "source": str(source),
        "variant": variant,
        "query_types": per_query_type,
        "outputs": counts,
        "id_policy": {
            "corpus": "<variant>::<original_id>",
            "queries": "<variant>::<query_type>::<original_id>",
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--dataset", choices=("epbench",), required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--variant", default="default_claude_short")
    args = parser.parse_args()

    manifest = normalize_epbench(args.source, args.out, args.variant)

    print(json.dumps(manifest["outputs"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
