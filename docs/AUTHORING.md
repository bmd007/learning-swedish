# Authoring guide (for any AI or human)

You can create lessons, grade results, and write reports **without touching code**. The server
(`server.py`) and the UI (`web/`) are a generic player. All content is data:

| What | Where | Who writes it |
|---|---|---|
| Lessons / tests | `lessons/NNN-slug.json` | lesson author |
| Listening audio | `audio/<lessonId>/<audioId>.m4a` | `tools/build_audio.py` (from the lesson JSON) |
| Images | `images/<lessonId>/<name>.svg/.png/.jpg` | lesson author (hand-drawn SVG or downloaded free photo) |
| Learner answers | `results/*.json` (final), `results/drafts/*.json` (unfinished, saved after every answer) | the app |
| Voice recordings | `recordings/` (gitignored) | the app |
| Photos of handwritten answers | `uploads/` (gitignored; the browser converts every photo to JPG before upload. HEIC that the browser cannot read: `sips` on macOS, else `pillow-heif` if installed, else rejected with a message) | the app (`write` items) |
| Feedback to learner | `feedback/<lessonId>__<attempt>.md` (shown in app) | grader |
| Learner model | `progress/learner-profile.md`, `progress/plan.md`, `progress/decisions.md`, `progress/log.md` | teacher/grader |
| Error stats | `progress/tag-stats.md` | `tools/report.py` (generated, never edit) |
| Research / exam facts | `docs/research.md` | anyone |

Only change `server.py` / `web/` when a new *kind* of interaction is truly needed. Then add the item
type to the UI, to `tools/validate.py`, and to this guide in the same commit.

## Tools (no dependencies except edge-tts for audio)

```
python3 tools/validate.py [lessons/x.json]     # ALWAYS run after writing a lesson. Must print OK.
.venv/bin/python tools/build_audio.py lessons/x.json [--force]   # generate audio (needs internet)
python3 tools/report.py                         # all attempts + regenerate progress/tag-stats.md
python3 tools/report.py results/drafts/x.json   # one attempt, item by item (incl. writing/speech transcripts)
```

## Lesson file

```json
{
  "id": "005-verb-starka",            // = file name without .json; NNN = next free number
  "title": "Starka verb i preteritum", "titleEn": "Strong verbs in past tense",
  "mode": "practice",                  // "practice": a Kontrollera button gives instant feedback per item
                                       // "exam": feedback only after submit (use for mock tests)
  "minutes": 12,
  "intro": "...", "introEn": "...",
  "sections": [ /* one screen each */ ]
}
```

A **section** is one screen:
```json
{ "id": "lasa", "title": "Del 1: ...", "titleEn": "...", "instructions": "...", "instructionsEn": "...",
  "items": [ ... ] }
```
or, with several blocks on the screen (each block can have a reading text, an audio player, and/or a
shared option list for matching):
```json
{ "id": "lasa", "title": "...", "parts": [
  { "heading": "Text 1", "headingEn": "...",
    "passageTitle": "Hyresavi", "passage": "Text with \n newlines",
    "audio": { ... },
    "options": ["A. ...", "B. ..."],     // shared options for select items in this part
    "items": [ ... ] } ] }
```

### Item types

Every item (except `info`) needs a unique `id` in the lesson, `type`, and at least one `tags` entry.
Optional on all: `q`, `qEn` (English hint), `explain`, `explainEn` (shown after checking/submitting).

| type | use for | required fields | auto-graded |
|---|---|---|---|
| `info` | teaching text, rules, tables, Persian notes (markdown) | `md` | – |
| `mcq` | multiple choice, Ja/Nej, Sant/Falskt | `options[]`, `answer` (0-based index) | yes |
| `select` | matching (people↔ads, headings↔radio items, synonym sentences) | `answer`; `options` on the item or the part | yes |
| `gap` | fill one word | `q` with exactly one `___`, `answers[]` (all accepted), optional `base` (shown in brackets) | yes, exact (case/punctuation ignored) |
| `order` | word order | `words[]` (shuffled), `answers[]` (accepted sentences, same words) | yes |
| `short` | 1–5 word written answer (Swedex listening del 2–3) | `answers[]` = key phrases; correct if the answer contains one | yes, grader re-checks wrong ones |
| `write` | free writing (typed, or photo upload of handwriting) | `q`, `bullets[]`, `minWords`, `maxWords` | no → grader |
| `speak` | recorded speech | `q`, `bullets[]`, `maxSeconds`, optional `audio` (examiner question played first) | no → grader |

