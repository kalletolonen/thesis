## 27.2.2026

### What I did

Started the thesis project by setting up the local LLM environment and creating the initial README.md file.

### What I learned

Learned how to use Ollama to run local LLMs. Also learned that the benchmarking might be a headache, if I'm going to use SWE-bench. It requires too much disk space for my computer (120 GB). https://www.swebench.com/SWE-bench/guides/docker_setup/

### What I want to do next

It's crucial to get the benchmarking right, so I need to research different benchmarking tools and methods for LLMs. Using MLFlow for tracking the experiments seems like a good idea.

## 28.2.2026

### What I did

Explored benchmarking options for evaluating the local Qwen models:

- Investigated **SWE-bench** (2,294 real-world GitHub issues) — requires ~120 GB Docker images for evaluation. Considered remote evaluation via `sb-cli` + Modal cloud, but pivoted to a simpler local solution. Aider benchmark is a much more practical alternative for local benchmarking — it's well-documented, reproducible, resource usage is neglible. https://aider.chat/2024/12/21/polyglot.html#the-polyglot-benchmark
- Settled on the **Aider polyglot benchmark** — 225 Exercism coding exercises across C++, Go, Java, JS, Python, and Rust. Runs locally in a lightweight Docker sandbox. Qwen 32B Coder is already on the Aider leaderboard, so we get a direct comparison.

Set up the benchmarking pipeline:

- Created `docs/architecture.md` with Mermaid diagrams showing the system architecture.
- Created `scripts/run_aider_benchmark.sh` for running the benchmark against Ollama.
- Created `scripts/log_benchmark_to_mlflow.py` for logging results to MLflow for experiment tracking.
- Decided to use **MLflow** to track benchmark results — this will be essential later when customizing/fine-tuning models and comparing progress.

**Important discovery: Ollama context window.** Ollama defaults to 2K context tokens, which is far too small for Aider. It silently drops context, leading to degraded results. Must set `OLLAMA_CONTEXT_LENGTH=8192` (or higher) before running benchmarks.

### What I learned

Learned that there are many different benchmarking tools and methods for LLMs. Also learned that MLFlow is a good tool for tracking experiments.
