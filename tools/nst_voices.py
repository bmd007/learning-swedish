"""Pick varied speakers from NST Swedish (Språkbanken, CC0) and stream only their clips out of the 32 GB tar.

  python3 -I tools/nst_voices.py pick      # materials/voices/nst/picked.json (needs NST_se.csv from metadata_se_csv.zip)
  python3 -I tools/nst_voices.py fetch     # read lydfiler_16_1.tar.gz (local copy if present, else stream), keep picked clips
                                           # streaming 32 GB often breaks: curl -C - it into materials/voices/nst/ first
  python3 -I tools/nst_voices.py refs      # build materials/voices/refs/nst-*.wav (~12 s per speaker)
"""
import csv
import json
import random
import subprocess
import sys
import tarfile
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NST = ROOT / "materials" / "voices" / "nst"
URL = "https://www.nb.no/sbfil/talegjenkjenning/16kHz_2020/se_2020/lydfiler_16_1.tar.gz"
BANDS = [(16, 19, 3), (20, 29, 3), (30, 39, 3), (40, 49, 3), (50, 59, 3), (60, 69, 3), (70, 99, 3)]
CLIPS = 4


def pick():
    speakers = defaultdict(lambda: {"utts": []})
    for r in csv.DictReader(open(NST / "NST_se.csv", encoding="utf-8", errors="replace")):
        if not r["Age"].isdigit() or r["Sex"] not in ("Male", "Female") or len(r["text"]) < 60:
            continue
        if any(r[k] not in ("0", "") for k in ("NOI", "SND")):
            continue
        s = speakers[r["filename_channel_1"].split("_")[0]]
        s.update(age=int(r["Age"]), sex=r["Sex"], region=r["Region_of_Youth"])
        s["utts"].append((len(r["text"]), r["filename_channel_1"], r["text"]))
    rnd = random.Random(7)
    picked = {}
    for lo, hi, n in BANDS:
        for sex in ("Female", "Male"):
            pool = [(k, s) for k, s in speakers.items() if lo <= s["age"] <= hi and s["sex"] == sex and len(s["utts"]) >= CLIPS]
            rnd.shuffle(pool)
            regions = set()
            for k, s in pool:
                if len([1 for p in picked.values() if lo <= p["age"] <= hi and p["sex"] == sex]) >= n:
                    break
                if s["region"] in regions:
                    continue
                regions.add(s["region"])
                utts = sorted(s["utts"], reverse=True)[:CLIPS]
                picked[k] = dict(age=s["age"], sex=s["sex"], region=s["region"],
                                 files=[u[1] for u in utts], texts=[u[2] for u in utts])
    (NST / "picked.json").write_text(json.dumps(picked, ensure_ascii=False, indent=1))
    for k, p in picked.items():
        print(k, p["age"], p["sex"], p["region"])


def fetch():
    picked = json.loads((NST / "picked.json").read_text())
    wanted = {f for p in picked.values() for f in p["files"]}
    out = NST / "clips"
    out.mkdir(exist_ok=True)
    wanted -= {f.name for f in out.glob("*.wav")}
    print(f"{len(wanted)} clips to find", flush=True)
    seen = 0
    local = NST / "lydfiler_16_1.tar.gz"
    resp = local.open("rb") if local.exists() else urllib.request.urlopen(URL)
    with resp, tarfile.open(fileobj=resp, mode="r|gz") as tar:
        for m in tar:
            seen += 1
            if seen % 20000 == 0:
                print(f"{seen} files scanned, {len(wanted)} left", flush=True)
            name = m.name.rsplit("/", 1)[-1]
            if m.isfile() and name in wanted:
                (out / name).write_bytes(tar.extractfile(m).read())
                wanted.discard(name)
                if not wanted:
                    break
    print(f"done, {len(wanted)} not found", flush=True)


def refs():
    picked = json.loads((NST / "picked.json").read_text())
    refs = ROOT / "materials" / "voices" / "refs"
    for k, p in picked.items():
        files = [NST / "clips" / f for f in p["files"] if (NST / "clips" / f).exists()]
        if not files:
            continue
        sex = "f" if p["sex"] == "Female" else "m"
        region = p["region"].lower().replace(" med omnejd", "").replace(" ", "-").replace("ö", "o").replace("ä", "a").replace("å", "a")
        name = f"nst-{sex}{p['age']}-{region}-{k.split('-')[0][-3:]}"
        inputs = sum((["-i", str(f)] for f in files[:3]), [])
        chain = "".join(f"[{i}]silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,apad=pad_dur=0.3[a{i}];" for i in range(len(files[:3])))
        chain += "".join(f"[a{i}]" for i in range(len(files[:3]))) + f"concat=n={len(files[:3])}:v=0:a=1,atrim=0:14[out]"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", chain, "-map", "[out]", "-ar", "24000", "-ac", "1",
                        str(refs / f"{name}.wav")], check=True)
        p["ref"] = f"{name}.wav"
        print(name)
    (NST / "picked.json").write_text(json.dumps(picked, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    {"pick": pick, "fetch": fetch, "refs": refs}[sys.argv[1]]()
