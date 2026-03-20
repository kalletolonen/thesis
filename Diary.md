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

## 2.3.2026

### What I did

Ran the Aider benchmark against the local Qwen 32B model. Also installed MLFlow in a virtual environment to have visibility of the results. The benchmark did not run at first, but after some debugging I got it to run. Then I made the results include charts and a summary markdown file.

### What I learned

Learned that the benchmark is going to take a lot of time to run fully, so I'll need to figure out ways to run language targetted benchmarks instead of the full benchmark.

### What I want to do next

After the benchmark is done, I'll need to figure out how to fine-tune the models to improve their performance. I'll also need to figure out how to use the models in an agentic style workflow.

## 3.3.2026

### What I did

Ran the Aider benchmark against the local Qwen 32B model for the whole benchmark. Started to second guess the OLLAMA_CONTEXT_LENGTH=8192 setting, so I added that to MLFlow logging. Pip requireremts were frozen, since they may provide variance in results otherwise.

### What I learned

Benchmarking is time consuming, so it's productive to run it overnight to utilize the time when I'm not using resources for other tasks.

### What I want to do next

I need to run the benchmark for the 7b model too at some point in the future to have a baseline for comparison for that one too and gather info on other possible models to use.

## 4.3.2026-7.3.2026

### What I did

Analysis on the results of the Aider benchmark for the large OLLAMA_CONTEXT told that it did not matter for the performance of the model. The results were almost identical with the stock context length of 2048 tokens, so I was suspicious of Ollama being able to read the environment variable that was set. I was right about that, since Aider does allow for overriding the context length of the model. It can be done with the `--num-ctx` flag. https://github.com/Aider-AI/aider/commit/c5ce57ea7fe93242600643541c4376ef015c7bdd. Documentation is not great, but studying source code revealed that it is possible to override the context length of the model. Context length should affect the performance, especially if we're defaulting to around 2048 tokens. https://datanorth.ai/blog/context-length

Now that there's a rudimentary, repeatable benchmark, I can start working on the fine-tuning part of the thesis. We should run the whole benchmark with different context windows, to gather some baseline results for the thesis. Then when we run the benchmark for the fine tuned model, we can compare the results to the baseline results to see if the fine-tuning improved the performance of the model and if there are regressions in performance for other languages, which should be expected somewhere along the fine tuning path.

The results produced by the benchmark did show that the context length was unnessary override, as Aider does adjust the context length of the model automatically based on the message size.

```
if self.is_ollama() and "num_ctx" not in kwargs:
    num_ctx = int(self.token_count(messages) * 1.25) + 8192
    kwargs["num_ctx"] = num_ctx
```

That would also explain why the results were almost identical with the stock context length of 2048 tokens, since the Aider would adjust the context size automatically based on the message size.

### Put pics here to show the almost identical results for context length.

I also benchmarked the 7b model and the results were almost identical to the 32b model.

### Put pics here to show the results of the 7b model.
