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

## 2026-11-18 – Graded 021 (full Rivstart reading test)
- 26/30 → B1 (del1 9/10, del2 6/6, del3 6/6, del4 5/8), 32 min. No short items.
- Misses: del 4 synonyms again (3x chose '0'), mil vs kilometer in l10.
- Next step: short del 4 drill (synonyms + units mil/km); then grade 026 writing and 027 listening when done.

## 2026-11-19 – Voices, highlighter, old official B1 hörprov
- Human voices: build_audio.py --chatterbox → materials/tts/ (private, app prefers it). Cast tools/voice_cast.json:
  LibriVox (4★ Anna Sofia, Cecilia2), NOK actors (7, private), NST (38 speakers 19–77, 10 regions), child = pitched ref.
  Done: 001 002 005 006 008 009 011 013 020; 010 two lines redone (TTS_TAKE=2); 014 + 025 building.
  Check with tools/check_tts.py (Whisper WER), fix lines with tools/redo_tts_line.py.
- Highlighter in exams + lessons (select → yellow, click removes, saved per attempt). Learner asked for it.
- Learner: attention tools only as practice lessons; tests stay exam-like (decisions.md).
- Research Swedex (docs/research.md 2026-11-18): old official B1/A2 tests downloaded to materials/swedex-old/.
- Private lessons in materials/lessons/. 028-swedex-b1-gammalt-horprov: real old B1 listening test, 26 items, 40 min,
  real picture options, q2 = draw the route on the real map (new `draw` item, graded by Claude). B1 ≈ 17 (no official mark).
- Exam booked: Swedex A2B1 Göteborg 2026-12-04.
- Next: learner takes 026 (writing) and 028; grade. Then Swedex oral practice from the old oral material
  (materials/swedex-old/swedex_b1_munt_*), then a short del 4 paraphrase lesson (key-word step, practice only).

## 2026-11-19 – Lessons 029–035: Modellsvar Swedex muntligt
- Learner asked for short lessons (≤ 5 min) with real-test-like speaking questions + good model answers to listen to,
  with good voices. 7 lessons: 029 presentation, 030 vardag, 031 annons svara, 032 annons fråga, 033 ämne bo,
  034 ämne mobilen, 035 ämne resor. Each: 2 model exchanges (Testledare = annasofia, candidates from the pool),
  technique items, "Fraser att låna", "Nu du" speak item (graded by Claude).
- Human voices built and Whisper-checked: all 21 files 0–4 % off.
- Next: grade 026 / 028 / "Nu du" recordings when the learner does them. Real speaking practice (learner speaks
  more) after the model-answer series.

## 2026-11-19 – Graded 002 writing (handwritten)
- Task 1 (reply to Maria): A2, all 4 content points, ~128 words, name Maja (wrong), MVH to friend, many noun/infinitive/spelling errors but understandable. Likely pass.
- Task 2 (week email): A2, 3 points, tenses right per section (improved), but NO greeting/closing and ~164 words (max 120) -> at risk of failing kommunikativ utformning.
- Top 3: letter frame + word limit; noun forms (min + noun, plural, en/ett); verb after modal-like verbs (no *att*, infinitive) + time-word errors.
- Feedback: feedback/002-skriva-tala__20261119-175433.md
- Next step: short writing practice (exam 50/100 words) with a frame checklist (Hej name ... Kram), word count, noun endings + "ska/behöver inte + infinitive" gap drill; then another handwritten email under time (exam 2026-12-04).

## 2026-11-20 – Collocation lessons 039–042

- Learner asked for small lessons on which adjectives go with which nouns (daily talk + speaking test).
- 039 människor, 040 väder/mat, 041 hem/jobb/stan, 042 åsikter (del 3 words). Each: 10 choose-the-word (English-trap
  distractors), 6 gap forms, TTS dialogue + 3 listening items, table sv/en/fa, Swedex-style speak item.
- Audio: edge + Chatterbox, Whisper check 0–2 %. Tags: ordförråd.kollokation, adjektiv.kongruens.
- Next: grade whatever the learner does (026, 028, 036, 037, 039–042 speak items).

## 2026-11-20 – Graded 039 (collocations: people)

- 18/19 auto, listening 3/3 first play, forms 5/6 (*hjälpsama*). Del 1 slow (10 min), 5 first-try misses on -sam/-ig vs -ande/English-built words.
- Speak 112 s, A2/B1: good adjectives (ärlig, trevlig, pigg och glad); *Vi ofta spelar*, *riktig ärlig*. Whisper used (browser transcript broken).
- Next: 040–042 and 043 (vocab check). Keep an eye on V2 + adverb (ofta/alltid/inte) in speech.

## 2026-11-20 – Graded 040 (collocations: weather/food)

- 18/19 auto in 8 min, 2 first-try misses (039: 5). *mätt* for *mätta*. Dialogue never played.
- Speak 92 s, A2/B1: used stark/mild mat, hård vind, klar himmel; *i Uppsala man kan*, *kraftig regn*; didn't compare countries.
- Watch: inversion in free speech, answer the exact speaking task, plural predicative -a.

