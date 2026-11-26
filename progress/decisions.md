# Notes from conversations with the learner

Newest first. Write down anything that changes the plan, a preference, or a fact about the learner.

## 2026-11-13
- **SFI C test memory (learner).** Had to write about "min första mobiltelefon" (who gave it, features) and froze:
  old-phone vocabulary was never taught. Lesson: unfamiliar-topic vocabulary is a real risk on SFI D too.
  → Train omskrivning (circumlocution chunks: *en sån där … som man …*, *en sak som man använder för att …*)
  and recycle it in writing/speaking tasks on unexpected everyday topics.
- **No time-based planning (learner).** Don't ask for dates, no week plans or countdowns. Just react: grade each
  attempt, then build the next lesson from the data. (Supersedes the Swedex timeline in plan.md.)
- **Main target is now the SFI D national test, old format** (learner is enrolled in SFI D and takes it before
  the 2027 change). Swedex A2B1 is a backup. ~70% of practice is shared; add SFI D shapes: charts/chat/sms/
  interview matching in reading, MCQ listening, formal opinion text + informal letter, "berätta och ge råd" and a
  pair discussion with agreement.
- **Reading practice in real exam shape + richer UI (learner request).** Reading tests 016 (Läs del 1+2) and
  017 (del 3+4) with original texts, calibrated on the model test (model test itself kept for the mock).
  UI: dashboard (countdown, skill meters, tabs, filters), separate exam view (timer, navigator, flags, A2/B1
  verdict), learning view (instant feedback, live first-try score, split text/questions for reading).
- **en/ett errors are memory, not grammar (learner, 2026-11-13).** The learner knows the agreement rule; they
  forget which nouns are en and which are ett. → Teach gender as vocabulary: always noun + article, ending
  rules that predict gender (-ing/-het/-are/-tion → en; -ande/-eri/-um/-em/-ment → ett), "guess en" (~75%),
  colour-coded concept pictures (ett = red, en = blue), and recycle ett-words in later lessons (vocab.md).
- **Narrow skill drills must be short (learner feedback).** A 14-min lesson on reading years was "too much".
  One small skill (numbers, one word, one rule) → 5–8 min, ~8–10 items, speaking only if it is the point.
  Keep 10–15 min for exam-shaped or mixed lessons.
- **Listening must sound native and B1 (learner feedback).** The TTS dialogues were "good but not B1": too
  short, too clean, slow, two robotic voices, answers word-matched. Decisions:
  1. Prefer **real audio**. SR **Klartext** (sverigesradio.se/klartext) = easy news with real reporters and
     real interviewees (dialect, *ju/liksom/väl*, slang like *pajat*), 1–3 min clips + headline + short text.
     Matches Swedex Hör del 2 and del 4. `tools/fetch_klartext.py` downloads them to materials/ (personal use,
     not in git). Radio Sweden på lätt svenska (SR program 4916) is another option (longer, ~10 min).
  2. Transcripts: huggingface is blocked here, but openai-whisper weights (openaipublic.azureedge.net) work.
     Model "turbo" transcribes Klartext well (small errors with names/slang). Check before using.
  3. Rivstart ch. 7–10 tracks for dialogues (not yet done in class). Swedex model-test audio is kept for a
     full mock exam (late November).
  4. TTS still used for controlled dialogues, but with B1 rules (AUTHORING → Audio): 120–250 words,
     spoken words, plan changes / corrected numbers as distractors, paraphrased questions, normal speed,
     pauses between turns, a 3rd voice via pitch.

## 2026-11-10
- **Word questions = "teach me this".** When the learner asks about a Swedish word, verb, noun or
  expression, they don't know it and want to practice it in all its forms (conjugation, declension,
  related words, chunks). They may mistype å/ä/ö – fix silently.
  → Don't drill in chat. Build a short practice lesson in the app (info cards with forms table +
  chunks + Persian note, then gap/mcq/order/listening/speak items). Log the word in
  progress/vocab.md so it comes back in later lessons (spaced repetition).
- **All practice, tests and lessons happen in the app**, never in the chat.
- **Rivstart B1/B2 extramaterial is downloaded locally** to `materials/nok/` (gitignored, licensed to the
  learner – never commit or publish). Exercises as text, 167 audio tracks, listening transcripts, answer
  keys, word/verb lists. See `materials/nok/README.md`. Use for themes/vocabulary and listening practice
  that matches the learner's course. Access tokens in `nt-access.txt` (gitignored, expire after ~1 h).
- **Rivstart is one good source, not the curriculum.** Use it well (exercises, audio, transcripts, word
  lists), but lessons are driven by the exam (Swedex A2B1) and the learner's errors, and mix in other
  sources (own texts, real-life Swedish, other material).
