---
task_categories:
  - text-retrieval
  - text-generation
  - question-answering
tags:
  - personalization
  - retrieval augmented generation
  - planning
  - question answering
pretty_name: "LaMP-QA: A Benchmark for Personalized Long-form Question Answering"
configs:
  - config_name: Art_and_Entertainment
    data_files:
      - split: train
        path: data/Art_and_Entertainment/train/train.json
      - split: validation
        path: data/Art_and_Entertainment/validation/validation.json
      - split: test
        path: data/Art_and_Entertainment/test/test.json
  - config_name: Lifestyle_and_Personal_Development
    data_files:
      - split: train
        path: data/Lifestyle_and_Personal_Development/train/train.json
      - split: validation
        path: data/Lifestyle_and_Personal_Development/validation/validation.json
      - split: test
        path: data/Lifestyle_and_Personal_Development/test/test.json
  - config_name: Society_and_Culture
    data_files:
      - split: train
        path: data/Society_and_Culture/train/train.json
      - split: validation
        path: data/Society_and_Culture/validation/validation.json
      - split: test
        path: data/Society_and_Culture/test/test.json
language:
  - en
---

#  LaMP-QA Dataset

## Dataset Description

- **Repository:** https://github.com/LaMP-Benchmark/LaMP-QA
- **Paper:** https://arxiv.org/abs/2506.00137

## Abstract

Personalization is essential for question answering systems that are user-centric. Despite its importance, personalization in answer generation has been relatively underexplored. This is mainly due to lack of resources for training and evaluating personalized question answering systems. We address this gap by introducing LaMP-QA---a benchmark designed for evaluating personalized long-form answer generation. The benchmark covers questions from three major categories: (1) Arts & Entertainment, (2) Lifestyle & Personal Development, and (3) Society & Culture, encompassing over 45 subcategories in total. To assess the quality and potential impact of the LaMP-QA benchmark for personalized question answering, we conduct comprehensive human and automatic evaluations, to compare multiple evaluation strategies for evaluating generated personalized responses and measure their alignment with human preferences. Furthermore, we benchmark a number of non-personalized and personalized approaches based on open-source and proprietary large language models (LLMs). Our results show that incorporating the personalized context provided leads to performance improvements of up to 39%. The benchmark is publicly released to support future research in this area.



## Dataset Summary

LaMP-QA is a benchmark dataset designed to evaluate personalized long-form question answering systems. It focuses on how well language models can generate informative, coherent, and contextually relevant answers when given a user profile. The dataset covers three high-level categories:

1. Arts & Entertainment

2. Lifestyle & Personal Development

3. Society & Culture

In total, LaMP-QA includes over 45 diverse subcategories, capturing a wide range of real-world information needs where personalization significantly enhances the quality of responses. Details about the dataset construction, task specifications, and evaluation metrics can be found in our paper.

## Accessing the Dataset

You can download the dataset using the Hugging Face datasets library. Here's an example of how to load the Society and Culture dataset:


```python
from datasets import load_dataset

ds = load_dataset("alireza7/LaMP-QA", "Society_and_Culture")

```

## Citation
If you use the LaMP-QA benchmark in your research, please cite our paper:

```
@misc{salemi2025lampqabenchmarkpersonalizedlongform,
      title={LaMP-QA: A Benchmark for Personalized Long-form Question Answering}, 
      author={Alireza Salemi and Hamed Zamani},
      year={2025},
      eprint={2506.00137},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2506.00137}, 
}
```