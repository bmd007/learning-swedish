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
