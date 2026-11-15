"""Export reading tests (lesson JSON) to one standalone HTML page for the phone (works offline).

  python3 tools/phone_reading.py <out.html> "<title>" lessons/a.json [lessons/b.json ...]

Several lessons are merged into one test: sections in order, question numbers continue,
timeLimit and scoring are summed. Only text items are kept (mcq, select, short, gap).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEEP = {"mcq", "select", "short", "gap"}


def merge(paths, title):
    lessons = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    sections = []
    for lesson in lessons:
        for sec in lesson["sections"]:
            parts = []
            for part in sec.get("parts", [sec]):
                items = [{k: it[k] for k in ("id", "type", "q", "options", "answer", "answers", "explain") if k in it}
                         for it in part.get("items", []) if it.get("type") in KEEP]
                if items:
                    parts.append({k: part[k] for k in ("heading", "passageTitle", "passage", "options") if part.get(k)} | {"items": items})
            if parts:
                sections.append({"title": sec.get("title", ""), "instructions": sec.get("instructions", ""), "parts": parts})
    scorings = [l.get("scoring") for l in lessons if l.get("scoring")]
    scoring = {k: sum(s.get(k, 0) for s in scorings) for k in scorings[0]} if len(scorings) == len(lessons) else None
    limits = [l.get("timeLimit") for l in lessons]
    return {
        "id": "-".join(l["id"].split("-")[0] for l in lessons),
        "title": title,
        "eyebrow": "Läsförståelse · " + ("SFI D" if scoring and "G" in scoring else "Swedex A2B1 / SFI D"),
        "numberStart": lessons[0].get("numberStart", 1),
        "timeLimit": sum(limits) if all(limits) else None,
        "scoring": scoring,
        "sections": sections,
    }


def main():
    out, title, *paths = sys.argv[1:]
    data = merge(paths, title)
    template = (ROOT / "reading" / "_template.html").read_text(encoding="utf-8")
    html = template.replace("__TITLE__", title).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    Path(out).write_text(html, encoding="utf-8")
    n = sum(len(p["items"]) for s in data["sections"] for p in s["parts"])
    print(f"{out}: {len(data['sections'])} delar, {n} frågor, {data['timeLimit']} min, scoring {data['scoring']}")


if __name__ == "__main__":
    main()
