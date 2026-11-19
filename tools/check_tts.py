"""Check Chatterbox lesson audio against the script with local Whisper (catches dropped/repeated/garbled words).

  .venv/bin/python -I tools/check_tts.py [lessons/x.json ...]
Prints character error rate (numbers spelled out) per audio in materials/tts/<lessonId>/; > 15 % = listen and rebuild (delete the
cached lines in materials/tts/.cache/ or pin another voice with "cast").
"""
import json
import re
import sys
import warnings
from pathlib import Path

import whisper

sys.path.insert(0, str(Path(__file__).resolve().parent))
from textnorm import cer  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent


def words(t):
    return re.findall(r"[a-zåäöé0-9]+", t.lower())


def wer(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
    return d[-1] / max(len(ref), 1)


def audios(lesson):
    for sec in lesson["sections"]:
        for part in sec.get("parts", [sec]):
            for a in [part.get("audio")] + [i.get("audio") for i in part.get("items", [])]:
                if a and a.get("script") and not a.get("source"):
                    yield a


model = whisper.load_model("turbo")
paths = sys.argv[1:] or sorted(str(p) for p in (ROOT / "lessons").glob("*.json"))
for p in paths:
    lesson = json.loads(Path(p).read_text(encoding="utf-8"))
    for a in audios(lesson):
        f = ROOT / "materials" / "tts" / lesson["id"] / f"{a['id']}.m4a"
        if not f.exists():
            continue
        hyp = model.transcribe(str(f), language="sv", fp16=False, condition_on_previous_text=False)["text"]
        ref = " ".join(l["text"] for l in a["script"])
        e = cer(ref, hyp)
        print(f"{'BAD ' if e > 0.15 else 'ok  '}{e:5.0%}  {lesson['id']}/{a['id']}", flush=True)
        if e > 0.15:
            print(f"      want: {ref}\n      got:  {hyp.strip()}", flush=True)
