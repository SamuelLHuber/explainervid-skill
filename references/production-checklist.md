# Production checklist

## Intake

- Source material received and accessible.
- Target audience known.
- Desired duration known, default 7-9 minutes.
- Deliverable known: package only, low-res preview, or high-res final.

## Source notes

- Source title and link/file recorded.
- Claims and equations traced.
- Measured values separated from illustrative animations.
- Limitations and caveats listed.

## Script and storyboard

- 6-ish major scenes.
- Cue durations contiguous and within scene duration.
- Narration is speakable at roughly 120-150 WPM.
- Visual directions are specific enough to implement.

## Code

- `PLAN` is literal Python data.
- One production Scene class per scene.
- Each cue has exactly one `self.beat(i)` call in order.
- `python build.py check` passes.

## Audio

- Piper or existing WAV route selected.
- Cue scripts exported to `audio/scripts/`.
- No cue is truncated.
- `out/voiceover.wav` matches total timeline duration.

## Render

- Preview at least one low-res scene first.
- Full render completes.
- Assembly completes.
- Final MP4 has video, audio, subtitles, chapters.

## Review

- Probe final file.
- Generate and inspect preview frames.
- Listen to at least representative voiceover sections.
- Record caveats in `QA.md`.
