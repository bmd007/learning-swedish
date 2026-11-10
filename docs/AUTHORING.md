# Authoring guide (for any AI or human)

You can create lessons, grade results, and write reports **without touching code**. The server
(`server.py`) and the UI (`web/`) are a generic player. All content is data:

| What | Where | Who writes it |
|---|---|---|
| Lessons / tests | `lessons/NNN-slug.json` | lesson author |
| Listening audio | `audio/<lessonId>/<audioId>.m4a` | `tools/build_audio.py` (from the lesson JSON) |
| Learner answers | `results/*.json` (final), `results/drafts/*.json` (unfinished, saved after every answer) | the app |
| Voice recordings | `recordings/` (gitignored) | the app |
| Photos of handwritten answers | `uploads/` (gitignored; HEIC auto-converted to JPG) | the app (`write` items) |
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
{"id":"q6","type":"speak","tags":["tal.interaktion"],"q":"Svara på frågan.","maxSeconds":45,
 "audio":{"id":"t6","maxPlays":2,"speakers":{"Examinator":"m"},"script":[{"speaker":"Examinator","text":"Vad gör du på fritiden?"}]}}
```

### Audio

```json
"audio": { "id": "a1",                 // unique in lesson; file = audio/<lessonId>/a1.m4a
  "title": "shown in the transcript after submit",
  "maxPlays": 2,                       // Swedex plays everything twice
  "speakers": {"Sara": "f", "Johan": "m"},   // f = sv-SE-SofieNeural, m = sv-SE-MattiasNeural
  "rate": "-5%",                       // optional, edge-tts rate
  "script": [{"speaker": "Sara", "text": "..."}] }
```
Write numbers the way they are said ("kvart över två", "tusen femtio kronor"). After writing a
lesson, run `build_audio.py`. Without the file, the browser reads the script aloud (worse quality).
Only two voices exist, so dialogues have at most one woman and one man.

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

Swedex A2B1, 2026-12-04. Format and timeline: `progress/plan.md`. Shapes to mirror:
- Reading: Ja/Nej on letters/fact texts (`mcq` with ["Ja","Nej"]), people↔ads (`select` + part `options`),
  insändare MCQ, fact text ↔ synonymous sentences (`select`).
- Listening (played twice): messages MCQ, radio/messages and dialogue answered in 1–5 words (`short`),
  radio items ↔ headings with 2 extra headings (`select`), interviews Sant/Falskt (`mcq`).
- Writing: answer the questions in an email; tell what you did / do / will do from calendar notes.
- Speaking (examiner): general questions; ask each other questions about an ad; discuss a topic.

## Pedagogy rules (follow these)

1. **Short:** 10–15 minutes per lesson. The learner's time is unpredictable.
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
