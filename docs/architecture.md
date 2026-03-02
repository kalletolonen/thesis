# Benchmarking Architecture

## Overview

The benchmarking pipeline evaluates locally-run Qwen LLMs on coding tasks from the [Aider polyglot benchmark](https://aider.chat/2024/12/21/polyglot.html) (225 Exercism exercises across 6 languages). Results are tracked in MLflow for experiment comparison.

## System Diagram

```mermaid
flowchart TB
    subgraph Host["Host Machine (macOS)"]
        Ollama["Ollama\nqwen2.5-coder:32b / :7b\nlocalhost:11434"]
        MLflow["MLflow Tracking Server\nlocalhost:5000"]
        LogScript["log_benchmark_to_mlflow.py"]
    end

    subgraph Docker["Docker Container"]
        Aider["Aider + benchmark.py"]
        Exercises["Polyglot Benchmark\n225 Exercism exercises\nC++ / Go / Java / JS / Python / Rust"]
        Tests["Unit Test Runner"]
    end

    Aider -- "OpenAI-compat API\nhttp://host.docker.internal:11434" --> Ollama
    Ollama -- "Code completions" --> Aider
    Aider --> Exercises
    Exercises --> Tests
    Tests -- "YAML results" --> LogScript
    LogScript -- "params + metrics + artifacts" --> MLflow
```

## Data Flow

```mermaid
sequenceDiagram
    participant B as benchmark.py
    participant A as Aider
    participant O as Ollama (Qwen)
    participant T as Test Runner
    participant M as MLflow

    loop For each of 225 exercises
        B->>A: Start exercise (problem description + starter code)
        A->>O: Generate/edit code (via OpenAI-compat API)
        O-->>A: Code completion
        A->>B: Write solution files
        B->>T: Run unit tests
        T-->>B: Pass / Fail
    end

    B->>B: Generate YAML stats report
    B->>M: Log params, metrics, artifacts
```

## Key Configuration

| Setting           | Value                               | Notes                                       |
| ----------------- | ----------------------------------- | ------------------------------------------- |
| Ollama API        | `http://host.docker.internal:11434` | Docker → host connectivity (macOS)          |
| Context window    | ≥8192 tokens                        | Ollama default 2K is too small for Aider    |
| Edit format       | `whole`                             | Recommended starting point for local models |
| MLflow experiment | `aider-polyglot-benchmark`          | Groups all benchmark runs                   |
