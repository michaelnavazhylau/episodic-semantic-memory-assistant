# E4B Thinking Bottom-10 LaMP-QA Sub-Eval

This sub-eval reruns the ten bottom-scoring E4B LaMP-QA rubric-native items from:

- `Research/03 Evaluation/LaMP-QA bottom 10 scoring items.md`
- Parent run: `evals/lampqa_embedding_e4b_no_thinking_sample100_v2/`

The selected question IDs are pinned in `question_ids.txt`.

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

Generation command:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/run_lampqa_embedding_e2b_eval.py \
  --dataset data/processed/lamp_qa_personalization_sample100 \
  --out evals/lampqa_embedding_e4b_no_thinking_sample100_v2/subevals/e4b_thinking_bottom10 \
  --embedding-base-url http://127.0.0.1:18084/v1 \
  --embedding-model embeddinggemma-300m \
  --chat-base-url http://127.0.0.1:18082/v1 \
  --chat-model gemma-4-e4b \
  --question-ids-file evals/lampqa_embedding_e4b_no_thinking_sample100_v2/subevals/e4b_thinking_bottom10/question_ids.txt \
  --top-k 10 \
  --generation-context-k 8 \
  --max-tokens 2048 \
  --ctx-size 131072 \
  --reasoning on \
  --reasoning-budget 1024 \
  --chat-timeout 900 \
  --embedding-timeout 180 \
  --retries 1
```

Embedding server:

```bash
llama-server \
  -m /Users/michaelnavazhylau/.cache/huggingface/hub/models--ggml-org--embeddinggemma-300M-GGUF/snapshots/0f741b5a6585bd53aeb15cd1372c56f2a0f65e12/embeddinggemma-300M-Q8_0.gguf \
  --embeddings \
  --alias embeddinggemma-300m \
  --host 127.0.0.1 \
  --port 18084 \
  --ctx-size 2048 \
  -b 2048 \
  -ub 2048
```

## Outputs

- `question_ids.txt`: pinned bottom-10 question set
- `results.jsonl` / `results.csv`: generated answers and retrieved profile memories
- `metrics.json`: generation/retrieval summary
- `manifest.json`: generation manifest
- `embedding_cache.jsonl`: seeded from the parent E4B LaMP-QA eval and appended as needed
- `claude_rubric_v3_scores.jsonl` / `claude_rubric_v3_scores.csv`: Claude rubric-native regrading results
- `claude_rubric_v3_metrics.json`: Claude rubric-native aggregate metrics
- `claude_rubric_v3_manifest.json`: Claude rubric-native judge manifest

## Verification

```text
completed questions: 10 / 10
empty final answers: 0
all rows include reasoning_content: true
answer length range: 448-3936 characters
reasoning_content length range: 2119-3579 characters
Claude rubric rows: 10 / 10
Claude rubric errors: 0
Claude mean rubric score: 0.5792
Claude coverage totals: covered=20, partial=17, missed=11
Mean delta vs parent no-thinking bottom-10 scores: +0.3694
```

The runner captures `raw_chat_message` and `chat_usage` in `results.jsonl` so the thinking traces remain available for later inspection and scoring provenance. The generated answer field is still named `e2b_answer` by the shared LaMP-QA runner; the E4B model identity is recorded in `manifest.json` as `chat_model: gemma-4-e4b`.
