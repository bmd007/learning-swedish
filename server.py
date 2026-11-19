import json
import re
import shutil
import subprocess
import sys
import threading
import uuid
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).parent.resolve()
LESSONS = ROOT / "lessons"
PRIVATE_LESSONS = ROOT / "materials" / "lessons"
RESULTS = ROOT / "results"
RECORDINGS = ROOT / "recordings"
UPLOADS = ROOT / "uploads"
IMAGE_EXT = {"jpg", "jpeg", "png", "heic", "heif", "webp"}
FEEDBACK = ROOT / "feedback"
DRAFTS = RESULTS / "drafts"
SAFE = re.compile(r"^[A-Za-z0-9_.-]+$")
JOBS = {}
GEN_LOCK = threading.Lock()


def run_job(job_id, topic, mode):
    job = JOBS[job_id]
    sys.path.insert(0, str(ROOT / "tools"))
    import generate
    with GEN_LOCK:
        job["status"] = "running"
        try:
            job["lessonId"] = generate.generate(topic, mode, log=job["log"].append)
            job["status"] = "done"
        except Exception as e:
            job["log"].append(f"Fel: {e}")
            job["status"] = "error"


SKILLS = {"läs": "läsa", "hör": "höra", "skriv": "skriva", "tal": "tala"}


def skill_of(tag):
    return SKILLS.get(tag.split(".")[0], "grammatik")


def lesson_items(data):
    for sec in data.get("sections", []):
        for part in sec.get("parts", [sec]):
            for item in part.get("items", []):
                if item.get("type") != "info":
                    yield item


