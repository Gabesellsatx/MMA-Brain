#!/usr/bin/env bash
set -euo pipefail
mma_runtime="${RUNNER_TEMP:?}/mma-ollama"
mkdir -p "$mma_runtime"
curl --fail --location --retry 3 --silent --show-error \
  https://github.com/ollama/ollama/releases/download/v0.40.14/ollama-linux-amd64.tar.zst \
  --output "$mma_runtime/ollama.tar.zst"
printf '%s  %s\n' 993e83d08c3d13d17c55009a3e2664c8a25445e644aec3a68bef5abb6abce67d "$mma_runtime/ollama.tar.zst" | sha256sum --check
tar --zstd --extract --file "$mma_runtime/ollama.tar.zst" --directory "$mma_runtime" \
  --exclude='lib/ollama/cuda*' --exclude='lib/ollama/vulkan*' --exclude='lib/ollama/rocm*'
rm "$mma_runtime/ollama.tar.zst"
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_MODELS="$mma_runtime/models"
export OLLAMA_NUM_PARALLEL=1 OLLAMA_CONTEXT_LENGTH=8192 OLLAMA_NO_CLOUD=1
nohup "$mma_runtime/bin/ollama" serve > "$mma_runtime/server.log" 2>&1 &
for attempt in $(seq 1 30); do
  if curl --fail --silent http://127.0.0.1:11434/api/version; then break; fi
  sleep 1
done
curl --fail --silent --show-error http://127.0.0.1:11434/api/version
"$mma_runtime/bin/ollama" pull qwen3.5:4b
"$mma_runtime/bin/ollama" list