Examples:
```json
{"id":"i1","type":"info","md":"**Regel:** verbet står på plats 2.\n\n| 1 | 2 (verb) | 3 |\n|---|---|---|\n| Igår | gick | jag |"}
{"id":"q1","type":"mcq","tags":["läs.detalj"],"q":"Var bor Anna?","options":["I Lund","I Malmö"],"answer":0}
{"id":"q2","type":"select","tags":["läs.matcha"],"q":"Lisa vill lära sig laga mat.","answer":2}
{"id":"q3","type":"gap","tags":["verb.preteritum"],"q":"Igår ___ jag ett brev.","base":"skriva","answers":["skrev"]}
{"id":"q4","type":"order","tags":["ordföljd.bisats"],"words":["att","han","inte","kommer","Jag","vet"],"answers":["Jag vet att han inte kommer"]}
{"id":"q5","type":"short","tags":["hör.detalj"],"q":"Vad ska Eva köpa?","answers":["mjölk"]}
{"id":"q6","type":"speak","tags":["tal.interaktion"],"q":"Svara på frågan.","maxSeconds":120,
 "audio":{"id":"t6","maxPlays":2,"speakers":{"Examinator":"m"},"script":[{"speaker":"Examinator","text":"Vad gör du på fritiden?"}]}}
```

### Images (required – every lesson needs them)

Text-only lessons are boring. Every lesson needs images; aim for one per section (validator fails
with zero). Put `image` on a part, on any item, or on an `info` item (shown above it):
```json
"image": { "src": "train.svg",          // file in images/<lessonId>/, or an https:// URL
  "alt": "Ett tåg lämnar perrongen",      // required, Swedish
  "caption": "Tåget har gått.",          // optional, shown under the image
  "credit": "Foto: X, CC BY-SA 4.0, Wikimedia Commons",  // required for downloaded photos
  "size": "small" }                      // optional: small | wide
```
Two sources:
1. **Hand-drawn SVG** (preferred for rules and scenes): simple flat illustrations that *teach* –
   a timeline for verb tenses, a battery for svag–svagare–svagast, a scene for a dialogue, labels in
   Swedish. Use a white background rect (the app shows images on white in dark mode too), viewBox
   ~ 600×300, system-ui font, readable text ≥ 16px. Check the SVG renders (valid XML).
2. **Free photos** (for real-life context: Swedish places, signs, documents): download from Wikimedia
   Commons (CC0 / CC BY / CC BY-SA) into `images/<lessonId>/`, keep it < 300 KB, and fill `credit`.
   Never hotlink random sites.

The picture must relate to the content. Use **both kinds**:
- **Rule images**: tables, timelines, charts that explain the grammar (text in a picture is fine).
- **Concept pictures**: what a word or idea looks like (sunrise for *i morse*, calendar for *i fredags*,
  big/small house for *stor/liten*). They create memory links. Add one for every key word or concept that
  can be drawn – not only rules.

### Audio

Two kinds. **Prefer real audio** for listening tasks; use TTS for dialogues you need to control.

**1. Real audio (native speakers)** – a private file under `materials/` (gitignored, served at `/materials/…`):
```json
"audio": { "id": "k1", "title": "…", "maxPlays": 2,
  "source": "materials/sr/klartext/<slug>.m4a",          // or materials/nok/audio/<file>.mp3
  "credit": "Klartext, Sveriges Radio (P4 …). Automatisk transkription – kan ha små fel.",
  "transcript": "full text, shown after submit" }      // or "script": [...] if you have speaker turns
```
Sources:
- **SR Klartext** (easy news, real reporters + real interviewees with dialect): `python3 -I tools/fetch_klartext.py`
  → `materials/sr/klartext/<slug>.m4a` + `index.json` (headline, short text, length). ~1–3 min each.
  Fits Swedex Hör del 2 (details, 1–5 words) and Hör del 4 (match radio items to headlines, 2 extra).
- **Rivstart B1/B2 tracks**: `materials/nok/audio/` (+ `audio_index.json`); transcripts in
  `materials/nok/docs/Horforstaelsetexter…pdf` (only some tracks). Use chapters 7–10 (not yet done in class).
- **Swedex model test** (`materials/swedex-a2b1/`): keep for a full mock exam. Don't spend it on practice.

Transcribe: `.venv/bin/python tools/transcribe.py --save <file>` (local Whisper "turbo"; writes `<file>.txt`).
Read the transcript, fix obvious ASR errors, and build questions only on parts you are sure of.
The file is not in git, so the lesson only works on a machine that has `materials/`.

