# explainervid-skill

Pi/Agent Skill for creating reproducible Manim + Piper educational explainer video production packages from papers, articles, scripts, PDFs, or technical source material.

The skill scaffolds a project with:

- `devenv.nix` + `devenv.lock` + `devenv.sh` using [cachix/devenv](https://github.com/cachix/devenv) for reproducible native dependencies
- Manim Community Edition project template
- Piper-compatible voiceover pipeline
- subtitle/chapter/final MP4 assembly via FFmpeg
- QA/test templates
- source-fidelity and storyboard workflow docs

## Install for Pi

```bash
mkdir -p ~/.pi/agent/skills
ln -s ~/git/explainervid-skill ~/.pi/agent/skills/explainervid-skill
```

Then ask Pi for `/skill:explainervid` or say something like:

> Create a 7–9 minute geometric educational explainer video from this PDF.

## Scaffold a project manually

```bash
./scripts/scaffold_project.sh my_paper ~/git/my_paper_video --with-sample-voice
cd ~/git/my_paper_video
./devenv.sh 'python -m pip install -r requirements.txt -r requirements-voice.txt'
./devenv.sh 'python build.py check'
./devenv.sh 'python build.py audio --tts piper --model voices/en_US-lessac-medium.onnx --length-scale 0.95 --force'
./devenv.sh 'python build.py render --quality low'
./devenv.sh 'python build.py assemble --quality low'
```

## Bundled voice

This repository may include `assets/voices/en_US-lessac-medium.onnx` and `.onnx.json` as a convenience sample Piper voice. Check the upstream Piper voice license before publishing outputs at scale. If absent, the generated project can download it with:

```bash
./devenv.sh 'python -m piper.download_voices en_US-lessac-medium --data-dir voices'
```
