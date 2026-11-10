# Log

## 2026-11-04 – Project start
- Built app (Python stdlib server + plain JS engine), lesson JSON format, audio via edge-tts.
- Research done: docs/research.md (SFI D format, citizenship test, agentic tutors, TTS/STT).
- Lesson `001-diagnos` built: reading (2 texts), listening (3 recordings), grammar (18),
  vocab (6), writing (formal email), speaking (read-aloud + 2 monologues).
- **Next step:** learner takes 001-diagnos → grade writing/speaking, write feedback,
  fill learner-profile skill table, build lesson 002 on the weakest areas.

## 2026-11-04 – New goal: Swedex A2B1 on 2026-12-04 (Göteborg)
- Swedex ends 2026-12-31. Learner may take it 2026-12-04. Plan in progress/plan.md.
- Downloaded official A2B1 model test to materials/ (gitignored).
- Engine: added `select` (matching) and `short` (1–5 word answers) item types; examiner audio on speak items.
- **Next step:** learner takes 001-diagnos; then official model test timed; then lessons in Swedex format.

## 2026-11-04 – 001-diagnos graded (draft, writing/speaking skipped)
- Reading 7/8, listening 8/9 (1 play), grammar 10/18 (word order perfect, morphology weak), vocab 0/6.
- Feedback: feedback/001-diagnos__2026-11-04T21-32-20-542Z.md
- Decoupled content from code: docs/AUTHORING.md, tools/validate.py, tools/report.py (tag-stats), new item type `info`, lesson `mode: practice` (instant check, firstTry recorded).
- **Next step:** 002 writing+speaking (Swedex shape), 003 practice strong verbs + vocab from errors; then official model test reading.

## 2026-11-10
- Learner asked about "gick så svagt". Built `004-ga-och-svag` (practice) – later split, see below: gå forms + chunks
  (hur går det, det går inte, så där), svag forms + svaghet/försvaga/vara svag för, adjective → adverb -t,
  a short dialogue (audio), word order, 1 speak item.
- New tag: `adjektiv.adverb`, `ord.tema.ordbildning`.
- Next step: grade 004 when results arrive. Recycle words from progress/vocab.md in later lessons.
- Learner: lessons need images/media, should be short and one topic. Added image support (`image` on
  part/item/info, files in images/<lessonId>/, validator requires ≥1 image). Split 004 into
  `004-ga-gick-gatt` (verb gå) and `005-svag-svagt` (svag forms + adverb -t + dialogue). Added SVG images
  to 002 and 003 too.
- Next step: learner takes 004/005 (and 002/003). Grade when results arrive.

## 2026-11-11
- Learner asked for a lesson about a job ad for a horse caretaker, with listening. Built
  `006-jobb-hastskotare` (practice, ~13 min): stable vocabulary (mocka, rykta, släppa ut, krav vs
  meriterande, varannan helg), ad with Ja/Nej (Swedex reading shape), phone call (Swedex listening:
  MCQ + 1–5 word answers), speaking: call about the ad. Images: 2 SVGs + 3 Wikimedia photos (credited).
- Next step: grade 004–006 when results arrive.
