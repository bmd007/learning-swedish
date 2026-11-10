# Notes from conversations with the learner

Newest first. Write down anything that changes the plan, a preference, or a fact about the learner.

## 2026-11-10
- Learner wants a break from tests: watch Swedish YouTube with Swedish auto-subs + English subs.
  Tested local Ollama (M2 Pro, 32 GB): gemma3:4b and qwen3:8b translate sv→en well (~5 s for 3 lines
  incl. model load); llama2 is chatty and weaker. Suggested Language Reactor first; a custom
  Ollama extension is possible (could also save sentences into this repo for review).

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
