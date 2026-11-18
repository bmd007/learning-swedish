import asyncio
import json
import random
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
    for attempt in range(4):
        try:
            with open(mp3, "wb") as f:
                async for chunk in edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
            return
        except edge_tts.exceptions.EdgeTTSException:
            if attempt == 3:
                raise
            await asyncio.sleep(2 * (attempt + 1))


def to_wav(src, wav):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-ac", "1", "-ar", str(RATE), "-c:a", "pcm_s16le", str(wav)], check=True)


def pcm(mp3, tmp):
    wav = Path(tmp) / "line.wav"
    to_wav(mp3, wav)
    with wave.open(str(wav)) as w:
        samples = array("h", w.readframes(w.getnframes()))
    loud = [i for i, v in enumerate(samples) if abs(v) > 400]
    if not loud:
        return b""
    pad = int(RATE * 0.04)
    return samples[max(0, loud[0] - pad):loud[-1] + pad].tobytes()


def silence(seconds):
    return b"\x00\x00" * int(RATE * seconds)


def add_noise(data, level):
    """level 0–1: background murmur (low-passed noise with slow swells), relative to full scale."""
    level = {"low": 0.03, "medium": 0.06, "high": 0.1}.get(level, level)
    samples = array("h", data)
    rnd = random.Random(1)
    low = swell = 0.0
    for i, v in enumerate(samples):
        low += 0.08 * (rnd.uniform(-1, 1) - low)
        if i % 2400 == 0:
            swell = 0.6 + 0.4 * rnd.random()
        samples[i] = max(-32768, min(32767, int(v + low * swell * level * 32767 * 4)))
    return samples.tobytes()


def add_scene(data, sound, level, tmp):
    """Loop sounds/<sound>.m4a under the speech, with 1 s of scene before and after and short fades."""
    wav = Path(tmp) / "scene.wav"
    to_wav(ROOT / "sounds" / f"{sound}.m4a", wav)
    with wave.open(str(wav)) as w:
        bg = array("h", w.readframes(w.getnframes()))
    lead = RATE
    speech = array("h", silence(1) + data + silence(1))
    n, fade, xf = len(speech), RATE // 2, RATE // 2
    for i in range(n):
        j = i % (len(bg) - xf)
        b = bg[j]
        if j < xf and i >= xf:
            b = b * j / xf + bg[len(bg) - xf + j] * (1 - j / xf)
        env = min(1.0, i / fade, (n - 1 - i) / fade)
        speech[i] = max(-32768, min(32767, int(speech[i] + b * level * env)))
    return speech.tobytes()


async def render(audio, m4a, engine="edge"):
    gap = audio.get("gap", 0.45)
    frames, previous = [], None
    with tempfile.TemporaryDirectory() as tmp:
        for i, line in enumerate(audio["script"]):
            voice, rate, pitch = speaker_settings(audio, line.get("speaker"))
            if engine == "chatterbox":
                import human_voice
                mp3 = Path(tmp) / f"{i}.wav"
                human_voice.render_line(line["text"], human_voice.voice_for(audio, line.get("speaker")), rate, mp3)
            else:
                mp3 = Path(tmp) / f"{i}.mp3"
                await render_line(line["text"], voice, rate, pitch, mp3)
            if i:
                default = gap if line.get("speaker") != previous else 0.25
                frames.append(silence(line.get("pause", default)))
            frames.append(pcm(mp3, tmp))
            previous = line.get("speaker")
        data = b"".join(frames)
        noise = audio.get("noise")
        if isinstance(noise, dict):
            data = add_scene(data, noise["sound"], noise.get("level", 0.3), tmp)
        elif noise:
            data = add_noise(data, noise)
        wav = Path(tmp) / "all.wav"
        with wave.open(str(wav), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(data)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(wav), str(m4a)], check=True)


def cut_clip(audio, out_dir, force):
    """Real audio part: cut audio.source to [start, end] seconds (private, under materials/clips/), short fades."""
    out = out_dir / f"{audio['id']}.m4a"
    if out.exists() and not force:
        print(f"skip {out.relative_to(ROOT)}")
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    start, end = audio["clip"]
    length = end - start
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(start), "-t", str(length), "-i", str(ROOT / audio["source"]),
                    "-af", f"afade=t=in:d=0.15,afade=t=out:st={max(0, length - 0.3)}:d=0.3", "-c:a", "aac", "-b:a", "96k", str(out)], check=True)
    print(f"cut {out.relative_to(ROOT)}")


async def main(paths, force, engine):
    for p in paths:
        lesson = json.loads(Path(p).read_text(encoding="utf-8"))
        out_dir = ROOT / ("materials/tts" if engine == "chatterbox" else "audio") / lesson["id"]
        for audio in audios(lesson):
            if audio.get("clip"):
                cut_clip(audio, ROOT / "materials" / "clips" / lesson["id"], force)
                continue
            if audio.get("source"):
                continue
            out_dir.mkdir(parents=True, exist_ok=True)
            m4a = out_dir / f"{audio['id']}.m4a"
            if m4a.exists() and not force:
                print(f"skip {m4a.relative_to(ROOT)}")
                continue
            await render(audio, m4a, engine)
            print(f"built {m4a.relative_to(ROOT)}")


if __name__ == "__main__":
    flags = {"--force", "--chatterbox"}
    args = [a for a in sys.argv[1:] if a not in flags]
    engine = "chatterbox" if "--chatterbox" in sys.argv else "edge"
    asyncio.run(main(args or sorted(str(p) for p in (ROOT / "lessons").glob("*.json")), "--force" in sys.argv, engine))