**2. TTS dialogue** (edge-tts) – file = `audio/<lessonId>/<id>.m4a`, built by `build_audio.py`:
```json
"audio": { "id": "a1", "title": "…", "maxPlays": 2,
  "speakers": {"Sara": "f", "Johan": "m",
               "Pelle": {"voice": "m", "pitch": "-8Hz", "rate": "+8%"}},  // 3rd person: same voice, other pitch
  "rate": "+0%",                    // default for all speakers
  "gap": 0.45,                      // pause in seconds between speaker turns (0.25 within a turn)
  "script": [{"speaker": "Sara", "text": "...", "pause": 1.0}] }    // pause = silence before this line
```
Only two Swedish voices exist (Sofie f, Mattias m); vary `pitch`/`rate` for extra people.

**Make TTS scripts sound like B1 speech, not a textbook:**
- **Length:** 120–250 words, 1–2.5 min. Not 6 short lines.
- **Spoken Swedish:** *ja, nä, mm, alltså, liksom, ju, väl, ba, typ, sen, nåt, nån, dom*; short answers
  (*Ja, absolut. Nä, tyvärr.*); interruptions and restarts (*Vi kan … eller nej, vänta.*); hesitation with "…".
- **Distractors the B1 way:** the speaker changes plans or corrects a number (*på tisdag – nej förresten,
  onsdag*), mentions two times/prices/places and only one is the answer, says what is NOT the case.
- **Paraphrase:** the question uses other words than the audio (*utan jobb* ↔ *arbetslös*). No word-matching.
- **Implied info:** some answers need a small conclusion (attitude, reason, who decides).
- Normal speed (`rate` +0% or faster). No slow, over-clear reading.
- TTS traps: *Mm* is read as "millimeter", *Wow* sounds odd – use *Jaha*, *Aha*, *Oj*. Write years/numbers as
  words (*nittonhundrafyrtiosju*) to control how they are said. Check new audio with `tools/transcribe.py`.
Write numbers the way they are said ("kvart över två", "tusen femtio kronor").
Without the file, the browser reads the script aloud (worse quality).

### Exam mode (tests)

`"mode": "exam"` (or no mode) opens the separate exam screen: dark exam header, countdown, section tabs,
question navigator with ⚑ flags, no hints/English/explanations until submit, level verdict on the result page.
Lesson-level fields for exams:
```json
"mode": "exam", "timeLimit": 32,               // minutes, countdown (overtime is allowed but recorded)
"scoring": {"max": 16, "A2": 9, "B1": 12},     // thresholds scaled from Swedex (reading 30/17/22, listening 30/14/22)
"numberStart": 17                               // first question number, to match the real test's numbering
```
Parts with a `passage` are shown side by side (text left, questions right) on wide screens, in both modes.
Write `(1)`, `(2)` … in a passage to get numbered sentence markers (Läs del 4).
`"mode": "practice"` = learning screen: instant feedback on mcq/select, Enter checks gaps, live first-try score.

## Tags (taxonomy)

Use existing tags when possible. New tags follow `area.sub`. Tags drive `progress/tag-stats.md`.

- Reading: `läs.detalj`, `läs.huvudtanke`, `läs.slutsats`, `läs.matcha`, `läs.synonym`, `läs.janej`
- Listening: `hör.detalj`, `hör.huvudtanke`, `hör.tid`, `hör.siffror`, `hör.åsikt`, `hör.matcha`, `hör.kortsvar`
- Word order: `ordföljd.inversion`, `ordföljd.bisats`, `ordföljd.fråga`
- Verbs: `verb.preteritum`, `verb.supinum`, `verb.presens`, `verb.passiv`, `verb.reflexiv`, `verb.partikel`, `verb.modal`, `verb.futurum`
- Nouns/adjectives: `substantiv.plural`, `substantiv.bestämd`, `substantiv.en-ett`, `adjektiv.ett-ord`, `adjektiv.plural`, `adjektiv.bestämd`, `adjektiv.komparation`, `adjektiv.adverb`
- Small words: `preposition`, `preposition.tid`, `preposition.plats`, `pronomen.sin`, `pronomen.objekt`, `bisats.om-att`, `konjunktion`
- Vocabulary: `ord.synonym`, `ord.kollokation`, `ord.förväxling`, `ord.tema.<topic>` (e.g. `ord.tema.boende`)
- Writing: `skriv.mejl.svar`, `skriv.mejl.formell`, `skriv.kalender`, `skriv.insändare`
- Speaking: `tal.läsa-högt`, `tal.berätta`, `tal.argumentera`, `tal.interaktion`, `tal.annons`

## Exam we prepare for

