"""Regenerate the README figures from committed eval artifacts.

Every number plotted here is read out of `evals/` at run time rather than
hard-coded, so the figures cannot drift away from the committed scores.

Usage (from the repo root):

    uv run python docs/figures/make_figures.py

Writes PNGs next to this file.
"""

from __future__ import annotations

import csv
import json
import random
import statistics as stats
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

REPO = Path(__file__).resolve().parents[2]
FIGDIR = Path(__file__).resolve().parent

E2B_RUN = REPO / "evals/epbench_embedding_e2b_full"
E4B_RUN = REPO / "evals/epbench_embedding_e4b_no_thinking_full_v2"
LAMPQA_E2B_RUN = REPO / "evals/lampqa_embedding_e2b_sample100"
LAMPQA_E4B_RUN = REPO / "evals/lampqa_embedding_e4b_no_thinking_sample100_v2"

C_E2B = "#4c6ef5"
C_E4B = "#e8590c"
C_MUTED = "#868e96"
C_GRID = "#dee2e6"

BOOTSTRAP_RESAMPLES = 20_000
BOOTSTRAP_SEED = 0

plt.rcParams.update(
    {
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.titleweight": "bold",
        "axes.labelsize": 9,
        "axes.edgecolor": "#adb5bd",
        "axes.linewidth": 0.8,
        "xtick.color": "#495057",
        "ytick.color": "#495057",
        "text.color": "#212529",
        "axes.labelcolor": "#212529",
        "legend.frameon": False,
    }
)


# ---------------------------------------------------------------- data loading


def read_json(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def read_scores(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open(newline="") as fh:
        return {row[key]: row for row in csv.DictReader(fh)}


def paired_bootstrap(
    diffs: list[float], resamples: int = BOOTSTRAP_RESAMPLES, seed: int = BOOTSTRAP_SEED
) -> tuple[float, float, float]:
    """Mean paired difference and its 95% percentile bootstrap CI."""
    rng = random.Random(seed)
    n = len(diffs)
    means = sorted(stats.mean([diffs[rng.randrange(n)] for _ in range(n)]) for _ in range(resamples))
    return stats.mean(diffs), means[int(0.025 * resamples)], means[int(0.975 * resamples)]


def epbench_data() -> dict:
    e2b = read_scores(E2B_RUN / "deterministic_grade_scores.csv", "query_id")
    e4b = read_scores(E4B_RUN / "deterministic_grade_scores.csv", "query_id")
    shared = sorted(set(e2b) & set(e4b))
    diffs = [float(e4b[k]["primary_score"]) - float(e2b[k]["primary_score"]) for k in shared]
    return {
        "e2b": e2b,
        "e4b": e4b,
        "shared": shared,
        "diffs": diffs,
        "retrieval": read_json(E2B_RUN / "metrics.json"),
        "components_e2b": read_json(E2B_RUN / "deterministic_grade_semantic_metrics.json"),
        "components_e4b": read_json(E4B_RUN / "deterministic_grade_metrics.json"),
    }


def lampqa_data() -> dict:
    e2b = read_scores(LAMPQA_E2B_RUN / "claude_rubric_v3_scores.csv", "question_id")
    e4b = read_scores(LAMPQA_E4B_RUN / "claude_rubric_v3_scores.csv", "question_id")
    shared = sorted(set(e2b) & set(e4b))
    diffs = [float(e4b[k]["rubric_score"]) - float(e2b[k]["rubric_score"]) for k in shared]
    return {"e2b": e2b, "e4b": e4b, "shared": shared, "diffs": diffs}


# ------------------------------------------------------------------- utilities


def style_axes(ax: plt.Axes, ylabel: str | None = None, grid_axis: str = "y") -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis=grid_axis, color=C_GRID, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    if ylabel:
        ax.set_ylabel(ylabel)


def group_bars(ax, labels, series, colors, width=0.38, value_fmt="{:.2f}", ylim=None, annotate=True, fontsize=7):
    xs = range(len(labels))
    for i, (name, values) in enumerate(series):
        offset = (i - (len(series) - 1) / 2) * width
        bars = ax.bar(
            [x + offset for x in xs],
            values,
            width,
            label=name,
            color=colors[i],
            zorder=3,
            edgecolor="white",
            linewidth=0.5,
        )
        if not annotate:
            continue
        for bar, val in zip(bars, values):
            ax.annotate(
                value_fmt.format(val),
                (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                textcoords="offset points",
                xytext=(0, 2.5),
                ha="center",
                fontsize=fontsize,
                color="#343a40",
            )
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels)
    if ylim:
        ax.set_ylim(*ylim)


def save(fig, name: str) -> Path:
    path = FIGDIR / name
    fig.savefig(path, bbox_inches="tight", pad_inches=0.25, facecolor="white")
    plt.close(fig)
    return path


# -------------------------------------------------------------------- figures


def fig_retrieval(ep: dict) -> Path:
    m = ep["retrieval"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.0, 3.0), gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.42})

    ks = [1, 3, 5, 10]
    hits = [m[f"hit_at_{k}"] for k in ks]
    ax1.plot(ks, hits, marker="o", color=C_E2B, linewidth=2, markersize=6, zorder=3)
    ax1.fill_between(ks, 0.8, hits, color=C_E2B, alpha=0.10, zorder=2)
    ax1.axhline(1.0, color=C_MUTED, linestyle=":", linewidth=1)
    for k, h in zip(ks, hits):
        ax1.annotate(f"{h:.3f}", (k, h), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=8)
    ax1.annotate("every query retrieves a gold passage", (6.0, 1.0), textcoords="offset points",
                 xytext=(0, 9), ha="center", fontsize=7.5, color=C_MUTED)
    ax1.set_xlim(0, 11.2)
    ax1.set_ylim(0.80, 1.055)
    ax1.set_xticks(ks)
    ax1.set_xlabel("k (retrieved passages)")
    ax1.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    ax1.set_title("Hit rate saturates by k=10")
    style_axes(ax1, "hit@k")

    labels = ["recall@10", "MRR", "nDCG@10"]
    values = [m["recall_at_10"], m["mrr"], m["ndcg_at_10"]]
    bars = ax2.barh(labels[::-1], values[::-1], color=C_E2B, height=0.55, zorder=3)
    for bar, val in zip(bars, values[::-1]):
        ax2.annotate(f"{val:.3f}", (bar.get_width(), bar.get_y() + bar.get_height() / 2),
                     textcoords="offset points", xytext=(5, 0), va="center", fontsize=8)
    ax2.set_xlim(0.85, 1.02)
    ax2.xaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    ax2.set_title("Ranking quality, 276 queries")
    style_axes(ax2, None, grid_axis="x")

    fig.suptitle("EmbeddingGemma-300M retrieval: the bottleneck is not here", fontsize=11, fontweight="bold", y=1.04)
    return save(fig, "fig1-retrieval.png")


