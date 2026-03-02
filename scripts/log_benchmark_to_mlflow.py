#!/usr/bin/env python3
"""
Log Aider benchmark results to MLflow for experiment tracking.

Usage:
    python scripts/log_benchmark_to_mlflow.py <results_dir>

Example:
    python scripts/log_benchmark_to_mlflow.py aider/tmp.benchmarks/2026-02-27-20-00-00--qwen32b-bench
"""

import argparse
import json
import sys
from pathlib import Path

import mlflow
import yaml


EXPERIMENT_NAME = "aider-polyglot-benchmark"

# Metrics to log from the benchmark YAML
METRIC_KEYS = [
    "pass_rate_1",
    "pass_rate_2",
    "percent_cases_well_formed",
    "error_outputs",
    "num_malformed_responses",
    "num_with_malformed_responses",
    "user_asks",
    "lazy_comments",
    "syntax_errors",
    "indentation_errors",
    "exhausted_context_windows",
    "test_timeouts",
    "seconds_per_case",
    "total_cost",
    "test_cases",
]

# Parameters to log
PARAM_KEYS = [
    "model",
    "edit_format",
    "commit_hash",
    "versions",
    "date",
    "command",
]


def find_stats_file(results_dir: Path) -> Path:
    """Find the benchmark stats YAML file in a results directory."""
    # benchmark.py --stats generates output to stdout as YAML
    # The raw results are in .aider.results.json files per exercise
    # We look for a pre-generated stats file or generate from the dir
    for candidate in [
        results_dir / "benchmark_stats.yaml",
        results_dir / "benchmark_stats.yml",
    ]:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        f"No benchmark stats file found in {results_dir}. "
        f"Generate it first with: ./benchmark/benchmark.py --stats {results_dir}"
    )


def parse_stats(stats_file: Path) -> dict:
    """Parse the benchmark stats YAML file."""
    with open(stats_file) as f:
        data = yaml.safe_load(f)

    # Stats file contains a list with one entry
    if isinstance(data, list):
        return data[0]
    return data


def log_to_mlflow(stats: dict, results_dir: Path):
    """Log benchmark results to MLflow."""
    mlflow.set_experiment(EXPERIMENT_NAME)

    run_name = stats.get("dirname", results_dir.name)

    with mlflow.start_run(run_name=run_name):
        # Log parameters
        for key in PARAM_KEYS:
            if key in stats:
                mlflow.log_param(key, stats[key])

        # Log metrics
        for key in METRIC_KEYS:
            if key in stats and stats[key] is not None:
                try:
                    mlflow.log_metric(key, float(stats[key]))
                except (ValueError, TypeError):
                    pass  # skip non-numeric values

        # Log the full stats as an artifact
        stats_file = results_dir / "benchmark_stats.yaml"
        if stats_file.exists():
            mlflow.log_artifact(str(stats_file))

        # Log any .aider.results.json files as artifacts
        results_files = list(results_dir.glob("**/.aider.results.json"))
        if results_files:
            for rf in results_files[:10]:  # limit to avoid huge uploads
                mlflow.log_artifact(str(rf), artifact_path="exercise_results")

        print(f"Logged to MLflow experiment '{EXPERIMENT_NAME}', run '{run_name}'")
        print(f"  pass_rate_1: {stats.get('pass_rate_1', 'N/A')}%")
        print(f"  pass_rate_2: {stats.get('pass_rate_2', 'N/A')}%")
        print(f"  model: {stats.get('model', 'N/A')}")
        print(f"\nView results: mlflow ui  (then browse to http://localhost:5000)")


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

    stats_file = find_stats_file(args.results_dir)
    stats = parse_stats(stats_file)
    log_to_mlflow(stats, args.results_dir)


if __name__ == "__main__":
    main()
