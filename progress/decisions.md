# Notes from conversations with the learner

Newest first. Write down anything that changes the plan, a preference, or a fact about the learner.

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
