import asyncio
import json
import subprocess
import sys
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parent.parent
VOICES = {"f": "sv-SE-SofieNeural", "m": "sv-SE-MattiasNeural"}


def audios(lesson):
    for sec in lesson["sections"]:
        for part in sec.get("parts", [sec]):
            if part.get("audio"):
                yield part["audio"]
            for item in part.get("items", []):
                if item.get("audio"):
                    yield item["audio"]


async def render(audio, out_mp3, rate):
    speakers = audio.get("speakers", {})
    with open(out_mp3, "wb") as f:
        for line in audio["script"]:
            voice = VOICES[speakers.get(line.get("speaker"), "f")]
            async for chunk in edge_tts.Communicate(line["text"], voice, rate=audio.get("rate", rate)).stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])


async def main(paths, force):
    for p in paths:
        lesson = json.loads(Path(p).read_text(encoding="utf-8"))
        out_dir = ROOT / "audio" / lesson["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        for audio in audios(lesson):
            m4a = out_dir / f"{audio['id']}.m4a"
            if m4a.exists() and not force:
                print(f"skip {m4a.relative_to(ROOT)}")
                continue
            mp3 = out_dir / f"{audio['id']}.mp3"
            await render(audio, mp3, "-5%")
            subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(mp3), str(m4a)], check=True)
            mp3.unlink()
            print(f"built {m4a.relative_to(ROOT)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--force"]
    asyncio.run(main(args or sorted(str(p) for p in (ROOT / "lessons").glob("*.json")), "--force" in sys.argv))
