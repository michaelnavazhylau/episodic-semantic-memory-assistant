#!/usr/bin/env python3
"""Validate a processed retrieval dataset directory."""

from __future__ import annotations

import argparse
import json
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


def read_qrels(path: Path) -> list[tuple[str, str, float]]:
    rows: list[tuple[str, str, float]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                raise ValueError(f"{path}:{line_number}: expected 3 tab-separated fields")
            query_id, corpus_id, score = parts
            rows.append((query_id, corpus_id, float(score)))
    return rows


def require_unique_ids(rows: list[dict[str, Any]], label: str) -> set[str]:
    ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        row_id = row.get("id")
        if not isinstance(row_id, str) or not row_id:
            raise ValueError(f"{label} row {index} has missing or invalid id")
        if row_id in ids:
            raise ValueError(f"{label} has duplicate id: {row_id}")
        ids.add(row_id)
    return ids


def validate(dataset_dir: Path) -> dict[str, int]:
    corpus_path = dataset_dir / "corpus.jsonl"
    queries_path = dataset_dir / "queries.jsonl"
    qrels_path = dataset_dir / "qrels.tsv"
    candidates_path = dataset_dir / "candidates.jsonl"

    for path in (corpus_path, queries_path, qrels_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

    corpus = read_jsonl(corpus_path)
    queries = read_jsonl(queries_path)
    qrels = read_qrels(qrels_path)

    corpus_ids = require_unique_ids(corpus, "corpus")
    query_ids = require_unique_ids(queries, "queries")

    missing_qrel_queries = sorted({query_id for query_id, _, _ in qrels if query_id not in query_ids})
    missing_qrel_docs = sorted({corpus_id for _, corpus_id, _ in qrels if corpus_id not in corpus_ids})
    if missing_qrel_queries:
        raise ValueError(f"qrels reference {len(missing_qrel_queries)} missing query IDs")
    if missing_qrel_docs:
        raise ValueError(f"qrels reference {len(missing_qrel_docs)} missing corpus IDs")

    counts = {
        "corpus": len(corpus),
        "queries": len(queries),
        "qrels": len(qrels),
    }

    if candidates_path.exists():
        candidates = read_jsonl(candidates_path)
        missing_candidate_queries: set[str] = set()
        missing_candidate_docs: set[str] = set()
        for index, row in enumerate(candidates, start=1):
            query_id = row.get("query_id")
            candidate_doc_ids = row.get("candidate_doc_ids")
            if not isinstance(query_id, str) or not query_id:
                raise ValueError(f"candidates row {index} has missing query_id")
            if query_id not in query_ids:
                missing_candidate_queries.add(query_id)
            if not isinstance(candidate_doc_ids, list):
                raise ValueError(f"candidates row {index} has non-list candidate_doc_ids")
            missing_candidate_docs.update(doc_id for doc_id in candidate_doc_ids if doc_id not in corpus_ids)
        if missing_candidate_queries:
            raise ValueError(f"candidates reference {len(missing_candidate_queries)} missing query IDs")
        if missing_candidate_docs:
            raise ValueError(f"candidates reference {len(missing_candidate_docs)} missing corpus IDs")
        counts["candidates"] = len(candidates)

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_dir", type=Path)
    args = parser.parse_args()

    counts = validate(args.dataset_dir)
    print(json.dumps({"status": "ok", "counts": counts}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
