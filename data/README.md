# Data

This directory stores raw and processed datasets for the benchmark-first memory evaluation.

## Layout

- `raw/`: unmodified source datasets.
- `processed/`: normalized datasets used by the retrieval and personalization pipelines.

`raw/` is documented here but its payloads are not committed: the source files
download as Git-LFS objects (~91 MB each) and this repository carries only the
READMEs and dataset cards. Fetch them per `raw/README.md` before re-running the
normalization scripts.

## Selected Benchmarks

- **EPBench:** episodic-memory retrieval through LMEB.
- **LaMP-QA:** personalization extension using validation splits.

## Primary Links

- LMEB GitHub: https://github.com/KaLM-Embedding/LMEB
- LMEB Hugging Face: https://huggingface.co/datasets/KaLM-Embedding/LMEB
- EPBench Hugging Face: https://huggingface.co/datasets/mteb/EPBench
- LaMP-QA GitHub: https://github.com/LaMP-Benchmark/LaMP-QA
- LaMP-QA Hugging Face: https://huggingface.co/datasets/alireza7/LaMP-QA
