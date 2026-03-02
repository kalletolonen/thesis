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

Set up the benchmarking pipeline with AI generated scripts:

- Created `docs/architecture.md` with Mermaid diagrams showing the system architecture.
- Created `scripts/run_aider_benchmark.sh` for running the benchmark against Ollama.
- Created `scripts/log_benchmark_to_mlflow.py` for logging results to MLflow for experiment tracking.

**Important discovery: Ollama context window.** Ollama defaults to 2K context tokens, which is far too small for Aider. It silently drops context, leading to degraded results. Must set `OLLAMA_CONTEXT_LENGTH=8192` (or higher) before running benchmarks.

### What I learned

Learned that there are many different benchmarking tools and methods for LLMs. Also learned that MLFlow is a good tool for tracking experiments https://mlflow.org/docs/latest/ml/tracking/.

## 3.3.2026

### What I did

Ran the Aider benchmark against the local Qwen 32B model. Also installed MLFlow in a virtual environment to have visibility of the results. The benchmark did not run at first, but after some debugging I got it to run.

### What I learned

Was not first able to get the benchmark to run. It seems like there is a problem with the benchmark script.

### What I want to do next

It's crucial to get the fine-tuning right, so I need to research different fine-tuning methods for LLMs.