## 2026-11-20 – Graded 029 (model answers: presentation)

- 2/4 auto (m1 missed "ask back"; *vinnade*). Speak 132 s, A2/B1: all bullets + asked back. Errors: för…sedan vs i,
  *en små lägenheten*, *lärade mig*, inversion without subject, *mor tung* (modersmål).
- Next idea: a short lesson on time phrases (i / för … sedan / på / om) + strong verbs in speech.

## 2026-11-21 – Fixed 014 sound, graded 014 (years)

- App bug: item-level audio only had a player for speak items → 014 drills were silent. Fixed in renderItem.
- 014: 10/13. Diktat 2/5 – last two digits of years (-tio/-ton, tens first). Interview 4/4.
- 043 (vocab check) has a draft in progress – grade when handed in. Next: number warm-ups in listening lessons.

## 2026-11-22 – Graded 030 (model answers: vardag)

- 4/4 listening/phrases. Speak 137 s, A2: good day structure + asked back, but only 2/5 bullets (no past/future weekend).
  min/mitt/mina, *sedan jag börjar*, *brukar äta jag*. Whisper hallucinated – graded from browser transcript.
- Pattern: speaking tasks not fully covered (040, 030) → next speaking lesson: a "past–now–future" frame drill.

## 2026-11-22 – Graded 041

- 17/19 auto; plural predicative *full* (2nd time). Speak 150 s A2/B1: en/ett (område, fönster), missing subject after därför.
- 043 draft: 33/36 answered, not handed in – asked the learner to finish it.

## 2026-11-22 – Lessons 044–046: adjective range

- Per learner wish (range, not precision): 16 new adjectives each – 044 personality/feelings, 045 things/places, 046 opinions.
  Word table (opposite/en/fa/example), 8 mcq, 6 opposites, TTS dialogue + 3 mcq, speak task. Audio ok (Whisper 0–2 %).

## 2026-11-22 – Graded 043 (vocab check)

- 34/36 (first try 26/36). 10 unknown words → trial lesson with video/memory cues (needs Pexels key or Commons).

## 2026-11-23 – Lessons 048–049: concrete daily words with photos

- 048 hemma/tvättstuga (21 typed items), 049 handla/betala (18). Pixabay photos (private), 2 videos (diska, betala).
  Words table + teacher voice, typed recall, Swedex-style phone message, speak task. Audio ok 0–5 %.
- materials.7z built (AES-256, hidden names, 901 MB), not committed: LFS quota + old materials.zip removal pending.
  Password is in docs/research.md comment (public!) – recommended a new password kept outside the repo.

## 2026-11-23 – Lessons 050–052: pronouns (short)

- Learner: pronoun tables feel like "random sounds"; "I can read them so I don't care about how they sound".
  → 050 objekt (mig/dig/honom…), 051 sig, 052 min/mitt/mina + er/ert/era. Anchored 1:1 to English (me/him/my…),
  pattern + chunks first, table only at the end. Typed gaps (8) + short dialogue. Audio ok 0–1 %.

## 2026-11-24 – Graded 028 (old Swedex B1 hörprov, exam mode, 39 min)

- 18/26 (~low B1; B1 ≈ 17/26, no official limit, key by Claude). Del1 2/3, del2 4/6, del3 9/12, del4 3/5 (q20 båttur accepted).
- Problems: (1) date/time answers (q16 torsdag→1935, q18 i övermorgon missing; known slow area); (2) Rätt/Fel with close wording
  (flytta/resa, stor fest/ofta fest); (3) q8/q9 matching shifted one letter; q2 map: only a scribble, no route (0).
- Note: del 3 has the same topic as new sample del 5 → the learner's del 5 result is inflated.
- q14b key unverifiable (transcript page missing in PDF); q12b key debatable.
- **Next step:** short spaced date/time listening in context (weekdays, i morgon/i övermorgon, vecka forms, "efter klockan fyra", answer the *när* question with a day), plus Rätt/Fel with close wording and route listening with arrows; check why q2 map failed (tool or time).

## 2026-11-24 – Graded 052 (min/mitt/mina, er/ert/era)

- Gaps 8/8. Listening 2/3 auto, 3/3 after check (l2 *skyras* = Shiraz, accepted). 7 min.
- Learner: TTS pronounces Persian names badly. Possessive agreement is solid in gaps.
- **Next step:** do lesson 054 (sin/sitt/sina vs hans/hennes/deras), then date/time listening review from the 028 grade.

## 2026-11-24 – Graded mock oral with Claude mobile (Prompt 1, docs/superfluent-tala-swedex.md)

- Learner did the speaking mock by voice with Claude mobile (Superfluent prompt too long). Transcript in results/speaking-with-claude-mobile/.
- Overall A2 (not yet B1): interaction good (asks back, self-corrects), Del 2 A ok (time wrong), Del 2 B weak (task unclear, needed help), Del 3 reason unclear.
- Errors: question word order (*hur man kan boka*), inversion after nu/ibland, bisats adverb, word forms (vaknar, kvällar, anmäla sig, henne, dit).
- **Next step:** lesson for Del 2 B (tips → questions, verb second, new ads, speak + model), then mock Prompt 2. Still pending: 054, 053.

