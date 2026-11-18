# Research notes (2026-11-04)

Some facts come from secondary blogs. Check them on skolverket.se, su.se, and uhr.se.

## SFI kurs D national test

- Grading is **pass/fail only**: G (pass) or IG (fail). The old E/C/A scale no longer applies.
- There are 4 parts (delprov), taken on paper. Together they take about 4–5 hours.
- Elevbrev 2026/27: https://www.skolverket.se/download/18.7d98572219f8ebe7db543d92/1785757256430/Elevbrev%20Sfi%202026-2027%20260617.pdf
- **From 2027-01-01 there is a new syllabus** (SKOLFS 2026:67). Course D becomes 1D, 2D, or 3D. New test versions start 2027-01-18.
- Official example tasks: https://www.skolverket.se/prov-och-bedomning/nationella-prov/bestall-nationella-prov/gamla-nationella-prov
- Stockholm University makes the tests: https://www.su.se/nationella-prov-i-sfi/om-sfi-proven

### Parts of the test

**Läsa (reading)**
- Short texts plus one longer article.
- Task types:
  - find information in ads
  - say what a text message wants
  - read a chart
  - match interview questions to answers (only on D)
  - say who a text is written for (only on D)
  - "who thinks what" from chat posts

**Höra (listening)**
- Interviews, conversations, and news, all with multiple-choice questions.
- Example topics: "Boka en resa", "Hur ofta går de på bio?", "Hur vill de bo när de blir gamla?".

**Skriva (writing)**
- One informal task (a letter or email to a friend).
- One formal task. Example on D: an answer to an insändare (letter to the newspaper), "Förbjud mobiltelefoner!". You give your opinion and your reasons, and you start and end the text in a fitting way.

**Tala (speaking)**
- One solo task, "Berätta och ge råd" (3–4 min).
- One pair discussion from a mind map (about 10 min). The pair must agree on the most important factors.

### How writing and speaking are graded

Each part is pass/fail. The criteria come from the SU matrices:
- content
- adapting the text to the reader and situation
- clear and connected text, with some flow
- structure
- textbindning (linking words such as eftersom, för att, också)
- ordförråd (vocabulary)
- grammar "med viss variation och viss säkerhet"
- spelling and basic writing rules

Speaking adds two criteria:
- interaction (small replies that show you are listening, and moving the talk forward)
- uttal (pronunciation) "i huvudsak begripligt"

Matrices:
- Skriva D: https://www.su.se/download/18.3e707ac0199a328fe972170/1759929197895/Bedo%CC%88mningsmatris%20och%20kommentar...skriva,%20kurs%20DBedo%CC%88mningsmatris%20och%20kommentar...skriva,%20kurs%20D.pdf
- Tala D: https://www.su.se/download/18.3e707ac0199a328fe972173/1759929198051/Bedo%CC%88mningsmatris%20och%20kommentar...Tala,%20kurs%20D.pdf

## Citizenship language requirement

- Required level: **B1 for reading and listening, A2 for speaking and writing**. Source: SOU 2021:2.
- The requirement has applied since 2026-06-06.
- The civics test (run by UHR) was first given 2026-08-15. The language test itself does **not exist yet**. One proposal says autumn 2029, but nothing is decided. https://www.uhr.se/medborgarskapsprovet/
- Today you show your Swedish with a pass in SFI D, with Tisus, or with grades from Swedish school.
- **So SFI D is the practical "B1 test".**
- Swedex A2B1 (Folkuniversitetet) is another option. Free mock exams with answer keys: https://www.folkuniversitetet.se/in-english/swedex-swedish-examinations/mock-exams/
  - Every recording is played twice.

## Free practice

- Radio Sweden på lätt svenska (daily podcast)
- Klartext (Sveriges Radio)
- 8 Sidor (8sidor.se)
- Språkkraft Läscoach: https://sprakkraft.org/ (has dictionaries for 32 languages)
- larasvenskan.se/nationellt-prov/kurs-d

## Agentic / LLM tutors (any language)

### Projects we can learn from

