# System Architecture

## Overview

The thesis currently evaluates an entirely private, local agentic workflow utilizing locally-run quantized models (e.g., Gemma 4). It evaluates autonomous agent abilities such as multi-step refactoring, linter loops, and project orchestration using IDE-native extensions (like Continue/Aider).

## Agentic IDE Architecture

```mermaid
flowchart TB
    subgraph Host["Host Machine (macOS)"]
        IDE["VS Code / IDE\n(Agent UI)"]
        Ollama["Ollama Server\n(Gemma-4-quantized)\nlocalhost:11434"]
        LocalEmbed["Local Embedding Model\n(e.g. nomic-embed-text)"]
        VectorDB["Local Vector Store\n(Chroma/FAISS)"]
        Linter["Language Linters / Compilers"]
    end

    IDE -- "Tool calls & chat (Local API)" --> Ollama
    Ollama -- "Code edits & terminal commands" --> IDE
    IDE -- "Index sources" --> LocalEmbed
    LocalEmbed -- "Embeddings" --> VectorDB
    IDE -- "Semantic search" --> VectorDB
    IDE -- "Run build/lint validation" --> Linter
    Linter -- "Errors (Fed to agent)" --> IDE
```

## Agentic Workflow Data Flow

```mermaid
sequenceDiagram
    participant U as Developer (VS Code)
    participant A as IDE Agent
    participant E as Embeddings / RAG
    participant O as Ollama (Gemma 4)
    participant L as Workspace Linters

    U->>A: "Refactor feature X to support Y"
    A->>E: Query codebase for X
    E-->>A: Relevant code snippets
    A->>O: Prompt: intent + code chunks + tools
    O-->>A: Tool Call: read_file(path)
    A-->>O: File contents
    O-->>A: Tool Call: edit_file(path, replacements)
    A->>L: Save & Run diagnostics
    L-->>A: Linting/Compile errors
    A->>O: Prompt: Fix these errors
    O-->>A: Tool Call: edit_file(path, final_replacements)
    A->>U: Validation complete, ready for review
```

## Benchmarking Architecture (Legacy / Polyglot)

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
