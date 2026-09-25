#!/usr/bin/env bash
set -euo pipefail
MODEL="${1:-voices/en_US-lessac-medium.onnx}"
LENGTH_SCALE="${2:-0.95}"
python build.py audio --tts piper --model "$MODEL" --length-scale "$LENGTH_SCALE" --force
