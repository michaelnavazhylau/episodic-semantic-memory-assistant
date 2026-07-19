#!/usr/bin/env python3
"""Deterministically grade saved EPBench generations by query type."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MONTHS = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}

NON_PERSON_WORDS = {
    "American",
    "Astronomy",
    "Beer",
    "Bethpage",
    "Black",
    "Bridge",
    "Brooklyn",
    "Building",
    "Business",
    "Cathedral",
    "Center",
    "Course",
    "Craft",
    "Cultural",
    "East",
    "Event",
    "Exhibition",
    "Fashion",
    "Festival",
    "Harbor",
    "High",
    "Hills",
    "Historical",
    "History",
    "Ice",
    "IPA",
    "Line",
    "Liberty",
    "Museum",
    "Natural",
    "Networking",
    "Night",
    "Park",
    "Parkour",
    "Performance",
    "Photography",
    "Port",
    "Queensboro",
    "Reenactment",
    "Sculpture",
    "Snug",
    "Square",
    "State",
    "Statue",
    "Tech",
    "Theater",
    "Washington",
    "Woolworth",
    "Workshop",
}

LEADING_NON_ENTITY_WORDS = {"At", "As", "On", "The", "Under", "When"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


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


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("'", "")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def strip_leading_articles(text: str) -> str:
    return re.sub(r"^(?:the|a|an)\s+", "", normalize_text(text))


def normalize_date(month: str, day: str, year: str) -> str:
    return f"{year}-{MONTHS[month.lower()]}-{int(day):02d}"


def extract_dates(text: str) -> set[str]:
    dates: set[str] = set()
    month_pattern = "|".join(month.title() for month in MONTHS)
    for match in re.finditer(rf"\b({month_pattern})\s+(\d{{1,2}}),\s+(\d{{4}})\b", text):
        dates.add(normalize_date(match.group(1), match.group(2), match.group(3)))
    for match in re.finditer(r"\b(\d{4})-(\d{2})-(\d{2})\b", text):
        dates.add(f"{match.group(1)}-{match.group(2)}-{match.group(3)}")
    return dates


def proper_noun_candidates(text: str) -> list[str]:
    return re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b", text)


def clean_candidate(candidate: str) -> str:
    parts = candidate.split()
    while parts and parts[0] in LEADING_NON_ENTITY_WORDS:
        parts = parts[1:]
    return " ".join(parts)


def build_event_inventory(queries: list[dict[str, Any]]) -> set[str]:
    events: set[str] = set()
    patterns = [
        r"events related to ([^.]+?)(?: that|\.|$)",
        r"involving both [A-Z][A-Za-z' -]+ and ([A-Z][A-Za-z' -]+?) at ",
        r"involving [A-Z][A-Za-z' -]+ and ([A-Z][A-Za-z' -]+?) at ",
    ]
    for query in queries:
        text = query["text"]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                event = match.group(1).strip()
                if event:
                    events.add(event)
    return events


def build_location_inventory(queries: list[dict[str, Any]], corpus: list[dict[str, Any]]) -> set[str]:
    locations: set[str] = set()
    for query in queries:
        text = query["text"]
        for match in re.finditer(r"\bat ([A-Z][A-Za-z'. -]+?)(?: on | and |\.|$)", text):
            location = match.group(1).strip()
            if not re.search(r"\b(?:events?|date|dates|location|locations)\b", location, flags=re.I):
                locations.add(location)
    location_words = {
        "Bridge",
        "Building",
        "Cathedral",
        "Center",
        "Course",
        "Harbor",
        "High Line",
        "Museum",
        "Park",
        "Port",
        "Square",
        "Statue",
    }
    for row in corpus:
        for candidate in proper_noun_candidates(row["text"]):
            candidate = clean_candidate(candidate)
            if any(word in candidate for word in location_words):
                locations.add(candidate)
    return {candidate for candidate in locations if candidate}


def build_person_inventory(corpus: list[dict[str, Any]], locations: set[str], events: set[str]) -> set[str]:
    blocked_norms = {normalize_text(item) for item in locations | events}
    people: set[str] = set()
    for row in corpus:
        for candidate in proper_noun_candidates(row["text"]):
            candidate = clean_candidate(candidate)
            if not candidate or normalize_text(candidate) in blocked_norms:
                continue
            parts = candidate.split()
            if len(parts) != 2:
                continue
            if any(part in NON_PERSON_WORDS for part in parts):
                continue
            people.add(candidate)
    return people


def items_in_text(inventory: set[str], text: str) -> set[str]:
    normalized = f" {normalize_text(text)} "
    found: set[str] = set()
    for item in inventory:
        item_norm = strip_leading_articles(item)
        if item_norm and f" {item_norm} " in normalized:
            found.add(item)
    return found


def query_subject_people(query_text: str, person_inventory: set[str]) -> set[str]:
    return items_in_text(person_inventory, query_text)


def item_metrics(gold: set[str], predicted: set[str]) -> dict[str, Any]:
    true_positive = len(gold & predicted)
    false_positive = len(predicted - gold)
    false_negative = len(gold - predicted)
    precision = true_positive / len(predicted) if predicted else (1.0 if not gold else 0.0)
    recall = true_positive / len(gold) if gold else (1.0 if not predicted else 0.0)
    f1 = 0.0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
    }


def tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalize_text(text))


def token_f1(candidate: str, reference: str) -> float:
    candidate_counts = Counter(tokens(candidate))
    reference_counts = Counter(tokens(reference))
    if not candidate_counts and not reference_counts:
        return 1.0
    if not candidate_counts or not reference_counts:
        return 0.0
    overlap = sum((candidate_counts & reference_counts).values())
    precision = overlap / sum(candidate_counts.values())
    recall = overlap / sum(reference_counts.values())
    return 0.0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)


def lcs_len(left: list[str], right: list[str]) -> int:
    previous = [0] * (len(right) + 1)
    for left_item in left:
        current = [0]
        for index, right_item in enumerate(right, start=1):
            if left_item == right_item:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[-1]))
        previous = current
    return previous[-1]


def rouge_l_f1(candidate: str, reference: str) -> float:
    candidate_tokens = tokens(candidate)
    reference_tokens = tokens(reference)
    if not candidate_tokens and not reference_tokens:
        return 1.0
    if not candidate_tokens or not reference_tokens:
        return 0.0
    lcs = lcs_len(candidate_tokens, reference_tokens)
    precision = lcs / len(candidate_tokens)
    recall = lcs / len(reference_tokens)
    return 0.0 if precision + recall == 0 else (2 * precision * recall) / (precision + recall)


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


def l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        raise ValueError("Embedding vector has zero norm")
    return [value / norm for value in vector]


def dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def load_embedding_cache(path: Path) -> dict[str, list[float]]:
    if not path.exists():
        return {}
    return {row["cache_key"]: row["embedding"] for row in read_jsonl(path)}


def append_embedding_cache(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def embed_text(
    cache: dict[str, list[float]],
    cache_path: Path,
    cache_key: str,
    text: str,
    base_url: str,
    model: str,
    timeout: int,
) -> list[float]:
    if cache_key in cache:
        return cache[cache_key]
    result = post_json(f"{base_url.rstrip('/')}/embeddings", {"model": model, "input": [text]}, timeout)
    embedding = result["data"][0]["embedding"]
    cache[cache_key] = embedding
    append_embedding_cache(
        cache_path,
        {
            "cache_key": cache_key,
            "embedding": embedding,
            "embedded_at": datetime.now(timezone.utc).isoformat(),
            "model": model,
        },
    )
    return embedding


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def grade_row(
    row: dict[str, Any],
    query: dict[str, Any],
    gold_text: str,
    person_inventory: set[str],
    location_inventory: set[str],
) -> dict[str, Any]:
    answer = row["e2b_answer"]
    query_type = row["query_type"]
    query_people = query_subject_people(query["text"], person_inventory)

    gold_dates = extract_dates(gold_text)
    predicted_dates = extract_dates(answer)
    gold_people = items_in_text(person_inventory, gold_text)
    predicted_people = items_in_text(person_inventory, answer)
    gold_locations = items_in_text(location_inventory, gold_text)
    predicted_locations = items_in_text(location_inventory, answer)

    if query_type == "Other_entities":
        gold_people -= query_people
        predicted_people -= query_people

    date_metrics = item_metrics(gold_dates, predicted_dates)
    person_metrics = item_metrics(gold_people, predicted_people)
    location_metrics = item_metrics(gold_locations, predicted_locations)

    gold_anchors = {f"date:{item}" for item in gold_dates}
    gold_anchors |= {f"person:{item}" for item in gold_people}
    gold_anchors |= {f"location:{item}" for item in gold_locations}
    predicted_anchors = {f"date:{item}" for item in predicted_dates}
    predicted_anchors |= {f"person:{item}" for item in predicted_people}
    predicted_anchors |= {f"location:{item}" for item in predicted_locations}
    anchor_metrics = item_metrics(gold_anchors, predicted_anchors)

    lexical_token_f1 = token_f1(answer, gold_text)
    lexical_rouge_l_f1 = rouge_l_f1(answer, gold_text)
    lexical_mean = mean([lexical_token_f1, lexical_rouge_l_f1])

    if query_type == "Times":
        primary_score = date_metrics["f1"]
        primary_metric = "date_set_f1"
    elif query_type in {"Entities", "Other_entities"}:
        primary_score = person_metrics["f1"]
        primary_metric = "person_set_f1"
    elif query_type == "Spaces":
        primary_score = location_metrics["f1"]
        primary_metric = "location_set_f1"
    else:
        primary_score = (0.6 * anchor_metrics["f1"]) + (0.4 * lexical_mean)
        primary_metric = "0.6_anchor_f1_plus_0.4_lexical_mean"

    return {
        "query_id": row["query_id"],
        "query_type": query_type,
        "primary_metric": primary_metric,
        "primary_score": primary_score,
        "date_precision": date_metrics["precision"],
        "date_recall": date_metrics["recall"],
        "date_f1": date_metrics["f1"],
        "person_precision": person_metrics["precision"],
        "person_recall": person_metrics["recall"],
        "person_f1": person_metrics["f1"],
        "location_precision": location_metrics["precision"],
        "location_recall": location_metrics["recall"],
        "location_f1": location_metrics["f1"],
        "anchor_precision": anchor_metrics["precision"],
        "anchor_recall": anchor_metrics["recall"],
        "anchor_f1": anchor_metrics["f1"],
        "token_f1": lexical_token_f1,
        "rouge_l_f1": lexical_rouge_l_f1,
        "lexical_mean_f1": lexical_mean,
        "gold_dates": sorted(gold_dates),
        "predicted_dates": sorted(predicted_dates),
        "gold_people": sorted(gold_people),
        "predicted_people": sorted(predicted_people),
        "gold_locations": sorted(gold_locations),
        "predicted_locations": sorted(predicted_locations),
        "query_text": row["query_text"],
        "e2b_answer": answer,
    }


def add_semantic_scores(
    rows: list[dict[str, Any]],
    result_rows_by_id: dict[str, dict[str, Any]],
    gold_text_by_id: dict[str, str],
    out_dir: Path,
    base_url: str,
    model: str,
    timeout: int,
) -> None:
    cache_path = out_dir / "deterministic_grade_embedding_cache.jsonl"
    cache = load_embedding_cache(cache_path)
    for index, graded in enumerate(rows, start=1):
        query_id = graded["query_id"]
        answer = result_rows_by_id[query_id]["e2b_answer"]
        gold_text = gold_text_by_id[query_id]
        answer_embedding = l2_normalize(
            embed_text(cache, cache_path, f"answer::{query_id}", answer, base_url, model, timeout)
        )
        gold_embedding = l2_normalize(
            embed_text(cache, cache_path, f"gold::{query_id}", gold_text, base_url, model, timeout)
        )
        graded["semantic_cosine"] = dot(answer_embedding, gold_embedding)
        if index % 25 == 0:
            print(json.dumps({"stage": "semantic_similarity", "completed": index, "total": len(rows)}, sort_keys=True))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "query_id",
        "query_type",
        "primary_metric",
        "primary_score",
        "date_f1",
        "person_f1",
        "location_f1",
        "anchor_f1",
        "token_f1",
        "rouge_l_f1",
        "lexical_mean_f1",
        "semantic_cosine",
        "gold_dates",
        "predicted_dates",
        "gold_people",
        "predicted_people",
        "gold_locations",
        "predicted_locations",
        "query_text",
        "e2b_answer",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            for field in (
                "gold_dates",
                "predicted_dates",
                "gold_people",
                "predicted_people",
                "gold_locations",
                "predicted_locations",
            ):
                csv_row[field] = json.dumps(csv_row[field], ensure_ascii=False)
            csv_row.setdefault("semantic_cosine", "")
            writer.writerow({field: csv_row[field] for field in fieldnames})


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_type[row["query_type"]].append(row)
    metrics: dict[str, Any] = {
        "queries": len(rows),
        "primary_score": mean([row["primary_score"] for row in rows]),
        "date_f1": mean([row["date_f1"] for row in rows]),
        "person_f1": mean([row["person_f1"] for row in rows]),
        "location_f1": mean([row["location_f1"] for row in rows]),
        "anchor_f1": mean([row["anchor_f1"] for row in rows]),
        "token_f1": mean([row["token_f1"] for row in rows]),
        "rouge_l_f1": mean([row["rouge_l_f1"] for row in rows]),
        "lexical_mean_f1": mean([row["lexical_mean_f1"] for row in rows]),
    }
    if all("semantic_cosine" in row for row in rows):
        metrics["semantic_cosine"] = mean([row["semantic_cosine"] for row in rows])
    metrics["by_query_type"] = {}
    for query_type, query_rows in sorted(by_type.items()):
        type_metrics = {
            "queries": len(query_rows),
            "primary_score": mean([row["primary_score"] for row in query_rows]),
            "date_f1": mean([row["date_f1"] for row in query_rows]),
            "person_f1": mean([row["person_f1"] for row in query_rows]),
            "location_f1": mean([row["location_f1"] for row in query_rows]),
            "anchor_f1": mean([row["anchor_f1"] for row in query_rows]),
            "token_f1": mean([row["token_f1"] for row in query_rows]),
            "rouge_l_f1": mean([row["rouge_l_f1"] for row in query_rows]),
            "lexical_mean_f1": mean([row["lexical_mean_f1"] for row in query_rows]),
        }
        if all("semantic_cosine" in row for row in query_rows):
            type_metrics["semantic_cosine"] = mean([row["semantic_cosine"] for row in query_rows])
        metrics["by_query_type"][query_type] = type_metrics
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", type=Path, default=Path("evals/epbench_embedding_e2b_full"))
    parser.add_argument("--dataset", type=Path, default=Path("data/processed/epbench_episodic"))
    parser.add_argument("--results-jsonl", default="results.jsonl")
    parser.add_argument("--prefix", default="deterministic_grade")
    parser.add_argument("--embedding-base-url")
    parser.add_argument("--embedding-model", default="embeddinggemma-300m")
    parser.add_argument("--embedding-timeout", type=int, default=180)
    args = parser.parse_args()

    started_at = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()

    result_rows = read_jsonl(args.eval_dir / args.results_jsonl)
    corpus = read_jsonl(args.dataset / "corpus.jsonl")
    queries = read_jsonl(args.dataset / "queries.jsonl")
    qrels = read_qrels(args.dataset / "qrels.tsv")

    corpus_by_id = {row["id"]: row for row in corpus}
    queries_by_id = {row["id"]: row for row in queries}
    result_rows_by_id = {row["query_id"]: row for row in result_rows}

    event_inventory = build_event_inventory(queries)
    location_inventory = build_location_inventory(queries, corpus)
    person_inventory = build_person_inventory(corpus, location_inventory, event_inventory)

    gold_text_by_id = {
        row["query_id"]: "\n\n".join(corpus_by_id[doc_id]["text"] for doc_id in qrels[row["query_id"]])
        for row in result_rows
    }
    graded_rows = [
        grade_row(
            row,
            queries_by_id[row["query_id"]],
            gold_text_by_id[row["query_id"]],
            person_inventory,
            location_inventory,
        )
        for row in result_rows
    ]

    if args.embedding_base_url:
        add_semantic_scores(
            graded_rows,
            result_rows_by_id,
            gold_text_by_id,
            args.eval_dir,
            args.embedding_base_url,
            args.embedding_model,
            args.embedding_timeout,
        )

    metrics = aggregate(graded_rows)
    manifest = {
        "run_type": "epbench_deterministic_generation_grading",
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        "eval_dir": str(args.eval_dir),
        "dataset": str(args.dataset),
        "results_jsonl": args.results_jsonl,
        "queries": len(graded_rows),
        "person_inventory_size": len(person_inventory),
        "location_inventory_size": len(location_inventory),
        "event_inventory_size": len(event_inventory),
        "semantic_similarity_enabled": bool(args.embedding_base_url),
        "semantic_embedding_model": args.embedding_model if args.embedding_base_url else None,
        "score_policy": {
            "Entities": "person set F1 over gold qrel passages and response",
            "Other_entities": "person set F1, excluding people named in the query",
            "Spaces": "location set F1 over known EPBench location inventory",
            "Times": "normalized date set F1",
            "Event_contents": "0.6 * anchor set F1 + 0.4 * mean(token F1, ROUGE-L F1)",
            "Full_event_details": "0.6 * anchor set F1 + 0.4 * mean(token F1, ROUGE-L F1)",
        },
    }

    jsonl_path = args.eval_dir / f"{args.prefix}_scores.jsonl"
    csv_path = args.eval_dir / f"{args.prefix}_scores.csv"
    metrics_path = args.eval_dir / f"{args.prefix}_metrics.json"
    manifest_path = args.eval_dir / f"{args.prefix}_manifest.json"

    jsonl_path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in graded_rows),
        encoding="utf-8",
    )
    write_csv(csv_path, graded_rows)
    write_json(metrics_path, metrics)
    write_json(manifest_path, manifest)

    print(json.dumps({"status": "ok", "metrics": metrics, "out": str(args.eval_dir)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
