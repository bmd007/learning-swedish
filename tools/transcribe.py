"""Transcribe Swedish audio with a local Whisper model (openai-whisper; weights come from openaipublic, not huggingface).

  .venv/bin/python tools/transcribe.py <audio> [...]          # print transcripts
  .venv/bin/python tools/transcribe.py --save <audio> [...]   # also write <audio>.txt next to each file
Model: env WHISPER_MODEL (default "turbo" = large-v3-turbo). Needs ffmpeg and .venv/bin/pip install openai-whisper
"""
import os
import sys
import warnings
from pathlib import Path

import whisper

warnings.filterwarnings("ignore")
args = [a for a in sys.argv[1:] if a != "--save"]
model = whisper.load_model(os.environ.get("WHISPER_MODEL", "turbo"))
for path in args:
    result = model.transcribe(path, language="sv", fp16=False, condition_on_previous_text=False)
    text = " ".join(s["text"].strip() for s in result["segments"])
    if "--save" in sys.argv:
        Path(f"{path}.txt").write_text(text + "\n", encoding="utf-8")
    print(f"== {os.path.basename(path)}\n{text}\n", flush=True)
