const app = document.getElementById("app");
const timerEl = document.getElementById("timer");
const enToggle = document.getElementById("enToggle");

const store = {
  get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  del(k) { try { localStorage.removeItem(k); } catch {} },
};

enToggle.checked = store.get("showEn", true);
document.body.classList.toggle("show-en", enToggle.checked);
enToggle.onchange = () => {
  document.body.classList.toggle("show-en", enToggle.checked);
  store.set("showEn", enToggle.checked);
};

const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const en = s => s ? `<div class="en">${esc(s)}</div>` : "";
const norm = s => String(s ?? "").toLowerCase().replace(/[.,!?;:"]/g, "").replace(/\s+/g, " ").trim();
const fmt = sec => `${Math.floor(sec / 60)}:${String(Math.floor(sec % 60)).padStart(2, "0")}`;
const isCompact = opts => opts.length > 6 && opts.every(o => /^([A-Z]\.|\d)/.test(o));
const AUTO = new Set(["mcq", "select", "gap", "order", "short"]);
const h = html => { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; };
const md = s => window.marked ? marked.parse(s ?? "") : `<pre>${esc(s)}</pre>`;
const pct = (c, t) => t ? Math.round(100 * c / t) : null;

const SKILLS = {
  läsa: { label: "Läsa", en: "Reading", icon: "📖" },
  höra: { label: "Höra", en: "Listening", icon: "🎧" },
  skriva: { label: "Skriva", en: "Writing", icon: "✍️" },
  tala: { label: "Tala", en: "Speaking", icon: "🗣️" },
  grammatik: { label: "Grammatik", en: "Grammar & words", icon: "🧩" },
};

let tick = null;
function stopClock() {
  clearInterval(tick);
  timerEl.textContent = "";
  timerEl.className = "timer";
}

window.addEventListener("hashchange", route);
route();

function setMode(mode) {
  document.body.classList.toggle("exam-mode", mode === "exam");
  document.body.classList.toggle("wide", mode === "exam" || mode === "wide");
}

function route() {
  stopClock();
  setMode(null);
  window.speechSynthesis?.cancel();
  const [, view, id] = location.hash.split("/");
  if (view === "lesson" && id) return openLesson(id);
  if (view === "feedback" && id) return openFeedback(id);
  return home();
}

async function home() {
  const [lessons, prog] = await Promise.all([
    fetch("/api/lessons").then(r => r.json()),
    fetch("/api/progress").then(r => r.ok ? r.json() : {}).catch(() => ({})),
  ]);
  const isExam = l => l.mode !== "practice";
  const todo = lessons.filter(l => !isExam(l) && !l.attempts);
  const exams = lessons.filter(isExam);
  const done = lessons.filter(l => !isExam(l) && l.attempts).reverse();
  const next = todo[0];
  const days = prog.examDate ? Math.ceil((new Date(prog.examDate) - new Date()) / 86400000) : null;
  let tab = store.get("homeTab", "todo");
  let filter = store.get("homeFilter", "all");

  const meter = key => {
    const s = prog.skills?.[key];
    const p = s && s.total >= 5 ? pct(s.correct, s.total) : null;
    const cls = p == null ? "" : p >= 73 ? "good" : p >= 57 ? "mid" : "low";
    return `<div class="meter ${cls}">
      <div class="meter-head"><span>${SKILLS[key].icon} ${SKILLS[key].label}</span><b>${p == null ? "–" : p + "%"}</b></div>
      <div class="bar"><span style="width:${p ?? 0}%"></span><i style="left:73%" title="B1"></i></div>
      <div class="muted small">${s?.total ? `${s.correct}/${s.total} rätt` : "inga svar än"}${s?.total && s.total < 5 ? " (för få)" : ""}${s?.teacher ? ` · ${s.teacher} bedöms av läraren` : ""}</div>
    </div>`;
  };

  const card = l => {
    const sc = l.lastScore?.total ? pct(l.lastScore.correct, l.lastScore.total) : null;
    const scCls = sc == null ? "" : sc >= 73 ? "good" : sc >= 57 ? "mid" : "low";
    return `<div class="lcard ${isExam(l) ? "is-exam" : ""}">
      <div class="lcard-main">
        <div class="lcard-skills">${l.skills.map(s => `<span class="skill-chip" title="${SKILLS[s]?.en ?? s}">${SKILLS[s]?.icon ?? ""} ${SKILLS[s]?.label ?? s}</span>`).join("")}</div>
        <h3>${esc(l.title)}</h3>${en(l.titleEn)}
        <div class="muted small">${isExam(l) ? `⏱ ${l.timeLimit ?? l.minutes ?? "?"} min · prov` : `ca ${l.minutes ?? "?"} min`}${l.attempts ? ` · ${l.attempts} försök · ${l.lastScore?.date ?? ""}` : ""}</div>
        ${l.generated && !l.reviewed ? `<span class="badge gen-badge">Lokal modell · inte granskad av Claude</span>` : ""}
      </div>
      <div class="lcard-side">
        ${sc != null ? `<div class="score-pill ${scCls}">${l.lastScore.correct}/${l.lastScore.total}</div>` : ""}
        <div class="lcard-btns">
          ${l.hasFeedback ? `<a class="btn secondary sm" href="#/feedback/${l.id}">Feedback</a>` : ""}
          <a class="btn sm" href="#/lesson/${l.id}">${l.attempts ? "Gör igen" : isExam(l) ? "Starta provet" : "Starta"}</a>
        </div>
      </div>
    </div>`;
  };

  app.innerHTML = `
    <section class="dash">
      <div class="dash-hero">
        <div>
          <div class="muted small">Mål: ${esc(prog.goal ?? "B1")}</div>
          <h1>${days != null && days >= 0 ? `${days} dagar kvar` : "Hej! Välkommen."}</h1>
          ${en(days != null && days >= 0 ? `${days} days to the exam (${prog.examDate})` : "")}
          <div class="muted small">${prog.attempts ?? 0} lektioner klara · ca ${Math.round(prog.minutes ?? 0)} min övning</div>
        </div>
        ${next ? `<a class="next-card" href="#/lesson/${next.id}">
          <span class="muted small">Nästa lektion →</span>
          <b>${esc(next.title)}</b>
          <span class="muted small">ca ${next.minutes ?? "?"} min</span>
        </a>` : ""}
      </div>
      <div class="meters">${Object.keys(SKILLS).map(meter).join("")}</div>
      <div class="muted small">Strecket = ungefär B1 (ca 73 % rätt). <span class="en">The line marks roughly B1.</span></div>
    </section>
    <div class="tabs">
      <button data-tab="todo">Att göra <span class="count">${todo.length}</span></button>
      <button data-tab="exam">Prov <span class="count">${exams.length}</span></button>
      <button data-tab="done">Klara <span class="count">${done.length}</span></button>
    </div>
    <div class="filters">${["all", ...Object.keys(SKILLS)].map(k => `<button data-f="${k}">${k === "all" ? "Alla" : SKILLS[k].icon + " " + SKILLS[k].label}</button>`).join("")}</div>
    <div id="list"></div>
    <details class="card gen">
      <summary><b>Skapa en egen lektion</b> <span class="en">Create your own lesson with the local AI model</span></summary>
      <textarea id="genTopic" rows="3" placeholder="Vad vill du träna? T.ex. &quot;prepositioner för tid&quot; eller &quot;ringa vårdcentralen och boka tid&quot;"></textarea>
      <div class="gen-row">
        <label><input type="radio" name="genMode" value="practice" checked> Lektion</label>
        <label><input type="radio" name="genMode" value="exam"> Test</label>
        <button class="btn" id="genBtn">Generera</button>
      </div>
      <div id="genStatus" class="muted"></div>
    </details>`;

  const list = app.querySelector("#list");
  const draw = () => {
    app.querySelectorAll(".tabs button").forEach(b => b.classList.toggle("on", b.dataset.tab === tab));
    app.querySelectorAll(".filters button").forEach(b => b.classList.toggle("on", b.dataset.f === filter));
    const src = { todo, exam: exams, done }[tab].filter(l => filter === "all" || l.skills.includes(filter));
    list.innerHTML = src.length ? src.map(card).join("") : `<p class="muted empty">Inget här just nu.</p>`;
  };
  app.querySelectorAll(".tabs button").forEach(b => b.onclick = () => { tab = b.dataset.tab; store.set("homeTab", tab); draw(); });
  app.querySelectorAll(".filters button").forEach(b => b.onclick = () => { filter = b.dataset.f; store.set("homeFilter", filter); draw(); });
  draw();
  generatorPanel();
}

function generatorPanel() {
  const btn = app.querySelector("#genBtn"), status = app.querySelector("#genStatus"), topic = app.querySelector("#genTopic");
  const savedJob = store.get("genJob", null);
  if (savedJob) { app.querySelector("details.gen").open = true; poll(savedJob); }
  btn.onclick = async () => {
    const mode = app.querySelector("input[name=genMode]:checked").value;
    if (topic.value.trim().length < 3) { status.textContent = "Beskriv ämnet först."; return; }
    btn.disabled = true;
    status.textContent = "Startar …";
    const res = await fetch("/api/generate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ topic: topic.value, mode }) }).then(r => r.json());
    if (res.error) { status.textContent = res.error; btn.disabled = false; return; }
    store.set("genJob", res.id);
    poll(res.id);
  };
  async function poll(id) {
    btn.disabled = true;
    const job = await fetch(`/api/generate/${id}`).then(r => r.ok ? r.json() : null).catch(() => null);
    if (!job || !document.body.contains(status)) { if (!job) { store.set("genJob", null); btn.disabled = false; } return; }
    const last = job.log.slice(-4).map(esc).join("<br>");
    if (job.status === "done") {
      store.set("genJob", null);
      status.innerHTML = `Klar! <a class="btn" href="#/lesson/${job.lessonId}">Öppna lektionen</a>`;
      btn.disabled = false;
      return;
    }
    if (job.status === "error") {
      store.set("genJob", null);
      status.innerHTML = last;
      btn.disabled = false;
      return;
    }
    status.innerHTML = `<b>Genererar (tar 3–6 min) …</b><br>${last}`;
    setTimeout(() => poll(id), 2000);
  }
}

async function openFeedback(id) {
  const res = await fetch(`/api/feedback/${id}`);
  const text = res.ok ? await res.text() : "Ingen feedback än.";
  app.innerHTML = `<a class="back" href="#/">← Startsidan</a><div class="card md feedback">${md(text)}</div>
    <a class="btn secondary" href="#/">← Tillbaka</a>`;
}

async function openLesson(id) {
  const lesson = await fetch(`/api/lessons/${id}`).then(r => r.json());
  const exam = lesson.mode !== "practice";
  const draftKey = `draft:${id}`;
  const local = store.get(draftKey, null);
  const remote = await fetch(`/api/draft/${id}`).then(r => r.ok ? r.json() : null).catch(() => null);
  const remoteState = remote?.state;
  const useRemote = remoteState && (!local || (remoteState.updatedAt ?? 0) > (local.updatedAt ?? 0));
  const state = (useRemote ? remoteState : local) ?? {
    step: -1, answers: {}, plays: {}, sectionTime: {}, startedAt: null,
  };
  state.attemptId ??= new Date().toISOString().replace(/[:.]/g, "-");
  state.flags ??= {};
  state.marks ??= {};
  let pushTimer = null;
  const save = () => {
    state.updatedAt = Date.now();
    store.set(draftKey, state);
    clearTimeout(pushTimer);
    pushTimer = setTimeout(pushDraft, 600);
  };
  const steps = lesson.sections;
  let stepEnter = Date.now();
  const timeLimit = exam && lesson.timeLimit ? lesson.timeLimit * 60 : null;

  function pushDraft() {
    if (!state.startedAt) return;
    leaveStep();
    store.set(draftKey, state);
    fetch("/api/draft", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...buildPayload(false), state }) })
      .catch(() => {});
  }

  function buildPayload(final) {
    const graded = allItems().map(i => ({
      id: i.id, section: i.section, type: i.type, tags: i.tags ?? [], prompt: i.q ?? null, ...grade(i),
    }));
    const bySection = {};
    for (const g of graded) {
      if (g.correct === null || (!final && g.given == null)) continue;
      const s = bySection[g.section] ??= { correct: 0, total: 0 };
      s.total++;
      if (g.correct) s.correct++;
    }
    const elapsed = (Date.now() - state.startedAt) / 1000;
    return {
      lessonId: lesson.id,
      attemptId: state.attemptId,
      final,
      mode: exam ? "exam" : "practice",
      startedAt: new Date(state.startedAt).toISOString(),
      finishedAt: final ? new Date().toISOString() : null,
      durationMin: Math.round(elapsed / 60),
      ...(timeLimit ? { timeLimitMin: lesson.timeLimit, overtime: elapsed > timeLimit } : {}),
      currentSection: steps[state.step]?.id ?? null,
      sectionMinutes: Object.fromEntries(Object.entries(state.sectionTime).map(([k, v]) => [k, Math.round(v / 6) / 10])),
      audioPlays: state.plays,
      firstTry: state.firstTry ?? {},
      flags: Object.keys(state.flags).filter(k => state.flags[k]),
      score: bySection,
      items: graded,
      userAgent: navigator.userAgent,
    };
  }

  function leaveStep() {
    if (state.step >= 0 && state.step < steps.length) {
      const sid = steps[state.step].id;
      state.sectionTime[sid] = (state.sectionTime[sid] ?? 0) + Math.min((Date.now() - stepEnter) / 1000, 1800);
    }
    stepEnter = Date.now();
  }

  function go(n, focusId) {
    leaveStep();
    state.step = n;
    save();
    render();
    const target = focusId && document.getElementById(`q-${focusId}`);
    if (target) target.scrollIntoView({ block: "center" });
    else window.scrollTo(0, 0);
  }

  function startClock() {
    clearInterval(tick);
    let warned = false;
    const upd = () => {
      const sec = (Date.now() - state.startedAt) / 1000;
      if (!timeLimit) { timerEl.textContent = `⏱ ${fmt(sec)}`; return; }
      const left = timeLimit - sec;
      timerEl.textContent = left > 0 ? `⏱ ${fmt(left)} kvar` : `⏱ Tiden är slut (+${fmt(-left)})`;
      timerEl.className = `timer ${left <= 0 ? "over" : left <= 300 ? "warn" : ""}`;
      if (left <= 0 && !warned && !state.timeUpShown) {
        warned = true;
        state.timeUpShown = true;
        save();
        showModal(`<h2>Tiden är slut</h2><p>På riktiga provet lämnar du in nu. Du kan lämna in direkt, eller göra klart – då markeras provet som <i>övertid</i>.</p>${en("Time is up. Submit now, or finish (marked as overtime).")}`,
          [["Fortsätt ändå", null, "secondary"], ["Lämna in", () => go(steps.length)]]);
      }
    };
    upd();
    tick = setInterval(upd, 1000);
  }

  function allItems() {
    return steps.flatMap((s, si) => (s.parts ?? [s]).flatMap(p => (p.items ?? []).filter(it => it.type !== "info").map(it => ({ ...it, options: it.options ?? p.options, section: s.id, step: si, audio: it.audio ?? p.audio, passage: p.passage }))));
  }

  function answered(id) {
    if (state.uploads?.[id]?.length) return true;
    const a = state.answers[id];
    return !(a == null || a === "" || (Array.isArray(a) && !a.length) || (typeof a === "object" && !Array.isArray(a) && !a.recording));
  }

  function render() {
    window.speechSynthesis?.cancel();
    setMode(exam ? "exam" : null);
    if (state.step === -1) return renderIntro();
    if (state.startedAt) startClock();
    if (state.step >= steps.length) return renderSubmit();
    renderSection(steps[state.step]);
  }

  function renderIntro() {
    const items = allItems();
    app.innerHTML = `
      <a class="back" href="#/">← Startsidan</a>
      <div class="intro ${exam ? "exam-intro" : ""}">
        <div class="muted small">${exam ? "PROV" : "LEKTION"}</div>
        <h1>${esc(lesson.title)}</h1>${exam ? "" : en(lesson.titleEn)}
        <p>${esc(lesson.intro)}</p>${exam ? "" : en(lesson.introEn)}
        ${lesson.generated && !lesson.generated.reviewed ? `<p class="badge gen-badge">Gjord av den lokala modellen ${esc(lesson.generated.model)} · inte granskad av Claude – det kan finnas fel.</p>` : ""}
        <div class="facts">
          <div><b>${items.length}</b><span>uppgifter</span></div>
          <div><b>${steps.length}</b><span>delar</span></div>
          <div><b>${exam && lesson.timeLimit ? lesson.timeLimit : lesson.minutes ?? "?"}</b><span>${exam && lesson.timeLimit ? "min (tidsgräns)" : "min ungefär"}</span></div>
          ${lesson.scoring ? `<div><b>${lesson.scoring.G ?? lesson.scoring.B1}/${lesson.scoring.max}</b><span>${lesson.scoring.G != null ? "för G (godkänt)" : "för B1"}</span></div>` : ""}
        </div>
        <ol class="toc">${steps.map(s => `<li>${esc(s.title)}${exam ? "" : ` <span class="en">— ${esc(s.titleEn ?? "")}</span>`}</li>`).join("")}</ol>
        ${exam ? `<div class="rules">
          <b>Provregler</b>
          <ul>
            <li>Inga ledtrådar och inga rätta svar förrän du lämnar in.</li>
            <li>Du kan gå fram och tillbaka mellan delarna.</li>
            <li>Markera ⚑ frågor du vill titta på igen.</li>
            ${timeLimit ? `<li>Klockan räknar ner från ${lesson.timeLimit} minuter.</li>` : ""}
          </ul>
        </div>` : ""}
      </div>
      <div class="nav">
        <span></span>
        <button class="btn big" id="start">${state.startedAt ? "Fortsätt" : exam ? "Starta provet" : "Börja"} →</button>
      </div>`;
    document.getElementById("start").onclick = () => {
      state.startedAt ??= Date.now();
      go(Object.keys(state.answers).length ? Math.max(state.lastStep ?? 0, 0) : 0);
    };
  }

  function sectionHeader(sec) {
    if (exam) {
      return `<div class="exam-tabs">${steps.map((s, i) => {
        const its = allItems().filter(x => x.step === i);
        const done = its.filter(x => answered(x.id)).length;
        return `<button data-step="${i}" class="${i === state.step ? "on" : ""}">${esc(s.title)} <span class="count">${done}/${its.length}</span></button>`;
      }).join("")}</div>`;
    }
    return `<div class="lesson-head">
      <div class="progress">${steps.map((_, i) => `<span class="${i < state.step ? "done" : i === state.step ? "cur" : ""}"></span>`).join("")}</div>
      <div class="lesson-meta"><span class="muted small">Del ${state.step + 1} av ${steps.length}</span><span id="live" class="live-score"></span></div>
    </div>`;
  }

  function updateLive() {
    const el = document.getElementById("live");
    if (!el) return;
    const ft = state.firstTry ?? {};
    const keys = Object.keys(ft);
    el.textContent = keys.length ? `✓ ${keys.filter(k => ft[k]).length} av ${keys.length} rätt första gången` : "";
  }

  function renderSection(sec) {
    state.lastStep = state.step;
    let n = 0;
    const offset = (lesson.numberStart ?? 1) - 1 + steps.slice(0, state.step).reduce((a, s) => a + (s.parts ?? [s]).flatMap(p => p.items ?? []).filter(i => i.type !== "info").length, 0);
    const hasPassage = (sec.parts ?? [sec]).some(p => p.passage);
    if (!exam) setMode(hasPassage ? "wide" : null);
    const el = h(`<div class="${exam ? "exam-view" : "lesson-view"}">
      ${sectionHeader(sec)}
      <h1 class="sec-title">${esc(sec.title)}</h1>${exam ? "" : en(sec.titleEn)}
      ${sec.instructions ? `<p class="instructions">${esc(sec.instructions)}</p>${exam ? "" : en(sec.instructionsEn)}` : ""}
      <div id="blocks"></div>
      <div class="nav">
        <button class="btn secondary" id="prev" ${state.step === 0 ? "disabled" : ""}>← Föregående</button>
        <button class="btn" id="next">${state.step === steps.length - 1 ? (exam ? "Granska och lämna in" : "Lämna in") : "Nästa del"} →</button>
      </div>
      ${exam ? `<div class="qnav-wrap"><div class="qnav">${allItems().map((it, i) => `<button data-id="${it.id}" data-step="${it.step}" class="${answered(it.id) ? "ans" : ""} ${state.flags[it.id] ? "flag" : ""} ${it.step === state.step ? "here" : ""}" title="${answered(it.id) ? "besvarad" : "obesvarad"}">${i + (lesson.numberStart ?? 1)}</button>`).join("")}</div>
        <div class="qnav-legend muted small"><span class="lg ans"></span> besvarad <span class="lg"></span> obesvarad <span class="lg flag"></span> markerad</div></div>` : ""}
    </div>`);
    app.replaceChildren(el);
    const blocks = el.querySelector("#blocks");
    for (const [pi, part] of (sec.parts ?? [{ items: sec.items, passage: sec.passage, audio: sec.audio, image: sec.image }]).entries()) {
      const split = !!part.passage;
      const card = h(`<div class="card part ${split ? "split" : ""}"></div>`);
      const left = split ? h(`<div class="part-text"></div>`) : card;
      const right = split ? h(`<div class="part-qs"></div>`) : card;
      if (split) card.append(left, right);
      if (part.heading) left.append(h(`<div class="part-head"><h2>${esc(part.heading)}</h2>${exam ? "" : en(part.headingEn)}</div>`));
      if (part.image) left.append(renderImage(part.image));
      if (part.passage) left.append(h(`<div class="passage">${part.passageTitle ? `<h3>${esc(part.passageTitle)}</h3>` : ""}<div class="passage-body" data-hl="p:${esc(sec.id)}:${pi}">${esc(part.passage).replace(/\((\d{1,2})\)/g, '<b class="sn">$1</b>')}</div></div>`));
      if (part.audio) right.append(renderPlayer(part.audio));
      if (part.options && !part.passage && isCompact(part.options)) right.append(h(`<ol class="optlist" type="A">${part.options.map(o => `<li>${esc(o)}</li>`).join("")}</ol>`));
      for (const raw of part.items ?? []) {
        const item = { ...raw, options: raw.options ?? part.options };
        if (item.type === "info") {
          const box = h(`<div class="teach"><div class="teach-label">💡 Så funkar det</div></div>`);
          if (item.image) box.append(renderImage(item.image));
          box.append(h(`<div class="md">${md(item.md)}${exam ? "" : en(item.mdEn)}</div>`));
          right.append(box);
          continue;
        }
        n++;
        const itemEl = renderItem(item, offset + n);
        if (item.image) itemEl.prepend(renderImage(item.image));
        if (exam) itemEl.append(flagButton(item));
        else if (AUTO.has(item.type)) attachCheck(itemEl, item);
        right.append(itemEl);
      }
      blocks.append(card);
    }
    el.querySelectorAll("[data-hl]").forEach(paintMarks);
    el.addEventListener("mouseup", addMark);
    el.addEventListener("touchend", () => setTimeout(addMark, 0));
    el.addEventListener("click", e => {
      const m = e.target.closest("mark.hl");
      if (m && getSelection().isCollapsed) removeMark(m);
    });
    el.querySelector("#prev").onclick = () => go(state.step - 1);
    el.querySelector("#next").onclick = () => go(state.step + 1);
    el.querySelectorAll(".exam-tabs button").forEach(b => b.onclick = () => go(Number(b.dataset.step)));
    el.querySelectorAll(".qnav button").forEach(b => b.onclick = () => {
      const step = Number(b.dataset.step);
      if (step === state.step) document.getElementById(`q-${b.dataset.id}`)?.scrollIntoView({ block: "center", behavior: "smooth" });
      else go(step, b.dataset.id);
    });
    if (exam) el.addEventListener("input", refreshExamNav), el.addEventListener("change", refreshExamNav), el.addEventListener("click", e => { if (e.target.closest(".chip")) setTimeout(refreshExamNav, 0); });
    updateLive();
  }

  function textOffset(box, node, offset) {
    const r = document.createRange();
    r.setStart(box, 0);
    r.setEnd(node, offset);
    return r.toString().length;
  }

  function addMark() {
    const sel = getSelection();
    if (!sel.rangeCount || sel.isCollapsed) return;
    const range = sel.getRangeAt(0);
    const box = range.commonAncestorContainer.nodeType === 1
      ? range.commonAncestorContainer.closest("[data-hl]")
      : range.commonAncestorContainer.parentElement.closest("[data-hl]");
    if (!box) return;
    const a = textOffset(box, range.startContainer, range.startOffset);
    const b = textOffset(box, range.endContainer, range.endOffset);
    if (b - a < 1) return;
    const key = box.dataset.hl;
    const list = [...(state.marks[key] ?? []), [a, b]].sort((x, y) => x[0] - y[0]);
    const merged = [];
    for (const m of list) {
      const last = merged.at(-1);
      if (last && m[0] <= last[1]) last[1] = Math.max(last[1], m[1]);
      else merged.push([...m]);
    }
    state.marks[key] = merged;
    sel.removeAllRanges();
    paintMarks(box);
    save();
  }

  function removeMark(mark) {
    const box = mark.closest("[data-hl]");
    const at = textOffset(box, mark.firstChild, 0);
    state.marks[box.dataset.hl] = (state.marks[box.dataset.hl] ?? []).filter(([a, b]) => !(a <= at && at < b));
    paintMarks(box);
    save();
  }

  function paintMarks(box) {
    box.dataset.orig ??= box.innerHTML;
    box.innerHTML = box.dataset.orig;
    const marks = state.marks[box.dataset.hl] ?? [];
    if (!marks.length) return;
    const walker = document.createTreeWalker(box, NodeFilter.SHOW_TEXT);
    const nodes = [];
    for (let n = walker.nextNode(), pos = 0; n; n = walker.nextNode()) {
      nodes.push([n, pos]);
      pos += n.length;
    }
    for (const [node, start] of nodes) {
      const end = start + node.length;
      const cuts = marks.filter(([a, b]) => a < end && b > start).map(([a, b]) => [Math.max(a, start) - start, Math.min(b, end) - start]);
      for (const [a, b] of cuts.reverse()) {
        const mid = node.splitText(a);
        mid.splitText(b - a);
        const m = document.createElement("mark");
        m.className = "hl";
        mid.replaceWith(m);
        m.append(mid);
      }
    }
  }

  function refreshExamNav() {
    document.querySelectorAll(".qnav button").forEach(b => {
      b.classList.toggle("ans", answered(b.dataset.id));
      b.classList.toggle("flag", !!state.flags[b.dataset.id]);
    });
    document.querySelectorAll(".exam-tabs button").forEach(b => {
      const its = allItems().filter(x => x.step === Number(b.dataset.step));
      b.querySelector(".count").textContent = `${its.filter(x => answered(x.id)).length}/${its.length}`;
    });
  }

  function flagButton(item) {
    const b = h(`<button class="flag-btn ${state.flags[item.id] ? "on" : ""}" type="button">⚑ ${state.flags[item.id] ? "Markerad" : "Markera"}</button>`);
    b.onclick = () => {
      state.flags[item.id] = !state.flags[item.id];
      b.classList.toggle("on", state.flags[item.id]);
      b.textContent = `⚑ ${state.flags[item.id] ? "Markerad" : "Markera"}`;
      save();
      refreshExamNav();
    };
    return b;
  }

  function renderPlayer(audio) {
    const max = audio.maxPlays ?? 2;
    const el = h(`<div class="player">
      <button class="btn play">▶ Spela upp</button>
      <div class="plays"></div>
      ${audio.context ? `<span>${esc(audio.context)}</span>` : ""}
    </div>`);
    const btn = el.querySelector("button");
    const plays = el.querySelector(".plays");
    const upd = () => {
      const used = state.plays[audio.id] ?? 0;
      plays.innerHTML = Array.from({ length: max }, (_, i) => `<span class="dot ${i < used ? "used" : ""}"></span>`).join("") + `<span class="muted small">${max - used} kvar</span>`;
      btn.disabled = used >= max;
    };
    upd();
    const strict = audio.strict !== false;
    if (strict && !(state.plays[audio.id] >= max)) btn.textContent = `▶ Spela upp (${max} gånger i rad)`;
    btn.onclick = async () => {
      btn.disabled = true;
      el.classList.add("playing");
      do {
        state.plays[audio.id] = (state.plays[audio.id] ?? 0) + 1;
        save();
        upd();
        btn.disabled = true;
        btn.textContent = `🔊 Spelar… (${state.plays[audio.id]}/${max})`;
        await playAudio(lesson.id, audio);
        if (strict && state.plays[audio.id] < max) await new Promise(r => setTimeout(r, 2000));
      } while (strict && state.plays[audio.id] < max);
      el.classList.remove("playing");
      btn.textContent = "▶ Spela upp";
      upd();
    };
    return el;
  }

  function renderImage(img) {
    const src = /^(https?:)?\//.test(img.src) ? img.src : `/images/${lesson.id}/${img.src}`;
    const cap = [img.caption ? esc(img.caption) : "", img.credit ? `<span class="credit">${esc(img.credit)}</span>` : ""].filter(Boolean).join(" ");
    return h(`<figure class="lesson-img${img.size ? " " + esc(img.size) : ""}"><img src="${esc(src)}" alt="${esc(img.alt)}" loading="lazy">${cap ? `<figcaption>${cap}</figcaption>` : ""}</figure>`);
  }

  function renderItem(item, num) {
    const wrap = h(`<div class="item" id="q-${esc(item.id)}"></div>`);
    const qEn = exam ? "" : en(item.qEn);
    const q = item.q ? `<div class="q"><span class="qnum">${num}</span><span data-hl="q:${esc(item.id)}">${esc(item.q)}</span></div>${qEn}` : `<span class="qnum">${num}</span>`;
    const set = v => { state.answers[item.id] = v; save(); };
    const cur = state.answers[item.id];

    if (item.type === "mcq" || item.type === "select") {
      const compact = isCompact(item.options);
      const yn = !compact && item.options.length === 2 && item.options.every(o => o.length < 8);
      const parts = o => {
        const m = o.match(/^([A-Z])\.\s*(.*)$/);
        return m ? [m[1], m[2]] : [null, o];
      };
      wrap.innerHTML = `${q}<div class="options ${yn ? "inline" : compact ? "grid" : ""}">${item.options.map((o, i) => {
        const [k, text] = parts(o);
        const wide = compact && /\s/.test(o);
        const inner = compact
          ? `<span>${esc(wide ? o : (k ?? o))}</span>`
          : `${yn ? "" : `<span class="key">${k ?? String.fromCharCode(65 + i)}</span>`}<span>${esc(text)}</span>`;
        return `<label class="opt ${cur === i ? "sel" : ""}${wide ? " wide" : ""}" title="${esc(o)}"><input type="radio" name="${item.id}" value="${i}" ${cur === i ? "checked" : ""}>${inner}</label>`;
      }).join("")}</div>`;
      wrap.querySelectorAll("input").forEach(inp => inp.onchange = () => {
        set(Number(inp.value));
        wrap.querySelectorAll(".opt").forEach(o => o.classList.toggle("sel", o.contains(inp)));
      });
    } else if (item.type === "short") {
      wrap.innerHTML = `${q}<input class="gap wide-in" autocomplete="off" spellcheck="false" placeholder="1–5 ord" value="${esc(cur ?? "")}">`;
      wrap.querySelector("input").oninput = e => set(e.target.value);
    } else if (item.type === "gap") {
      const [before, after] = item.q.split("___");
      wrap.innerHTML = `<div class="q"><span class="qnum">${num}</span>${esc(before)}<input class="gap" autocomplete="off" autocapitalize="off" spellcheck="false" value="${esc(cur ?? "")}">${esc(after ?? "")}${item.base ? ` <span class="base">(${esc(item.base)})</span>` : ""}</div>${qEn}`;
      wrap.querySelector("input").oninput = e => set(e.target.value);
    } else if (item.type === "order") {
      wrap.innerHTML = `${q}<div class="chips built"></div><div class="chips pool"></div>
        <button class="btn secondary sm clear" type="button">Rensa</button>`;
      const built = wrap.querySelector(".built"), pool = wrap.querySelector(".pool");
      let chosen = Array.isArray(cur) ? [...cur] : [];
      const draw = () => {
        built.innerHTML = chosen.map((wi, pos) => `<button type="button" class="chip" data-pos="${pos}">${esc(item.words[wi])}</button>`).join("");
        pool.innerHTML = item.words.map((w, wi) => `<button type="button" class="chip ${chosen.includes(wi) ? "used" : ""}" data-wi="${wi}">${esc(w)}</button>`).join("");
        built.querySelectorAll(".chip").forEach(c => c.onclick = () => { chosen.splice(Number(c.dataset.pos), 1); set([...chosen]); draw(); });
        pool.querySelectorAll(".chip").forEach(c => c.onclick = () => { chosen.push(Number(c.dataset.wi)); set([...chosen]); draw(); });
      };
      wrap.querySelector("button.clear").onclick = () => { chosen = []; set([]); draw(); };
      draw();
    } else if (item.type === "write") {
      wrap.innerHTML = `${q}${item.bullets ? `<ul>${item.bullets.map(b => `<li>${esc(b)}</li>`).join("")}</ul>` : ""}
        <textarea spellcheck="false" autocorrect="off" placeholder="Skriv här… eller ladda upp ett foto av din handskrivna text nedan.">${esc(cur ?? "")}</textarea>
        <div class="wordcount"></div>
        <div class="upload">
          <label class="btn secondary sm">📷 Ladda upp foto av handskriven text
            <input type="file" accept="image/*" multiple hidden>
          </label>
          <span class="en">Upload a photo of your handwritten text (several pages ok). Write clearly.</span>
          <div class="thumbs"></div>
        </div>`;
      const ta = wrap.querySelector("textarea"), wc = wrap.querySelector(".wordcount");
      const thumbs = wrap.querySelector(".thumbs"), file = wrap.querySelector("input[type=file]");
      const drawThumbs = () => {
        const files = state.uploads?.[item.id] ?? [];
        thumbs.innerHTML = files.map((f, i) => `<div class="thumb"><a href="/uploads/${esc(f)}" target="_blank"><img src="/uploads/${esc(f)}" alt="sida ${i + 1}"></a><button type="button" data-i="${i}" title="Ta bort">✕</button></div>`).join("");
        thumbs.querySelectorAll("button").forEach(b => b.onclick = () => {
          state.uploads[item.id].splice(Number(b.dataset.i), 1);
          save();
          drawThumbs();
        });
      };
      file.onchange = async () => {
        for (const f of file.files) {
          thumbs.insertAdjacentHTML("beforeend", `<span class="muted uploading">Laddar upp…</span>`);
          const jpg = await toJpeg(f);
          const body = jpg ?? f;
          const ext = jpg ? "jpg" : (f.name.split(".").pop() || "jpg").toLowerCase();
          const r = await fetch(`/api/upload?name=${lesson.id}__${item.id}&ext=${encodeURIComponent(ext)}`, { method: "POST", body })
            .then(r => r.json()).catch(() => ({}));
          if (r.saved) {
            state.uploads ??= {};
            (state.uploads[item.id] ??= []).push(r.saved);
            save();
          } else {
            alert(r.error ?? "Uppladdningen misslyckades. Använd JPG eller PNG.");
          }
          drawThumbs();
        }
        file.value = "";
      };
      drawThumbs();
      const count = () => {
        const words = ta.value.trim().split(/\s+/).filter(Boolean).length;
        wc.textContent = `${words} ord${item.minWords ? ` (mål: ${item.minWords}–${item.maxWords})` : ""}`;
      };
      ta.oninput = () => { set(ta.value); count(); };
      count();
    } else if (item.type === "speak") {
      wrap.append(...h(`<div>${q}${item.bullets ? `<ul>${item.bullets.map(b => `<li>${esc(b)}</li>`).join("")}</ul>` : ""}</div>`).childNodes);
      if (item.audio) wrap.append(renderPlayer(item.audio));
      wrap.append(renderRecorder(item, set));
    }
    return wrap;
  }

  function renderRecorder(item, set) {
    const cur = state.answers[item.id] ?? {};
    const el = h(`<div class="player recorder">
      <div class="rec-row">
        <button class="btn rec" type="button">● Spela in</button>
        <span class="muted rtime">Max ${fmt(item.maxSeconds ?? 120)}</span>
        <span class="muted saved">${cur.recording ? "✓ Inspelning sparad" : ""}</span>
      </div>
      <div class="live"></div>
      <audio controls style="width:100%;display:${cur.recording ? "block" : "none"}"></audio>
    </div>`);
    const btn = el.querySelector("button"), rtime = el.querySelector(".rtime"), saved = el.querySelector(".saved");
    const live = el.querySelector(".live"), player = el.querySelector("audio");
    if (cur.transcript) live.textContent = cur.transcript;
    let rec = null, chunks = [], t0 = 0, iv = null, recog = null, finalText = "";

    const stop = () => {
      if (rec?.state === "recording") rec.stop();
      recog?.stop();
      clearInterval(iv);
      el.classList.remove("recording");
    };

    btn.onclick = async () => {
      if (rec?.state === "recording") return stop();
      let stream;
      try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
      catch { live.textContent = "Mikrofonen är blockerad. Tillåt mikrofon i webbläsaren."; return; }
      const mime = ["audio/webm;codecs=opus", "audio/mp4", "audio/webm"].find(m => MediaRecorder.isTypeSupported(m)) ?? "";
      rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
      chunks = [];
      rec.ondataavailable = e => chunks.push(e.data);
      rec.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        btn.textContent = "● Spela in igen";
        const blob = new Blob(chunks, { type: rec.mimeType });
        player.src = URL.createObjectURL(blob);
        player.style.display = "block";
        const ext = rec.mimeType.includes("mp4") ? "m4a" : "webm";
        saved.textContent = "Sparar…";
        const r = await fetch(`/api/recording?name=${lesson.id}__${item.id}&ext=${ext}`, { method: "POST", body: blob }).then(r => r.json());
        const seconds = Math.round((Date.now() - t0) / 1000);
        set({ recording: r.saved, transcript: finalText.trim(), seconds });
        saved.textContent = "✓ Inspelning sparad";
        if (exam) refreshExamNav();
      };
      rec.start();
      t0 = Date.now();
      el.classList.add("recording");
      btn.textContent = "■ Stoppa";
      const max = item.maxSeconds ?? 120;
      iv = setInterval(() => {
        const s = (Date.now() - t0) / 1000;
        rtime.textContent = `${fmt(s)} / ${fmt(max)}`;
        if (s >= max) stop();
      }, 250);
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      finalText = "";
      live.textContent = "";
      if (SR) {
        recog = new SR();
        recog.lang = "sv-SE";
        recog.continuous = true;
        recog.interimResults = true;
        recog.onresult = e => {
          let interim = "";
          for (let i = e.resultIndex; i < e.results.length; i++) {
            if (e.results[i].isFinal) finalText += e.results[i][0].transcript + " ";
            else interim += e.results[i][0].transcript;
          }
          live.textContent = finalText + interim;
        };
        recog.onend = () => { if (rec?.state === "recording") try { recog.start(); } catch {} };
        try { recog.start(); } catch {}
      }
    };
    return el;
  }

  function attachCheck(itemEl, item) {
    const el = h(`<div class="check"><button class="btn secondary sm" type="button">Kontrollera</button><div class="fb"></div></div>`);
    const btn = el.querySelector("button");
    const fb = el.querySelector(".fb");
    const show = () => {
      const g = grade(item);
      itemEl.classList.toggle("is-ok", !!g.correct);
      itemEl.classList.toggle("is-bad", !g.correct);
      fb.className = `fb review ${g.correct ? "ok" : "bad"}`;
      fb.innerHTML = `${g.correct ? "✓ Rätt!" : `✗ Rätt svar: <b>${esc(g.expected)}</b>`}
        ${item.explain ? `<div class="muted">${esc(item.explain)}</div>` : ""}${en(item.explainEn)}`;
    };
    btn.onclick = () => {
      const a = state.answers[item.id];
      if (a == null || a === "" || (Array.isArray(a) && !a.length)) { fb.className = "fb muted"; fb.textContent = "Svara först."; return; }
      state.firstTry ??= {};
      if (!(item.id in state.firstTry)) state.firstTry[item.id] = grade(item).correct;
      save();
      show();
      updateLive();
    };
    if (item.type === "mcq" || item.type === "select") {
      btn.hidden = true;
      itemEl.addEventListener("change", () => btn.click());
    }
    itemEl.addEventListener("keydown", e => { if (e.key === "Enter" && e.target.tagName === "INPUT") { e.preventDefault(); btn.click(); } });
    if (state.firstTry && item.id in state.firstTry) show();
    itemEl.append(el);
  }

  function grade(item) {
    const a = state.answers[item.id];
    if (item.type === "short") {
      const given = norm(a);
      return { given: a ?? null, expected: item.answers[0], correct: !!given && item.answers.some(x => given.includes(norm(x))), teacherCheck: true };
    }
    if (item.type === "mcq" || item.type === "select") return { given: a == null ? null : item.options[a], expected: item.options[item.answer], correct: a === item.answer };
    if (item.type === "gap") return { given: a ?? null, expected: item.answers[0], correct: item.answers.some(x => norm(x) === norm(a)) };
    if (item.type === "order") {
      const given = Array.isArray(a) ? a.map(i => item.words[i]).join(" ") : null;
      return { given, expected: item.answers[0], correct: item.answers.some(x => norm(x) === norm(given)) };
    }
    return { given: a ?? null, expected: null, correct: null, ...(state.uploads?.[item.id]?.length ? { images: state.uploads[item.id] } : {}) };
  }

  function renderSubmit() {
    const items = allItems();
    const missing = items.filter(i => !answered(i.id));
    const flagged = items.filter(i => state.flags[i.id]);
    const num = id => items.findIndex(i => i.id === id) + (lesson.numberStart ?? 1);
    const jump = list => list.map(i => `<button class="qlink" data-id="${i.id}" data-step="${i.step}">${num(i.id)}</button>`).join("");
    app.innerHTML = `
      ${exam ? sectionHeader(null) : ""}
      <h1>Lämna in</h1><div class="en">Submit</div>
      <div class="card submit-card">
        <div class="facts">
          <div><b>${items.length - missing.length}/${items.length}</b><span>besvarade</span></div>
          ${exam ? `<div><b>${flagged.length}</b><span>markerade</span></div>` : ""}
        </div>
        ${missing.length ? `<p>Obesvarade: ${jump(missing)}</p>` : "<p>✓ Du har svarat på alla uppgifter.</p>"}
        ${flagged.length ? `<p>Markerade ⚑: ${jump(flagged)}</p>` : ""}
        ${exam ? `<p class="muted small">Tips: på Swedex blir det inga minuspoäng. Gissa hellre än att lämna tomt.</p>` : ""}
      </div>
      <div class="nav">
        <button class="btn secondary" id="prev">← Tillbaka</button>
        <button class="btn big" id="submit">Lämna in ✓</button>
      </div>`;
    app.querySelectorAll(".qlink").forEach(b => b.onclick = () => go(Number(b.dataset.step), b.dataset.id));
    app.querySelectorAll(".exam-tabs button").forEach(b => b.onclick = () => go(Number(b.dataset.step)));
    document.getElementById("prev").onclick = () => go(steps.length - 1);
    document.getElementById("submit").onclick = submit;
  }

  async function submit() {
    leaveStep();
    clearTimeout(pushTimer);
    const items = allItems();
    const payload = buildPayload(true);
    const btn = document.getElementById("submit");
    btn.disabled = true;
    const r = await fetch("/api/results", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!r.ok) { btn.disabled = false; alert("Kunde inte spara. Är servern igång?"); return; }
    store.del(draftKey);
    stopClock();
    renderResults(items, payload);
  }

  function renderResults(items, payload) {
    setMode(exam ? "wide" : null);
    const graded = payload.items, bySection = payload.score;
    const auto = graded.filter(g => g.correct !== null);
    const right = auto.filter(g => g.correct).length;
    const ft = Object.values(payload.firstTry);
    const byId = Object.fromEntries(items.map(i => [i.id, i]));
    const shownAudio = new Set(), shownPassage = new Set();
    const sc = lesson.scoring;
    const level = !sc ? null : sc.G != null ? (right >= sc.G ? "G" : "IG") : (right >= sc.B1 ? "B1" : right >= sc.A2 ? "A2" : "under A2");
    const marks = !sc ? [] : Object.entries(sc).filter(([k]) => k !== "max");
    app.innerHTML = `
      <h1>Resultat</h1><div class="en">Results — saved. Your teacher will grade writing and speaking.</div>
      <div class="card result-card">
        <div class="result-top">
          <div class="score">${right}<span>/ ${auto.length}</span></div>
          ${level ? `<div class="level level-${level.replace(" ", "-")}">${sc.G != null ? "Resultat" : "Nivå"}: <b>${level}</b></div>` : ""}
          ${!exam && ft.length ? `<div class="muted">Första försöket: ${ft.filter(Boolean).length} av ${ft.length}</div>` : ""}
          ${payload.overtime ? `<div class="badge warn-badge">Övertid</div>` : ""}
          <div class="muted">${payload.durationMin} min</div>
        </div>
        ${sc ? `<div class="levelbar"><span style="width:${pct(right, sc.max)}%"></span>
          ${marks.map(([k, v]) => `<i style="left:${pct(v, sc.max)}%"><em>${k} ${v}</em></i>`).join("")}</div>` : ""}
        <table class="scores">${steps.filter(s => bySection[s.id]).map(s => {
          const b = bySection[s.id];
          return `<tr><td>${esc(s.title)}</td><td class="mini"><span style="width:${pct(b.correct, b.total)}%"></span></td><td>${b.correct} / ${b.total}</td></tr>`;
        }).join("")}</table>
        ${graded.some(g => g.correct === null) ? `<p class="muted">Skrivande och tal bedöms av läraren.</p>` : ""}
      </div>
      <div class="review-filter"><label><input type="checkbox" id="onlyWrong"> Visa bara fel</label></div>
      <div class="card" id="review">
        <h2>Genomgång</h2><div class="en">Review</div>
        ${graded.map((g, idx) => {
          const it = byId[g.id];
          let extra = "";
          if (it.passage && !shownPassage.has(it.passage)) {
            shownPassage.add(it.passage);
            extra += `<details class="rev-text"><summary>Visa texten</summary><div class="passage-body">${esc(it.passage)}</div></details>`;
          }
          if (it.audio && !shownAudio.has(it.audio.id)) {
            shownAudio.add(it.audio.id);
            const lines = it.audio.script
              ? it.audio.script.map(l => `${l.speaker ? `<b>${esc(l.speaker)}:</b> ` : ""}${esc(l.text)}`).join("\n")
              : esc(it.audio.transcript);
            const credit = it.audio.credit ? `<div class="muted">${esc(it.audio.credit)}</div>` : "";
            extra += `<details><summary>Transkription: ${esc(it.audio.title ?? it.audio.id)}</summary><div class="transcript">${lines}</div>${credit}</details>`;
          }
          const cls = g.correct === null ? "manual" : g.correct ? "ok" : "bad";
          const given = typeof g.given === "object" && g.given ? (g.given.transcript || "(inspelning)") : g.given;
          return `${extra}<div class="review ${cls}">
            <div><span class="qnum">${idx + (lesson.numberStart ?? 1)}</span>${esc(it.q ?? "")}</div>
            ${g.correct === null ? `<div class="muted">Bedöms av läraren.</div>` : `
              <div>Ditt svar: <b>${esc(given ?? "—")}</b></div>
              ${g.correct ? "" : `<div>Rätt svar: <b>${esc(g.expected)}</b></div>`}`}
            ${it.explain ? `<div class="muted">${esc(it.explain)}</div>` : ""}${en(it.explainEn)}
          </div>`;
        }).join("")}
      </div>
      <a class="btn secondary" href="#/">← Till startsidan</a>`;
    app.querySelector("#onlyWrong").onchange = e => app.querySelector("#review").classList.toggle("only-wrong", e.target.checked);
    window.scrollTo(0, 0);
  }

  render();
}

