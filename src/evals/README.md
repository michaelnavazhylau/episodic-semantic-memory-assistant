# Evaluation Methods

## EPBench Grading Method

Pinned policy: EPBench generation quality is graded with deterministic metrics first. LLM-as-judge scores are secondary diagnostics, not the primary EPBench score.

EPBench provides query rows, corpus passages, and qrel links. The normalized dataset does not provide gold final answers, so the grader derives expected answer items from the gold qrel passages.

### Primary Grades

Use `src/evals/grade_epbench_deterministic.py` as the canonical EPBench answer grader.

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/grade_epbench_deterministic.py \
  --eval-dir evals/epbench_embedding_e2b_full \
  --dataset data/processed/epbench_episodic \
  --prefix deterministic_grade
```

Query-type scoring:

| Query type | Primary score |
| --- | --- |
| `Times` | normalized date set F1 |
| `Entities` | person-name set F1 |
| `Spaces` | known-location set F1 |
| `Other_entities` | person-name set F1 after excluding people named in the query |
| `Event_contents` | `0.6 * anchor_f1 + 0.4 * lexical_mean_f1` |
| `Full_event_details` | `0.6 * anchor_f1 + 0.4 * lexical_mean_f1` |

`anchor_f1` combines extracted dates, people, and locations. `lexical_mean_f1` is the mean of token F1 and ROUGE-L F1 against the gold qrel passage text.

### Secondary Semantic Score

Use normalized embedding dot product, reported as cosine similarity, as a secondary semantic similarity score. It is useful for prose-heavy query types but should not replace the deterministic primary grade.

Run with a local embedding server:

```bash
llama-server \
  -m /Users/michaelnavazhylau/.cache/huggingface/hub/models--ggml-org--embeddinggemma-300M-GGUF/snapshots/0f741b5a6585bd53aeb15cd1372c56f2a0f65e12/embeddinggemma-300M-Q8_0.gguf \
  --embeddings \
  --alias embeddinggemma-300m \
  --host 127.0.0.1 \
  --port 8083 \
  --ctx-size 2048 \
  --batch-size 2048 \
  --ubatch-size 2048
```

Then:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/evals/grade_epbench_deterministic.py \
  --eval-dir evals/epbench_embedding_e2b_full \
  --dataset data/processed/epbench_episodic \
  --prefix deterministic_grade_semantic \
  --embedding-base-url http://127.0.0.1:8083/v1 \
  --embedding-model embeddinggemma-300m
```

### Role Of LLM-As-Judge

LLM-as-judge is allowed only as a diagnostic fallback:

- Use it for qualitative review of `Event_contents` and `Full_event_details`.
- Do not treat mixed judges as one clean benchmark.
- Do not use E2B judging E2B as the primary score.
- If a judge is used, report judge model, reasoning setting, rate-limit interruptions, and number of rows scored.

### Current Full EPBench Result

From `evals/epbench_embedding_e2b_full/deterministic_grade_semantic_metrics.json`:

```json
{
  "queries": 276,
  "primary_score": 0.65970197848199,
  "semantic_cosine": 0.43375904278648714
}
```

Primary scores by query type:

| Query type | Score |
| --- | ---: |
| `Entities` | `0.7572` |
| `Times` | `0.8579` |
| `Spaces` | `0.6249` |
| `Other_entities` | `0.8933` |
| `Event_contents` | `0.3991` |
| `Full_event_details` | `0.7512` |
