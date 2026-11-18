"""Make voice samples with Chatterbox (local) for rating in the app (#/voices).

  .venv-tts/bin/python tools/voice_samples.py [batch]
Weights: models/chatterbox/ (tools/download/). References: materials/voices/refs/*.wav (~12 s of one speaker;
NST speakers via tools/nst_voices.py, kid-* = pitch/formant-raised adult, others LibriVox).
Each voice says a line that fits its age/sex (a role), so it is judged as a person.
Output: materials/voices/samples/<batch>/*.wav + samples/index.json (private, gitignored).
"""
import json
import re
import sys
from pathlib import Path

import torch
import torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "materials" / "voices" / "samples"
REFS = ROOT / "materials" / "voices" / "refs"
ROLES = {
    "barn": ("Barn", "Mamma! Får jag gå hem till Elsa efter skolan? Hon har fått en kattunge, och den är jättesöt!"),
    "tonåring": ("Tonåring", "Asså, jag orkar inte. Bussen kom inte, och nu kommer jag typ en kvart sent igen."),
    "kompis": ("Kompis", "Nej men hej! Vad kul att du ringer! Ska vi ta en fika på lördag, kanske runt tre?"),
    "butik": ("Kassör", "Det blir hundrafemtiotvå kronor. Vill du ha kvittot, eller ska jag slänga det?"),
    "chef": ("Chef", "Okej, allihop. Från och med måndag börjar vi klockan åtta i stället för nio. Några frågor?"),
    "handläggare": ("Handläggare", "Du behöver skicka in ett läkarintyg senast den femtonde. Annars kan vi tyvärr inte betala ut någon ersättning."),
    "läkare": ("Läkare", "Ta två tabletter på morgonen och två på kvällen. Och ring oss om febern inte går ner."),
    "pensionär": ("Pensionär", "När jag var ung fanns det ingen tv hemma. Vi satt och lyssnade på radio på kvällarna, hela familjen."),
    "uppläsare": ("Uppläsare", "Hej och välkommen till Stadsbiblioteket. Vi har öppet måndag till fredag mellan tio och sju."),
}


def roles_for(ref):
    m = re.match(r"nst-([fm])(\d+)-(.+)-\w+$", ref.stem)
    if ref.stem.startswith("kid-"):
        return [("barn", "barn, ~10 år (konstgjord)")]
    if not m:
        return [("uppläsare", "LibriVox-uppläsare"), ("kompis", "LibriVox-uppläsare")]
    sex, age, region = m.group(1), int(m.group(2)), m.group(3)
    who = f"{'kvinna' if sex == 'f' else 'man'} {age}, {region}"
    if age < 20:
        return [("tonåring", who)]
    if age < 30:
        return [("kompis", who), ("butik", who)][age % 2:][:1]
    if age < 45:
        return [("chef", who)] if age % 2 else [("handläggare", who)]
    if age < 60:
        return [("läkare", who)] if age % 2 else [("handläggare", who)]
    return [("pensionär", who)]


def main(batch):
    out = SAMPLES / batch
    out.mkdir(parents=True, exist_ok=True)
    index_file = SAMPLES / "index.json"
    index = [s for s in json.loads(index_file.read_text()) if s["batch"] != batch] if index_file.exists() else []
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model = ChatterboxMultilingualTTS.from_local(ROOT / "models" / "chatterbox", dev)
    for ref in sorted(REFS.glob("*.wav")):
        for role, who in roles_for(ref):
            label, text = ROLES[role]
            f = out / f"{ref.stem}-{role}.wav"
            if not f.exists():
                torch.manual_seed(0)
                wav = model.generate(text, language_id="sv", audio_prompt_path=str(ref), exaggeration=0.5, cfg_weight=0.4)
                torchaudio.save(str(f), wav, model.sr)
                print("built", f.relative_to(ROOT), flush=True)
            index.append(dict(file=str(f.relative_to(ROOT)), voice=label, label=who, group=label, text=text,
                              engine="chatterbox", batch=batch, ref=ref.name))
            index_file.write_text(json.dumps(index, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v2")
