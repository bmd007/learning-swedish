"""Transcribe learner recordings with a local Swedish Whisper model.

  .venv/bin/python tools/transcribe.py recordings/<file>.webm [...]   # prints transcript
Model: KBLab/kb-whisper-small (env WHISPER_MODEL). Needs: .venv/bin/pip install faster-whisper "av<17"
"""
import os
import sys

from faster_whisper import WhisperModel

model = WhisperModel(os.environ.get("WHISPER_MODEL", "KBLab/kb-whisper-small"), device="cpu", compute_type="int8")
for path in sys.argv[1:]:
    segments, info = model.transcribe(path, language="sv", beam_size=5, condition_on_previous_text=False)
    text = " ".join(s.text.strip() for s in segments)
    print(f"== {os.path.basename(path)} ({info.duration:.0f}s)\n{text}\n")
