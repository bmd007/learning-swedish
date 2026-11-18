"""Chatterbox voices for build_audio.py --engine chatterbox (run with .venv-tts/bin/python).

Who speaks with which voice: tools/voice_cast.json
  people: fixed voice per character name across all lessons (Sara, Johan, Morfar …)
  pool:   voices per sex for everyone else; picked per audio id, so each message is a different person
A speaker spec in a lesson can pin a voice: {"voice": "f", "cast": "nok-f-03"}.
References: materials/voices/refs/<voice>.wav (private; see docs/sources.md).
"""
import hashlib
import json
import random
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "materials" / "voices" / "refs"
CAST = json.loads((ROOT / "tools" / "voice_cast.json").read_text(encoding="utf-8"))
_model = None


def model():
    global _model
    if _model is None:
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        dev = "mps" if torch.backends.mps.is_available() else "cpu"
        _model = ChatterboxMultilingualTTS.from_local(ROOT / "models" / "chatterbox", dev)
    return _model


def voice_for(audio, name):
    spec = audio.get("speakers", {}).get(name, "f")
    spec = spec if isinstance(spec, dict) else {"voice": spec}
    if spec.get("cast"):
        return spec["cast"]
    if name in CAST["people"]:
        return CAST["people"][name]
    taken = {CAST["people"].get(n) for n in audio.get("speakers", {})}
    pool = [v for v in CAST["pool"][spec["voice"]] if v not in taken]
    others = sorted(n for n in audio.get("speakers", {}) if n not in CAST["people"])
    seed = int(hashlib.md5(audio["id"].encode()).hexdigest(), 16)
    return pool[(seed + others.index(name)) % len(pool)]


def chunks(text, limit=180):
    parts, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", text.strip()):
        if cur and len(cur) + len(s) > limit:
            parts.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    return parts + [cur] if cur else parts


CACHE = ROOT / "materials" / "tts" / ".cache"


def render_line(text, voice, rate, wav):
    """One script line as 24 kHz wav, cached by (voice, rate, text) in materials/tts/.cache/."""
    import shutil
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{hashlib.md5(f'{voice}|{rate}|{text}'.encode()).hexdigest()}.wav"
    if not cached.exists():
        generate(text, voice, rate, cached)
    shutil.copy(cached, wav)


def generate(text, voice, rate, wav):
    """Retries with another seed when the length looks wrong (babble or cut-off)."""
    import torch
    import torchaudio
    m = model()
    pieces = []
    for chunk in chunks(text):
        expected = len(chunk) / 14
        best = None
        for attempt in range(3):
            torch.manual_seed(random.Random(chunk + str(attempt)).randint(0, 2**31))
            w = m.generate(chunk, language_id="sv", audio_prompt_path=str(REFS / f"{voice}.wav"),
                           exaggeration=0.5, cfg_weight=0.4)
            seconds = w.shape[-1] / m.sr
            score = abs(seconds / max(expected, 0.6) - 1)
            if best is None or score < best[0]:
                best = (score, w)
            if score < 0.6:
                break
        pieces += [best[1], torch.zeros(1, int(m.sr * 0.2))]
    torchaudio.save(str(wav), torch.cat(pieces[:-1], dim=-1).clamp(-1, 1), m.sr, encoding="PCM_S", bits_per_sample=16)
    speed = 1 + int(str(rate).strip("%+") or 0) / 100 if str(rate).startswith("+") else 1.0
    if speed > 1.02:
        tmp = wav.with_suffix(".fast.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-af", f"atempo={speed}", "-c:a", "pcm_s16le", str(tmp)], check=True)
        tmp.replace(wav)
