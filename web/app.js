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
const h = html => { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; };

let tick = null;
function startClock(state) {
  clearInterval(tick);
  tick = setInterval(() => {
    const sec = (Date.now() - state.startedAt) / 1000;
    timerEl.textContent = fmt(sec);
  }, 1000);
}
function stopClock() { clearInterval(tick); timerEl.textContent = ""; }

window.addEventListener("hashchange", route);
route();

function route() {
  stopClock();
  window.speechSynthesis?.cancel();
  const [, view, id] = location.hash.split("/");
  if (view === "lesson" && id) return openLesson(id);
  if (view === "feedback" && id) return openFeedback(id);
  return home();
}

async function home() {
  const lessons = await fetch("/api/lessons").then(r => r.json());
  app.innerHTML = `
    <h1>Hej! Välkommen.</h1>
    <p class="muted">Ta ett test i taget. Läraren (Claude) läser dina svar och gör nästa lektion.</p>
    <div class="en">Take one test at a time. Your teacher reads your answers and builds the next lesson.</div>
    ${lessons.map(l => `
      <div class="card lesson-row">
        <div>
          <h2>${esc(l.title)}</h2>
          ${en(l.titleEn)}
          <div class="muted">${l.minutes ? `ca ${l.minutes} min · ` : ""}${l.attempts} försök</div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end">
          ${l.hasFeedback ? `<a class="btn secondary" href="#/feedback/${l.id}">Feedback</a>` : ""}
          <a class="btn" href="#/lesson/${l.id}">${l.attempts ? "Gör igen" : "Starta"}</a>
        </div>
      </div>`).join("")}
  `;
}

async function openFeedback(id) {
  const res = await fetch(`/api/feedback/${id}`);
  const md = res.ok ? await res.text() : "Ingen feedback än.";
  app.innerHTML = `<div class="card md">${window.marked ? marked.parse(md) : `<pre>${esc(md)}</pre>`}</div>
    <a class="btn secondary" href="#/">← Tillbaka</a>`;
}

