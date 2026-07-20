# E4B Thinking Bottom-10 EPBench Sub-Eval

This sub-eval reruns the ten bottom-scoring E4B deterministic EPBench items from:

- `Research/03 Evaluation/EPBench bottom 10 scoring items.md`
- Parent run: `evals/epbench_embedding_e4b_no_thinking_full_v2/`

The selected query IDs are pinned in `query_ids.txt`.

## Run Configuration

Generation server:

```bash
llama-server \
  -m /Users/michaelnavazhylau/.cache/huggingface/hub/models--google--gemma-4-E4B-it-qat-q4_0-gguf/snapshots/4b4a2c1d584be7264f87aac328a1bc739ce81b6c/gemma-4-E4B_q4_0-it.gguf \
  --alias gemma-4-e4b \
  --host 127.0.0.1 \
  --port 18082 \
  --ctx-size 131072 \
  --reasoning on \
  --reasoning-budget 1024
```

`Research/01 Models/models.md` records the small Gemma 4 context window as 128K, so this run used `--ctx-size 131072`. The server model metadata reported `n_ctx: 131072`.

The first attempt used `--reasoning on` with `--max-tokens 1024` and no thinking budget, but E4B spent the whole completion budget on reasoning and returned an empty final answer for the first row. The completed run kept thinking enabled and bounded it with `--reasoning-budget 1024`, then used `--max-tokens 2048` so final answers could be emitted.

Generation command:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/run_epbench_embedding_e2b_eval.py \
  --dataset data/processed/epbench_episodic \
  --out evals/epbench_embedding_e4b_no_thinking_full_v2/subevals/e4b_thinking_bottom10 \
  --embedding-base-url http://127.0.0.1:18084/v1 \
  --embedding-model embeddinggemma-300m \
  --chat-base-url http://127.0.0.1:18082/v1 \
  --chat-model gemma-4-e4b \
  --query-ids-file evals/epbench_embedding_e4b_no_thinking_full_v2/subevals/e4b_thinking_bottom10/query_ids.txt \
  --top-k 10 \
  --generation-context-k 10 \
  --max-tokens 2048 \
  --ctx-size 131072 \
  --reasoning on \
  --reasoning-budget 1024 \
  --chat-timeout 900 \
  --embedding-timeout 180 \
  --retries 1 \
  --workers 1
```

Deterministic grading command:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/grade_epbench_deterministic.py \
  --eval-dir evals/epbench_embedding_e4b_no_thinking_full_v2/subevals/e4b_thinking_bottom10 \
  --dataset data/processed/epbench_episodic \
  --prefix deterministic_grade \
  --embedding-base-url http://127.0.0.1:18084/v1 \
  --embedding-model embeddinggemma-300m \
  --embedding-timeout 180
```

The grader used the larger-batch embedding server on port `18084`.

## Outputs

- `results.jsonl` / `results.csv`: generation and retrieval rows
- `deterministic_grade_scores.jsonl` / `deterministic_grade_scores.csv`: deterministic answer scores
- `deterministic_grade_metrics.json`: aggregate deterministic answer metrics
- `manifest.json`: generation manifest
- `deterministic_grade_manifest.json`: grading manifest

## Summary

The original pulled E4B bottom-10 items all had `primary_score = 0.0000`.
With E4B thinking enabled, the same ten items scored:

```text
queries:          10
primary_score:    0.9000
semantic_cosine:  0.4111
location_f1:      0.9000
person_f1:        0.3733
date_f1:          0.5000
anchor_f1:        0.5886
```

By query type:

```text
Other_entities: 1 query, primary_score 1.0000
Spaces:         9 queries, primary_score 0.8889
```

All ten raw chat messages include nonempty `reasoning_content`, and all ten include nonempty final answer content.

## Row-Level Primary Scores

| Query ID | Type | Primary score |
|---|---|---:|
| `default_claude_short::Other_entities::query_3` | Other_entities | 1.0000 |
| `default_claude_short::Spaces::query_12` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_14` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_15` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_16` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_28` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_29` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_31` | Spaces | 0.0000 |
| `default_claude_short::Spaces::query_36` | Spaces | 1.0000 |
| `default_claude_short::Spaces::query_42` | Spaces | 1.0000 |