## 2026-11-24 – Lesson 055: fråga om en annons (Muntligt Del 2 B)

- Built from the mock oral: hidden ad + tips box → questions. Info (how Del 2 B works, verb second, chunks), 8 typed
  tip→question, 3 mcq + 4 order (direct question vs "Jag undrar hur man bokar"), canoe-rental dialogue (4 items),
  3 speak items with hidden ads. Audio ok 0–3 %.
- **Next step:** learner does 054 → 055 → 053; grade; then mock Prompt 2 (voice, Claude mobile).

## 2026-11-24 – Graded 026 (Swedex writing, handwritten, exam mode, 35/60 min)

- Del 1 A2+/B1-, Del 2 B1-. Overall clear A2 pass, near B1. Big gain since 002: letter frame right, tense switching good, pluperfect used.
- Problems: klockan + 14.00 read as 4; inversion after därför; -de past (titta), för att, ett tåg; word choice (hämta/lämna, ta hand om). Too long again.
- **Next step:** 054 → 055 → 053 (053 covers klockan/times). Writing: next time aim at the word count and spend 5 min re-reading for en/ett, -de, verb 2nd.

## 2026-11-24 – Lesson 056: bindeord och ordföljd

- Learner asked for the connector table as a card + typed sentences. Evidence: därför + wrong order (009, 041, 026), "för hälsa på" (026).
- 2 info cards with SVG (4 groups; därför vs därför att), 4 mcq, 12 typed (gap + order; inversion with inte, bisats with inte, så, för att + infinitive). No audio.
- **Next step:** unchanged (054 → 055 → 053, then 056 as a reference/review).

## 2026-11-25 – Lesson 057: som som subjekt eller objekt

- From 026: "en jobbintervju som det började 8.30". 2 info cards (test: gör substantivet verbet? + Persian pronoun-repeat contrast; inte before verb, som can't be dropped as subject), 3 mcq, 3 order, 2 gap, 5 short (1 correction, 4 combine two sentences). No audio.
- **Next step:** unchanged (054 → 055 → 053, 056, 057 as reference/practice).

## 2026-11-25 – Lesson 059: Hörprov Swedex A2B1, provtest 3

- Full listening mock (30 items, exam mode, same shape as 025): del 1 six messages (4 options), del 2 three messages + three radio bits (short), del 3 neighbours plan a courtyard flea market (6 short), del 4 four TTS news items + 6 headlines (2 extra), del 5 four interviews, same question ("50-årsdag"), 2 Rätt/Fel each. Real-test rate of traps (a few per part, not every item). Listening weak spots only: day/time corrections, number, close-wording Rätt/Fel, var vs vad. 21 clips, NST voices from 7 regions, noise on ~9 clips.
- **Next step:** unchanged; take 058 and 059 as the final listening practice before 2026-12-04.

## 2026-11-25 – Graded 027 (riktiga röster, Klartext) from draft (not submitted)

- Final 15/17, first try 10/16 (~65 %). Misses: q1 answered a heard word (*dusch*) not the asked thing (*ha på sig* → mössa); q4 *varsin* (apart). Numbers right only on 2nd try (q6).
- Note: a 054 draft in results/drafts/ (step 3, 0 answers, 2026-11-24 20:15) was created by Claude's headless UI test, not the learner. Delete it.
- **Next step:** 054 → 055 → 056 → 057 → 053; mock 058 when built.

## 2026-11-25 – Lesson 058: Hörprov Swedex A2B1, provtest 2

- Full mock listening test (30 items, 35 min, A2 14 / B1 22), same shape as 025 and the official sample: Del 1 six phone messages (mcq, 4 options), Del 2 three messages + three radio bits (short), Del 3 dialogue Maja/Henrik (six short), Del 4 four real Klartext clips (maraton, lunch Vaggeryd, bombhot Italien, parahandboll) with 6 headlines, Del 5 four interviews with the same question (Vad gör du för att må bra på vintern?), 8 Rätt/Fel.
- Listening traps only at exam rate: weekday correction (måndag → torsdag), number corrections (jackor, hyra), i övermorgon, kvart i sju, close-wording Rätt/Fel. 17 audios with pinned NST voices from different regions/ages, noise on about half; Whisper check all ≤ 4%.
- **Next step:** unchanged; give 058 when the learner wants another full mock.

## 2026-11-25 – Graded 042 (adjektiv för åsikter)

- 17/19 auto (frisk→sund, h1 flera→stor). Speak A2+: all bullets, 4 word pairs. Learner noticed English structure in speech.
  Main: "är att" + inte before verb (English drops "that"); jag tycker in the middle; prepositions med/på; när vs om.
- → Fixed opinion frame (Jag tycker att / En fördel är att / En nackdel är att / En rimlig lösning är att) + Persian این است که.
- **Next step:** 058 mock; practice 054 → 057 (056/057 cover att/bisats inte placement). Consider a short speaking drill with the frame.