function showModal(html, buttons) {
  const m = h(`<div class="modal-bg"><div class="modal">${html}<div class="nav"></div></div></div>`);
  const nav = m.querySelector(".nav");
  for (const [label, fn, cls] of buttons) {
    const b = h(`<button class="btn ${cls ?? ""}">${esc(label)}</button>`);
    b.onclick = () => { m.remove(); fn?.(); };
    nav.append(b);
  }
  document.body.append(m);
}

async function toJpeg(file, maxSide = 2400) {
  try {
    const bmp = await createImageBitmap(file);
    const scale = Math.min(1, maxSide / Math.max(bmp.width, bmp.height));
    const canvas = document.createElement("canvas");
    canvas.width = Math.round(bmp.width * scale);
    canvas.height = Math.round(bmp.height * scale);
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(bmp, 0, 0, canvas.width, canvas.height);
    return await new Promise(res => canvas.toBlob(res, "image/jpeg", 0.88));
  } catch {
    return null;
  }
}

function playAudio(lessonId, audio) {
  return new Promise(resolve => {
    const urls = audio.clip ? [`/materials/clips/${lessonId}/${audio.id}.m4a`]
      : audio.source ? [`/${audio.source}`]
      : [`/materials/tts/${lessonId}/${audio.id}.m4a`, `/audio/${lessonId}/${audio.id}.m4a`];
    const fallback = () => audio.script
      ? speak(audio.script).then(resolve)
      : (alert("Ljudfilen saknas på den här datorn. (Audio file missing on this computer.)"), resolve());
    const tryUrl = i => {
      if (i >= urls.length) return fallback();
      const el = new Audio(urls[i]);
      let failed = false;
      const next = () => { if (!failed) { failed = true; tryUrl(i + 1); } };
      el.onended = resolve;
      el.onerror = next;
      el.play().catch(next);
    };
    tryUrl(0);
  });
}

