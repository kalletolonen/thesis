#!/usr/bin/env bash
# Run the Aider agentic benchmark against a local Ollama model (tailored for Gemma 4 / Local Agent testing).
# Usage: ./scripts/run_aider_benchmark.sh [MODEL] [EDIT_FORMAT] [THREADS] [RUN_NAME]
#
# Examples:
#   ./scripts/run_aider_benchmark.sh                                          # defaults: gemma4:9b, tool, 1 thread
#   ./scripts/run_aider_benchmark.sh ollama_chat/gemma4:9b tool 1 gemma4-agent-test
#   ./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:32b whole 1 qwen32b-smoke --num-tests 2
set -euo pipefail

MODEL="${1:-ollama_chat/gemma4:9b}"
EDIT_FORMAT="${2:-tool}"
THREADS="${3:-1}"
RUN_NAME="${4:-gemma4-bench}"
shift 4 2>/dev/null || true  # remaining args passed through to benchmark.py

AIDER_DIR="$(cd "$(dirname "$0")/../aider" && pwd)"

# Verify Ollama is running
if ! curl -s http://localhost:11434/v1/models > /dev/null 2>&1; then
    echo "ERROR: Ollama is not running. Start it with: brew services start ollama"
    exit 1
fi

echo "=== Aider Polyglot Benchmark ==="
echo "Model:       $MODEL"
echo "Edit format: $EDIT_FORMAT"
echo "Threads:     $THREADS"
echo "Run name:    $RUN_NAME"
echo "Aider dir:   $AIDER_DIR"
echo ""

cd "$AIDER_DIR"

# Launch Docker container and run benchmark inside it
# OLLAMA_API_BASE is set inside the container to reach host Ollama
docker run \
    --rm \
    --memory=12g \
    --memory-swap=12g \
    --add-host=host.docker.internal:host-gateway \
    -v "$AIDER_DIR":/aider \
    -v "$AIDER_DIR"/tmp.benchmarks/.:/benchmarks \
    -e OLLAMA_API_BASE="http://host.docker.internal:11434" \
    -e AIDER_DOCKER=1 \
    -e AIDER_BENCHMARK_DIR=/benchmarks \
    -e HOME=/tmp \
    -w /aider \
    --user "$(id -u):$(id -g)" \
    aider-benchmark \
    bash -c "pip install --user -e .[dev] --quiet 2>/dev/null; ./benchmark/benchmark.py '$RUN_NAME' --model '$MODEL' --edit-format '$EDIT_FORMAT' --threads '$THREADS' --dataset swe-bench-lite $*"

echo ""
echo "=== Agentic Benchmark complete ==="
echo "Results in: $AIDER_DIR/tmp.benchmarks/"
echo "Generate report: ./benchmark/benchmark.py --stats tmp.benchmarks/<results-dir>"
