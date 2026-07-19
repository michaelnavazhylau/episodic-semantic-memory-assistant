# EPBench Embedding + E2B Smoke Eval

This is a 10-query EPBench smoke test over
`data/processed/epbench_episodic`.

The run uses:

- `embeddinggemma-300m` for retrieval embeddings.
- `gemma-4-e2b` for answer generation from the top retrieved context.
- Deterministic qrels-based grading for retrieval only.

EPBench does not provide gold generated answers in the processed dataset, so
`e2b_answer` is saved for inspection but is not deterministically graded here.

## Servers

Embedding server:

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

E2B chat server, with reasoning disabled:

```bash
llama-server \
  -m /Users/michaelnavazhylau/.cache/huggingface/hub/models--google--gemma-4-E2B-it-qat-q4_0-gguf/snapshots/675cff42a74c774d6cb76f76d8eacb49b48c9b93/gemma-4-E2B_q4_0-it.gguf \
  --alias gemma-4-e2b \
  --host 127.0.0.1 \
  --port 8081 \
  --ctx-size 2048 \
  --batch-size 1024 \
  --ubatch-size 1024 \
  --reasoning off
```

Reasoning is disabled so responses are returned in normal
`choices[0].message.content` instead of being consumed by
`reasoning_content`.

## Eval Command

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/run_epbench_embedding_e2b_smoke.py \
  --dataset data/processed/epbench_episodic \
  --out evals/epbench_embedding_e2b_smoke \
  --embedding-base-url http://127.0.0.1:8083/v1 \
  --embedding-model embeddinggemma-300m \
  --chat-base-url http://127.0.0.1:8081/v1 \
  --chat-model gemma-4-e2b \
  --limit 10 \
  --top-k 10 \
  --max-tokens 96
```

## Outputs

- `results.csv`: per-query retrieval grades, top-10 rankings, and E2B answers.
- `results.jsonl`: same data as JSON.
- `metrics.json`: aggregate deterministic retrieval grades.
- `manifest.json`: run metadata.
- `answer_scores.csv`: per-answer LLM-judge scores.
- `answer_scores.jsonl`: per-answer LLM-judge scores as JSON.
- `answer_metrics.json`: aggregate answer scores.
- `answer_score_manifest.json`: answer-scoring run metadata.

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

All 10 retrieval rows passed. The final run had zero blank E2B answers.

## Answer Scoring

The generated E2B answers were scored separately with a reasoning-disabled
`gemma-4-e2b` judge against all gold qrel passages for each query.

Judge server:

```bash
llama-server \
  -m /Users/michaelnavazhylau/.cache/huggingface/hub/models--google--gemma-4-E2B-it-qat-q4_0-gguf/snapshots/675cff42a74c774d6cb76f76d8eacb49b48c9b93/gemma-4-E2B_q4_0-it.gguf \
  --alias gemma-4-e2b \
  --host 127.0.0.1 \
  --port 8081 \
  --ctx-size 8192 \
  --batch-size 2048 \
  --ubatch-size 1024 \
  --reasoning off
```

Scoring command:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/score_epbench_e2b_answers.py \
  --eval-dir evals/epbench_embedding_e2b_smoke \
  --dataset data/processed/epbench_episodic \
  --chat-base-url http://127.0.0.1:8081/v1 \
  --chat-model gemma-4-e2b \
  --max-tokens 384
```

Answer-score metrics:

```json
{
  "answers": 10,
  "mean_answer_score": 3.8,
  "pass_count": 5,
  "partial_count": 5,
  "fail_count": 0,
  "score_distribution": {
    "0": 0,
    "1": 0,
    "2": 1,
    "3": 4,
    "4": 1,
    "5": 4
  }
}
```

These answer scores are not deterministic EPBench metrics. They are local
LLM-as-judge scores for the generated text, while `metrics.json` remains the
deterministic retrieval grade from qrels.

## Nemotron Answer Scoring

The same saved E2B answers were also scored with OpenRouter using
`nvidia/nemotron-3-ultra-550b-a55b:free`. The successful run explicitly disabled
reasoning in the OpenRouter request:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/score_epbench_answers_openrouter.py \
  --eval-dir evals/epbench_embedding_e2b_smoke \
  --dataset data/processed/epbench_episodic \
  --judge-model nvidia/nemotron-3-ultra-550b-a55b:free \
  --reasoning off \
  --max-tokens 768 \
  --prefix nemotron_no_reason_answer
```

Nemotron answer-score metrics:

```json
{
  "answers": 10,
  "mean_answer_score": 3.1,
  "pass_count": 2,
  "partial_count": 7,
  "fail_count": 1,
  "score_distribution": {
    "0": 0,
    "1": 0,
    "2": 3,
    "3": 5,
    "4": 0,
    "5": 2
  }
}
```

The Nemotron artifacts are:

- `nemotron_no_reason_answer_scores.csv`
- `nemotron_no_reason_answer_scores.jsonl`
- `nemotron_no_reason_answer_metrics.json`
- `nemotron_no_reason_answer_score_manifest.json`

Reasoning-enabled Nemotron attempts were not kept as scoring artifacts because
the model spent completion tokens on reasoning and returned truncated JSON.
