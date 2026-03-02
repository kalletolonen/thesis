#!/usr/bin/env bash
# Run the Aider polyglot benchmark against a local Ollama model.
# Usage: ./scripts/run_aider_benchmark.sh [MODEL] [EDIT_FORMAT] [THREADS] [RUN_NAME]
#
# Examples:
#   ./scripts/run_aider_benchmark.sh                                          # defaults: qwen2.5-coder:32b, whole, 1 thread
#   ./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:7b whole 1 qwen7b-test
#   ./scripts/run_aider_benchmark.sh ollama_chat/qwen2.5-coder:32b whole 1 qwen32b-smoke --num-tests 2
set -euo pipefail

MODEL="${1:-ollama_chat/qwen2.5-coder:32b}"
EDIT_FORMAT="${2:-whole}"
THREADS="${3:-1}"
RUN_NAME="${4:-qwen-bench}"
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
./benchmark/docker.sh bash -c "
    export OLLAMA_API_BASE=http://host.docker.internal:11434
    pip install -e .[dev] --quiet
    ./benchmark/benchmark.py '$RUN_NAME' \
        --model '$MODEL' \
        --edit-format '$EDIT_FORMAT' \
        --threads '$THREADS' \
        --exercises-dir polyglot-benchmark \
        $*
"

echo ""
echo "=== Benchmark complete ==="
echo "Results in: $AIDER_DIR/tmp.benchmarks/"
echo "Generate report: ./benchmark/benchmark.py --stats tmp.benchmarks/<results-dir>"
