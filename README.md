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

Without audio files, the browser reads the dialogues aloud itself (lower quality).

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
| `tools/` | `validate.py` (check a lesson), `build_audio.py` (make audio), `report.py` (scores per skill), `generate.py` (local-model generator) |
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

**With a chat-only AI** (ChatGPT or Gemini in the browser):
1. Paste or upload `docs/AUTHORING.md`, `progress/learner-profile.md` and `progress/tag-stats.md`.
2. Ask: *"Write one lesson JSON file following this format, about <topic>."*
3. Save the answer as `lessons/NNN-slug.json` (the file name must match `id`) and run
   `python3 tools/validate.py` on it. If it complains, paste the errors back into the chat.
4. Images: ask the AI for simple SVG drawings, save them in `images/<lesson-id>/`, and reference them
   as described under "Images" in the guide. Lessons without images fail validation.
5. To get your answers graded, paste the output of `python3 tools/report.py results/<file>.json`.

**With a local model, no cloud AI at all:** the panel at the bottom of the app's home page
("Skapa en egen lektion") uses Ollama on your machine (`tools/generate.py`, default `gemma3:12b`). A
small model makes mistakes, so the generator splits the work into small steps, reviews the language,
drops doubtful items, and checks the answer keys. Its lessons are marked *"Lokal modell · inte granskad
av Claude"*. Use them for extra practice, and expect an occasional wrong answer.

Whichever AI you use, check that it:
- double-checks every answer key (a wrong key teaches you the mistake);
- keeps lessons short (10–15 min) and on one topic;
- adds pictures: rule images *and* pictures of what words mean.

---

## Private material

- `materials/` (gitignored) holds course material licensed to the learner, for example the Rivstart
  B1/B2 extra material. A password-protected copy is in `materials.zip` (Git LFS). Never publish it.
- `recordings/` and `uploads/` (voice recordings, photos of handwriting) are gitignored.
- Access tokens such as `nt-access.txt` are gitignored. Never commit them.