function speak(script) {
  return new Promise(resolve => {
    const voices = speechSynthesis.getVoices().filter(v => v.lang.replace("_", "-").startsWith("sv"));
    const speakers = [...new Set(script.map(l => l.speaker ?? ""))];
    let i = 0;
    const next = () => {
      if (i >= script.length) return resolve();
      const line = script[i++];
      const u = new SpeechSynthesisUtterance(line.text);
      u.lang = "sv-SE";
      const si = speakers.indexOf(line.speaker ?? "");
      if (voices.length) u.voice = voices[si % voices.length];
      if (voices.length < 2) u.pitch = si % 2 ? 0.75 : 1.1;
      u.rate = 0.95;
      u.onend = () => setTimeout(next, 450);
      u.onerror = () => setTimeout(next, 100);
      speechSynthesis.speak(u);
    };
    next();
  });
}

(function swedishKeys() {
  const bar = h(`<div class="sv-keys" hidden>${["å", "ä", "ö", "Å", "Ä", "Ö", "é"].map(c => `<button type="button" data-c="${c}">${c}</button>`).join("")}</div>`);
  document.body.append(bar);
  const isText = el => el && (el.tagName === "TEXTAREA" || (el.tagName === "INPUT" && el.type !== "radio" && el.type !== "checkbox"));
  document.addEventListener("focusin", e => { bar.hidden = !isText(e.target); });
  document.addEventListener("focusout", () => setTimeout(() => { if (!isText(document.activeElement)) bar.hidden = true; }, 0));
  bar.addEventListener("mousedown", e => e.preventDefault());
  bar.addEventListener("click", e => {
    const c = e.target.dataset?.c, el = document.activeElement;
    if (!c || !isText(el)) return;
    el.setRangeText(c, el.selectionStart, el.selectionEnd, "end");
    el.dispatchEvent(new Event("input", { bubbles: true }));
  });
})();