def fig_model_size(ep: dict, lq: dict) -> Path:
    ep_diff = paired_bootstrap(ep["diffs"])
    lq_diff = paired_bootstrap(lq["diffs"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 3.1), gridspec_kw={"width_ratios": [1, 1.3], "wspace": 0.5})

    # left: absolute means
    labels = ["EPBench\n(276 q)", "LaMP-QA\n(100 q)"]
    e2b_scores = [float(ep["components_e2b"]["primary_score"]), stats.mean(float(lq["e2b"][k]["rubric_score"]) for k in lq["shared"])]
    e4b_scores = [float(ep["components_e4b"]["primary_score"]), stats.mean(float(lq["e4b"][k]["rubric_score"]) for k in lq["shared"])]
    group_bars(ax1, labels, [("E2B", e2b_scores), ("E4B", e4b_scores)], [C_E2B, C_E4B], width=0.32, ylim=(0, 0.85))
    ax1.set_title("Absolute score by benchmark")
    ax1.legend(loc="upper left", fontsize=8)
    style_axes(ax1, "mean primary score")

    # right: forest plot of paired differences
    rows = [("EPBench\n(276 q)", ep_diff), ("LaMP-QA\n(100 q)", lq_diff)]
    ys = [1, 0]
    ax2.axvline(0, color=C_MUTED, linewidth=1, linestyle="--", zorder=2)
    for y, (label, (mean, lo, hi)) in zip(ys, rows):
        color = C_E4B if lo > 0 else C_MUTED
        ax2.plot([lo, hi], [y, y], color=color, linewidth=2.5, solid_capstyle="round", zorder=3)
        ax2.scatter([mean], [y], color=color, s=42, zorder=4)
        verdict = "significant" if lo > 0 else "spans zero"
        ax2.annotate(f"{mean:+.3f}  [{lo:+.3f}, {hi:+.3f}]\n{verdict}", (hi, y),
                     textcoords="offset points", xytext=(8, 0), va="center", fontsize=7.5, color=color, linespacing=1.35)
    ax2.set_yticks(ys)
    ax2.set_yticklabels([label for label, _ in rows], fontsize=8)
    ax2.set_ylim(-0.55, 1.55)
    ax2.set_xlim(-0.025, 0.17)
    ax2.set_xlabel("E4B − E2B paired difference (95% bootstrap CI)")
    ax2.set_title("Model size buys one real gain")
    style_axes(ax2, None, grid_axis="x")

    fig.suptitle("Generation is where the two models separate — only for personalization",
                 fontsize=11, fontweight="bold", y=1.04)
    return save(fig, "fig2-model-size.png")


