#!/usr/bin/env python3
"""
Log Aider benchmark results to MLflow for experiment tracking.

Reads per-exercise .aider.results.json files, aggregates them, generates
visual charts and a markdown summary, and logs everything to MLflow.

Usage:
    python3 scripts/log_benchmark_to_mlflow.py <results_dir>

Example:
    python3 scripts/log_benchmark_to_mlflow.py aider/tmp.benchmarks/2026-03-02-16-11-28--pipeline-test
"""

import argparse
import json
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import mlflow


EXPERIMENT_NAME = "aider-polyglot-benchmark"


def load_exercise_results(results_dir: Path) -> list[dict]:
    """Load all .aider.results.json files from the results directory."""
    results = []
    for fname in results_dir.glob("*/exercises/practice/*/.aider.results.json"):
        try:
            data = json.loads(fname.read_text())
            if data:
                # Add language info from path
                parts = str(fname.relative_to(results_dir)).split("/")
                data["language"] = parts[0] if parts else "unknown"
                results.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  Warning: skipping {fname}: {e}", file=sys.stderr)
    return results


def aggregate_stats(results: list[dict], results_dir: Path) -> dict:
    """Aggregate per-exercise results into summary statistics."""
    if not results:
        return {}

    total_exercises = len(list(results_dir.glob("*/exercises/practice/*")))

    tries = max(
        len(r.get("tests_outcomes", [])) for r in results if r
    ) if results else 0

    passed_per_try = [0] * tries
    total_cost = 0.0
    total_duration = 0.0
    total_error_outputs = 0
    total_user_asks = 0
    total_test_timeouts = 0
    total_exhausted_ctx = 0
    total_malformed = 0
    exercises_with_malformed = 0
    total_syntax_errors = 0
    total_indentation_errors = 0
    total_lazy_comments = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0

    variants = defaultdict(set)

    for r in results:
        outcomes = r.get("tests_outcomes", [])
        passed = outcomes and outcomes[-1]
        if passed:
            for i in range(len(outcomes) - 1, tries):
                passed_per_try[i] += 1

        total_cost += r.get("cost", 0)
        total_duration += r.get("duration", 0)
        total_error_outputs += r.get("num_error_outputs", 0)
        total_user_asks += r.get("num_user_asks", 0)
        total_test_timeouts += r.get("test_timeouts", 0)
        total_exhausted_ctx += r.get("num_exhausted_context_windows", 0)
        total_malformed += r.get("num_malformed_responses", 0)
        if r.get("num_malformed_responses"):
            exercises_with_malformed += 1
        total_syntax_errors += r.get("syntax_errors", 0)
        total_indentation_errors += r.get("indentation_errors", 0)
        total_lazy_comments += r.get("lazy_comments", 0)
        total_prompt_tokens += r.get("prompt_tokens", 0)
        total_completion_tokens += r.get("completion_tokens", 0)

        for key in ("model", "edit_format", "commit_hash"):
            val = r.get(key)
            if val:
                variants[key].add(val)

    completed = len(results)
    stats = {
        "completed_tests": completed,
        "total_tests": total_exercises,
        "total_cost": total_cost,
        "total_duration": total_duration,
        "seconds_per_case": total_duration / completed if completed else 0,
        "error_outputs": total_error_outputs,
        "user_asks": total_user_asks,
        "test_timeouts": total_test_timeouts,
        "exhausted_context_windows": total_exhausted_ctx,
        "num_malformed_responses": total_malformed,
        "num_with_malformed_responses": exercises_with_malformed,
        "syntax_errors": total_syntax_errors,
        "indentation_errors": total_indentation_errors,
        "lazy_comments": total_lazy_comments,
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "percent_cases_well_formed": (
            (1.0 - exercises_with_malformed / completed) * 100
            if completed else 0
        ),
    }

    for i in range(tries):
        rate = 100 * passed_per_try[i] / completed if completed else 0
        stats[f"pass_rate_{i + 1}"] = round(rate, 1)
        stats[f"pass_num_{i + 1}"] = passed_per_try[i]

    for key, vals in variants.items():
        stats[key] = ", ".join(sorted(str(v) for v in vals))

    stats["dirname"] = results_dir.name

    return stats


# ── Chart generators ─────────────────────────────────────────────────────────

