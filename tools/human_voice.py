"""Chatterbox voices for build_audio.py --engine chatterbox (run with .venv-tts/bin/python).

Who speaks with which voice: tools/voice_cast.json
  people: fixed voice per character name across all lessons (Sara, Johan, Morfar …)
  pool:   voices per sex for everyone else; picked per audio id, so each message is a different person
A speaker spec in a lesson can pin a voice: {"voice": "f", "cast": "nok-f-03"}.
References: materials/voices/refs/<voice>.wav (private; see docs/sources.md).
"""
import hashlib
import json
import os
import random
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "materials" / "voices" / "refs"
CAST = json.loads((ROOT / "tools" / "voice_cast.json").read_text(encoding="utf-8"))
_model = None
_whisper = None


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
    seed = int(hashlib.md5(f'{audio.get("_lesson", "")}/{audio["id"]}'.encode()).hexdigest(), 16)
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
        free_memory()
    shutil.copy(cached, wav)


def free_memory():
    """MPS keeps memory after each generation; without this one long build grew to 38 GB and swapped."""
    import gc
    import torch
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


def heard(w, sr):
    """Whisper transcript of a generated chunk (CPU, so it doesn't fight the TTS model for GPU memory)."""
    global _whisper
    import whisper
    import torchaudio.functional as F
    if _whisper is None:
        _whisper = whisper.load_model("turbo", device="cpu")
    audio = F.resample(w, sr, 16000)[0].numpy()
    return _whisper.transcribe(audio, language="sv", fp16=False)["text"]


def generate(text, voice, rate, wav):
    """Each chunk: generate, let Whisper listen, retry with a new seed until it matches the text (max 5 tries)."""
    import torch
    import torchaudio
    from textnorm import cer
    m = model()
    pieces = []
    for chunk in chunks(text):
        best = None
        for attempt in range(5):
            torch.manual_seed(random.Random(chunk + str(attempt) + os.environ.get("TTS_TAKE", "")).randint(0, 2**31))
            with torch.inference_mode():
                w = m.generate(chunk, language_id="sv", audio_prompt_path=str(REFS / f"{voice}.wav"),
                               exaggeration=0.5, cfg_weight=0.4).cpu()
            seconds = w.shape[-1] / m.sr
            if seconds > 3 + len(chunk) / 7:
                score = 1.0
            else:
                score = cer(chunk, heard(w, m.sr))
            if best is None or score < best[0]:
                best = (score, w)
            if score <= 0.08:
                break
        if best[0] > 0.08:
            print(f"  warn: best take {best[0]:.0%} off for {voice}: {chunk[:60]}", flush=True)
        pieces += [best[1], torch.zeros(1, int(m.sr * 0.2))]
    torchaudio.save(str(wav), torch.cat(pieces[:-1], dim=-1).clamp(-1, 1), m.sr, encoding="PCM_S", bits_per_sample=16)
    speed = 1 + int(str(rate).strip("%+") or 0) / 100 if str(rate).startswith("+") else 1.0
    if speed > 1.02:
        tmp = wav.with_suffix(".fast.wav")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-af", f"atempo={speed}", "-c:a", "pcm_s16le", str(tmp)], check=True)
        tmp.replace(wav)