**Main: SFI D national test (old format).** Format and priorities: `progress/plan.md`. SFI D shapes:
- Reading: ads (find info), purpose of an sms, read a chart/table, match interview questions ↔ answers,
  who a text is written for, "who thinks what" in chat/forum posts, one longer article with MCQ.
- Listening: interviews, conversations, news – `mcq`.
- Writing: informal letter/email to a friend; formal opinion text (e.g. reply to an insändare).
- Speaking: solo "Berätta och ge råd" (3–4 min, `maxSeconds` 240); pair discussion from a mind map where the
  partner (TTS voice, item `audio`) gives views and the learner must react, argue and agree.
SFI D is pass/fail: in `scoring` use `{"max": n, "G": ~60–65% of n}` (no official per-item cut-offs;
the app shows A2/B1 only when those keys exist).

**Backup: Swedex A2B1** (2026-12-04). Shapes to mirror:
- Reading: Ja/Nej on letters/fact texts (`mcq` with ["Ja","Nej"]), people↔ads (`select` + part `options`),
  insändare MCQ, fact text ↔ synonymous sentences (`select`).
- Listening (played twice): messages MCQ, radio/messages and dialogue answered in 1–5 words (`short`),
  radio items ↔ headings with 2 extra headings (`select`), interviews Sant/Falskt (`mcq`).
- Writing: answer the questions in an email; tell what you did / do / will do from calendar notes.
- Speaking (examiner): general questions; ask each other questions about an ad; discuss a topic.

## Pedagogy rules (follow these)

1. **Short and focused:** 10–15 minutes (a narrow skill drill like numbers or one word: **5–8 min**, ~8–10 items), **one topic per lesson** (one verb family, one rule, one
   exam task). About 10–16 items. If a word question touches two topics, make two lessons.
1c. **Speaking time:** `maxSeconds` = at least 120, and 60 + 30 per bullet (5 bullets → 210). The learner
   likes to add extra sentences – never cut them off.
1b. **Media in every lesson:** images (see Images) and, where it fits, a short audio dialogue.
2. **Target the data:** read `progress/tag-stats.md` + the latest feedback. ~70% of items on the weakest
   tags, ~30% review of strong areas. Aim for 60–70% correct.
3. **Patterns, not lists.** The learner (Persian L1, English fluent) hates rote memorization and finds
   Swedish "categorical". Start practice lessons with an `info` item showing the pattern/group
   (e.g. strong-verb vowel patterns i–e–i: skriva–skrev–skrivit), a memory hook, and when useful a
   Persian/English comparison. Then practise in context sentences, not isolated words.
4. **Reuse errors:** recycle the exact words the learner got wrong (see tag-stats examples) in new contexts.
5. **Level:** B1 texts, everyday topics (boende, arbete, vård, skola, fritid, resor, samhälle). Natural,
   correct Swedish. Double-check every answer key — a wrong key destroys trust.
6. **English hints** (`qEn`, `explainEn`) on new or hard items; fewer over time.
7. Distractors must be plausible but clearly wrong for someone who understands.
8. For `gap`, list every acceptable answer in `answers[]`.
9. Vary the position of the correct option in `mcq` (the UI does not shuffle). The validator rejects lessons where most answers sit at the same index.

## Grading workflow (results → feedback)

1. `python3 tools/report.py results/<file>.json` (or a draft) to see answers.
2. If a `write` item has `images` (photos of handwriting in `uploads/`), open each image with the Read tool,
   transcribe it exactly (keep the learner's errors) into the feedback, then grade. Note handwriting
   problems that could cost points (unclear å/ä/ö, word boundaries).
   Grade `write` with the Swedex criteria: task fulfilment/content, communicative form (greeting,
   register, coherence, linking words), formal correctness (grammar, spelling, word order). Grade
   `speak` transcripts on production/interaction, vocabulary, correctness; pronunciation can't be
   judged from a transcript (Chrome speech recognition may mishear — don't punish odd single words).
   Give an estimated CEFR level (A1/A2/B1/B2) per part.
3. Write `feedback/<same basename as the results file>.md` (this is what the learner sees):
   - Score table, per part, with an estimated level.
   - What went well (short).
   - Top 3 problems: each with the pattern/rule, 2–3 examples, and a memory hook. Persian note if it helps.
   - For writing: the learner's text corrected, with changes **bold**.
   - Simple English, short sentences, no fluff.
4. Run `python3 tools/report.py` (regenerates tag-stats).
5. Update `progress/learner-profile.md` (skill table), append to `progress/log.md` (with "Next step").
6. Commit and push.
