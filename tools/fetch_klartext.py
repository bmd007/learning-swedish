"""Download recent SR Klartext articles (real radio clip + headline + short text) for listening practice.

Saves to materials/sr/klartext/ (gitignored, personal use): <slug>.m4a and index.json.
Usage: python3 -I tools/fetch_klartext.py [max_articles]
"""
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "materials" / "sr" / "klartext"
BASE = "https://www.sverigesradio.se"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (learning-client)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def text_lines(page):
    page = re.sub(r"<script.*?</script>|<style.*?</style>", "", page, flags=re.S)
    page = html.unescape(re.sub(r"<[^>]+>", "\n", page))
    return [line.strip() for line in page.split("\n") if line.strip()]


def parse(slug, page):
    audio = re.findall(r"https://lyssna-cdn\.sr\.se/[^\"' ]+?_a96\.m4a", page)
    if not audio:
        return None
    lines = text_lines(page)
    pub = next((i for i, line in enumerate(lines) if line.startswith("Publicerad")), None)
    if pub is None:
        return None
    end = next((i for i in range(pub, len(lines)) if lines[i] == "Dela"), len(lines))
    body = [line for line in lines[pub + 1:end] if not re.fullmatch(r"·?\s*\d+:\d+ min", line)]
    title_idx = next(i for i in range(pub - 1, -1, -1) if not re.fullmatch(r"\d+ MIN", lines[i]))
    duration = re.search(r"(\d+):(\d+) min", " ".join(lines[pub:pub + 3]))
    category = lines[title_idx - 1]
    if category.startswith("Foto:") or category == lines[title_idx] or category.isupper() is False:
        category = None
    return {
        "slug": slug,
        "title": lines[title_idx],
        "category": category.capitalize() if category else None,
        "published": lines[pub].removeprefix("Publicerad ").strip(),
        "seconds": int(duration[1]) * 60 + int(duration[2]) if duration else None,
        "text": body,
        "audioUrl": audio[0],
        "file": f"materials/sr/klartext/{slug}.m4a",
        "url": f"{BASE}/artikel/{slug}",
    }


def main(limit):
    OUT.mkdir(parents=True, exist_ok=True)
    index_file = OUT / "index.json"
    index = {a["slug"]: a for a in json.loads(index_file.read_text(encoding="utf-8"))} if index_file.exists() else {}
    listing = get(f"{BASE}/klartext").decode("utf-8")
    slugs = list(dict.fromkeys(re.findall(r'href="/artikel/([^"#?]+)"', listing)))[:limit]
    for slug in slugs:
        if slug in index and (OUT / f"{slug}.m4a").exists():
            continue
        try:
            art = parse(slug, get(f"{BASE}/artikel/{slug}").decode("utf-8"))
            if not art:
                print(f"skip {slug} (no audio)")
                continue
            (OUT / f"{slug}.m4a").write_bytes(get(art["audioUrl"]))
            index[slug] = art
            print(f"ok   {slug}  [{art['category']}] {art['seconds']}s")
        except Exception as e:
            print(f"fail {slug}: {e}")
    index_file.write_text(json.dumps(list(index.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(index)} articles in {index_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 60)
