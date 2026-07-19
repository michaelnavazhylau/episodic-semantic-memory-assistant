# EPBench Smoke Eval

This is a 10-query deterministic retrieval smoke test over
`data/processed/epbench_episodic`.

## Server

The run used the local OpenAI-compatible `llama-server` embeddings endpoint from
`src/docs/openai-llama-benchmarking.md`, with a larger physical batch size so
full EPBench corpus rows fit without truncation:

```bash
llama-server \
  -m /Users/michaelnavazhylau/.cache/huggingface/hub/models--ggml-org--embeddinggemma-300M-GGUF/snapshots/0f741b5a6585bd53aeb15cd1372c56f2a0f65e12/embeddinggemma-300M-Q8_0.gguf \
  --embeddings \
  --alias embeddinggemma-300m \
  --host 127.0.0.1 \
  --port 8083 \
  --ctx-size 1024 \
  --batch-size 1024 \
  --ubatch-size 1024
```

## Eval Command

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/run_epbench_smoke.py \
  --dataset data/processed/epbench_episodic \
  --out evals/epbench_smoke \
  --base-url http://127.0.0.1:8083/v1 \
  --model embeddinggemma-300m \
  --limit 10 \
  --top-k 10
```

## Outputs

- `results.csv`: per-query grades and top-10 rankings.
- `results.jsonl`: per-query grades and top-10 rankings as JSON.
- `metrics.json`: aggregate deterministic retrieval grades.
- `manifest.json`: run metadata.

## Metrics

```json
{
  "hit_at_1": 1.0,
  "hit_at_3": 1.0,
  "hit_at_5": 1.0,
  "hit_at_10": 1.0,
  "mrr": 1.0,
  "ndcg_at_10": 1.0,
  "queries": 10,
  "recall_at_10": 1.0
}
```

All 10 smoke-test rows passed by retrieving at least one gold qrel document in
the top 10. In this run, each first relevant document appeared at rank 1.
