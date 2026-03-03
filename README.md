# thesis

Turku University of Applied Sciences thesis repository. The thesis is about using locally run, privacy-focused, tech stack tuned LLMs for code generation in agentic style workflows.

## Local LLMs with Ollama

This project uses [Ollama](https://ollama.com/) to run local large language models.

### Installation (macOS)

Install Ollama using Homebrew:

```bash
brew install ollama
brew services start ollama
```

### Models Used

We use the following models:

- `qwen2.5-coder:32b`
- `qwen2.5-coder:7b`

To pull them locally, run:

```bash
ollama pull qwen2.5-coder:32b
ollama pull qwen2.5-coder:7b
```

To run and interact with a model in your terminal:

```bash
ollama run qwen2.5-coder:32b
ollama run qwen2.5-coder:7b
```

### Ollama Context Window

Ollama defaults to a 2K context window, which is too small for Aider (it silently drops context). Increase it before running benchmarks:

```bash
# Option 1: Set when starting Ollama
OLLAMA_CONTEXT_LENGTH=8192 ollama serve

# Option 2: Set via environment variable (add to ~/.zshrc)
export OLLAMA_CONTEXT_LENGTH=8192
```

## Benchmarking with Aider

We use the [Aider polyglot benchmark](https://aider.chat/2024/12/21/polyglot.html) — 225 Exercism coding exercises across C++, Go, Java, JavaScript, Python, and Rust. See [docs/architecture.md](docs/architecture.md) for full architecture diagrams.

### Setup

```bash
# Clone aider and the exercise set (one-time)
git clone https://github.com/Aider-AI/aider.git
cd aider && mkdir tmp.benchmarks
git clone https://github.com/Aider-AI/polyglot-benchmark tmp.benchmarks/polyglot-benchmark
./benchmark/docker_build.sh
cd ..

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install mlflow
```

### Running the Benchmark

```bash
# Smoke test (1 exercise, ~2 min)
./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:32b whole 1 smoke-test --new --num-tests 1

# Full benchmark (225 exercises, ~8 hours with 32b)
./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:32b whole 1 qwen32b-full

# Benchmark the 7b model
./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:7b whole 1 qwen7b-full
```

### Running for Specific Languages

Use `--languages` (or `-l`) with a comma-separated list to run only a subset of the six supported languages (C++, Go, Java, JavaScript, Python, Rust):

```bash
# Python only
./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:32b whole 1 qwen32b-python --languages "python"

# Python + JavaScript
./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:32b whole 1 qwen32b-py-js --languages "python,javascript"
```

You can also filter by exercise name keywords with `--keywords` / `-k`:

```bash
# Only exercises whose name contains "hello"
./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:32b whole 1 hello-test --keywords "hello"
```

When reviewing stats from a completed full run, use `--stats-languages` to show results for specific languages without re-running:

```bash
cd aider
./benchmark/benchmark.py --stats --stats-languages "python,rust" tmp.benchmarks/<results-dir>
```

### Logging Results to MLflow

```bash
source .venv/bin/activate  # if not already active

# Log benchmark results to MLflow (reads .aider.results.json files)
python3 scripts/log_benchmark_to_mlflow.py aider/tmp.benchmarks/<results-dir>

# Specify the Ollama context window size used during the benchmark
python3 scripts/log_benchmark_to_mlflow.py aider/tmp.benchmarks/<results-dir> --context-window 8192

# View results in browser
mlflow ui  # http://localhost:5000
```

The `--context-window` flag records the Ollama context window size as an MLflow parameter. If omitted, the script reads `$OLLAMA_CONTEXT_LENGTH` from the environment, falling back to Ollama's default of 2048.

The MLflow script aggregates all `.aider.results.json` files found under the results directory. If the benchmark was run with `--languages`, only those languages will have results, and the MLflow metrics will reflect that subset automatically.