def fig_epbench_breakdown(ep: dict) -> Path:
    c2, c4 = ep["components_e2b"], ep["components_e4b"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.3), gridspec_kw={"width_ratios": [1, 1.35]})

    components = [("Primary", "primary_score"), ("Anchor", "anchor_f1"), ("Location", "location_f1"),
                  ("Date", "date_f1"), ("Person", "person_f1"), ("Semantic", "semantic_cosine")]
    labels = [name for name, _ in components]
    group_bars(
        ax1,
        labels,
        [("E2B", [c2[key] for _, key in components]), ("E4B", [c4[key] for _, key in components])],
        [C_E2B, C_E4B],
        width=0.36,
        ylim=(0, 0.72),
        annotate=False,
    )
    ax1.tick_params(axis="x", labelsize=8, rotation=20)
    for tick in ax1.get_xticklabels():
        tick.set_ha("right")
    ax1.set_title("Score components (F1 unless noted)")
    ax1.legend(loc="upper right", fontsize=8)
    style_axes(ax1, "mean score")

    order = ["Times", "Entities", "Spaces", "Event_contents", "Full_event_details", "Other_entities"]
    display = {"Event_contents": "Event\ncontents", "Full_event_details": "Full event\ndetails", "Other_entities": "Other\nentities"}
    q2 = c2["by_query_type"]
    q4 = c4["by_query_type"]
    labels = [f"{display.get(t, t)}\n(n={q2[t]['queries']})" for t in order]
    group_bars(
        ax2,
        labels,
        [("E2B", [q2[t]["primary_score"] for t in order]), ("E4B", [q4[t]["primary_score"] for t in order])],
        [C_E2B, C_E4B],
        width=0.36,
        ylim=(0, 1.14),
        fontsize=6.5,
    )
    ax2.tick_params(axis="x", labelsize=7.5)
    ax2.set_title("By EPBench query type")
    ax2.legend(loc="upper right", fontsize=8, ncol=2)
    style_axes(ax2, "primary score")

    fig.suptitle("Where E4B's point-estimate gain comes from — and where it does not",
                 fontsize=11, fontweight="bold", y=1.04)
    return save(fig, "fig3-epbench-breakdown.png")


