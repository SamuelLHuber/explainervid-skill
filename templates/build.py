#!/usr/bin/env python3
"""Render, voice, subtitle, and assemble the Explainer explainer.

The PLAN is extracted from explainer.py with ast.literal_eval, so checking
and audio assembly do not import Manim. All subprocesses use argument lists,
never shell=True. Human recordings and external TTS WAVs are also supported.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import textwrap
import wave
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'explainer.py'
WORK = ROOT / 'build'
OUT = ROOT / 'out'
FPS = 30
LEAD = 0.35
TAIL = 0.65
SAMPLE_RATE = 48000
SIZES = {'low': (854, 480), 'medium': (1280, 720), 'high': (1920, 1080)}


def final_name() -> str:
    stem = ROOT.name
    if stem.endswith('_video'):
        stem = stem[:-6]
    if stem.endswith('-video'):
        stem = stem[:-6]
    stem = stem or 'explainer'
    safe = re.sub(r'[^A-Za-z0-9_.-]+', '_', stem).strip('._-') or 'explainer'
    return f'{safe}.mp4'


def load_plan(source: Path = SOURCE) -> list[dict[str, Any]]:
    tree = ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PLAN'
                                               for t in node.targets):
            plan = ast.literal_eval(node.value)
            if not isinstance(plan, list):
                raise ValueError('PLAN must be a literal list.')
            return plan
    raise ValueError('No literal PLAN assignment found in explainer.py.')


def cue_name(scene: str, index: int) -> str:
    return f'{scene}_{index:02d}'


def run(command: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    print('+', ' '.join(str(c) for c in command), flush=True)
    return subprocess.run(command, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None)


def require_program(name: str):
    if shutil.which(name) is None:
        raise RuntimeError(f'{name} was not found on PATH. See README.md for installation.')


def probe(path: Path) -> dict[str, Any]:
    require_program('ffprobe')
    result = run(['ffprobe', '-v', 'error', '-show_format', '-show_streams',
                  '-of', 'json', str(path)], capture=True)
    return json.loads(result.stdout)


def duration(path: Path) -> float:
    return float(probe(path)['format']['duration'])


def stamp(seconds: float, srt: bool = False) -> str:
    ms = round(seconds * 1000)
    hours, rest = divmod(ms, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    if srt:
        return f'{hours:02}:{minutes:02}:{secs:02},{millis:03}'
    return f'{hours * 60 + minutes:02}:{secs:02}'


def total_duration(plan: list[dict[str, Any]]) -> float:
    return sum(float(s['duration']) for s in plan)


def check(plan: list[dict[str, Any]]):
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    scene_nodes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    offset = 0.0
    words = 0
    print('Scene                    Time          Duration  Words  Words/min')
    for spec in plan:
        if spec['scene'] not in scene_nodes:
            raise ValueError(f'Missing Scene class: {spec["scene"]}')
        beats = spec['beats']
        if beats[0]['start'] != 0 or beats[-1]['end'] != spec['duration']:
            raise ValueError(f'Beat endpoints do not span {spec["scene"]}.')
        for i, b in enumerate(beats):
            if b['end'] <= b['start']:
                raise ValueError('Cue duration must be positive.')
            if i and b['start'] != beats[i - 1]['end']:
                raise ValueError(f'Non-contiguous beats in {spec["scene"]}.')
            if not b['text'].strip():
                raise ValueError('Empty narration cue.')
        calls = []
        construct = next(n for n in scene_nodes[spec['scene']].body
                         if isinstance(n, ast.FunctionDef) and n.name == 'construct')
        for n in ast.walk(construct):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'beat':
                calls.append((n.lineno, ast.literal_eval(n.args[0])))
        if [i for _, i in sorted(calls)] != list(range(len(beats))):
            raise ValueError(f'Animation cue calls do not match narration: {spec["scene"]}')
        wc = sum(len(b['text'].split()) for b in beats)
        words += wc
        print(f'{spec["scene"]:24} {stamp(offset)}-{stamp(offset + spec["duration"])}'
              f'  {spec["duration"]:5.0f}s   {wc:4}   {60 * wc / spec["duration"]:6.1f}')
        offset += spec['duration']
    if not (420 <= offset <= 540):
        raise ValueError(f'Expected a 7-9 minute timeline (420-540 seconds), found {offset}.')
    for py in ROOT.glob('*.py'):
        compile(py.read_text(encoding='utf-8'), str(py), 'exec')
    print(f'PASS: {len(plan)} scenes, {sum(len(s["beats"]) for s in plan)} cues, '
          f'{words} words, {stamp(offset)} total. Python syntax checked.')
    print('This command does not render Manim or assess synthesized speech.')


def export_text(plan: list[dict[str, Any]]):
    OUT.mkdir(parents=True, exist_ok=True)
    scripts = ROOT / 'audio' / 'scripts'
    scripts.mkdir(parents=True, exist_ok=True)
    manifest, offset = [], 0.0
    for s in plan:
        for i, b in enumerate(s['beats']):
            name = cue_name(s['scene'], i)
            (scripts / f'{name}.txt').write_text(b['text'] + '\n', encoding='utf-8')
            manifest.append({'id': name, 'scene': s['scene'], 'index': i,
                             'start': offset + b['start'], 'end': offset + b['end'],
                             'local_start': b['start'], 'local_end': b['end'],
                             'text': b['text'], 'visual': b['visual']})
        offset += s['duration']
    (OUT / 'timeline.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    project_title = ROOT.name.replace('_', ' ').replace('-', ' ').title()
    chapter_lines = [';FFMETADATA1', f'title={project_title}',
                     'artist=Independent educational explainer']
    offset = 0.0
    for s in plan:
        chapter_lines.extend(['[CHAPTER]', 'TIMEBASE=1/1000', f'START={round(offset * 1000)}',
                              f'END={round((offset + s["duration"]) * 1000)}', f'title={s["title"]}'])
        offset += s['duration']
    (OUT / 'chapters.ffmeta').write_text('\n'.join(chapter_lines) + '\n', encoding='utf-8')
    return manifest


def spoken_text(s: str) -> str:
    """Pronunciation substitutions only; captions keep the original terminology."""
    for old, new in [('T5', 'tee five'),
                     ('MoE', 'M O E'), ('BLEU-four', 'blue four'),
                     ('BLEU@4', 'blue four'), ('ROUGE-L', 'rouge L'),
                     ('BERTScore', 'BERT score')]:
        s = s.replace(old, new)
    return s


def write_concat(paths: list[Path], destination: Path):
    def escaped(p: Path) -> str:
        return p.resolve().as_posix().replace("'", "'\\''")
    destination.write_text(''.join(f"file '{escaped(p)}'\n" for p in paths), encoding='utf-8')


def write_subtitles(manifest: list[dict[str, Any]], report: dict[str, Any] | None = None):
    """Cue-locked, approximate phrase timing; not forced word alignment."""
    report = report or {}
    blocks, number = [], 1
    for cue in manifest:
        info = report.get(cue['id'], {})
        speech_seconds = info.get('speech_seconds', cue['end'] - cue['start'] - LEAD - TAIL)
        start = cue['start'] + LEAD
        words = cue['text'].split()
        # No caption contains more than 14 words; wrap to two typical lines.
        chunks = [words[i:i + 14] for i in range(0, len(words), 14)]
        used = 0
        for chunk in chunks:
            a = start + speech_seconds * used / len(words)
            used += len(chunk)
            z = start + speech_seconds * used / len(words)
            body = '\n'.join(textwrap.wrap(' '.join(chunk), width=47))
            blocks.append(f'{number}\n{stamp(a, True)} --> {stamp(z, True)}\n{body}\n')
            number += 1
    (OUT / 'narration.srt').write_text('\n'.join(blocks), encoding='utf-8')


def generate_audio(plan: list[dict[str, Any]], args: argparse.Namespace):
    require_program('ffmpeg')
    require_program('ffprobe')
    manifest = export_text(plan)
    raw_dir = ROOT / 'audio' / 'raw'
    prepared = WORK / 'cue_audio'
    raw_dir.mkdir(parents=True, exist_ok=True)
    prepared.mkdir(parents=True, exist_ok=True)
    voice = None
    if args.tts == 'piper':
        if not args.model:
            raise ValueError('--model is required for Piper; pass the path to the .onnx voice.')
        model = Path(args.model).expanduser().resolve()
        if not model.is_file() or not Path(str(model) + '.json').is_file():
            raise FileNotFoundError(f'Need both {model} and {model}.json; download the voice first.')
        try:
            from piper import PiperVoice, SynthesisConfig
        except ImportError as e:
            raise RuntimeError('Install requirements-voice.txt, or use --tts existing.') from e
        voice = PiperVoice.load(str(model))
        synthesis = SynthesisConfig(length_scale=args.length_scale,
                                    noise_scale=0.5, noise_w_scale=0.6)
    paths, report = [], {}
    for cue in manifest:
        raw = raw_dir / f'{cue["id"]}.wav'
        metadata_path = raw.with_suffix('.json')
        vocal_text = spoken_text(cue['text'])
        fingerprint = hashlib.sha256(json.dumps({
            'text': vocal_text, 'tts': args.tts, 'model': args.model,
            'length_scale': args.length_scale, 'noise_scale': 0.5, 'noise_w_scale': 0.6
        }, sort_keys=True).encode()).hexdigest()
        cached = None
        if metadata_path.exists():
            cached = json.loads(metadata_path.read_text(encoding='utf-8')).get('fingerprint')
        if voice is not None and (args.force or not raw.exists() or cached != fingerprint):
            print('Synthesizing', cue['id'], flush=True)
            with wave.open(str(raw), 'wb') as wav_file:
                voice.synthesize_wav(vocal_text, wav_file, syn_config=synthesis)
            metadata_path.write_text(json.dumps({'fingerprint': fingerprint, 'text': vocal_text}, indent=2))
        if not raw.is_file():
            raise FileNotFoundError(f'Missing recording: {raw}. Supply one WAV per cue, or use --tts piper.')
        raw_duration = duration(raw)
        if raw_duration <= 0:
            raise ValueError(f'Empty audio: {raw}')
        window = cue['end'] - cue['start']
        available = window - LEAD - TAIL
        speed = max(1.0, raw_duration / available)
        if speed > args.max_speedup + 1e-6:
            raise ValueError(f'{cue["id"]} lasts {raw_duration:.2f}s, but its speech budget is '
                             f'{available:.2f}s. Required tempo {speed:.3f} exceeds '
                             f'--max-speedup {args.max_speedup}. Nothing was truncated. '
                             'Re-record more briskly, shorten this cue in PLAN, or lower '
                             '--length-scale and regenerate the Piper recording.')
        speech_duration = raw_duration / speed
        fade_start = max(0.0, speech_duration - 0.03)
        filters = (f'aresample={SAMPLE_RATE},atempo={speed:.9f},asetpts=N/SR/TB,'
                   'afade=t=in:st=0:d=0.015,'
                   f'afade=t=out:st={fade_start:.9f}:d=0.03,'
                   f'adelay={round(LEAD * 1000)}:all=1,apad,'
                   f'atrim=end_sample={round(window * SAMPLE_RATE)},asetpts=N/SR/TB')
        destination = prepared / f'{cue["id"]}.wav'
        run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(raw),
             '-af', filters, '-ar', str(SAMPLE_RATE), '-ac', '1', '-c:a', 'pcm_s16le', str(destination)])
        # WAV sample counts, rather than encoded duration rounding, define cue boundaries.
        with wave.open(str(destination), 'rb') as f:
            if abs(f.getnframes() / f.getframerate() - window) > 1 / SAMPLE_RATE:
                raise RuntimeError(f'Audio cue length mismatch for {cue["id"]}.')
        paths.append(destination)
        report[cue['id']] = {'raw_seconds': raw_duration, 'speech_seconds': speech_duration,
                            'speedup': speed, 'start': cue['start'], 'end': cue['end']}
    concat_file = WORK / 'audio_concat.txt'
    write_concat(paths, concat_file)
    joined = WORK / 'voiceover_unmastered.wav'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0',
         '-i', str(concat_file), '-c:a', 'pcm_s16le', str(joined)])
    # Two-pass loudness normalization, with a -1.5 dBTP true-peak ceiling.
    first = run(['ffmpeg', '-hide_banner', '-i', str(joined), '-af',
                 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture=True)
    matches = re.findall(r'\{\s*"input_i"[\s\S]*?\}', first.stderr)
    if not matches:
        raise RuntimeError('FFmpeg did not return loudness measurements.')
    measured = json.loads(matches[-1])
    if measured['input_i'] == '-inf':
        raise ValueError('The supplied recordings are silent.')
    normalizer = ('loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:'
                  f'measured_I={measured["input_i"]}:measured_TP={measured["input_tp"]}:'
                  f'measured_LRA={measured["input_lra"]}:measured_thresh={measured["input_thresh"]}:'
                  f'offset={measured["target_offset"]}')
    normalizer += (f',aresample={SAMPLE_RATE},apad,'
                   f'atrim=end_sample={round(total_duration(plan) * SAMPLE_RATE)},asetpts=N/SR/TB')
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(joined),
         '-af', normalizer, '-ar', str(SAMPLE_RATE), '-ac', '1', '-c:a', 'pcm_s16le',
         str(OUT / 'voiceover.wav')])
    (OUT / 'audio_timing.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    write_subtitles(manifest, report)
    print('Audio complete:', OUT / 'voiceover.wav')
    print('Subtitles use cue-locked, approximate within-cue phrase timing.')


def clip_path(scene: str, quality: str) -> Path:
    _, h = SIZES[quality]
    return WORK / 'media' / 'videos' / SOURCE.stem / f'{h}p{FPS}' / f'{scene}.mp4'


def render(plan: list[dict[str, Any]], args: argparse.Namespace):
    width, height = SIZES[args.quality]
    try:
        import importlib.util
        if importlib.util.find_spec('manim') is None:
            raise RuntimeError('Manim is not installed. Run pip install -r requirements.txt.')
    except ValueError as e:
        raise RuntimeError('Manim installation could not be located.') from e
    requested = [s for s in plan if args.scene is None or s['scene'] == args.scene]
    if not requested:
        raise ValueError(f'Unknown scene: {args.scene}')
    for s in requested:
        run([sys.executable, '-m', 'manim', '--renderer', 'cairo',
             '-r', f'{width},{height}', '--fps', str(FPS),
             '--media_dir', str(WORK / 'media'), '-o', s['scene'],
             str(SOURCE), s['scene']])
        path = clip_path(s['scene'], args.quality)
        if not path.exists():
            candidates = list((WORK / 'media').rglob(f'{s["scene"]}.mp4'))
            raise FileNotFoundError(f'Expected render at {path}; found alternatives: {candidates}')
        d = duration(path)
        if abs(d - s['duration']) > 0.25:
            raise RuntimeError(f'{s["scene"]}: rendered {d:.3f}s; expected {s["duration"]}s.')
    print('Render step complete.')


def assemble(plan: list[dict[str, Any]], args: argparse.Namespace):
    require_program('ffmpeg')
    require_program('ffprobe')
    manifest = export_text(plan)
    voiceover = OUT / 'voiceover.wav'
    if not voiceover.is_file():
        raise FileNotFoundError('Generate or assemble voiceover first: python build.py audio ...')
    if abs(duration(voiceover) - total_duration(plan)) > 1 / FPS:
        raise ValueError('The voiceover does not match the authored timeline.')
    if not (OUT / 'narration.srt').exists():
        write_subtitles(manifest)
    clips, report = [], []
    for s in plan:
        path = clip_path(s['scene'], args.quality)
        if not path.is_file():
            raise FileNotFoundError(f'Missing render: {path}')
        data = probe(path)
        video = next(stream for stream in data['streams'] if stream['codec_type'] == 'video')
        d = float(data['format']['duration'])
        width, height = SIZES[args.quality]
        if video['width'] != width or video['height'] != height:
            raise ValueError(f'Wrong frame size: {path}')
        num, den = map(int, video['avg_frame_rate'].split('/'))
        if abs(num / den - FPS) > 0.01:
            raise ValueError(f'Expected {FPS} fps: {path}')
        if abs(d - s['duration']) > 0.25:
            raise ValueError(f'{s["scene"]} is off by more than 0.25s. Fix the scene instead of stretching it.')
        # Conform only small frame-quantization discrepancies; never stretch motion.
        if abs(d - s['duration']) > 0.5 / FPS:
            corrected = WORK / 'conformed' / path.name
            corrected.parent.mkdir(parents=True, exist_ok=True)
            run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(path),
                 '-an', '-vf', f'tpad=stop_mode=clone:stop_duration=0.3,trim=duration={s["duration"]},setpts=PTS-STARTPTS',
                 '-r', str(FPS), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
                 '-pix_fmt', 'yuv420p', str(corrected)])
            path = corrected
        clips.append(path)
        report.append({'scene': s['scene'], 'original_duration': d, 'target_duration': s['duration']})
    WORK.mkdir(parents=True, exist_ok=True)
    concat = WORK / 'video_concat.txt'
    write_concat(clips, concat)
    silent = WORK / 'silent.mp4'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0',
         '-i', str(concat), '-an', '-c:v', 'copy', str(silent)])
    final = OUT / final_name()
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
         '-i', str(silent), '-i', str(voiceover), '-i', str(OUT / 'narration.srt'),
         '-f', 'ffmetadata', '-i', str(OUT / 'chapters.ffmeta'),
         '-map', '0:v:0', '-map', '1:a:0', '-map', '2:s:0',
         '-map_metadata', '3', '-map_chapters', '3',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-c:s', 'mov_text',
         '-metadata:s:s:0', 'language=eng', '-metadata:s:s:0', 'title=English',
         '-t', str(total_duration(plan)), '-movflags', '+faststart', str(final)])
    final_probe = probe(final)
    if abs(float(final_probe['format']['duration']) - total_duration(plan)) > 0.1:
        raise RuntimeError('Final MP4 duration failed validation.')
    (OUT / 'render_report.json').write_text(json.dumps({'scenes': report, 'final_probe': final_probe}, indent=2))
    print('Final MP4:', final)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['check', 'export', 'audio', 'render', 'assemble', 'all'])
    parser.add_argument('--quality', choices=SIZES, default='medium')
    parser.add_argument('--scene', help='Render one class only; assemble/all require every scene.')
    parser.add_argument('--tts', choices=['piper', 'existing'], default='existing')
    parser.add_argument('--model', help='Piper .onnx voice path (also requires .onnx.json)')
    parser.add_argument('--length-scale', type=float, default=1.05,
                        help='Piper speaking length scale; larger values speak more slowly.')
    parser.add_argument('--max-speedup', type=float, default=1.15,
                        help='Maximum allowed per-cue pitch-preserving tempo correction.')
    parser.add_argument('--force', action='store_true', help='Regenerate cached Piper cue recordings.')
    args = parser.parse_args()
    if args.command in ['assemble', 'all'] and args.scene:
        parser.error('--scene is only meaningful for render.')
    if args.length_scale <= 0 or not 1 <= args.max_speedup <= 2:
        parser.error('Use positive --length-scale and --max-speedup between 1 and 2.')
    try:
        plan = load_plan()
        if args.command == 'check':
            check(plan)
        elif args.command == 'export':
            write_subtitles(export_text(plan))
        elif args.command == 'audio':
            generate_audio(plan, args)
        elif args.command == 'render':
            render(plan, args)
        elif args.command == 'assemble':
            assemble(plan, args)
        elif args.command == 'all':
            check(plan)
            generate_audio(plan, args)
            render(plan, args)
            assemble(plan, args)
    except (ValueError, RuntimeError, FileNotFoundError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr[-4000:], file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == '__main__':
    main()