def generate_pass_rate_chart(stats: dict, out_path: Path):
    """Bar chart: pass rate per try."""
    tries = []
    rates = []
    i = 1
    while f"pass_rate_{i}" in stats:
        tries.append(f"Try {i}")
        rates.append(stats[f"pass_rate_{i}"])
        i += 1

    if not tries:
        return

    fig, ax = plt.subplots(figsize=(5, 3.5))
    colors = ["#4C72B0", "#55A868", "#C44E52", "#8172B2"][:len(tries)]
    bars = ax.bar(tries, rates, color=colors, width=0.5, edgecolor="white")

    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                f"{rate:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylim(0, max(max(rates) * 1.2, 10))
    ax.set_ylabel("Pass Rate (%)")
    ax.set_title(f"Pass Rate — {stats.get('model', '?')}", fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def generate_language_chart(results: list[dict], out_path: Path):
    """Stacked bar chart: pass/fail per language."""
    lang_pass = defaultdict(int)
    lang_fail = defaultdict(int)

    for r in results:
        lang = r.get("language", "unknown")
        outcomes = r.get("tests_outcomes", [])
        if outcomes and outcomes[-1]:
            lang_pass[lang] += 1
        else:
            lang_fail[lang] += 1

    languages = sorted(set(list(lang_pass.keys()) + list(lang_fail.keys())))
    if not languages:
        return

    passes = [lang_pass.get(l, 0) for l in languages]
    fails = [lang_fail.get(l, 0) for l in languages]

    fig, ax = plt.subplots(figsize=(max(5, len(languages) * 1.2), 3.5))
    x = range(len(languages))
    ax.bar(x, passes, label="Pass", color="#55A868", width=0.6, edgecolor="white")
    ax.bar(x, fails, bottom=passes, label="Fail", color="#C44E52", width=0.6, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(languages, fontsize=10)
    ax.set_ylabel("Exercises")
    ax.set_title("Results by Language", fontsize=12, fontweight="bold")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def generate_error_chart(stats: dict, out_path: Path):
    """Bar chart of error categories."""
    categories = {
        "Syntax Errors": stats.get("syntax_errors", 0),
        "Indentation Errors": stats.get("indentation_errors", 0),
        "Malformed Responses": stats.get("num_malformed_responses", 0),
        "Exhausted Context": stats.get("exhausted_context_windows", 0),
        "Test Timeouts": stats.get("test_timeouts", 0),
        "Lazy Comments": stats.get("lazy_comments", 0),
    }

    # Only show categories with non-zero values, or show all if all zero
    non_zero = {k: v for k, v in categories.items() if v > 0}
    if not non_zero:
        non_zero = categories

    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.barh(list(non_zero.keys()), list(non_zero.values()),
                   color="#C44E52", height=0.5, edgecolor="white")

    for bar, val in zip(bars, non_zero.values()):
        if val > 0:
            ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                    str(int(val)), va="center", fontsize=10, fontweight="bold")

    ax.set_xlabel("Count")
    ax.set_title("Error Breakdown", fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ── Markdown summary ─────────────────────────────────────────────────────────

def generate_summary_markdown(stats: dict, results: list[dict], out_path: Path):
    """Generate a human-readable markdown summary of the benchmark run."""

    model = stats.get("model", "N/A")
    edit_fmt = stats.get("edit_format", "N/A")
    completed = stats.get("completed_tests", 0)
    total = stats.get("total_tests", 0)
    duration_min = stats.get("total_duration", 0) / 60

    lines = [
        f"# Benchmark Summary",
        f"",
        f"| Parameter | Value |",
        f"|---|---|",
        f"| **Model** | `{model}` |",
        f"| **Edit Format** | `{edit_fmt}` |",
        f"| **Exercises** | {completed} / {total} |",
        f"| **Total Duration** | {duration_min:.1f} min |",
        f"| **Avg per Exercise** | {stats.get('seconds_per_case', 0):.0f}s |",
        f"| **Total Cost** | ${stats.get('total_cost', 0):.4f} |",
        f"| **Well-Formed** | {stats.get('percent_cases_well_formed', 0):.0f}% |",
        f"",
    ]

    # Pass rates
    i = 1
    while f"pass_rate_{i}" in stats:
        lines.append(f"- **Pass Rate (Try {i}):** {stats[f'pass_rate_{i}']}%"
                      f" ({stats.get(f'pass_num_{i}', 0)}/{completed})")
        i += 1
    lines.append("")

    # Token usage
    lines.extend([
        f"## Token Usage",
        f"",
        f"| | Tokens |",
        f"|---|---|",
        f"| Prompt | {stats.get('prompt_tokens', 0):,} |",
        f"| Completion | {stats.get('completion_tokens', 0):,} |",
        f"| **Total** | **{stats.get('prompt_tokens', 0) + stats.get('completion_tokens', 0):,}** |",
        f"",
    ])

    # Per-exercise table
    if results:
        lines.extend([
            f"## Exercise Details",
            f"",
            f"| Language | Exercise | Result | Duration | Tokens |",
            f"|---|---|---|---|---|",
        ])

        sorted_results = sorted(results, key=lambda r: (r.get("language", ""), r.get("testcase", "")))
        for r in sorted_results:
            lang = r.get("language", "?")
            name = r.get("testcase", "?")
            outcomes = r.get("tests_outcomes", [])
            result_str = "✅ Pass" if (outcomes and outcomes[-1]) else "❌ Fail"
            dur = r.get("duration", 0)
            tokens = r.get("prompt_tokens", 0) + r.get("completion_tokens", 0)
            lines.append(f"| {lang} | {name} | {result_str} | {dur:.0f}s | {tokens:,} |")

        lines.append("")

    out_path.write_text("\n".join(lines))


# ── MLflow logging ───────────────────────────────────────────────────────────

def log_to_mlflow(stats: dict, results: list[dict], results_dir: Path):
    """Log aggregated benchmark results, charts, and summary to MLflow."""
    mlflow.set_experiment(EXPERIMENT_NAME)

    run_name = stats.get("dirname", results_dir.name)

    param_keys = [
        "model", "edit_format", "commit_hash", "dirname",
        "completed_tests", "total_tests",
    ]
    metric_keys = [
        "pass_rate_1", "pass_rate_2",
        "pass_num_1", "pass_num_2",
        "percent_cases_well_formed",
        "error_outputs", "num_malformed_responses",
        "num_with_malformed_responses",
        "user_asks", "lazy_comments",
        "syntax_errors", "indentation_errors",
        "exhausted_context_windows", "test_timeouts",
        "seconds_per_case", "total_cost",
        "prompt_tokens", "completion_tokens",
    ]

    with mlflow.start_run(run_name=run_name):
        for key in param_keys:
            if key in stats:
                mlflow.log_param(key, stats[key])

        for key in metric_keys:
            if key in stats and stats[key] is not None:
                try:
                    mlflow.log_metric(key, float(stats[key]))
                except (ValueError, TypeError):
                    pass

        # Generate and log visual artifacts
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Charts
            print("  Generating charts...")
            pass_chart = tmpdir / "pass_rate.png"
            generate_pass_rate_chart(stats, pass_chart)
            if pass_chart.exists():
                mlflow.log_artifact(str(pass_chart), artifact_path="charts")

            lang_chart = tmpdir / "results_by_language.png"
            generate_language_chart(results, lang_chart)
            if lang_chart.exists():
                mlflow.log_artifact(str(lang_chart), artifact_path="charts")

            error_chart = tmpdir / "error_breakdown.png"
            generate_error_chart(stats, error_chart)
            if error_chart.exists():
                mlflow.log_artifact(str(error_chart), artifact_path="charts")

            # Markdown summary
            print("  Generating summary...")
            summary = tmpdir / "summary.md"
            generate_summary_markdown(stats, results, summary)
            mlflow.log_artifact(str(summary))

    print(f"\n✓ Logged to MLflow experiment '{EXPERIMENT_NAME}', run '{run_name}'")
    print(f"  model:       {stats.get('model', 'N/A')}")
    print(f"  exercises:   {stats.get('completed_tests', 0)}/{stats.get('total_tests', 0)}")

    i = 1
    while f"pass_rate_{i}" in stats:
        print(f"  pass_rate_{i}: {stats[f'pass_rate_{i}']}%")
        i += 1

    print(f"\nView results: mlflow ui  (then http://localhost:5000)")


def main():
    parser = argparse.ArgumentParser(
        description="Log Aider benchmark results to MLflow"
    )
    parser.add_argument(
        "results_dir",
        type=Path,
        help="Path to the benchmark results directory",
    )
    args = parser.parse_args()

    if not args.results_dir.is_dir():
        print(f"ERROR: {args.results_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Loading results from {args.results_dir} ...")
    results = load_exercise_results(args.results_dir)

    if not results:
        print("ERROR: No .aider.results.json files found", file=sys.stderr)
        print("  (If files exist but are unreadable, fix permissions with:)")
        print(f"  sudo chown -R $(whoami) {args.results_dir}")
        sys.exit(1)

    print(f"  Found {len(results)} exercise results")
    stats = aggregate_stats(results, args.results_dir)
    log_to_mlflow(stats, results, args.results_dir)


if __name__ == "__main__":
    main()