**m98/fluent** (https://github.com/m98/fluent)
- 12 Claude Code skills.
- The learner model is JSON files:
  - profile
  - progress
  - mistakes-db (error patterns + examples)
  - mastery 0–5 per skill
  - SM-2 queue
  - session log
- Aims for 60–70% correct answers: the work gets easier or harder to stay in that range.

**ai-language-tutor** (https://github.com/ezchgivemethisshitplease/ai-language-tutor)
- FSRS cloze cards built from the learner's own errors.
- Notes on typical errors for each native language (L1).
- Reading texts use 95–98% known words.
- Typed answers never count as speaking.

**Sollu** (https://github.com/arosselet/language-tutor)
- Main rule: "LLM is the writer, Python is the brain".
- Python owns the state and the SRS.
- Each observation is tagged by channel: heard, read, or produced.

**swedish-ai-tutor** (https://github.com/WenqingYan/swedish-ai-tutor)
- Daily Radio Sweden lätt svenska episode → Whisper transcript → grammar and vocabulary per sentence → SRS.

**Anki MCP servers**
- They push cards into Anki, so you can review on your phone.
- https://github.com/ankimcp
- https://github.com/johwiebe/anki-mcp

### Swedish learner-error data

- SweLL-gold has 29 correction codes: https://spraakbanken.gu.se/en/resources/learner-language
- DaLAJ

### Papers

- Alignment Drift in CEFR-prompted LLMs (BEA 2025): an LLM drifts away from the level you ask for, so check the level of the text it generates.
- Grammar Control in Dialogue (NAACL 2025)
- L1-interference error labeling (EMNLP 2025)
- Duolingo Birdbrain (IRT)
- Duolingo Half-Life Regression

### Ideas to copy

- Deterministic state and an LLM that writes the content.
- Tagged error log, built from the parts of the grading matrix.
- An item generator that makes tasks in the same shape as the exam tasks.
- A rubric grader.
- Daily radio listening.
- FSRS cloze cards built from errors.

## Listening and speaking tech

### TTS (text to speech)

- **edge-tts** (verified)
  - Voices: sv-SE-SofieNeural (f) and sv-SE-MattiasNeural (m).
  - Join the mp3 chunks, then convert with `afconvert -f m4af -d aac`.
  - Needs internet and uses an unofficial endpoint, so generate the audio once and commit the files.
- macOS `say`
  - Only the Alva voice is installed.
  - You can add Klara and Oskar: System Settings > Accessibility > Read & Speak > Manage Voices > Swedish.
- Piper has sv_SE voices, but they sound more robotic.

### STT (speech to text)

- KBLab kb-whisper (small is better than whisper-large-v3 on Swedish)
  - Runs with faster-whisper: `pip install faster-whisper "av<17"`.
  - PyAV decodes webm/m4a, so you don't need ffmpeg.
  - Needs access to huggingface.co, which was blocked from the sandbox.
- Chrome `webkitSpeechRecognition` with sv-SE (live transcript, used now). It sends the audio to Google.

### Pronunciation

- Azure Pronunciation Assessment supports sv-SE. It has a free tier but needs a key.
- Practical local option: a read-aloud task.
  1. Transcribe with kb-whisper using word timestamps.
  2. Compare the words to the target text with difflib.
  3. Flag words with low probability.

## Update 2026-11-04: citizenship + Swedex (verified on official pages)

- Migrationsverket (medborgarskap för vuxna): age 16–66, **läs + hör B1, muntlig + skriftlig A2**.
  Ways to show it: pass in "den högsta kursen" of sfi; school grades in Swedish; Tisus; during the
  transition also "annat kunskapsprov … på funktionell nivå", **e.g. Swedex**.
- **Swedex ends: no Swedex tests after 2026-12-31** (Migrationsverket + Folkuniversitetet).
  Last dates seen: A2B1 Göteborg 2026-12-04, Lund 2026-12-18. Migrationsverket will say during 2027
  whether another test can replace Swedex.
- Swedex versions are **A2B1** and **B2C1** (no "B1B2"). Overall result = lowest part. Free B1
  model test: https://www.folkuniversitetet.se/mer-om-sprak/sprakexamina-och-sprakprov/swedex-swedish-examinations/modelltest/modelltest-b1/
- The law (prop. 2025/26:175) says "the highest sfi course", not "kurs D". So the 2027 courses
  1D/2D/3D should count (each is the highest course of its study path), but no official text says so explicitly.
- sfi started before 2027-01-01 finishes under the old rules and the existing national tests.
- Citizenship language test: by law in place by 2027-10-01 at the latest (stage 1: reading +
  listening). UHR recommended a delay (Migrationsverket news 2026-09-30); the government decides.
  Stage 2 adds speaking + writing, and then "annat kunskapsprov" stops counting (only Tisus +
  grades + sfi + the state test remain).

<!-- archive: material-material -->

## Swedex A2B1 – report from a test taker (learner's friend, 2026-11)
- Reading: easiest part. Clear instructions, little writing.
- Listening: hardest. The teacher plays each recording twice **back to back, no pause**. You write answers
  while listening. 5 min before start to read the questions; ~30 s between parts. Some recordings have
  background noise or unclear speakers.
- Writing: two emails, ~50 and ~100 words (model test del 2 says "ca 100 ord"). Practise asking questions
  and describing things.
- Speaking: 15 min, exactly as in the model test (muntligt deltagarmaterial).

## Swedex A2B1 – research beyond the model test (2026-11-18)

Labels: **[official]** = Folkuniversitetet document/page; **[official, old format]** = Folkuniversitetet
material from the pre-2022 separate A2/B1 tests (still downloadable, not the current test);
**[third party]** = test centre or school page; **[anecdotal]** = test-taker report.
FU = `https://www.folkuniversitetet.se/globalassets/dokumentbanken/lokala-dokument/dokument_region_vast/goteborg/swedex`

### Test-taker reports: almost none online
- No Reddit, Flashback, Persian or Arabic first-hand reports of the **current** A2B1 test were found
  (searched sv/en/fa/ar, YouTube). The friend's report above stays our best source.
- [anecdotal, official site] One doctor failed **hörförståelse** first time and passed it later as a
  restprov; oral examiner "mycket hjälpsam", nerves went after a few minutes; staff chat with you while
  you wait for the oral part (so the oral is held later in the day, separately).
  https://www.folkuniversitetet.se/mer-om-sprak/sprakexamina-och-sprakprov/swedex-swedish-examinations/deltagarintervjuer/roster-om-swedex/
- [anecdotal, old A2 format, 2017] Order: reading → (ord & grammatik) → break → writing → listening → oral.
  Fast connected speech in listening was the hard part; oral lasted 15 min, not the 8 min she expected.
  https://www.alicetehlarsson.se/blog/swedex2

### Göteborg test day (current)
- [official] A2B1 Göteborg dates: 20 Nov, **4 Dec** (shows "Boka reservplats" = full, waiting list) and
  **9 Dec 2026** (Wed, "Boka nu" = seats left) — 9 Dec is a backup date. Norra Allégatan 6, 09:00–17:00,
  3125 kr. "Schemat för examen får du i samband med testet. Räkna med att det tar en heldag."
  Booking closes one week before; cancel ≤1 week before = 25 % fee.
  https://www.folkuniversitetet.se/kurser-utbildningar/sprak/svenskaswedish/swedex-test/goteborg/92398/ ,
  https://www.folkuniversitetet.se/kurser-utbildningar/sprak/svenskaswedish/swedex-test/goteborg/108597/
- [official] Restprov (one part, e.g. läsförståelse 1041 kr) must be done within 6 months **and by
  2026-12-31**. Re-marking (ombedömning) costs 1500 kr, refunded if the overall result improves.
  Certificate ~3 weeks after the test. Overall level = lowest part; just under A2 → A1 certificate.
  https://www.folkuniversitetet.se/mer-om-sprak/sprakexamina-och-sprakprov/swedex-swedish-examinations/faq
- [official] FAQ: "Swedex B1 motsvarar ungefär nivån för sfi kurs D." (same page)
- [third party] Barcelona centre: written part ~3 h 15 min in one block (läs + hör + skriv), oral ~25 min
  incl. admin, A2B1 oral individual. https://institutnordic.com/en/swedex/

### Grading details (what we can and cannot know)
- [official] Current A2B1: läs and hör are pure point counts (A2/B1 limits in the testformat PDF); writing
  and speaking are judged by testledare against "bestämda bedömningskriterier"; the current criteria
  tables are **not published** (testformat only names the criteria). FAQ link above.
- [official, old format, 2009] The old A2/B1 marking guide shows how Swedex scores, likely the same
  logic today (inference, not confirmed): `FU/modelltest-b1/swedex_b1_bedomning_a2_b1.pdf`
  - Old B1 writing (10 p): **fullgörande** = number of content points covered (5→3 p, 4→2, 3→1, <3→0);
    **kommunikativ utformning** 0–4 (coherence between points, acceptable phrasing, **correct letter
    phrases** – greeting/closing); **formell korrekthet** 0–3 (morphology, syntax, spelling).
    **Any criterion at 0 = whole task failed.** "Brister" judged against what the level requires.
  - Old oral (40 p): 1) kommunikativa färdigheter och interaktion 18/15/10/0, 2) formell korrekthet och
    uttrycksförmåga 12/10/7/0, 3) uttal, intonation, flyt 10/8/5/0. A = no/small faults; B = faults that
    don't disturb; C = "man måste fråga för att förstå"; D = no communication. **Any D = oral failed.**
    Judged as a whole, not per task part. Form: `FU/modelltest-b1/swedex_b1_munt_bedomningsblankett.pdf`
- [official, B2C1 doc] B2C1 rules say: several answers to one question = 0 p; minor spelling errors give
  no deduction in written short answers. Not stated for A2B1, but probably the same policy —
  practise writing ONE short answer. `FU/modelltest-b2c1/b2c1-testformat.pdf`
- Typical fail reasons (inference from the criteria, not from reports): skipping a content point/question
  in the email, missing greeting/closing, wrong tense in the calendar task, listening below 22/30.

### Extra practice material (official, old format, still downloadable 2026-11-18)
Same institution, same task families; use for extra realistic practice, not as a copy of the current test.
- **Old B1 listening** (40 min): `FU/modelltest-b1/swedex_b1_hf.pdf`, audio
  `FU/modelltest-b1/swedex_b1_hf_modelltest_01.mp3` … `_04.mp3`, key + transcript
  `FU/modelltest-b1/swedex_b1_facit_hf_transkription.pdf`. Parts: picture MCQ on short dialogues,
  draw a route on a map from a phone message, **match 6 radio clips to headings (3 extra)**, **interviews
  with R/F statements**, questions on answering-machine messages. Del 2+3 = same task types as current
  Hör del 4 and 5. Each part gives 15–45 s to read the questions first.
- **Old B1 reading**: `FU/modelltest-b1/swedex_b1_las.pdf` (+ `swedex_b1_facit_las.pdf`): match headings to
  7 paragraphs (extra options), questions on a fact text where **the answer may not be in the text**,
  MCQ on an argumentative text (≈ current del 3 insändare).
- **Old B1 writing**: `FU/modelltest-b1/swedex_b1_skriv.pdf` – reply to a pen-friend letter, describe your
  week from a calendar, "Tänk på att det är den 7 maj idag", at least five dates, ~100 words. The calendar
  task has existed since at least 2003 → stable task: "today" sits in the middle of the week, so past days
  need preteritum/perfekt and later days need ska/kommer att.
- **Old B1 oral** (pair format, now replaced): examiner script `FU/modelltest-b1/swedex_b1_munt_manus.pdf`,
  statements `FU/modelltest-b1/swedex_b1_munt_amnen.pdf` (e.g. city vs countryside, money and happiness,
  cats vs dogs). Good prompts for current oral **del 3 "prata om ett ämne / säg vad du tycker"**.
  Old format description: `FU/modelltest-b1/swedex_b1_testformat_muntligt_a2_b1.pdf`.
- **Old A2** (easier warm-up): `FU/swedex_a2_las.pdf` (Ja/Nej on texts – same as current Läs del 1),
  `FU/swedex_a2_hf.pdf` + `FU/swedex_a2_hf_modelltest_02.mp3`. Old A2 listening says "Varje meddelande
  repeteras direkt" – matches the friend's report (played twice back to back).
- Not retrievable: `FU/modelltest-a2b1/modelltest-a2b1-muntlig-uppgift.pdf` (listed in 2022, now
  redirects; probably the examiner side of the current oral). Full file list via Wayback CDX:
  https://web.archive.org/cdx/search/cdx?url=folkuniversitetet.se/globalassets/dokumentbanken/lokala-dokument/dokument_region_vast/goteborg/swedex/*
- Copyright: FU says the model tests are for individual self-study only. Fine for the learner's own
  practice; don't republish. https://www.folkuniversitetet.se/mer-om-sprak/sprakexamina-och-sprakprov/swedex-swedish-examinations/swedex-a2b1-och-b2c1/modelltest/

### Outdated / misleading third-party sources (ignore)
- Pages still describing an "ord och grammatik" part, 5 parts, or A2/B1/B2 as separate levels are pre-2022:
  https://www.scandinavianschool.org/swedex , https://theswedishteacher.com/sv/blog/which-exam-should-i-choose/ ,
  Wikipedia. The svenska.app "Swedex B1" mock uses that old format: https://www.svenska.app/exams
- [official] Current format since spring 2022 (A2B1 + B2C1, level per skill):
  https://www.folkuniversitetet.se/mer-om-sprak/sprakexamina-och-sprakprov/swedex-swedish-examinations/swedex-a2b1-och-b2c1/
- [official] Prep advice for A2B1 is only generic: Klartext, 8 Sidor, Radio Sweden på lätt svenska,
  Nyheter på lätt svenska. https://www.folkuniversitetet.se/mer-om-sprak/sprakexamina-och-sprakprov/swedex-swedish-examinations/tips-och-rad/