- **B1 level ≈ Rivstart B1/B2 chapters 1–9 (maybe 10).** Chapters 11–18 are B2 – don't use them for
  B1/exam prep unless a specific item fits the level.
- **Local lesson generator (2026-11-11).** Learner wanted a panel to generate lessons/tests with the local
  Ollama model. Tested qwen3:8b, gemma3:4b (bad Swedish keys) and pulled gemma3:12b (best). One-shot output
  had wrong grammar (e.g. "i 2015", "för tre år" without sedan), and blind self-check did not catch it (same
  blind spots). What works: the model as a *reviewer* (yes/no verdicts on filled-in sentences) is reliable;
  its own fixes are not. So the harness drops items the reviewer rejects, grounds prompts with real textbook
  sentences, and code does all structure. Grammar drills come out mostly correct; theme lessons are weaker.
  Not Claude Code on Ollama: a 12B model is unreliable as an agent; a fixed pipeline is better.
- **Two kinds of images, both wanted (2026-11-11).** (1) Rule images: text/tables/timelines that explain
  grammar – useful. (2) Concept pictures: what a word or idea *looks like* (sunrise for "i morse", a
  calendar for "i fredags", a horse being groomed for "rykta"). These build memory links and are needed
  whenever the meaning can be drawn. Anything other than plain text helps. → every lesson: rule image(s)
  + concept pictures for the key words.
- **Speaking needs wiggle room (2026-11-11).** 60 s was too short for 5 speaking questions; the learner adds
  extra sentences. Rule: maxSeconds ≥ 120 and 60 + 30 s per bullet. All existing speak items updated.
- **Lessons need media and focus.** Text-only lessons are boring. Every lesson has related images
  (hand-drawn SVG that teaches the rule/scene, or free photos with credit) and audio where it fits.
  One topic per lesson, 10–15 min. A word question with two topics → two lessons.

## 2026-11-04
- **Study time is unknown and varies.** The learner does a test whenever they have time.
  → Keep lessons short: 10–15 min units. Many small lessons are better than one long one.
  → Every answer is saved to the server right away (`results/drafts/`), so leaving halfway loses nothing.
  Grade drafts too, not only final results.
- **Target: Swedex A2B1, Göteborg, 2026-12-04** ("might be able to"). The learner meant Swedex from
  Folkuniversitetet when they said "Sweden B1 test". Swedex has no B1/B2 version, only A2B1 and B2C1.
- Swedex overall level = the lowest part. The certificate also shows the level per part.
  Migrationsverket asks for B1 in reading and listening and A2 in speaking and writing, but it is
  unclear whether a Swedex certificate with A2 overall is accepted.
  → Told the learner to ask Migrationsverket. Ask them about the answer later.
- Learner asked: what do the 2027 sfi changes mean for citizenship? Answer: the law says "the highest
  sfi course", so 1D/2D/3D should count. sfi started before 2027 ends with the old test.
  Details in docs/research.md.
- Learner wants Claude to lead, commit and push without asking, keep notes, and be able to resume
  after a restart (CLAUDE.md resume checklist).
- Learner offered a Spring Boot setup. Not needed: Python stdlib server + plain JS is enough.
- Learner offered photos of Rivstart B1/B2 pages (ch. 1–6 done). Ask for them when a lesson should
  build on the book's vocabulary or themes.
- Persian explanations are welcome. English hints early, fewer later.
- Learner found the first research brief too narrow. They wanted agentic language-learning work in
  general, not only Swedish.

## 2026-11-04 (later)
- Learner skipped writing + speaking in 001; wants them in the next round.
- Learner asked to decouple content (questions, results, interactions) from server/UI code so simpler AIs
  can generate lessons, reports, plans from repo documents. → docs/AUTHORING.md is the contract; tools/ do
  deterministic work (validate, report, audio); .claude/agents/ define author/grader roles.

## 2026-11-16 – Rivstart reading photos
- Learner sent 9 photos of Rivstart B1/B2 readings (`materials/nok/rivstart_reading_pics/`, private):
  Fritid förr och nu (ch 1), Konst och vänskap runt 1900 – Thiel, Jansson, af Klint (ch 2),
  Sveriges styrelseskick (ch 6), Stickande och bitande djur. The learner's handwritten notes in the
  photos show words they looked up (knappt, orka, okänt, växte fram, olämpligt, ordnade, passande,
  orsakar, lidande, vågar, ändå, däremot, lindriga besvär, skamliga, förrän, beundrade).
