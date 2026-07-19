# EPBench Embedding + E2B Top-10 Context Smoke Eval

This run checks the full 10-row EPBench path:

```text
EPBench processed data
  -> EmbeddingGemma query/document embeddings
  -> cosine top-10 retrieval
  -> top-10 retrieved passages injected into Gemma E2B
  -> final LLM answer
  -> Nemotron LLM-as-judge scoring against all gold qrel passages
```

## Run Configuration

- Dataset: `data/processed/epbench_episodic`
- Query limit: `10`
- Embedding model: `embeddinggemma-300m`
- Chat model: `gemma-4-e2b`
- Retrieved context injected into generation: top `10` passages
- Chat reasoning: disabled at server startup with `--reasoning off`
- Judge model: `nvidia/nemotron-3-ultra-550b-a55b:free`
- Judge reasoning: disabled

## Retrieval Results

The deterministic retrieval metrics use `qrels.tsv`.

```json
{
  "queries": 10,
  "hit_at_1": 1.0,
  "hit_at_3": 1.0,
  "hit_at_5": 1.0,
  "hit_at_10": 1.0,
  "recall_at_10": 1.0,
  "mrr": 1.0,
  "ndcg_at_10": 1.0
}
```

## Nemotron Judge Results

Nemotron scored the generated final LLM answers against the gold qrel passages.

```json
{
  "answers": 10,
  "mean_answer_score": 4.0,
  "pass_count": 6,
  "partial_count": 3,
  "fail_count": 1,
  "score_distribution": {
    "0": 0,
    "1": 1,
    "2": 0,
    "3": 3,
    "4": 0,
    "5": 6
  }
}
```

This revised run improves over the prior top-1 context run, where Nemotron judged the answers at mean `3.1/5`. The retrieval stage already found the right gold passages for this smoke set; the key change here is that E2B now receives the full retrieved top-10 context instead of only the top document.

## Artifacts

- `manifest.json`: generation run metadata
- `metrics.json`: deterministic retrieval metrics
- `results.csv`: per-query retrieval and E2B generation output
- `results.jsonl`: full per-query retrieval and E2B generation output
- `nemotron_no_reason_answer_metrics.json`: Nemotron aggregate answer scores
- `nemotron_no_reason_answer_scores.csv`: per-query Nemotron scores
- `nemotron_no_reason_answer_scores.jsonl`: full per-query Nemotron judge output
- `nemotron_no_reason_answer_score_manifest.json`: Nemotron judge run metadata

## Notes

- Retrieval scores are deterministic for this processed dataset and qrels file.
- Nemotron scores are LLM-as-judge scores, so they are useful for smoke testing generation quality but are not deterministic in the same way as retrieval metrics.
