#!/bin/sh
# Re-examine the bundled example projects (Apertus explanations are cached in data/cache).
set -e
cd "$(dirname "$0")/src"
for s in school-assistant-v1:school-assistant municipal-assistant:municipal-assistant town-hall-chat:town-hall-chat civicgpt:civicgpt school-assistant-v2:school-assistant; do
  python3 -m sigillum audit "../data/samples/${s%%:*}" --name "${s##*:}"
done
