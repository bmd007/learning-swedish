"""Find and fetch short Pixabay videos (or photos) as memory cues for words.

  python3 -I tools/pixabay.py search "ashamed person" [--n 8] [--photo]
      → prints id, duration, tags; saves thumbnails to materials/video/_thumbs/<query>/ to look at
  python3 -I tools/pixabay.py get <id> <lessonId> <name> [--photo]
      → materials/video/<lessonId>/<name>.mp4 (or .jpg); use as image.src "/materials/video/<lessonId>/<name>.mp4"

Key: materials/.pixabay_key (gitignored). Pixabay content licence: free to use, but no redistribution of the raw
files as such → files stay in materials/ (private), never committed.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEY = (ROOT / "materials" / ".pixabay_key").read_text().strip()
OUT = ROOT / "materials" / "video"


def api(photo, **params):
    base = "https://pixabay.com/api/" if photo else "https://pixabay.com/api/videos/"
    url = base + "?" + urllib.parse.urlencode({"key": KEY, "safesearch": "true", **params})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        dest.write_bytes(r.read())


def search(query, n, photo):
    hits = api(photo, q=query, per_page=max(n, 3))["hits"][:n]
    thumbs = OUT / "_thumbs" / re.sub(r"\W+", "-", query)
    for h in hits:
        thumb = h["webformatURL"] if photo else h["videos"]["tiny"]["thumbnail"]
        fetch(thumb, thumbs / f"{h['id']}.jpg")
        print(h["id"], "" if photo else f"{h['duration']}s", h["tags"])
    print("thumbnails:", thumbs)


def get(item_id, lesson, name, photo):
    h = api(photo, id=item_id)["hits"][0]
    if photo:
        dest = OUT / lesson / f"{name}.jpg"
        fetch(h["webformatURL"], dest)
    else:
        v = h["videos"]
        dest = OUT / lesson / f"{name}.mp4"
        fetch((v.get("small") or v["tiny"])["url"], dest)
    print("saved", dest.relative_to(ROOT), f"(pixabay {item_id}, {h.get('user')})")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    photo = "--photo" in sys.argv
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 6
    if args and args[0] == "search":
        search(" ".join(a for a in args[1:] if a != str(n)), n, photo)
    elif args and args[0] == "get":
        get(args[1], args[2], args[3], photo)
    else:
        print(__doc__)