- Length: Rivstart texts are 400–700 words per theme. Test texts: Swedex 220–530 words, SFI D has one
  longer article. So about the same as the longest test text, but denser (names, years, rare words).
- Repo is PUBLIC → never copy book text into lessons. Rewrite the same facts in own words (also trains
  paraphrase), reuse the words the learner marked. Done in 023 + 024.

## 2026-11-16 – Friend's Swedex report
- Friend took Swedex A2B1: listening hardest (twice in a row, no pause, noise, unclear speakers, write while
  listening). Writing = two emails ~50 + ~100 words. Details in docs/research.md.
- → App: exam-mode audio now plays twice in a row on one click. build_audio.py: `noise` option.
  Listening practice must include exam conditions; Swedex writing tasks use 50/100 words.

## 2026-11-18 – Voices
- Learner finds TTS voices clearly machine-made; wants human-like voices with different personalities and accents.
  Real audio cut into short parts is the accepted fallback (lesson 027).
- Learner is fine using the work AI gateway for this project ("you are my work AI already"), but it has no TTS.
- huggingface.co is blocked on the Mac's network; learner downloads models on another network (scripts in tools/download/).

## 2026-11-18 – Human voices: decision
- Learner rated samples (then stopped rating: "you know enough"): Chatterbox voices 3–4★, edge 1–3★.
  Best: Anna Sofia, Cecilia2, child voice (Anna Sofia pitched ×1.25) = 4★; Petra, Måns 3★; Lars 2★; Cecilia as
  friend 1★. "Calm" vs "lively" settings sound the same → personality must come from different reference speakers.
- Learner wants high variety: old, young, man, boy, girl, boss, administrator … → cast in tools/voice_cast.json from
  LibriVox + NST (age/region) + NOK actors. Learner OK with using NOK audio as voice references.
- All Chatterbox audio is private (materials/tts/), app prefers it; audio/ (edge) stays as public fallback.

## 2026-11-18 – Attention / false friends
- Learner: attention span is lower now → doesn't read the whole question; takes a Swedish word for a similar
  English word and only later sees the mistake. Wants to work on focus.
- Decision (learner): attention training ONLY as practice lessons. Tests/exams must NOT change or get easier –
  they stay as close as possible to the real Swedex / SFI D. Do: key-word step in practice lessons, short focus
  sprints (5–8 items). Skip: false-friends drill, end-of-exam check pass.
- Exams get free highlighting (select text → marker), like the learner does on paper. A tool, not a hint.
- Research real Swedex question types beyond the official sample PDF (online reports, other mock tests).

## 2026-11-19 – Exam booked
- Learner has booked Swedex A2B1, Göteborg, **2026-12-04** (confirmed booking, not waiting list). 15 days left.

## 2026-11-20 – Rivstart word list = vocabulary target

- Learner added the Rivstart B1/B2 Ordlista PDF ("the words we are supposed to learn"). Learner: "half of the book is B1".
- Decision: chapters 1–9 (≈2800 unique words) are the B1 target vocabulary; ch. 10 borderline; 11–18 = B2, not a goal.
  Parsed to `materials/ordlista/rivstart-b1b2.json` (private). Lessons should prefer these words.

## 2026-11-22 – Vocabulary: range, not precision

- Learner: "I don't really care about high load vs long queue … I'm more interested in range of useful adjectives."
  → Adjective lessons from now on teach many useful words (meaning, opposite, use in speech), not collocation traps.
  039–042 stay as they are.
- Video word cues: agreed to a trial after 043 is handed in (stock clips for concrete words, Persian/English sound
  hints for abstract words; YouGlish suggested for real usage).

## 2026-11-22 – Vocabulary checks: production, not recognition

- Learner after 043 (34/36 mcq): "I kinda guessed some words correct, it's not like now I can spell or remember or use all of them."
  → MCQ recognition ≠ knowing a word. Vocabulary checks use typed recall (gap + Swedish hint + first letter), and the
  "known" list only counts words the learner can produce. 043 = "seen before" only.

## 2026-11-23 – Vocabulary level: concrete daily words first

- Learner (during 047): words like tröttna/bry sig/oavsett feel early; "I need more common and daily useful and
  tangible vocabulary. maybe that would A1/A2 level".
  → Next vocab lessons: concrete, everyday nouns + action verbs by theme (home, laundry room, shopping, transport,
  health, city services, clothes, small things). These also fill Swedex listening del 1–3 (phone messages).
  Abstract Rivstart words (043/047) later.
- Level check source: Kelly list (Språkbanken, CC BY 4.0) → `materials/kelly/kelly-sv.json` (8425 words, CEFR A1–C2,
  web-frequency based, so mixed with news words – use as a level filter, not as the curriculum).
