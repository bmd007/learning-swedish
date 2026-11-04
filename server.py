import json
import re
import sys
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent.resolve()
LESSONS = ROOT / "lessons"
RESULTS = ROOT / "results"
RECORDINGS = ROOT / "recordings"
FEEDBACK = ROOT / "feedback"
DRAFTS = RESULTS / "drafts"
SAFE = re.compile(r"^[A-Za-z0-9_.-]+$")


def lesson_summaries():
    attempts = {}
    for f in RESULTS.glob("*.json"):
        lesson_id = f.name.rsplit("__", 1)[0]
        attempts[lesson_id] = attempts.get(lesson_id, 0) + 1
    out = []
    for f in sorted(LESSONS.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        out.append({
            "id": data["id"],
            "title": data.get("title"),
            "titleEn": data.get("titleEn"),
            "minutes": data.get("minutes"),
            "attempts": attempts.get(data["id"], 0),
            "hasFeedback": any(FEEDBACK.glob(f"{data['id']}__*.md")),
        })
    return out


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s\n" % (fmt % args))

    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text, ctype="text/markdown; charset=utf-8"):
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        p = url.path
        if p == "/":
            self.path = "/web/index.html"
            return super().do_GET()
        if p == "/api/lessons":
            return self.send_json(lesson_summaries())
        m = re.fullmatch(r"/api/lessons/([A-Za-z0-9_.-]+)", p)
        if m:
            f = LESSONS / f"{m.group(1)}.json"
            if not f.exists():
                return self.send_json({"error": "not found"}, 404)
            return self.send_text(f.read_text(encoding="utf-8"), "application/json; charset=utf-8")
        m = re.fullmatch(r"/api/feedback/([A-Za-z0-9_.-]+)", p)
        if m:
            files = sorted(FEEDBACK.glob(f"{m.group(1)}__*.md"))
            if not files:
                return self.send_json({"error": "not found"}, 404)
            return self.send_text(files[-1].read_text(encoding="utf-8"))
        if p.startswith(("/web/", "/audio/")):
            return super().do_GET()
        self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        if url.path in ("/api/results", "/api/draft"):
            data = json.loads(body)
            lesson_id = data.get("lessonId", "unknown")
            attempt = str(data.get("attemptId", stamp))
            if not SAFE.match(lesson_id) or not SAFE.match(attempt):
                return self.send_json({"error": "bad id"}, 400)
            data["savedAt"] = datetime.now().isoformat(timespec="seconds")
            draft = DRAFTS / f"{lesson_id}__{attempt}.json"
            if url.path == "/api/draft":
                draft.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                return self.send_json({"saved": draft.name})
            f = RESULTS / f"{lesson_id}__{stamp}.json"
            f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            draft.unlink(missing_ok=True)
            return self.send_json({"saved": f.name})
        if url.path == "/api/recording":
            q = parse_qs(url.query)
            name = q.get("name", [""])[0]
            ext = q.get("ext", ["webm"])[0]
            if not SAFE.match(name) or not SAFE.match(ext):
                return self.send_json({"error": "bad name"}, 400)
            f = RECORDINGS / f"{name}__{stamp}.{ext}"
            f.write_bytes(body)
            return self.send_json({"saved": f.name})
        self.send_json({"error": "not found"}, 404)


if __name__ == "__main__":
    for d in (LESSONS, RESULTS, DRAFTS, RECORDINGS, FEEDBACK, ROOT / "audio"):
        d.mkdir(exist_ok=True)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Svenska B1 -> http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
