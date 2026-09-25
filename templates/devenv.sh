#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if ! command -v devenv >/dev/null 2>&1; then
  echo "ERROR: devenv is required. Install from https://devenv.sh or use native dependencies manually." >&2
  exit 1
fi

if [ ! -d .venv ]; then
  uv venv --python 3.11 --seed .venv
fi

if [ "$#" -eq 0 ]; then
  exec devenv shell bash -lc '. .venv/bin/activate && exec bash -i'
else
  exec devenv shell bash -lc ". .venv/bin/activate && $*"
fi
