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

## 2026-11-11 (later)
- Built local lesson generator: `tools/generate.py` (Ollama, gemma3:12b) + panel at the bottom of the home
  page (`POST /api/generate`, job polling, badge "Lokal modell · inte granskad av Claude").
- Quality after several harness fixes: grammar drills mostly correct; theme lessons weaker (off-topic
  mcq, unnatural lines). Last fixes (mcq gets the dialogue, keep dialogue lines if fix fails) are NOT yet
  verified – a test-mode job ("s-passiv i presens och preteritum") was running when we stopped.
- Next step: check that test-mode lesson (lessons/*-gen-*), review it; if bad, delete it and keep
  tuning. Then grade 004–006 when results arrive.

## 2026-11-11 (evening)
- Learner asked for a lesson on important daily verbs and one on daily adjectives. Built (via lesson-author
  agents, reviewed by Claude): `008-vardagsverb` (verb groups -ade/-te/strong, äta/se/gå/förstå/säga +
  ta/komma/göra/veta, titta vs se, chunks, dialogue, speaking) and `009-vardagsadjektiv` (en/ett/plural
  forms, irregulars liten/gammal/ny, opposite pairs, comparison bra–bättre–bäst etc., flat dialogue,
  speaking). Fixed: a listening question not supported by the dialogue, an image that gave away answers.
- 007-gen-s-passiv-nu-och-da (local model, test mode) is still uncommitted and unreviewed.
- Next step: review 007-gen; grade 003–009 when results arrive.
- Reviewed + deleted 007-gen-s-passiv-nu-och-da (local model, test mode): 5/9 items bad – contradictory
  context (q1), two valid answers (q2, q3 presens/preteritum; q6 two correct options), truncated question
  (q5 "Vad betyder"). Generator TODO: ambiguity check (ask reviewer "can another form also fit?"), reject
  questions shorter than ~4 words / ending without ?/./___, mcq "only one correct" check by filling each
  option into a sentence-type question.

## 2026-11-11 (night)
- Graded 003 (26/26 final, first try: strong verbs 3/10, vocab 7/8), 004 (9/9 + speaking A2+), 008 (15/19
  + speaking A2+). Feedback files written. Speaking recordings were both cut at 60 s → all speak items now
  maxSeconds ≥120 (60 + 30/bullet); rule in AUTHORING + decisions.
- Tried local Whisper (KBLab/kb-whisper-small via faster-whisper, tools/transcribe.py): huggingface.co is
  blocked on this network (connection reset) → still grading from Chrome transcripts.
- Next step: lesson 011 on signal word → verb form (har + supinum, igår + preteritum, nu + presens,
  group 2 -er) + också/inte placement + speaking with "i måndags hade jag". Then 005/006/009/010 when done.

## 2026-11-13
- Learner: listenings feel below B1 / not native. Added real-audio support: `audio.source` (file under
  materials/, served at /materials/), `transcript` + `credit` shown after submit. `tools/fetch_klartext.py`
  (56 SR Klartext clips downloaded), `tools/transcribe.py` switched to openai-whisper turbo (works offline).
  build_audio.py: per-line rendering, trimmed silence, pauses between turns, speaker pitch/rate, default rate +0%.
  AUTHORING + lesson-author agent: "prefer real audio" + B1 TTS script rules.
- Built `012-radio-klartext`: 4 real Klartext clips (snow warning, hacker attack on shop freezers, chocolate
  fight, blind masseur) → Swedex Hör del 4 headline matching (2 extra, near-miss traps) + 1–5 word details
  + retell (speak).
- 011 draft in results/drafts (learner started 011).
- Next step: learner finishes 011, then takes 012. Grade both. Next listening lesson: a Rivstart ch. 7 dialogue
  track, or a B1-style TTS dialogue with plan changes. Mock exam with the Swedex model test in late November.

## 2026-11-13 (evening)
- Graded 011 (final 14/15; first-try gaps 5/9; listening 3/3; speaking A2+, improved: också after verb, har+supinum correct). Whisper transcript used for speaking. Feedback written.
- Next step: lesson on telling a past story (preteritum chain, sedan/då, i/för/sedan with time, i måndags) + speed gaps on signal words. Then grade 012, 009.

## 2026-11-13 (night)
- Graded 009 (auto 16/18: former 6/6, motsatser 4/4, jämförelse 4/5, lyssna 2/3; first-try gaps weak on ett-ord/plural endings). Speaking A2 (Whisper transcript; end unclear). Feedback written.
- Next step: adjective agreement lesson (en/ett/plural, hem/rum/hus as ett-ord, learn noun + article, den/det + adjektiv-a) + irregular comparison (sämre, större, äldre, bäst). Then grade 012, plus a past-story lesson from the previous plan.

## 2026-11-13 (later)
- Graded 011 (14/15, speaking A2+) and 009 (16/18, speaking A2; adjective agreement + irregular comparison weak).
- Built 013-adjektiv-kongruens (lesson-author, reviewed: keys OK, fixed info claim + h2 answers).
- Learner asked for listening practice on numbers/years (1947, 1448, 1884). Built 014-artal-och-tal: year pattern
  (19|hundra|47), -ton vs -tio pairs (17/70, 14/40, 18/80), 6 "which number" mcq, 8 year dictations, B1 TTS
  interview with a self-corrected year (1971 → 72), speak: own timeline. Audio verified with Whisper.
- Found: edge-tts reads "Mm" as "millimeter" → rule in AUTHORING; fixed 013 audio. build_audio retries on TTS errors.
- Next step: learner takes 012, 013, 014. Then the past-story lesson (preteritum chain, i måndags, i/för … sedan).

## 2026-11-13 (night 2)
- Graded 013 (boende 7/12, jämförelse 6/6 but 1/6 first try, lyssna 5/7; speaking A2, Whisper). Feedback written. g9 'Men det' acceptable.
- Vs 009: adjective endings and irregular comparison NOT yet automatic; listening förra/nu trap repeated.
- Next step: short drill on adjective after mitt/den/det (-a) + comparison pairs, with förra/nuvarande listening; then grade 012 and 014; then past-story lesson.

## 2026-11-13 (night)
- Graded 013 (19/25; agreement errors repeat; learner says en/ett = memory problem) → built 015-en-eller-ett.
- Learner asked for exam-like reading + a richer UI. Built 016-las-prov-a (Läs del 1 Ja/Nej ×10 + del 2 ads ×6,
  32 min, B1 ≥ 12/16) and 017-las-prov-b (del 3 insändare ×6 + del 4 synonym sentences ×8, 28 min, B1 ≥ 10/14),
  reviewed keys. New UI: dashboard, exam view, learning view (see CLAUDE.md / AUTHORING "Exam mode").
- Next step: learner takes 012, 014, 015, 016, 017. Then grade; past-story lesson; listening test in exam view.

## 2026-11-13 (late)
- Goal switched to SFI D (old national test); no time-based planning (react to efforts).
- Built 018-sfi-d-lasa (SFI D reading test: ads, sms purpose, chart, who-thinks-what, interview matching,
  addressee; 16 items, 25 min, G ≥ 10) and 019-asiktstext (formal opinion text: skeleton, linking words +
  word order, model answer, write a reply to "Förbjud fyrverkerier!"). Both reviewed.
- Next step: grade whatever the learner does (012, 014–019). Then SFI D speaking: "berätta och ge råd" +
  pair discussion with a TTS partner.

## 2026-11-15
- Learner wants reading practice on the phone (train). Built `reading/tagslasning-1.html`: one self-contained
  page, 3 texts on Rivstart themes (ch. 6 socker – faktatext Ja/Nej + MCQ; ch. 1/7 allemansrätten – insändare
  MCQ; ch. 5 helgen – forum "vem tycker vad"), self-check with explanations, a copyable result summary to paste
  into chat. Artifact publishing unavailable (API-token session) → file sent to the phone manually.
- Next step: when the learner pastes the result, log the errors in the learner model.

## 2026-11-15 – Full-length reading for the phone
- Learner: phone reading too short → wants real exam length.
- New `tools/phone_reading.py` + `reading/_template.html`: lesson JSON → standalone phone page (timer, check per part, copyable result).
- Exported: `reading/swedex-lasprov-helt.html` (016+017, 30 q, 60 min), `reading/sfi-d-lasprov.html` (018), `reading/taglasning-2.html` (new 021, full Swedex reading on Rivstart themes: friluftsliv, träning/kurser, husdjur, vardagen 1960–idag).
- 021 reviewed: fixed grammar in del 4 sentence 30, two explanations.
- Next: grade whatever the learner pastes/finishes. Then SFI D speaking lesson (berätta + ge råd, pair discussion).

## 2026-11-15 – Graded 016 (läsprov A)
- 15/16 → B1 (threshold 12). 11 min of 32. Del 2 annonser 6/6. Only miss j5: contrast after *men*.
- Pattern: misses come from contrast words (men/däremot), also seen in 001 listening. Tag `läs.kontrast`.
- App change same day: select items now buttons (no dropdowns). Learner asked about classic radio circles; waiting for their answer.
- Next: 017 (del 3+4) or Tågläsning 2. Add contrast-word traps in next listening/reading lesson.

## 2026-11-15 – Graded 017 (läsprov B)
- 9/14 (A2 on its own; B1 needs 10). 016+017 = 24/30 → B1 on a full Swedex reading test.
- Del 4: 3 misses all '0' where text says the same with other words. Del 3: 'det kan stämma, men' trap again.
- Fixed 017 i4 explanation (it contradicted the key).
- Learner: A/B/C cards are fine (no radio circles).
- Next: lesson 022 – paraphrase/synonyms (del 4 shape) + contrast words (men, däremot, fast, det kan stämma men).

## 2026-11-15 – Lesson 022 ready
- 022-samma-sak-andra-ord (12 min): del-4 strategy card + paraphrase pairs, 7 paraphrase mcq, mini del 4 (Sopsortering, 6 items), 5 contrast traps (men/däremot/fast/det kan stämma men).
- Reviewed: fixed passage grammar, Persian line, moved contrast texts into passages. App now shows `mdEn` on info cards.
- Next: grade 022. Then Tågläsning 2 / SFI D speaking lesson.

## 2026-11-16 – Long reading from Rivstart themes
- Learner sent photos of Rivstart readings. Built two exam-mode tests in own words (repo is public):
  - 023-langlasning-fritid-djur (22 q, 30 min): long article "Fritid förr och nu" (SFI D long text, MCQ,
    one chart item) + fact text on huggorm/geting/fästing (del 4 paraphrase + Ja/Nej with däremot/ändå traps).
  - 024-langlasning-samhalle-konst (23 q, 30 min): "Så styrs Sverige" Ja/Nej (rösträtt, 4 %, talman,
    myndigheter, region/kommun) + three portraits Thiel/Jansson/af Klint, A/B/C matching.
- Phone page: reading/langlasning-rivstart.html (both tests, 45 q, 60 min).
- Next: grade 022/023/024 when done. Then SFI D speaking lesson (berätta + ge råd, pair discussion).

## 2026-11-16 – Exam-like listening
- Friend's Swedex report (docs/research.md): listening hardest – played twice back to back, noise.
- App: exam-mode audio plays maxPlays times in a row on one click. build_audio.py: `noise` low/medium/high.
- Next: lesson 025 = full Swedex hörprov (5 parts, exam conditions, some noisy recordings).

## 2026-11-16 – Scene sounds + two plays in a row everywhere
- Learner: noise = scene sounds (car, vacuum …), apply to all listening. Added 8 real scene sounds
  (sounds/, Wikimedia Commons, credits in sounds/CREDITS.md); `noise: {sound, level}` in build_audio.py.
- All listening audio (practice + exam) now plays maxPlays times in a row on one click; speaking-task
  examiner prompts opt out (`strict: false`).
- Scene sounds added to 10 old dialogues (001 a2, 005, 006, 008, 009, 010, 011, 013, 014 morfar, 020);
  001 voicemail + news stay clean; 014 number drills clean. Audio rebuilt.

## 2026-11-16 – Lesson 025: full Swedex hörprov (exam mode)
- 30 items like the model test: del 1 six messages (mcq), del 2 six short (2 TTS + 1 Klartext Musikhjälpen), del 3 one dialogue (6 short, 237 words), del 4 four real Klartext clips (posttåg, kamel, julvärd, assistanshund) ↔ 6 headings, del 5 two interviews (8 Sant/Falskt). timeLimit 35, A2 14 / B1 22.
- Scene sounds: m2 train .35, m6 car .3, a1 traffic .5, d1 cafe .35, i2 cafe .45. Whisper check: all answers audible. Fast/low-pitched speakers: Martin, Daniel, Karin, Mikael.
- Traps: corrections (tisdag–onsdag, torsdag not onsdag, hundrafemtio–femtio, tre–fyra), förra/nu (hyra, barnavdelning, förra året), 'det kan stämma, men'.
- Next: learner takes 025 once without pausing; grade, check which parts fail (noise vs. numbers vs. corrections).

## 2026-11-17 – Graded 025 (hörprov Swedex)
- 24/30 → B1 (threshold 22), 31 of 35 min, under test conditions (two plays in a row, scene noise).
  Accepted q18 'önsdag'; q12 spelling not accepted. Del 4 real radio 4/4, del 3 dialogue 6/6.
- Misses: 'fast' contrast (3rd test in a row with men/fast trap), wrong kind of answer for 'var' (building/programme
  name instead of place), time 14 taken for platform, 'när jag gick i pension' ≠ before. Spelling of short answers.
- Reading B1 (24/30) + listening B1 (24/30) → Swedex B1 receptive skills look safe.
- Next: writing in Swedex shape (email ~50 words answering questions + ~100 words calendar email). Then speaking.

## 2026-11-17 – Lesson 026: Swedex skrivprov (exam mode)
- 026-skriv-swedex (60 min, 2 write items, no scoring; Claude grades). Del 1: Nina's email, 3 questions (describe area, which day, food) + own question back, 40–80 words. Del 2: calendar tis–lör, today = torsdag, mail to moster Lena, 90–140 words: i förrgår/i går (preteritum), i morse + nu (past vs presens), i morgon/på lördag (ska/presens), say what you thought.
- Next: grade 026 with Swedex criteria (content, form, correctness); watch signal word → verb form, inversion after time words, -s forms.
- Reviewed 026: removed the signal words and grammar summary from the calendar (the real test gives only dates),
  added Monday 7 Dec → forces *i måndags*. Today = torsdag 10 dec, after lunch (interview = i morse, städa = nu).

## 2026-11-18 – Human voices: real clips now, Chatterbox TTS next
- Learner: TTS voices sound like machines; wants human voices (personalities, accents) or real audio cut into parts.
- edge-tts has only 3 Swedish voices. Work Gemini gateway has no TTS (404). Plan: Chatterbox multilingual (local,
  Swedish, voice cloning from ~10 s reference). huggingface.co is blocked on this network → learner downloads the
  weights elsewhere with tools/download/chatterbox.sh (Pi) / .ps1 (Windows) and copies them to models/chatterbox/.
  Reference voices: LibriVox Swedish readers (public domain) in materials/voices/librivox/ (private). Never clone
  SR speakers (repo is public, audio/ is committed). .venv-tts (python 3.11) has chatterbox-tts installed.
- New: audio `clip: [start, end]` → build_audio.py cuts real audio to materials/clips/<lesson>/<id>.m4a.
  transcribe.py --timestamps.
- Lesson 027-riktiga-roster: 8 real interview clips (Skåne, Värmland, fast Stockholm, foreign accent, one-word
  answers), 17 q. Unused but transcribed: gordon/karin café, emily golf, daniel MFF, elpris expert (next lesson).
- Next: when models/chatterbox/ exists: test Swedish quality with LibriVox refs, send samples, add engine to
  build_audio.py (speaker → reference voice), rebuild dialogue audio. Grade 026/027 when done.