async function openLesson(id) {
  const lesson = await fetch(`/api/lessons/${id}`).then(r => r.json());
  const draftKey = `draft:${id}`;
  const state = store.get(draftKey, null) ?? {
    step: -1, answers: {}, plays: {}, sectionTime: {}, startedAt: null,
  };
  state.attemptId ??= new Date().toISOString().replace(/[:.]/g, "-");
  let pushTimer = null;
  const save = () => {
    store.set(draftKey, state);
    clearTimeout(pushTimer);
    pushTimer = setTimeout(pushDraft, 600);
  };

  function pushDraft() {
    if (!state.startedAt) return;
    leaveStep();
    store.set(draftKey, state);
    fetch("/api/draft", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(buildPayload(false)) })
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
    return {
      lessonId: lesson.id,
      attemptId: state.attemptId,
      final,
      startedAt: new Date(state.startedAt).toISOString(),
      finishedAt: final ? new Date().toISOString() : null,
      durationMin: Math.round((Date.now() - state.startedAt) / 60000),
      currentSection: steps[state.step]?.id ?? null,
      sectionMinutes: Object.fromEntries(Object.entries(state.sectionTime).map(([k, v]) => [k, Math.round(v / 6) / 10])),
      audioPlays: state.plays,
      score: bySection,
      items: graded,
      userAgent: navigator.userAgent,
    };
  }
  const steps = lesson.sections;
  let stepEnter = Date.now();

  function leaveStep() {
    if (state.step >= 0 && state.step < steps.length) {
      const sid = steps[state.step].id;
      state.sectionTime[sid] = (state.sectionTime[sid] ?? 0) + (Date.now() - stepEnter) / 1000;
    }
    stepEnter = Date.now();
  }

  function go(n) {
    leaveStep();
    state.step = n;
    save();
    render();
    window.scrollTo(0, 0);
  }

  function progress() {
    return `<div class="progress">${steps.map((_, i) =>
      `<span class="${i < state.step ? "done" : i === state.step ? "cur" : ""}"></span>`).join("")}</div>`;
  }

  function render() {
    window.speechSynthesis?.cancel();
    if (state.step === -1) return renderIntro();
    if (state.step >= steps.length) return renderSubmit();
    if (state.startedAt) startClock(state);
    renderSection(steps[state.step]);
  }

  function renderIntro() {
    app.innerHTML = `
      <h1>${esc(lesson.title)}</h1>${en(lesson.titleEn)}
      <div class="card">
        <p>${esc(lesson.intro)}</p>${en(lesson.introEn)}
        <ul>${steps.map(s => `<li>${esc(s.title)} <span class="en">— ${esc(s.titleEn ?? "")}</span></li>`).join("")}</ul>
        ${lesson.minutes ? `<p class="muted">Tid: ca ${lesson.minutes} minuter.</p>` : ""}
      </div>
      <div class="nav">
        <a class="btn secondary" href="#/">← Tillbaka</a>
        <button class="btn" id="start">${state.startedAt ? "Fortsätt" : "Börja"} →</button>
      </div>`;
    document.getElementById("start").onclick = () => {
      state.startedAt ??= Date.now();
      go(Object.keys(state.answers).length ? Math.max(state.lastStep ?? 0, 0) : 0);
    };
  }

  function renderSection(sec) {
    state.lastStep = state.step;
    let n = 0;
    const offset = steps.slice(0, state.step).reduce((a, s) => a + (s.items?.length ?? 0), 0);
    const el = h(`<div>
      ${progress()}
      <h1>${esc(sec.title)}</h1>${en(sec.titleEn)}
      ${sec.instructions ? `<p>${esc(sec.instructions)}</p>${en(sec.instructionsEn)}` : ""}
      <div id="blocks"></div>
      <div class="nav">
        <button class="btn secondary" id="prev">← Tillbaka</button>
        <button class="btn" id="next">${state.step === steps.length - 1 ? "Granska och lämna in" : "Nästa"} →</button>
      </div>
    </div>`);
    app.replaceChildren(el);
    const blocks = el.querySelector("#blocks");
    for (const part of sec.parts ?? [{ items: sec.items, passage: sec.passage, audio: sec.audio }]) {
      const card = h(`<div class="card"></div>`);
      if (part.heading) card.append(h(`<div><h2>${esc(part.heading)}</h2>${en(part.headingEn)}</div>`));
      if (part.passage) card.append(h(`<div class="passage">${part.passageTitle ? `<h3>${esc(part.passageTitle)}</h3>` : ""}${esc(part.passage)}</div>`));
      if (part.audio) card.append(renderPlayer(part.audio));
      if (part.options) card.append(h(`<div class="passage">${part.options.map(o => esc(o)).join("\n")}</div>`));
      for (const item of part.items ?? []) {
        n++;
        card.append(renderItem({ ...item, options: item.options ?? part.options }, offset + n));
      }
      blocks.append(card);
    }
    el.querySelector("#prev").onclick = () => go(state.step - 1);
    el.querySelector("#next").onclick = () => go(state.step + 1);
  }

  function renderPlayer(audio) {
    const max = audio.maxPlays ?? 2;
    const el = h(`<div class="player">
      <button class="btn">▶ Spela upp</button>
      <span class="muted"></span>
      ${audio.context ? `<span>${esc(audio.context)}</span>` : ""}
    </div>`);
    const btn = el.querySelector("button");
    const info = el.querySelector(".muted");
    const upd = () => {
      const used = state.plays[audio.id] ?? 0;
      info.textContent = `Du kan lyssna ${max - used} gång(er) till.`;
      btn.disabled = used >= max;
    };
    upd();
    btn.onclick = async () => {
      state.plays[audio.id] = (state.plays[audio.id] ?? 0) + 1;
      save();
      btn.disabled = true;
      btn.textContent = "🔊 Spelar…";
      await playAudio(lesson.id, audio);
      btn.textContent = "▶ Spela upp";
      upd();
    };
    return el;
  }

  function renderItem(item, num) {
    const wrap = h(`<div class="item"></div>`);
    const q = item.q ? `<div><span class="qnum">${num}.</span>${esc(item.q)}</div>${en(item.qEn)}` : `<span class="qnum">${num}.</span>`;
    const set = v => { state.answers[item.id] = v; save(); };
    const cur = state.answers[item.id];

    if (item.type === "mcq") {
      wrap.innerHTML = `${q}<div class="options">${item.options.map((o, i) => `
        <label class="opt ${cur === i ? "sel" : ""}"><input type="radio" name="${item.id}" value="${i}" ${cur === i ? "checked" : ""}><span>${esc(o)}</span></label>`).join("")}</div>`;
      wrap.querySelectorAll("input").forEach(inp => inp.onchange = () => {
        set(Number(inp.value));
        wrap.querySelectorAll(".opt").forEach(o => o.classList.toggle("sel", o.contains(inp)));
      });
    } else if (item.type === "select") {
      wrap.innerHTML = `${q}<select class="gap"><option value="">– välj –</option>${item.options.map((o, i) =>
        `<option value="${i}" ${cur === i ? "selected" : ""}>${esc(o.split(/\s+/).slice(0, 8).join(" "))}${o.split(/\s+/).length > 8 ? "…" : ""}</option>`).join("")}</select>`;
      wrap.querySelector("select").onchange = e => set(e.target.value === "" ? null : Number(e.target.value));
    } else if (item.type === "short") {
      wrap.innerHTML = `${q}<input class="gap" style="width:100%;margin-top:8px" autocomplete="off" spellcheck="false" placeholder="1–5 ord" value="${esc(cur ?? "")}">`;
      wrap.querySelector("input").oninput = e => set(e.target.value);
    } else if (item.type === "gap") {
      const [before, after] = item.q.split("___");
      wrap.innerHTML = `<div><span class="qnum">${num}.</span>${esc(before)}<input class="gap" autocomplete="off" autocapitalize="off" spellcheck="false" value="${esc(cur ?? "")}">${esc(after ?? "")}${item.base ? ` <span class="muted">(${esc(item.base)})</span>` : ""}</div>${en(item.qEn)}`;
      wrap.querySelector("input").oninput = e => set(e.target.value);
    } else if (item.type === "order") {
      wrap.innerHTML = `${q}<div class="chips built"></div><div class="chips pool"></div>
        <button class="btn secondary" style="padding:4px 12px;font-size:14px">Rensa</button>`;
      const built = wrap.querySelector(".built"), pool = wrap.querySelector(".pool");
      let chosen = Array.isArray(cur) ? [...cur] : [];
      const draw = () => {
        built.innerHTML = chosen.map((wi, pos) => `<button class="chip" data-pos="${pos}">${esc(item.words[wi])}</button>`).join("");
        pool.innerHTML = item.words.map((w, wi) => `<button class="chip ${chosen.includes(wi) ? "used" : ""}" data-wi="${wi}">${esc(w)}</button>`).join("");
        built.querySelectorAll(".chip").forEach(c => c.onclick = () => { chosen.splice(Number(c.dataset.pos), 1); set([...chosen]); draw(); });
        pool.querySelectorAll(".chip").forEach(c => c.onclick = () => { chosen.push(Number(c.dataset.wi)); set([...chosen]); draw(); });
      };
      wrap.querySelector("button.btn").onclick = () => { chosen = []; set([]); draw(); };
      draw();
    } else if (item.type === "write") {
      wrap.innerHTML = `${q}${item.bullets ? `<ul>${item.bullets.map(b => `<li>${esc(b)}</li>`).join("")}</ul>` : ""}
        <textarea spellcheck="false" autocorrect="off" placeholder="Skriv här…">${esc(cur ?? "")}</textarea>
        <div class="wordcount"></div>`;
      const ta = wrap.querySelector("textarea"), wc = wrap.querySelector(".wordcount");
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
    const el = h(`<div class="player" style="flex-direction:column;align-items:stretch">
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <button class="btn rec">● Spela in</button>
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
      };
      rec.start();
      t0 = Date.now();
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

  function allItems() {
    return steps.flatMap(s => (s.parts ?? [s]).flatMap(p => (p.items ?? []).map(it => ({ ...it, options: it.options ?? p.options, section: s.id, audio: it.audio ?? p.audio, passage: p.passage }))));
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
    return { given: a ?? null, expected: null, correct: null };
  }

  function renderSubmit() {
    const items = allItems();
    const missing = items.filter(i => {
      const a = state.answers[i.id];
      return a == null || a === "" || (Array.isArray(a) && !a.length);
    });
    app.innerHTML = `
      ${progress()}
      <h1>Lämna in</h1><div class="en">Submit</div>
      <div class="card">
        ${missing.length ? `<p>Du har inte svarat på ${missing.length} uppgift(er). Du kan gå tillbaka eller lämna in ändå.</p>` : "<p>Du har svarat på alla uppgifter.</p>"}
      </div>
      <div class="nav">
        <button class="btn secondary" id="prev">← Tillbaka</button>
        <button class="btn" id="submit">Lämna in ✓</button>
      </div>`;
    document.getElementById("prev").onclick = () => go(steps.length - 1);
    document.getElementById("submit").onclick = submit;
  }

  async function submit() {
    leaveStep();
    clearTimeout(pushTimer);
    const items = allItems();
    const payload = buildPayload(true);
    const graded = payload.items;
    const bySection = payload.score;
    const btn = document.getElementById("submit");
    btn.disabled = true;
    const r = await fetch("/api/results", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!r.ok) { btn.disabled = false; alert("Kunde inte spara. Är servern igång?"); return; }
    store.del(draftKey);
    stopClock();
    renderResults(items, graded, bySection);
  }

  function renderResults(items, graded, bySection) {
    const auto = graded.filter(g => g.correct !== null);
    const right = auto.filter(g => g.correct).length;
    const byId = Object.fromEntries(items.map(i => [i.id, i]));
    const shownAudio = new Set();
    app.innerHTML = `
      <h1>Resultat</h1><div class="en">Results — saved. Tell your teacher you are done.</div>
      <div class="card">
        <div class="score">${right} / ${auto.length}</div>
        <table class="scores">${steps.filter(s => bySection[s.id]).map(s => `<tr><td>${esc(s.title)}</td><td>${bySection[s.id].correct} / ${bySection[s.id].total}</td></tr>`).join("")}</table>
        <p class="muted">Skrivande och tal bedöms av läraren.</p>
      </div>
      <div class="card">
        <h2>Genomgång</h2><div class="en">Review</div>
        ${graded.map((g, idx) => {
          const it = byId[g.id];
          let audioHtml = "";
          if (it.audio && !shownAudio.has(it.audio.id)) {
            shownAudio.add(it.audio.id);
            audioHtml = `<details><summary>Transkription: ${esc(it.audio.title ?? it.audio.id)}</summary><div class="transcript">${it.audio.script.map(l => `${l.speaker ? `<b>${esc(l.speaker)}:</b> ` : ""}${esc(l.text)}`).join("\n")}</div></details>`;
          }
          const cls = g.correct === null ? "manual" : g.correct ? "ok" : "bad";
          const given = typeof g.given === "object" && g.given ? (g.given.transcript || "(inspelning)") : g.given;
          return `${audioHtml}<div class="review ${cls}">
            <div><span class="qnum">${idx + 1}.</span>${esc(it.q ?? "")}</div>
            ${g.correct === null ? `<div class="muted">Bedöms av läraren.</div>` : `
              <div>Ditt svar: <b>${esc(given ?? "—")}</b></div>
              ${g.correct ? "" : `<div>Rätt svar: <b>${esc(g.expected)}</b></div>`}`}
            ${it.explain ? `<div class="muted">${esc(it.explain)}</div>` : ""}${en(it.explainEn)}
          </div>`;
        }).join("")}
      </div>
      <a class="btn secondary" href="#/">← Till startsidan</a>`;
    window.scrollTo(0, 0);
  }

  render();
}

function playAudio(lessonId, audio) {
  return new Promise(resolve => {
    const el = new Audio(`/audio/${lessonId}/${audio.id}.m4a`);
    el.onended = resolve;
    el.onerror = () => speak(audio.script).then(resolve);
    el.play().catch(() => speak(audio.script).then(resolve));
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