def fig_lampqa(lq: dict) -> Path:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.1), gridspec_kw={"width_ratios": [1, 1], "wspace": 0.28})

    buckets = ["Covered", "Partial", "Missed"]
    colors = ["#2f9e44", "#f59f00", "#e03131"]
    e2b_totals = [sum(int(r[k]) for r in lq["e2b"].values()) for k in ("covered_aspects", "partial_aspects", "missed_aspects")]
    e4b_totals = [sum(int(r[k]) for r in lq["e4b"].values()) for k in ("covered_aspects", "partial_aspects", "missed_aspects")]
    # stacked bars, one per model, so the shift between buckets is visible
    left2 = left4 = 0
    for bucket, color, v2, v4 in zip(buckets, colors, e2b_totals, e4b_totals):
        ax1.barh("E2B", v2, left=left2, color=color, height=0.5, edgecolor="white", label=bucket, zorder=3)
        ax1.barh("E4B", v4, left=left4, color=color, height=0.5, edgecolor="white", zorder=3)
        ax1.annotate(str(v2), (left2 + v2 / 2, 0), ha="center", va="center", fontsize=8, color="white", fontweight="bold", zorder=4)
        ax1.annotate(str(v4), (left4 + v4 / 2, 1), ha="center", va="center", fontsize=8, color="white", fontweight="bold", zorder=4)
        left2 += v2
        left4 += v4
    ax1.set_xlabel("rubric aspects across 100 questions")
    ax1.set_title("Aspect coverage shifts out of 'missed'")
    ax1.tick_params(axis="y", pad=6)
    ax1.legend(loc="lower center", bbox_to_anchor=(0.5, -0.44), ncol=3, fontsize=8)
    style_axes(ax1, None, grid_axis="x")

    # right: score distribution comparison
    bins = [i / 10 for i in range(11)]
    adds = [0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    hist2 = [0] * 10
    hist4 = [0] * 10
    for r in lq["e2b"].values():
        s = float(r["rubric_score"])
        hist2[min(9, max(0, int(s * 10)))] += 1
    for r in lq["e4b"].values():
        s = float(r["rubric_score"])
        hist4[min(9, max(0, int(s * 10)))] += 1
    ax2.bar([a - 0.11 for a in adds], hist2, width=0.2, color=C_E2B, label="E2B", zorder=3)
    ax2.bar([a + 0.11 for a in adds], hist4, width=0.2, color=C_E4B, label="E4B", zorder=3)
    ax2.set_xticks([adds[i] for i in (0, 2, 4, 6, 8)])
    ax2.set_xticklabels([f"{bins[i]:.1f}" for i in (0, 2, 4, 6, 8)])
    ax2.set_xlim(-0.02, 1.02)
    ax2.set_xlabel("rubric score per question")
    ax2.set_title("Same median (0.50), heavier right tail")
    ax2.legend(loc="upper right", fontsize=8)
    style_axes(ax2, "questions")

    fig.suptitle("Personalization: both models are weak, E4B is less weak", fontsize=11, fontweight="bold", y=1.04)
    return save(fig, "fig4-lampqa-aspects.png")


def fig_reasoning(ep: dict, lq: dict) -> Path:
    ep_e2b = read_json(EPBENCH_E2B_SUB / "deterministic_grade_metrics.json")["primary_score"]
    ep_e4b = read_json(EPBENCH_E4B_SUB / "deterministic_grade_metrics.json")["primary_score"]
    lq_e2b = read_json(LAMPQA_E2B_SUB / "claude_rubric_v3_metrics.json")["mean_rubric_score"]
    lq_e4b = read_json(LAMPQA_E4B_SUB / "claude_rubric_v3_metrics.json")["mean_rubric_score"]

    ep_base_e2b = stats.mean(float(ep["e2b"][k]["primary_score"]) for k in read_ids(EPBENCH_E2B_SUB, "query_ids.txt"))
    ep_base_e4b = stats.mean(float(ep["e4b"][k]["primary_score"]) for k in read_ids(EPBENCH_E4B_SUB, "query_ids.txt"))
    lq_base_e2b = stats.mean(float(lq["e2b"][k]["rubric_score"]) for k in read_ids(LAMPQA_E2B_SUB, "question_ids.txt"))
    lq_base_e4b = stats.mean(float(lq["e4b"][k]["rubric_score"]) for k in read_ids(LAMPQA_E4B_SUB, "question_ids.txt"))

    labels = ["EPBench\nE2B", "EPBench\nE4B", "LaMP-QA\nE2B", "LaMP-QA\nE4B"]
    baseline = [ep_base_e2b, ep_base_e4b, lq_base_e2b, lq_base_e4b]
    thinking = [ep_e2b, ep_e4b, lq_e2b, lq_e4b]

    fig, ax = plt.subplots(figsize=(6.6, 3.0))
    group_bars(
        ax,
        labels,
        [("baseline (temperature 0)", baseline), ("with reasoning", thinking)],
        [C_MUTED, "#7048e8"],
        width=0.36,
        ylim=(0, 1.22),
    )
    ax.set_title("Bottom-10 items: reasoning recovers the hard tail, most for E4B")
    ax.legend(loc="upper left", fontsize=8, ncol=2, bbox_to_anchor=(0, 1.0))
    style_axes(ax, "mean score on the 10 hardest items")
    return save(fig, "fig5-reasoning-lift.png")


EPBENCH_E2B_SUB = E2B_RUN / "subevals/e2b_thinking_bottom10"
EPBENCH_E4B_SUB = E4B_RUN / "subevals/e4b_thinking_bottom10"
LAMPQA_E2B_SUB = LAMPQA_E2B_RUN / "subevals/e2b_thinking_bottom10"
LAMPQA_E4B_SUB = LAMPQA_E4B_RUN / "subevals/e4b_thinking_bottom10"


def read_ids(sub: Path, filename: str) -> list[str]:
    return [line.strip() for line in (sub / filename).read_text().splitlines() if line.strip()]


def main() -> None:
    ep = epbench_data()
    lq = lampqa_data()
    written = [
        fig_retrieval(ep),
        fig_model_size(ep, lq),
        fig_epbench_breakdown(ep),
        fig_lampqa(lq),
        fig_reasoning(ep, lq),
    ]
    for path in written:
        print(f"wrote {path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
