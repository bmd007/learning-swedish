"""Validate lesson files against content/SCHEMA rules (see docs/AUTHORING.md).

  python3 tools/validate.py                  # all lessons
  python3 tools/validate.py lessons/x.json   # one lesson
Exit code 1 if any error.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TYPES = {"mcq", "select", "gap", "order", "short", "write", "speak", "info", "draw"}
ID = re.compile(r"^[A-Za-z0-9_.-]+$")


def check(path):
    errors = []
    err = errors.append
    try:
        lesson = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:
        return [f"invalid JSON: {e}"]
    if Path(path).stem != lesson.get("id"):
        err(f"file name must equal id ({lesson.get('id')})")
    for k in ("id", "title", "sections"):
        if k not in lesson:
            err(f"missing '{k}'")
    if lesson.get("mode", "exam") not in ("exam", "practice"):
        err("mode must be 'exam' or 'practice'")
    item_ids, audio_ids = set(), set()
    image_count = 0

    def check_image(img, where):
        nonlocal image_count
        image_count += 1
        if not isinstance(img, dict) or not img.get("src") or not img.get("alt"):
            err(f"{where}: image needs src and alt")
            return
        src = img["src"]
        if src.startswith("/materials/"):
            if not (ROOT / src.lstrip("/")).is_file():
                print(f"warning: {where}: {src} not on this machine (private material)")
        elif not re.match(r"^(https?:)?/", src) and not (ROOT / "images" / lesson.get("id", "") / src).is_file():
            err(f"{where}: image file images/{lesson.get('id')}/{src} not found")

    def check_audio(a, where):
        if not ID.match(str(a.get("id", ""))):
            err(f"{where}: audio needs a safe id")
        if a.get("id") in audio_ids:
            err(f"{where}: duplicate audio id {a.get('id')}")
        audio_ids.add(a.get("id"))
        src = a.get("source")
        if src:
            if not re.fullmatch(r"materials/[\w./-]+\.(m4a|mp3)", src) or ".." in src:
                err(f"{where}: audio.source must be materials/....m4a|mp3")
            elif not (ROOT / src).is_file():
                print(f"warning: {where}: {src} not on this machine (private material)")
            clip = a.get("clip")
            if clip is not None and not (isinstance(clip, list) and len(clip) == 2 and 0 <= clip[0] < clip[1]):
                err(f"{where}: audio.clip must be [start, end] in seconds")
            if not (a.get("script") or a.get("transcript")):
                err(f"{where}: real audio needs script or transcript (shown after submit)")
            return
        if not a.get("script"):
            err(f"{where}: audio.script is empty")
        speakers = a.get("speakers", {})
        for line in a.get("script", []):
            if "text" not in line:
                err(f"{where}: script line without text")
            if line.get("speaker") and line["speaker"] not in speakers:
                err(f"{where}: speaker '{line['speaker']}' not in audio.speakers")
        for g in speakers.values():
            voice = g.get("voice") if isinstance(g, dict) else g
            if voice not in ("f", "m"):
                err(f"{where}: speaker must be 'f'/'m' or {{voice: 'f'|'m', pitch?, rate?}}")

    for s in lesson.get("sections", []):
        sid = s.get("id", "?")
        if "title" not in s:
            err(f"section {sid}: missing title")
        parts = s.get("parts") or [s]
        for p in parts:
            if p.get("audio"):
                check_audio(p["audio"], f"section {sid}")
            if p.get("image"):
                check_image(p["image"], f"section {sid}")
            for it in p.get("items", []):
                iid = it.get("id", "?")
                where = f"{sid}/{iid}"
                t = it.get("type")
                if t not in TYPES:
                    err(f"{where}: unknown type {t}")
                    continue
                if it.get("image"):
                    check_image(it["image"], where)
                if t == "info":
                    if not it.get("md"):
                        err(f"{where}: info needs 'md'")
                    continue
                if not ID.match(iid):
                    err(f"{where}: bad id")
                if iid in item_ids:
                    err(f"{where}: duplicate item id")
                item_ids.add(iid)
                if not it.get("tags"):
                    err(f"{where}: needs at least one tag")
                opts = it.get("options") or p.get("options")
                if t in ("mcq", "select"):
                    if not opts or not isinstance(it.get("answer"), int) or not 0 <= it["answer"] < len(opts):
                        err(f"{where}: needs options and a valid answer index")
                if t == "gap":
                    if it.get("q", "").count("___") != 1:
                        err(f"{where}: gap q must contain exactly one ___")
                    if not it.get("answers"):
                        err(f"{where}: gap needs answers[]")
                if t == "short" and not it.get("answers"):
                    err(f"{where}: short needs answers[]")
                if t == "order":
                    words, answers = it.get("words", []), it.get("answers", [])
                    if not words or not answers:
                        err(f"{where}: order needs words[] and answers[]")
                    norm = lambda x: sorted(re.sub(r"[.,!?;:]", "", x).lower().split())
                    for a in answers:
                        if norm(a) != sorted(w.lower() for w in words):
                            err(f"{where}: answer '{a}' does not use exactly the given words")
                if t == "draw" and not (it.get("map") or {}).get("src"):
                    err(f"{where}: draw item needs map: {{src, alt}}")
                if t == "order" and " ".join(it.get("words", [])).lower() in [a.lower() for a in it.get("answers", [])]:
                    err(f"{where}: order words are already in the answer order – shuffle them")
                if t in ("write", "speak", "draw") and not it.get("q"):
                    err(f"{where}: needs q")
                if it.get("audio"):
                    check_audio(it["audio"], where)
    if not lesson.get("legacy") and image_count == 0:
        err("lesson has no images – add at least one image (see docs/AUTHORING.md, Images)")
    mcq_answers = [it.get("answer") for s in lesson.get("sections", []) for p in (s.get("parts") or [s])
                   for it in p.get("items", []) if it.get("type") == "mcq" and len(it.get("options", [])) > 2]
    if not lesson.get("legacy") and len(mcq_answers) >= 4 and max(mcq_answers.count(a) for a in set(mcq_answers)) > 0.6 * len(mcq_answers):
        err("mcq answers are mostly at the same position – vary the position of the correct option")
    return errors


if __name__ == "__main__":
    paths = sys.argv[1:] or sorted(str(p) for d in ("lessons", "materials/lessons") for p in (ROOT / d).glob("*.json"))
    bad = 0
    for p in paths:
        errs = check(p)
        print(f"{'OK ' if not errs else 'ERR'} {p}")
        for e in errs:
            print(f"    - {e}")
        bad += bool(errs)
    sys.exit(1 if bad else 0)
