#!/bin/sh
# Re-examine the bundled example projects (Apertus explanations are cached in data/cache).
set -e
cd "$(dirname "$0")/src"
for s in assistant-ecole-v1:assistant-ecole gemeinde-assistent:gemeinde-assistent chat-commune:chat-commune civicgpt:civicgpt assistant-ecole-v2:assistant-ecole; do
  python3 -m sigillum audit "../data/samples/${s%%:*}" --name "${s##*:}"
done
