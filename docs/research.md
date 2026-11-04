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
