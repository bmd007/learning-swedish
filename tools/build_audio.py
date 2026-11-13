import asyncio
import json
import subprocess
import sys
import tempfile
import wave
from array import array
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
VOICES = {"f": "sv-SE-SofieNeural", "m": "sv-SE-MattiasNeural"}
RATE = 24000


def audios(lesson):
    for sec in lesson["sections"]:
        for part in sec.get("parts", [sec]):
            if part.get("audio"):
                yield part["audio"]
            for item in part.get("items", []):
                if item.get("audio"):
                    yield item["audio"]


def speaker_settings(audio, name):
    spec = audio.get("speakers", {}).get(name, "f")
    spec = spec if isinstance(spec, dict) else {"voice": spec}
    return VOICES[spec["voice"]], spec.get("rate", audio.get("rate", "+0%")), spec.get("pitch", "+0Hz")


async def render_line(text, voice, rate, pitch, mp3):
    with open(mp3, "wb") as f:
        async for chunk in edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])


def pcm(mp3, tmp):
    wav = Path(tmp) / "line.wav"
    subprocess.run(["afconvert", "-f", "WAVE", "-d", f"LEI16@{RATE}", "-c", "1", str(mp3), str(wav)], check=True)
    with wave.open(str(wav)) as w:
        samples = array("h", w.readframes(w.getnframes()))
    loud = [i for i, v in enumerate(samples) if abs(v) > 400]
    if not loud:
        return b""
    pad = int(RATE * 0.04)
    return samples[max(0, loud[0] - pad):loud[-1] + pad].tobytes()


def silence(seconds):
    return b"\x00\x00" * int(RATE * seconds)


async def render(audio, m4a):
    gap = audio.get("gap", 0.45)
    frames, previous = [], None
    with tempfile.TemporaryDirectory() as tmp:
        for i, line in enumerate(audio["script"]):
            voice, rate, pitch = speaker_settings(audio, line.get("speaker"))
            mp3 = Path(tmp) / f"{i}.mp3"
            await render_line(line["text"], voice, rate, pitch, mp3)
            if i:
                default = gap if line.get("speaker") != previous else 0.25
                frames.append(silence(line.get("pause", default)))
            frames.append(pcm(mp3, tmp))
            previous = line.get("speaker")
        wav = Path(tmp) / "all.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(b"".join(frames))
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(wav), str(m4a)], check=True)


async def main(paths, force):
    for p in paths:
        lesson = json.loads(Path(p).read_text(encoding="utf-8"))
        out_dir = ROOT / "audio" / lesson["id"]
        for audio in audios(lesson):
            if audio.get("source"):
                continue
            out_dir.mkdir(parents=True, exist_ok=True)
            m4a = out_dir / f"{audio['id']}.m4a"
            if m4a.exists() and not force:
                print(f"skip {m4a.relative_to(ROOT)}")
                continue
            await render(audio, m4a)
            print(f"built {m4a.relative_to(ROOT)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    asyncio.run(main(args or sorted(str(p) for p in (ROOT / "lessons").glob("*.json")), "--force" in sys.argv))
