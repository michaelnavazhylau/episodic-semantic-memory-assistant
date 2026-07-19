# EPBench Embedding + E2B Full Eval

This run evaluates the full processed EPBench query set with embedding retrieval, E2B answer generation, and deterministic EPBench grading.

Pinned grading policy: deterministic query-type grading is the primary EPBench score. Semantic similarity is a secondary diagnostic. LLM-as-judge scores are retained only as fallback diagnostics for prose-heavy answers.

```text
data/processed/epbench_episodic
  -> EmbeddingGemma embeddings
  -> cosine top-10 retrieval
  -> top-10 retrieved passages injected into Gemma E2B
  -> E2B final answer
  -> deterministic query-type grader against gold qrel passages
  -> optional semantic similarity and LLM-as-judge diagnostics
```

## Scope

- Query rows generated: `276`
- Gold qrel rows used for retrieval/judging: `378`
- Corpus passages: `19`
- Generation context: top `10` retrieved passages
- E2B reasoning: disabled at server startup with `--reasoning off`
- Primary grader: `src/evals/grade_epbench_deterministic.py`
- Secondary semantic score: EmbeddingGemma normalized dot product/cosine similarity
- Diagnostic judge: `nvidia/nemotron-3-ultra-550b-a55b:free`, reasoning disabled, partial due rate limit

## Generation And Retrieval Status

Generation completed for all `276` query rows.

```json
{
  "queries": 276,
  "hit_at_1": 0.8876811594202898,
  "hit_at_3": 0.9710144927536232,
  "hit_at_5": 0.9927536231884058,
  "hit_at_10": 1.0,
  "recall_at_10": 0.9963768115942029,
  "mrr": 0.9313750862663905,
  "ndcg_at_10": 0.9430171304195293
}
```

## Judge Status

Nemotron scoring is partial because OpenRouter hit the daily free-model limit after `31` successful scores.

```json
{
  "answers": 31,
  "mean_answer_score": 3.096774193548387,
  "pass_count": 9,
  "partial_count": 17,
  "fail_count": 5,
  "score_distribution": {
    "0": 1,
    "1": 3,
    "2": 7,
    "3": 10,
    "4": 1,
    "5": 9
  }
}
```

OpenRouter returned `HTTP 429` with `free-models-per-day` exhausted. The reset time reported by OpenRouter was `2026-07-20T00:00:00Z`.

The remaining `245` answers were then scored with local E2B as judge, skipping the `31` query IDs already scored by Nemotron.

```json
{
  "answers": 245,
  "mean_answer_score": 3.6857142857142855,
  "pass_count": 158,
  "partial_count": 63,
  "fail_count": 24,
  "score_distribution": {
    "0": 10,
    "1": 27,
    "2": 11,
    "3": 39,
    "4": 53,
    "5": 105
  }
}
```

Mixed judge coverage is now `276/276`: `31` Nemotron-judged rows plus `245` E2B-judged rows.

```json
{
  "answers": 276,
  "mean_answer_score": 3.619565217391304,
  "pass_count": 167,
  "partial_count": 80,
  "fail_count": 29,
  "score_distribution": {
    "0": 11,
    "1": 30,
    "2": 18,
    "3": 49,
    "4": 54,
    "5": 114
  }
}
```

The mixed aggregate should be read as operational coverage, not a single clean judge benchmark, because it combines two different judging models.

To resume the Nemotron-only judge pass after the limit resets or credits are added:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/score_epbench_answers_openrouter.py \
  --eval-dir evals/epbench_embedding_e2b_full \
  --dataset data/processed/epbench_episodic \
  --judge-model nvidia/nemotron-3-ultra-550b-a55b:free \
  --reasoning off \
  --max-tokens 768 \
  --prefix nemotron_no_reason_answer
```

The scorer is resumable: it appends successful judge rows to `nemotron_no_reason_answer_scores.jsonl` and skips already-scored `query_id` rows on retry.

## Durability

- `embedding_cache.jsonl`: append-only embedding cache for corpus and query rows
- `results.jsonl`: append-only generated E2B answers; reruns skip completed `query_id` rows
- `errors.jsonl`: generation errors retained for audit
- `progress.json`: latest generation checkpoint
- `nemotron_no_reason_answer_scores.jsonl`: append-only Nemotron scores
- `nemotron_no_reason_answer_errors.jsonl`: judge errors retained for audit
- `nemotron_no_reason_answer_progress.json`: latest judge checkpoint
- `e2b_remaining_answer_scores.jsonl`: append-only local E2B judge scores for rows not scored by Nemotron
- `e2b_remaining_answer_metrics.json`: local E2B judge metrics for the remaining rows
- `e2b_remaining_answer_progress.json`: latest local E2B judge checkpoint
- `deterministic_grade_scores.jsonl`: offline deterministic grading rows
- `deterministic_grade_metrics.json`: offline deterministic aggregate metrics
- `deterministic_grade_semantic_scores.jsonl`: deterministic grading rows with embedding cosine similarity
- `deterministic_grade_semantic_metrics.json`: deterministic aggregate metrics with semantic similarity

The four generation errors in `errors.jsonl` came from a rejected 4-worker run that exceeded the local E2B KV cache. Those same queries were retried successfully by the sequential run and are present in `results.jsonl`.

## Deterministic Grader

The deterministic grader avoids LLM-as-judge for the query types that can be scored structurally:

- `Times`: normalized date set F1
- `Entities`: person-name set F1
- `Spaces`: known-location set F1
- `Other_entities`: person-name set F1 after excluding people named in the query
- `Event_contents` and `Full_event_details`: anchor set F1 plus lexical overlap

Offline command:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/grade_epbench_deterministic.py \
  --eval-dir evals/epbench_embedding_e2b_full \
  --dataset data/processed/epbench_episodic \
  --prefix deterministic_grade
```

Semantic-enabled command:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/grade_epbench_deterministic.py \
  --eval-dir evals/epbench_embedding_e2b_full \
  --dataset data/processed/epbench_episodic \
  --prefix deterministic_grade_semantic \
  --embedding-base-url http://127.0.0.1:8083/v1 \
  --embedding-model embeddinggemma-300m
```

Deterministic headline metrics:

```json
{
  "queries": 276,
  "primary_score": 0.65970197848199,
  "semantic_cosine": 0.43375904278648714,
  "by_query_type": {
    "Entities": {
      "primary_score": 0.7571837884337884,
      "person_f1": 0.7571837884337884,
      "semantic_cosine": 0.34567668901772197
    },
    "Times": {
      "primary_score": 0.857936507936508,
      "date_f1": 0.857936507936508,
      "semantic_cosine": 0.32394553106721347
    },
    "Spaces": {
      "primary_score": 0.6249496981891348,
      "location_f1": 0.6249496981891348,
      "semantic_cosine": 0.3277003534275162
    },
    "Other_entities": {
      "primary_score": 0.8933333333333333,
      "person_f1": 0.8933333333333333,
      "semantic_cosine": 0.7182593309720839
    },
    "Event_contents": {
      "primary_score": 0.39913916688481005,
      "anchor_f1": 0.5159167248590787,
      "semantic_cosine": 0.6628356650869277
    },
    "Full_event_details": {
      "primary_score": 0.7511568808253808,
      "anchor_f1": 0.9338217338217338,
      "semantic_cosine": 0.899775154784721
    }
  }
}
```
