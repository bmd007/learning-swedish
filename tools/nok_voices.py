"""Find distinct speakers (actors) in the Rivstart/NOK tracks and cut a ~12 s solo reference for each.

  .venv-tts/bin/python tools/nok_voices.py
Splits each track at pauses, embeds every piece with Chatterbox's voice encoder, joins neighbouring pieces of the
same voice into runs, keeps runs >= 10 s, then merges runs of the same actor across tracks.
Output: materials/voices/refs/nok-<f|m>-<n>.wav + materials/voices/nok_speakers.json (private: NOK is licensed).
"""
import json
import subprocess
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from chatterbox.models.voice_encoder import VoiceEncoder
import torch

ROOT = Path(__file__).resolve().parent.parent
AUDIO = ROOT / "materials" / "nok" / "audio"
REFS = ROOT / "materials" / "voices" / "refs"
SR = 16000


def pieces(y):
    iv = librosa.effects.split(y, top_db=32, frame_length=1024, hop_length=256)
    out, cur = [], None
    for s, e in iv:
        if cur and s - cur[1] < 0.35 * SR:
            cur[1] = e
        else:
            if cur:
                out.append(cur)
            cur = [s, e]
    if cur:
        out.append(cur)
    return [(s, e) for s, e in out if e - s > 1.2 * SR]


def main():
    ve = VoiceEncoder()
    ve.load_state_dict(torch.load(ROOT / "models" / "chatterbox" / "ve.pt", map_location="cpu", weights_only=True))
    ve.eval()
    runs = []
    for f in sorted(AUDIO.glob("Kapitel_*.mp3")):
        y, _ = librosa.load(f, sr=SR, mono=True)
        ps = pieces(y)
        if not ps:
            continue
        embs = ve.embeds_from_wavs([y[s:e] for s, e in ps], sample_rate=SR)
        run = [0]
        for i in range(1, len(ps) + 1):
            same = i < len(ps) and float(np.dot(embs[i], embs[run[-1]])) > 0.80 and ps[i][0] - ps[run[-1]][1] < 1.0 * SR
            if same:
                run.append(i)
                continue
            seg = [ps[j] for j in run]
            dur = sum(e - s for s, e in seg) / SR
            if dur >= 10:
                emb = embs[run].mean(0)
                runs.append(dict(file=f.name, seg=seg, dur=dur, emb=emb / np.linalg.norm(emb)))
            run = [i]
        print(f.name, len(ps), "pieces", len(runs), "runs so far", flush=True)
    speakers = []
    for r in sorted(runs, key=lambda r: -r["dur"]):
        for sp in speakers:
            if float(np.dot(sp["emb"], r["emb"])) > 0.85:
                sp["runs"].append(r)
                break
        else:
            speakers.append(dict(emb=r["emb"], runs=[r]))
    meta = []
    for n, sp in enumerate(speakers):
        best = sp["runs"][0]
        y, _ = librosa.load(AUDIO / best["file"], sr=24000, mono=True)
        clip = np.concatenate([np.concatenate([y[int(s * 1.5):int(e * 1.5)], np.zeros(int(0.25 * 24000))]) for s, e in best["seg"]])[:14 * 24000]
        f0 = librosa.yin(clip, fmin=60, fmax=400, sr=24000)
        pitch = float(np.median(f0))
        sex = "f" if pitch > 165 else "m"
        name = f"nok-{sex}-{n:02d}"
        sf.write(REFS / f"{name}.wav", clip, 24000)
        meta.append(dict(name=name, sex=sex, pitch=round(pitch), tracks=len(sp["runs"]), source=best["file"],
                         seconds=round(best["dur"], 1)))
        print(meta[-1], flush=True)
    (ROOT / "materials" / "voices" / "nok_speakers.json").write_text(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
