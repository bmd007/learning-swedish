"""Make voice samples with Chatterbox (local) for rating in the app (#/voices).

  .venv-tts/bin/python tools/voice_samples.py [batch]
Weights: models/chatterbox/ (tools/download/). References: materials/voices/refs/<name>.wav (~12 s of one speaker).
Output: materials/voices/samples/<batch>/*.wav + materials/voices/samples/index.json (private, gitignored).
"""
import json
import subprocess
import sys
from pathlib import Path

import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "materials" / "voices" / "samples"
REFS = ROOT / "materials" / "voices" / "refs"
TEXTS = [
    "Hej Karin, det är Lars här! Du, jag kan tyvärr inte komma på tisdag. Kan vi ses på onsdag i stället, runt fyra?",
    "Nej men vad kul att du ringer! Jo, jag har det bra, fast jobbet är lite stressigt just nu. Och du då?",
    "Hej och välkommen till Stadsbiblioteket. Vi har öppet måndag till fredag mellan tio och sju, och på lördagar mellan elva och tre.",
]
STYLES = {"lugn": dict(exaggeration=0.4, cfg_weight=0.5), "livlig": dict(exaggeration=0.8, cfg_weight=0.3)}
LABELS = {"lars": "man, Sverige", "mans": "man, finlandssvenska", "petra": "kvinna", "annasofia": "kvinna",
          "cecilia": "kvinna", "cecilia2": "kvinna"}


def edge_baseline(batch, out, index):
    edge = ROOT / ".venv" / "bin" / "edge-tts"
    for voice, short in (("sv-SE-MattiasNeural", "Mattias"), ("sv-SE-SofieNeural", "Sofie")):
        for t, text in enumerate(TEXTS):
            f = out / f"edge-{short.lower()}-{t}.mp3"
            if not f.exists():
                subprocess.run([str(edge), "--voice", voice, "--text", text, "--write-media", str(f)], check=True)
            index.append(dict(file=str(f.relative_to(ROOT)), voice=f"{short} (gammal)", label="edge-tts, nuvarande röst",
                              text=text, engine="edge", batch=batch))


def main(batch):
    out = SAMPLES / batch
    out.mkdir(parents=True, exist_ok=True)
    index_file = SAMPLES / "index.json"
    index = [s for s in json.loads(index_file.read_text()) if s["batch"] != batch] if index_file.exists() else []
    edge_baseline(batch, out, index)
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model = ChatterboxMultilingualTTS.from_local(ROOT / "models" / "chatterbox", dev)
    for ref in sorted(REFS.glob("*.wav")):
        for style, params in STYLES.items():
            for t, text in enumerate(TEXTS):
                f = out / f"{ref.stem}-{style}-{t}.wav"
                if not f.exists():
                    torch.manual_seed(t)
                    wav = model.generate(text, language_id="sv", audio_prompt_path=str(ref), **params)
                    torchaudio.save(str(f), wav, model.sr)
                    print("built", f.relative_to(ROOT), flush=True)
                index.append(dict(file=str(f.relative_to(ROOT)), voice=f"{ref.stem.capitalize()} ({style})",
                                  label=LABELS.get(ref.stem, ""), text=text, engine="chatterbox", batch=batch,
                                  ref=ref.name, **params))
                index_file.write_text(json.dumps(index, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