def final_results():
    out = {}
    for f in sorted(RESULTS.glob("*.json")):
        try:
            out.setdefault(f.name.rsplit("__", 1)[0], []).append(json.loads(f.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            continue
    return out


def draft_has_answers(f):
    try:
        state = json.loads(f.read_text(encoding="utf-8")).get("state") or {}
    except (OSError, ValueError):
        return False
    return any(v not in (None, "", [], {}) for v in (state.get("answers") or {}).values()) or bool(state.get("uploads"))


def lesson_files():
    """Public lessons + private ones built from licensed material (materials/lessons/, gitignored)."""
    return sorted([*LESSONS.glob("*.json"), *PRIVATE_LESSONS.glob("*.json")], key=lambda f: f.name)


def lesson_summaries():
    results = final_results()
    out = []
    for f in lesson_files():
        data = json.loads(f.read_text(encoding="utf-8"))
        runs = results.get(data["id"], [])
        last = runs[-1] if runs else None
        score = None
        if last:
            parts = (last.get("score") or {}).values()
            score = {"correct": sum(p["correct"] for p in parts), "total": sum(p["total"] for p in parts),
                     "date": (last.get("finishedAt") or last.get("savedAt") or "")[:10]}
        skills = sorted({skill_of(t) for it in lesson_items(data) for t in it.get("tags", [])})
        out.append({
            "id": data["id"],
            "title": data.get("title"),
            "titleEn": data.get("titleEn"),
            "minutes": data.get("minutes"),
            "timeLimit": data.get("timeLimit"),
            "attempts": len(runs) or int(any(FEEDBACK.glob(f"{data['id']}__*.md"))),
            "lastScore": score,
            "skills": skills,
            "hasFeedback": any(FEEDBACK.glob(f"{data['id']}__*.md")),
            "inProgress": any(draft_has_answers(f) for f in DRAFTS.glob(f"{data['id']}__*.json")),
            "teacherGraded": any(it.get("type") in ("write", "speak", "draw") for it in lesson_items(data)),
            "lastDate": max([(r.get("finishedAt") or r.get("savedAt") or "")[:10] for r in runs] or [""]),
            "mode": data.get("mode"),
            "generated": bool(data.get("generated")),
            "reviewed": bool((data.get("generated") or {}).get("reviewed")),
        })
    return out


def progress_summary():
    plan = (ROOT / "progress" / "plan.md")
    text = plan.read_text(encoding="utf-8") if plan.exists() else ""
    m = re.search(r"^Test date:\s*(\d{4}-\d{2}-\d{2})", text, re.M)
    goal = re.search(r"^# Plan:\s*(.+)$", text, re.M)
    skills, minutes, done = {}, 0, 0
    for runs in final_results().values():
        for r in runs:
            done += 1
            minutes += min(sum((r.get("sectionMinutes") or {}).values()) or (r.get("durationMin") or 0), 60)
            for it in r.get("items", []):
                for skill in {skill_of(t) for t in it.get("tags", [])} or {"grammatik"}:
                    s = skills.setdefault(skill, {"correct": 0, "total": 0, "teacher": 0})
                    if it.get("correct") is None:
                        s["teacher"] += 1
                    else:
                        s["total"] += 1
                        s["correct"] += bool(it["correct"])
    return {"examDate": m.group(1) if m else None, "goal": goal.group(1) if goal else None, "skills": skills, "minutes": minutes, "attempts": done}


def heic_to_jpg(src):
    jpg = src.with_suffix(".jpg")
    if shutil.which("sips"):
        done = subprocess.run(["sips", "-s", "format", "jpeg", str(src), "--out", str(jpg)], capture_output=True)
        if done.returncode == 0:
            return jpg
    try:
        from PIL import Image
        from pillow_heif import register_heif_opener
        register_heif_opener()
        Image.open(src).convert("RGB").save(jpg, "JPEG", quality=88)
        return jpg
    except Exception:
        return None


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
        if p == "/api/progress":
            return self.send_json(progress_summary())
        m = re.fullmatch(r"/api/lessons/([A-Za-z0-9_.-]+)", p)
        if m:
            f = LESSONS / f"{m.group(1)}.json"
            if not f.exists():
                f = PRIVATE_LESSONS / f"{m.group(1)}.json"
            if not f.exists():
                return self.send_json({"error": "not found"}, 404)
            return self.send_text(f.read_text(encoding="utf-8"), "application/json; charset=utf-8")
        m = re.fullmatch(r"/api/generate/([a-f0-9]+)", p)
        if m:
            job = JOBS.get(m.group(1))
            return self.send_json(job if job else {"error": "not found"}, 200 if job else 404)
        m = re.fullmatch(r"/api/draft/([A-Za-z0-9_.-]+)", p)
        if m:
            files = sorted(DRAFTS.glob(f"{m.group(1)}__*.json"), key=lambda f: f.stat().st_mtime)
            if not files:
                return self.send_json({"error": "not found"}, 404)
            return self.send_text(files[-1].read_text(encoding="utf-8"), "application/json; charset=utf-8")
        m = re.fullmatch(r"/api/feedback/([A-Za-z0-9_.-]+)", p)
        if m:
            files = sorted(FEEDBACK.glob(f"{m.group(1)}__*.md"))
            if not files:
                return self.send_json({"error": "not found"}, 404)
            return self.send_text(files[-1].read_text(encoding="utf-8"))
        if p.startswith(("/web/", "/audio/", "/uploads/", "/images/", "/reading/")):
            return super().do_GET()
        if p.startswith("/materials/") and p.endswith((".m4a", ".mp3", ".wav", ".png", ".jpg")) and ".." not in p:
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
        if url.path == "/api/generate":
            data = json.loads(body or b"{}")
            topic = str(data.get("topic", "")).strip()[:500]
            mode = "exam" if data.get("mode") == "exam" else "practice"
            if len(topic) < 3:
                return self.send_json({"error": "beskriv ämnet"}, 400)
            job_id = uuid.uuid4().hex[:12]
            queued = GEN_LOCK.locked()
            JOBS[job_id] = {"id": job_id, "topic": topic, "mode": mode, "status": "queued",
                            "log": ["Väntar på att förra genereringen blir klar …"] if queued else [], "lessonId": None}
            threading.Thread(target=run_job, args=(job_id, topic, mode), daemon=True).start()
            return self.send_json({"id": job_id})
        if url.path == "/api/recording":
            q = parse_qs(url.query)
            name = q.get("name", [""])[0]
            ext = q.get("ext", ["webm"])[0]
            if not SAFE.match(name) or not SAFE.match(ext):
                return self.send_json({"error": "bad name"}, 400)
            f = RECORDINGS / f"{name}__{stamp}.{ext}"
            f.write_bytes(body)
            return self.send_json({"saved": f.name})
        if url.path == "/api/upload":
            q = parse_qs(url.query)
            name = q.get("name", [""])[0]
            ext = q.get("ext", [""])[0].lower()
            if not SAFE.match(name) or ext not in IMAGE_EXT:
                return self.send_json({"error": "bad name or type"}, 400)
            f = UPLOADS / f"{name}__{stamp}-{datetime.now().microsecond:06d}.{ext}"
            f.write_bytes(body)
            if ext in ("heic", "heif"):
                jpg = heic_to_jpg(f)
                f.unlink(missing_ok=True)
                if not jpg:
                    return self.send_json({"error": "Kunde inte läsa HEIC-bilden. Spara den som JPG och försök igen."}, 415)
                f = jpg
            return self.send_json({"saved": f.name})
        self.send_json({"error": "not found"}, 404)


if __name__ == "__main__":
    for d in (LESSONS, RESULTS, DRAFTS, RECORDINGS, UPLOADS, FEEDBACK, ROOT / "audio"):
        d.mkdir(exist_ok=True)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Svenska B1 -> http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
