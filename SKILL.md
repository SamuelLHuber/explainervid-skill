---
name: explainervid
description: Creates complete reproducible Manim + Piper educational explainer video packages from papers, articles, scripts, PDFs, or technical source material. Use when the user asks for a 3Blue1Brown-inspired/geometric visual explainer, storyboard, narration, Manim code, voiceover generation, render pipeline, or final MP4.
compatibility: Requires Python 3.11+, uv, devenv/Nix, Cairo/Pango/LaTeX/FFmpeg dependencies, and enough time to render Manim scenes.
---

# Explainervid Skill

Create complete educational video production packages using Manim Community Edition, Piper TTS, FFmpeg, and a reproducible `devenv.nix` environment.

Use this skill for papers, PDFs, articles, pasted text, technical docs, or scripts that should become an intuitive geometric explainer. The style should be dark-background, clean, mathematical, and visual-first; never claim to be an official 3Blue1Brown production or use cloned voices/branding.

## Intake: ask for the input first

If the user has not already provided source material, ask one concise question:

> What source should the explainer be based on: PDF, link, pasted text, article, existing script, or outline/topic?

If still underspecified, ask for:

1. target audience,
2. desired length, default 7-9 minutes,
3. final deliverable: production package only or rendered MP4,
4. whether to use Piper TTS,
5. any claims/equations/results that must be included.

Do not invent paper facts, metrics, equations, or results. Mark visual metaphors as illustrative unless they are actual measurements or source figures.

## Required project output

Create a directory named `<slug>_video/` containing:

```text
<slug>_video/
├── devenv.nix
├── devenv.lock
├── devenv.sh
├── build.py
├── explainer.py              # or rename consistently and update build.py SOURCE
├── README.md
├── STORYBOARD.md
├── NARRATION.md
├── narration.txt
├── SOURCE_NOTES.md
├── QA.md
├── requirements.txt
├── requirements-voice.txt
├── tests/
├── audio/scripts/
├── audio/raw/
├── voices/                   # optional Piper model copy/download target
├── build/
└── out/
```

Use files under `templates/` as the starting point. Resolve relative paths against this skill directory.

## Source-fidelity workflow

Before writing scenes, produce `SOURCE_NOTES.md` with:

- source files/links and title,
- core claims used in the video,
- equations/tables/numbers copied from the source,
- ambiguous notation or interpretation decisions,
- what is illustrative vs measured,
- what the video must not imply,
- limitations and safety caveats.

For PDFs, extract text first. Use `scripts/extract_pdf_text.py` if helpful.

## Narrative arc

Default 7-9 minute structure:

1. motivation/problem,
2. key insight,
3. how the method/idea works,
4. why the constraint/regularization/caveat matters,
5. evidence/results,
6. takeaway.

Prefer progressive visual metaphors, morphing diagrams, term-by-term equations, and timed reveals. Avoid dense text slides.

## Manim implementation rules

Use a single self-contained Manim CE file, normally `explainer.py`.

Maintain a literal top-level `PLAN` list containing scene metadata, durations, beat start/end times, narration text, visual directions, and source references. `build.py` statically reads this `PLAN`, so it must remain literal Python data.

Each production scene must call `self.beat(i)` once for each cue in order. Use the `TimedScene` pattern from `templates/explainer.py`.

Do not use Manim `-a`; render only production scene classes.

## Reproducible environment

Use cachix/devenv via the bundled `devenv.nix`, pinned `devenv.lock`, and `devenv.sh` wrapper. Initial setup in a generated project:

```bash
./devenv.sh 'python -m pip install -r requirements.txt'
./devenv.sh 'python build.py check'
```

Install Piper support:

```bash
./devenv.sh 'python -m pip install -r requirements-voice.txt'
```

If `voices/en_US-lessac-medium.onnx` is bundled/copied into the project, use it. Otherwise download:

```bash
./devenv.sh 'python -m piper.download_voices en_US-lessac-medium --data-dir voices'
```

Generate narration:

```bash
./devenv.sh 'python build.py audio --tts piper --model voices/en_US-lessac-medium.onnx --length-scale 0.95 --force'
```

If a cue overflows, lower `--length-scale` or shorten that cue. Never truncate narration.

## Render and assemble

Run checks first:

```bash
./devenv.sh 'python build.py check'
./devenv.sh 'python -m unittest discover -s tests -v'
```

Preview one scene:

```bash
./devenv.sh 'python build.py render --quality low --scene Motivation'
```

Render and assemble low quality:

```bash
./devenv.sh 'python build.py render --quality low'
./devenv.sh 'python build.py assemble --quality low'
```

High quality release:

```bash
./devenv.sh 'python build.py render --quality high'
./devenv.sh 'python build.py assemble --quality high'
```

## QA before reporting success

Before saying the video is complete:

1. verify final MP4 exists,
2. probe duration, resolution, FPS, audio, subtitles,
3. generate at least two preview PNG frames with FFmpeg,
4. inspect those preview frames,
5. report known warnings, e.g. font fallback or TTS speedups,
6. update `QA.md` with what was and was not verified.

## Helpful commands

Scaffold a new project from this skill:

```bash
scripts/scaffold_project.sh my_explainer /path/to/my_explainer_video --with-sample-voice
```