- Format: a photo per word (Pixabay, private), hear the word, then TYPE it (production), then a Swedex-style message.

## 2026-11-24 – Date/time words are slow for the learner in every language
- Learner: weekdays, month names, date words took long to feel natural even in English and Persian as a child.
  Not a Swedish problem. 028 showed it: "35 på torsdag" → wrote "1935"; missed "i övermorgon" (trap: "i morgon" first).
- → Teach date/time words with many short spaced repetitions in context (phone messages, appointments, "när?"
  questions), not one list. Recycle them in later listening lessons. Learner's own note: mahdi-s-thoughs.md.

## 2026-11-24 – Superfluent as speaking examiner
- Learner uses the Superfluent app (speaking AI tutor, Swedish supported; custom scenario / free chat per user
  reviews) as a Swedex A2B1 oral examiner. Prompts: docs/superfluent-tala-swedex.md (3 full mocks, own ads).
  App mishears numbers/web addresses. Learner sends back the app's feedback → add to errors.md.

## 2026-11-24 – Persian names in TTS
- Learner: TTS pronounces Persian names/places badly (052: Shiraz → heard, wrote "skyras"). In audio, use Swedish or
  common international names/places, or names the voices handle; don't ask the learner to spell foreign names.

## 2026-11-24 – "Mina kort" page
- Learner wanted to come back to rule cards (e.g. the därför table) without opening the lesson. App: ☆ Spara on every
  info card and every auto-graded question (practice mode only); page "Mina kort" (Sparade / Alla kort, search).
  Saved list in progress/saved.json → Claude reads it to build review lessons from what the learner chose.

## 2026-11-25 – Mock exams: realism first
- Learner: focusing on past issues must not change the exam style; errors from reading/writing don't apply to listening.
  → Mock exams copy the official sample (task shapes, question mix, difficulty, audio). Targeting only from errors in the
  same skill, at the exam's natural trap rate. Drills belong in practice lessons.

## 2026-11-27 – Speaking test: what's on paper
- Official A2B1 muntligt (deltagarmaterial): Del 1 presentation – no paper. Del 2 – ad A on paper (30 s to read), then
  a tips box (question words) for ad B. Del 3 – page C = **8 photos** (seasons: autumn leaves, spring flowers, swimming,
  hiking, snow-clearing, skiing, beach cycling) → talk about the topic (årstider), say what you think, tell something.
  No preparation time, no notes ("inga hjälpmedel"). All three parts are speaking only.
- → Del 3 practice must use a picture page, not only a written question. Feedback page now replays the question + own recording.
- **Correction:** in Del 2 B the learner SEES ad B (4 photos + text) plus a "Frågor:" tips box (deltagarmaterial p. 4);
  asking is a role-play. Earlier feedback/055/voice prompts said it was hidden – corrected 2026-11-27.
- Learner: make every untaken speaking practice/exam follow the exam structure → AUTHORING rule + conversion of
  006, 010, 012, 031, 032, 035, 036, 044, 045, 046, 048, 049, 055.

## 2026-11-27 – Audit: our exams vs the real A2B1 sample (pages + audio)
- Learner asked to re-check all skills after the speaking miss. Real shapes now in docs/AUTHORING.md "Real exam shapes".
- Biggest gaps: listening is self-paced in our app (real: paced by the recording, fixed reading time, del 4/5 "all once,
  then all again", picture options in del 1, clean studio audio, number-list distractors more than corrections);
  reading Del 4 not chronological + too easy, Del 3 4 options/no headline questions, Del 2 no inference;
  writing Del 1 had numbered questions + own question, Del 2 5-day calendar without weather / "choose 5".
- 028 (old B1, taken 24/11) shares the biluthyrning dialogue + 10-miljoner interviews with the A2B1 sample's Hör del 3+5
  → that part of the official listening sample is no longer a clean mock.
- Official reading, writing and listening (del 1, 2, 4) samples are unused → final dress rehearsal around 1–2 Dec.

## 2026-11-27 – Noise in listening + which sources decide exam shape
- Official A2B1 sample audio is studio-clean; the learner's friend heard background noise on the real test day.
  → Keep scene noise on about a third of practice/mock clips (058/059 have it); 072 (official audio) stays clean.
  Both conditions get practised.
- Source order for exam shape: (1) official A2B1 sample pages + audio, (2) friend's test-day report, (3) the
  format PDF text, (4) old B1 test 028 / general research. Lessons built before the 2026-11-27 audit (e.g. 016,
  021, 026, early speaking) followed (3)/(4); the untaken ones were converted, the taken ones stay as history.
