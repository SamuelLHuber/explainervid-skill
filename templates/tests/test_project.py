"""Static timeline checks and a real FFmpeg assembly smoke test.

The smoke test uses a tone and a black test clip, NOT a Manim render or a voice.
Run: python -m unittest discover -s tests -v
"""
import argparse
import array
import importlib.util
import math
import shutil
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('video_builder', PROJECT / 'build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ProjectTests(unittest.TestCase):
    def test_timeline_and_classes(self):
        plan = builder.load_plan()
        total = sum(s['duration'] for s in plan)
        self.assertGreaterEqual(total, 420)
        self.assertLessEqual(total, 540)
        self.assertGreaterEqual(sum(len(s['beats']) for s in plan), len(plan))
        self.assertGreaterEqual(len(plan), 5)
        builder.check(plan)

    def test_timestamps(self):
        self.assertEqual(builder.stamp(500), '08:20')
        self.assertEqual(builder.stamp(62.35, True), '00:01:02,350')

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg unavailable')
    def test_audio_and_mp4_pipeline(self):
        originals = {k: getattr(builder, k) for k in ('ROOT', 'WORK', 'OUT')}
        try:
            with tempfile.TemporaryDirectory(prefix='explainer_pipeline_test_') as temp:
                root = Path(temp)
                builder.ROOT, builder.WORK, builder.OUT = root, root / 'build', root / 'out'
                plan = [{'scene': 'SmokeTest', 'title': 'Pipeline test only', 'duration': 4,
                         'beats': [{'start': 0, 'end': 2, 'text': 'First test cue.', 'visual': 'Test'},
                                   {'start': 2, 'end': 4, 'text': 'Second test cue.', 'visual': 'Test'}]}]
                raw = root / 'audio' / 'raw'
                raw.mkdir(parents=True)
                rate = 24000
                samples = array.array('h', [int(6000 * math.sin(2 * math.pi * 220 * i / rate))
                                           for i in range(int(0.75 * rate))])
                for i in range(2):
                    with wave.open(str(raw / f'SmokeTest_{i:02d}.wav'), 'wb') as f:
                        f.setnchannels(1)
                        f.setsampwidth(2)
                        f.setframerate(rate)
                        f.writeframes(samples.tobytes())
                args = argparse.Namespace(tts='existing', model=None, length_scale=1.05,
                                          force=False, max_speedup=1.15, quality='low', scene=None)
                builder.generate_audio(plan, args)
                with wave.open(str(builder.OUT / 'voiceover.wav'), 'rb') as f:
                    self.assertEqual(f.getframerate(), 48000)
                    self.assertEqual(f.getnframes(), 4 * 48000)
                clip = builder.clip_path('SmokeTest', 'low')
                clip.parent.mkdir(parents=True)
                # 121 frames deliberately exercise small duration correction.
                subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                                '-f', 'lavfi', '-i', 'color=c=black:s=854x480:r=30',
                                '-frames:v', '121', '-an', '-c:v', 'libx264', '-threads', '1',
                                '-pix_fmt', 'yuv420p', str(clip)], check=True)
                builder.assemble(plan, args)
                result = builder.probe(builder.OUT / builder.final_name())
                self.assertAlmostEqual(float(result['format']['duration']), 4, places=2)
                types = {s['codec_type'] for s in result['streams']}
                self.assertTrue({'video', 'audio', 'subtitle'}.issubset(types))
        finally:
            for k, v in originals.items():
                setattr(builder, k, v)


if __name__ == '__main__':
    unittest.main()
