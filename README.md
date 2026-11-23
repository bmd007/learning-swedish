# Svenska B1 – a personal AI Swedish teacher

A small app plus a set of files that let an AI act as your Swedish teacher. The goal is level B1
(SFI D / Swedex A2B1).

- You take short lessons and tests in the browser: reading, listening, writing, speaking.
- Every answer is saved as a file.
- The AI reads those files, grades your answers, writes feedback, updates notes about you, and builds
  the next lesson for your weak spots.

Lessons are plain JSON files. Making a new lesson means writing one file. The app shows any lesson that
follows the format.

## Quick start

```
./start-app.sh            # starts the server and opens http://localhost:8765
```

You need Python 3 and nothing else. Optional extras:

| For | Install |
|---|---|
| Good-quality listening audio | `python3 -m venv .venv && .venv/bin/pip install edge-tts` (needs internet) |
| Checking SVG images | `brew install librsvg` (`rsvg-convert`) |
| Generating lessons with a local model | [Ollama](https://ollama.com) + `ollama pull gemma3:12b` |
| Better speech transcripts (local Whisper) | install ffmpeg (`brew install ffmpeg`) and `.venv/bin/pip install openai-whisper`, then `.venv/bin/python tools/transcribe.py [--save] <audio>` (downloads the "turbo" model, 1.5 GB, once; works offline after) |
| Real radio for listening | `python3 -I tools/fetch_klartext.py` downloads SR Klartext clips to `materials/sr/klartext/` (private, not in git). Lessons with `audio.source` need these files |
| HEIC photos on Windows/Linux | `pip install pillow-heif` (optional, see "Photos" below) |

Without audio files, the browser reads the dialogues aloud itself (lower quality).

### Windows and Linux

Everything is plain Python and works on all three systems. Differences:
- On Windows, start with `python server.py` and open http://localhost:8765, or use Git Bash or WSL for
  `./start-app.sh`.
- The venv Python is `.venv\Scripts\python` on Windows instead of `.venv/bin/python`.
- openai-whisper needs PyTorch; on Windows use Python 3.12 or 3.13 if the install fails. With an NVIDIA GPU it runs much faster.
- Use `rsvg-convert` from your package manager (`apt install librsvg2-bin`) or skip it.

### Photos and recordings

- **Photos of handwriting:** the browser converts every photo to JPG before upload, so any format the
  browser can open works. If a HEIC still arrives (Chrome can't open HEIC), the server converts it with
  `sips` (macOS) or `pillow-heif` if installed, otherwise it asks you to save the photo as JPG.
  iPhone tip: Settings → Camera → Formats → *Most Compatible* saves JPG directly.
- **Speaking:** recorded in the browser (`.webm`). Each speaking task gives at least 2 minutes (60 s +
  30 s per question), so there is room for extra sentences. The transcript comes from the browser's
  speech recognition. `tools/transcribe.py` gives a better one if Whisper is installed.

## How it works

```
you take a lesson ──▶ results/*.json ──▶ AI grades ──▶ feedback/*.md (shown in the app)
        ▲                                        │
        └──── lessons/NNN-*.json ◀── AI writes ◀──┴── progress/ (your profile, errors, plan)
```

| Folder | What |
|---|---|
| `lessons/` | one JSON file per lesson or test |
| `images/<lesson>/`, `audio/<lesson>/` | pictures and listening audio for each lesson |
| `results/` (`drafts/` = unfinished) | your answers, saved after every answer |
| `feedback/` | graded feedback, shown with the **Feedback** button |
| `progress/` | learner model: `plan.md`, `learner-profile.md`, `decisions.md`, `log.md`, `vocab.md`, `tag-stats.md` |
| `docs/AUTHORING.md` | **the contract**: lesson format, item types, image and audio rules, how to grade |
| `tools/` | `validate.py` (check a lesson), `build_audio.py` (make audio), `report.py` (scores per skill), `generate.py` (local-model generator), `transcribe.py` (Swedish speech-to-text) |
| `web/`, `server.py` | the app (Python standard library + plain JS, no build step) |
| `materials/` | private course material (gitignored, see below) |

---

## Using it with Claude Code

This is the intended setup. Claude Code reads `CLAUDE.md` automatically. That file makes Claude the
**teacher and project lead**: it decides the next lesson, builds it, grades you, keeps notes, and commits.

1. Open a terminal in the repo and run `claude`.
2. Start with something like **"continue"** or **"what's next?"**. Claude follows the resume checklist
   in `CLAUDE.md`: it reads your plan, profile and log, grades any ungraded attempt, and goes on from the
   last "Next step".
3. Run `./start-app.sh` and take the lesson.
4. Tell Claude **"done"** (or just come back later). It grades, writes feedback, updates `progress/`,
   builds the next lesson, and pushes.

Useful things to ask:

| You say | Claude does |
|---|---|
| "what does *i morse* mean?" or any word or phrase | explains it briefly, then builds a short practice lesson in the app and adds the word to `progress/vocab.md` for spaced repetition |
| "a lesson about X" / "a test on Y" | writes `lessons/NNN-*.json` with pictures, listening and speaking, validates it, makes the audio |
| "grade my last test" | grades `results/` (or a draft you abandoned), writes `feedback/…md` |
| "how am I doing?" | summary from `progress/tag-stats.md` and the log |

Claude also uses the subagents in `.claude/agents/`: `lesson-author` writes a lesson, `grader` grades
one. You don't need to call them yourself.

Tips:
- Preferences you tell Claude ("more pictures", "shorter lessons", "explain in Persian") go into
  `progress/decisions.md`, so they last across sessions.
- Writing tasks can be typed or uploaded as a photo of your handwriting. Speaking tasks are recorded in
  the browser, and Claude grades the transcript.

## Using it with another AI (ChatGPT, Gemini, Cursor, Codex, …)

Nothing here depends on Claude. Everything is in files, so any AI that can read text and write a JSON
file can be the teacher. The rules live in **`docs/AUTHORING.md`**. Give the AI that file first.

**With an AI that can read and edit files** (Cursor, Codex, Copilot agent, Gemini CLI, …):
1. Tell it: *"Read CLAUDE.md and docs/AUTHORING.md. You are the teacher described there."*
   `CLAUDE.md` is plain instructions. Only its name is Claude-specific.
2. Ask for a lesson, then make it run the checks:
   ```
   python3 tools/validate.py lessons/NNN-name.json     # must print OK
   .venv/bin/python tools/build_audio.py lessons/NNN-name.json
   ```
3. After you take the lesson, ask it to grade: `python3 tools/report.py results/<file>.json` shows
   your answers item by item. The grading steps are at the end of `docs/AUTHORING.md`.

**With a local model, no cloud AI at all:** the panel at the bottom of the app's home page
("Skapa en egen lektion") uses Ollama on your machine (`tools/generate.py`, default `gemma3:12b`). A
small model makes mistakes, so the generator splits the work into small steps, reviews the language,
drops doubtful items, and checks the answer keys. Its lessons are marked *"Lokal modell · inte granskad
av Claude"*. Use them for extra practice, and expect an occasional wrong answer.

Whichever AI you use, check that it:
- double-checks every answer key (a wrong key teaches you the mistake);
- keeps lessons short (5-10–15 min) and on one topic;
- adds pictures: rule images *and* pictures of what words mean.

---

## Private material

- `materials/` (gitignored) holds course material licensed to the learner, for example the Rivstart
  B1/B2 extra material. An encrypted copy (7z, AES-256, file names hidden) is made with `tools/pack_materials.sh` → `materials.7z` (Git LFS).
  Unpack with `7zz x materials.7z`. The old `materials.zip` (weak ZipCrypto, file names visible) is being replaced. Never publish the plain files.
- `recordings/` and `uploads/` (voice recordings, photos of handwriting) are gitignored.
