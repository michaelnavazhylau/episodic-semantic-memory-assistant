# E2B Thinking Bottom-10 EPBench Sub-Eval

This sub-eval reruns the ten bottom-scoring E2B deterministic EPBench items from:

- `Research/03 Evaluation/EPBench bottom 10 scoring items.md`
- Parent run: `evals/epbench_embedding_e2b_full/`

The selected query IDs are pinned in `query_ids.txt`.

## Run Configuration

Generation server:

```bash
llama-server \
  -m /Users/michaelnavazhylau/.cache/huggingface/hub/models--google--gemma-4-E2B-it-qat-q4_0-gguf/snapshots/675cff42a74c774d6cb76f76d8eacb49b48c9b93/gemma-4-E2B_q4_0-it.gguf \
  --alias gemma-4-e2b \
  --host 127.0.0.1 \
  --port 18081 \
  --ctx-size 131072 \
  --reasoning on
```

`Research/01 Models/models.md` records the small Gemma 4 context window as 128K, so this run used `--ctx-size 131072`. The server model metadata reported `n_ctx: 131072`.

Generation command:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/run_epbench_embedding_e2b_eval.py \
  --dataset data/processed/epbench_episodic \
  --out evals/epbench_embedding_e2b_full/subevals/e2b_thinking_bottom10 \
  --embedding-base-url http://127.0.0.1:18083/v1 \
  --embedding-model embeddinggemma-300m \
  --chat-base-url http://127.0.0.1:18081/v1 \
  --chat-model gemma-4-e2b \
  --query-ids-file evals/epbench_embedding_e2b_full/subevals/e2b_thinking_bottom10/query_ids.txt \
  --top-k 10 \
  --generation-context-k 10 \
  --max-tokens 1024 \
  --ctx-size 131072 \
  --reasoning on \
  --chat-timeout 900 \
  --embedding-timeout 180 \
  --retries 1 \
  --workers 1
```

Deterministic grading command:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/grade_epbench_deterministic.py \
  --eval-dir evals/epbench_embedding_e2b_full/subevals/e2b_thinking_bottom10 \
  --dataset data/processed/epbench_episodic \
  --prefix deterministic_grade \
  --embedding-base-url http://127.0.0.1:18084/v1 \
  --embedding-model embeddinggemma-300m \
  --embedding-timeout 180
```

The grader used a larger-batch embedding server on port `18084` because one gold text exceeded the default physical batch size.

## Outputs

- `results.jsonl` / `results.csv`: generation and retrieval rows
- `deterministic_grade_scores.jsonl` / `deterministic_grade_scores.csv`: deterministic answer scores
- `deterministic_grade_metrics.json`: aggregate deterministic answer metrics
- `manifest.json`: generation manifest
- `deterministic_grade_manifest.json`: grading manifest

## Summary

The original pulled E2B bottom-10 items all had `primary_score = 0.0000`.
With E2B thinking enabled, the same ten items scored:

```text
queries:          10
primary_score:    0.7145
semantic_cosine:  0.3785
location_f1:      0.6600
person_f1:        0.3445
date_f1:          0.2667
anchor_f1:        0.5030
```

By query type:

```text
Entities: 1 query, primary_score 0.5455
Spaces:   9 queries, primary_score 0.7333
```

All ten raw chat messages include `reasoning_content`, confirming the server returned thinking traces for the run.

## Row-Level Primary Scores

| Query ID | Type | Primary score |
|---|---|---:|
| `default_claude_short::Entities::query_21` | Entities | 0.5455 |
| `default_claude_short::Spaces::query_10` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_12` | Spaces | 0.8000 |
| `default_claude_short::Spaces::query_14` | Spaces | 0.0000 |
| `default_claude_short::Spaces::query_15` | Spaces | 0.8000 |
| `default_claude_short::Spaces::query_16` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_27` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_28` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_29` | Spaces | 0.0000 |
| `default_claude_short::Spaces::query_31` | Spaces | 1.0000 |
