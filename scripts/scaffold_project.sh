#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <slug> <destination> [--with-sample-voice]" >&2
  exit 2
fi

SLUG="$1"
DEST="$2"
WITH_VOICE="${3:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$DEST"/audio/scripts "$DEST"/audio/raw "$DEST"/out "$DEST"/tests "$DEST"/voices
cp "$SKILL_DIR/templates/devenv.nix" "$DEST/devenv.nix"
if [ -f "$SKILL_DIR/templates/devenv.lock" ]; then
  cp "$SKILL_DIR/templates/devenv.lock" "$DEST/devenv.lock"
fi
cp "$SKILL_DIR/templates/devenv.sh" "$DEST/devenv.sh"
cp "$SKILL_DIR/templates/build.py" "$DEST/build.py"
cp "$SKILL_DIR/templates/explainer.py" "$DEST/explainer.py"
cp "$SKILL_DIR/templates/requirements.txt" "$DEST/requirements.txt"
cp "$SKILL_DIR/templates/requirements-voice.txt" "$DEST/requirements-voice.txt"
cp "$SKILL_DIR/templates/tests/test_project.py" "$DEST/tests/test_project.py"
chmod +x "$DEST/devenv.sh"

cat > "$DEST/README.md" <<EOF
# ${SLUG} explainer video

Generated from explainervid-skill.

## Setup

\`\`\`bash
./devenv.sh 'python -m pip install -r requirements.txt'
./devenv.sh 'python build.py check'
\`\`\`

## Piper voice

\`\`\`bash
./devenv.sh 'python -m pip install -r requirements-voice.txt'
./devenv.sh 'python -m piper.download_voices en_US-lessac-medium --data-dir voices'
./devenv.sh 'python build.py audio --tts piper --model voices/en_US-lessac-medium.onnx --length-scale 0.95 --force'
\`\`\`

## Render

\`\`\`bash
./devenv.sh 'python build.py render --quality low --scene Motivation'
./devenv.sh 'python build.py render --quality low'
./devenv.sh 'python build.py assemble --quality low'
\`\`\`
EOF

cat > "$DEST/STORYBOARD.md" <<EOF
# ${SLUG} storyboard

Replace with scene-by-scene outline. See explainervid-skill references/storyboard-template.md.
EOF
cat > "$DEST/NARRATION.md" <<EOF
# ${SLUG} narration

Replace with timed narration grouped by scene. The authoritative cue text lives in PLAN inside explainer.py.
EOF
cat > "$DEST/narration.txt" <<EOF
Replace with plain narration text after finalizing PLAN.
EOF
cat > "$DEST/SOURCE_NOTES.md" <<EOF
# Source notes

Record source title/files/links, claims, equations, measured values, illustrative diagrams, and limitations.
EOF
cat > "$DEST/QA.md" <<EOF
# QA

## Verified

- Not yet verified.

## Not verified

- Replace after checks/renders.
EOF

if [ "$WITH_VOICE" = "--with-sample-voice" ]; then
  if [ -f "$SKILL_DIR/assets/voices/en_US-lessac-medium.onnx" ] && [ -f "$SKILL_DIR/assets/voices/en_US-lessac-medium.onnx.json" ]; then
    cp "$SKILL_DIR/assets/voices/en_US-lessac-medium.onnx" "$DEST/voices/"
    cp "$SKILL_DIR/assets/voices/en_US-lessac-medium.onnx.json" "$DEST/voices/"
  else
    echo "Sample voice missing; use piper.download_voices in generated project." >&2
  fi
fi

echo "Created $DEST"
echo "Next: cd $DEST && ./devenv.sh 'python -m pip install -r requirements.txt -r requirements-voice.txt && python build.py check'"
