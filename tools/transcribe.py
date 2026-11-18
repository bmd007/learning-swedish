"""Transcribe Swedish audio with a local Whisper model (openai-whisper; weights come from openaipublic, not huggingface).

  .venv/bin/python tools/transcribe.py <audio> [...]          # print transcripts
  .venv/bin/python tools/transcribe.py --save <audio> [...]   # also write <audio>.txt next to each file
  .venv/bin/python tools/transcribe.py --timestamps <audio>    # one line per segment: [start–end] text (for cutting clips)
Model: env WHISPER_MODEL (default "turbo" = large-v3-turbo). Needs ffmpeg and .venv/bin/pip install openai-whisper
"""
import os
import sys
import warnings
from pathlib import Path

import whisper

warnings.filterwarnings("ignore")
args = [a for a in sys.argv[1:] if a not in ("--save", "--timestamps")]
model = whisper.load_model(os.environ.get("WHISPER_MODEL", "turbo"))
for path in args:
    result = model.transcribe(path, language="sv", fp16=False, condition_on_previous_text=False)
    if "--timestamps" in sys.argv:
        text = "\n".join(f"[{s['start']:6.1f}–{s['end']:6.1f}] {s['text'].strip()}" for s in result["segments"])
    else:
        text = " ".join(s["text"].strip() for s in result["segments"])
    if "--save" in sys.argv:
        Path(f"{path}.txt").write_text(text + "\n", encoding="utf-8")
    print(f"== {os.path.basename(path)}\n{text}\n", flush=True)
