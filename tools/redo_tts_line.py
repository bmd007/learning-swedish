"""Forget cached Chatterbox lines so the next build regenerates them (use with TTS_TAKE=<n> for a new seed).

  python3 -I tools/redo_tts_line.py lessons/x.json <audioId> "<part of the line text>" [...]
Then: TTS_TAKE=2 .venv-tts/bin/python tools/build_audio.py --chatterbox --force lessons/x.json
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
CACHE = ROOT / "materials" / "tts" / ".cache"
CAST = json.loads((ROOT / "tools" / "voice_cast.json").read_text(encoding="utf-8"))

lesson = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
audio_id, needles = sys.argv[2], sys.argv[3:]
from human_voice import voice_for  # noqa: E402

for sec in lesson["sections"]:
    for part in sec.get("parts", [sec]):
        for a in [part.get("audio")] + [i.get("audio") for i in part.get("items", [])]:
            if not a or a.get("id") != audio_id:
                continue
            for line in a["script"]:
                if any(n in line["text"] for n in needles):
                    spec = a.get("speakers", {}).get(line.get("speaker"), "f")
                    rate = spec.get("rate", a.get("rate", "+0%")) if isinstance(spec, dict) else a.get("rate", "+0%")
                    voice = voice_for(a, line.get("speaker"))
                    f = CACHE / f"{hashlib.md5(f'{voice}|{rate}|{line['text']}'.encode()).hexdigest()}.wav"
                    print("forget" if f.exists() else "not cached", voice, line["text"][:60])
                    f.unlink(missing_ok=True)
