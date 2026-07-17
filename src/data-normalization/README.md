# Data Normalization

Scripts in this directory convert the local raw benchmark downloads into the
normalized files used by retrieval and personalization evaluation.

## Scripts

- `normalize_lmeb.py`: converts LMEB parquet retrieval datasets.
- `normalize_lampqa.py`: converts LaMP-QA JSON validation data.
- `validate_retrieval_dataset.py`: validates processed retrieval datasets.
- `validate_lampqa_dataset.py`: validates processed LaMP-QA question/profile
  links.

The LMEB normalizer requires `pyarrow`, which is declared in `pyproject.toml`.

## EPBench

EPBench is the episodic-memory retrieval dataset. The first baseline uses the
`default_claude_short` variant and combines these query types:

- `Entities`
- `Event_contents`
- `Full_event_details`
- `Other_entities`
- `Spaces`
- `Times`

Process:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/data-normalization/normalize_lmeb.py \
  --source data/raw/lmeb/epbench \
  --dataset epbench \
  --variant default_claude_short \
  --out data/processed/epbench_episodic
```

Validate:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/data-normalization/validate_retrieval_dataset.py \
  data/processed/epbench_episodic
```

Verified output counts:

```json
{
  "corpus": 19,
  "queries": 276,
  "qrels": 378
}
```

ID policy:

- Corpus IDs: `<variant>::<original_id>`
- Query IDs: `<variant>::<query_type>::<original_id>`

This avoids collisions because EPBench reuses query IDs across query types.

## LaMP-QA

LaMP-QA is the personalized long-form QA extension. The current local scope is
the validation split for these three configs:

- `Art_and_Entertainment`
- `Lifestyle_and_Personal_Development`
- `Society_and_Culture`

Before processing, make sure the validation JSON files are real LFS payloads,
not pointer files:

```bash
git lfs pull --include="data/raw/lamp_qa/data/**/validation/validation.json"
```

Process:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/data-normalization/normalize_lampqa.py \
  --source data/raw/lamp_qa/data \
  --split validation \
  --out data/processed/lamp_qa_personalization
```

Validate:

```bash
UV_CACHE_DIR=.uv-cache uv run python src/data-normalization/validate_lampqa_dataset.py \
  data/processed/lamp_qa_personalization
```

Verified output counts:

```json
{
  "questions": 2503,
  "profiles": 280456,
  "source_configs": {
    "Art_and_Entertainment": 801,
    "Lifestyle_and_Personal_Development": 892,
    "Society_and_Culture": 810
  },
  "min_profiles_per_question": 10,
  "max_profiles_per_question": 1619
}
```

The normalizer writes:

- `questions.jsonl`
- `profiles.jsonl`
- `manifest.json`

It does not create `retrieved_contexts.jsonl` or `answers.jsonl`. Those belong
to the later evaluation stage after embedding retrieval and generation are run.

## Processed Files

After processing, the expected files are:

```text
data/processed/epbench_episodic/
  corpus.jsonl
  queries.jsonl
  qrels.tsv
  manifest.json

data/processed/lamp_qa_personalization/
  questions.jsonl
  profiles.jsonl
  manifest.json
```

## Next Evaluation Step

Run retrieval evaluation first:

1. Embed `corpus.jsonl` and `queries.jsonl` for EPBench.
2. Rank with cosine similarity.
3. Compute `nDCG@10`, `Recall@k`, `Hit@k`, and `MRR`.

Then run LaMP-QA personalization:

1. Embed each question and its associated profile rows.
2. Write top-k profile IDs to `retrieved_contexts.jsonl`.
3. Generate answers with and without retrieved profile context.
4. Write outputs to `answers.jsonl`.
