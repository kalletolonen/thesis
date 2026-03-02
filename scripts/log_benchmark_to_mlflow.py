#!/usr/bin/env python3
"""
Log Aider benchmark results to MLflow for experiment tracking.

Reads the per-exercise .aider.results.json files directly from the benchmark
results directory and aggregates them into MLflow metrics and parameters.

Usage:
    python scripts/log_benchmark_to_mlflow.py <results_dir>

Example:
    python scripts/log_benchmark_to_mlflow.py aider/tmp.benchmarks/2026-03-02-15-59-09--smoke-test
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import mlflow


EXPERIMENT_NAME = "aider-polyglot-benchmark"


def load_exercise_results(results_dir: Path) -> list[dict]:
    """Load all .aider.results.json files from the results directory."""
    results = []
    for fname in results_dir.glob("*/exercises/practice/*/.aider.results.json"):
        try:
            data = json.loads(fname.read_text())
            if data:
                results.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  Warning: skipping {fname}: {e}", file=sys.stderr)
    return results


def aggregate_stats(results: list[dict], results_dir: Path) -> dict:
    """Aggregate per-exercise results into summary statistics."""
    if not results:
        return {}

    total_exercises = len(
        list(results_dir.glob("*/exercises/practice/*"))
    )

    # Determine max number of tries
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

    # Flatten variant sets to single values for params
    for key, vals in variants.items():
        stats[key] = ", ".join(sorted(str(v) for v in vals))

    stats["dirname"] = results_dir.name

    return stats


def log_to_mlflow(stats: dict, results_dir: Path):
    """Log aggregated benchmark results to MLflow."""
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

        # Log per-exercise results as artifacts
        result_files = list(
            results_dir.glob("*/exercises/practice/*/.aider.results.json")
        )
        for rf in result_files[:20]:
            mlflow.log_artifact(str(rf), artifact_path="exercise_results")

    print(f"✓ Logged to MLflow experiment '{EXPERIMENT_NAME}', run '{run_name}'")
    print(f"  model:       {stats.get('model', 'N/A')}")
    print(f"  exercises:   {stats.get('completed_tests', 0)}/{stats.get('total_tests', 0)}")
    print(f"  pass_rate_1: {stats.get('pass_rate_1', 'N/A')}%")
    print(f"  pass_rate_2: {stats.get('pass_rate_2', 'N/A')}%")
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
    log_to_mlflow(stats, args.results_dir)


if __name__ == "__main__":
    main()
