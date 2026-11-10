(() => {
  const DEFAULTS = { model: 'gemma3:4b', enMode: 'show', scale: 1, enabled: true, svSource: 'human' };
  const SOURCE_LABEL = { human: 'made by people', asr: 'auto-generated' };
  const EN_MODES = ['show', 'blur', 'hidden'];
  const S = { settings: { ...DEFAULTS }, videoId: null, key: null, tracks: {}, active: null, cues: [], gen: 0, shown: -2, fontPx: 0 };
  let overlay, svEl, enEl, statusEl, statusTimer, hintTimer;

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const player = () => document.querySelector('#movie_player');
  const video = () => document.querySelector('#movie_player video');

  chrome.storage.sync.get(DEFAULTS).then(s => {
    S.settings = { ...DEFAULTS, ...s };
    applyMode();
  });
  chrome.storage.onChanged.addListener((changes, area) => {
    if (area !== 'sync') return;
    const before = { ...S.settings };
    for (const [k, v] of Object.entries(changes)) S.settings[k] = v.newValue;
    applyMode();
    S.fontPx = 0;
    S.shown = -2;
    if (changes.svSource) choose();
    else if (S.cues.length && (before.model !== S.settings.model || changes.enabled)) restart();
  });

  function ensureUi() {
    const p = player();
    if (!p) return null;
    if (!overlay) {
      overlay = document.createElement('div');
      overlay.className = 'yds-overlay yds-none';
      overlay.innerHTML = '<div class="yds-sv-row"><span class="yds-line yds-sv" title="Click: replay this line"></span></div>'
        + '<div class="yds-en-row"><span class="yds-line yds-en"></span></div>';
      svEl = overlay.querySelector('.yds-sv');
      enEl = overlay.querySelector('.yds-en');
      for (const ev of ['click', 'mousedown', 'dblclick']) overlay.addEventListener(ev, e => e.stopPropagation());
      svEl.addEventListener('click', () => {
        const cue = S.cues[S.shown];
        const v = video();
        if (cue && v) v.currentTime = cue.start / 1000;
      });
      statusEl = document.createElement('div');
      statusEl.className = 'yds-status yds-hide';
      applyMode();
    }
    if (!p.contains(overlay)) p.append(overlay, statusEl);
    return p;
  }

  function applyMode() {
    if (overlay) overlay.dataset.en = S.settings.enMode;
  }

  function status(text, { error = false, hideAfter = 0 } = {}) {
    if (!ensureUi()) return;
    clearTimeout(statusTimer);
    statusEl.textContent = text;
    statusEl.classList.toggle('yds-error', error);
    statusEl.classList.remove('yds-hide');
    if (hideAfter) statusTimer = setTimeout(() => statusEl.classList.add('yds-hide'), hideAfter);
  }

  function hideStatus() {
    clearTimeout(statusTimer);
    statusEl?.classList.add('yds-hide');
  }

  function reset(videoId) {
    S.gen++;
    S.videoId = videoId;
    S.key = null;
    S.tracks = {};
    S.active = null;
    S.cues = [];
    S.shown = -2;
    player()?.classList.remove('yds-active');
    overlay?.classList.add('yds-none');
    hideStatus();
  }

  window.addEventListener('message', e => {
    if (e.source !== window || e.data?.source !== 'yt-dual-subs') return;
    onTrack(e.data.url, e.data.body);
  });

  function onTrack(url, body) {
    const p = new URL(url, location.origin).searchParams;
    const v = p.get('v');
    const lang = (p.get('lang') ?? '').toLowerCase();
    if (p.get('tlang')) return;
    if (v && v !== S.videoId) reset(v);
    if (!lang.startsWith('sv')) return;
    const kind = p.get('kind') === 'asr' ? 'asr' : 'human';
    if (S.tracks[kind]) return;
    let cues;
    try {
      cues = YDS.toCues(body, kind === 'asr');
    } catch (err) {
      return;
    }
    if (!cues.length) return;
    clearTimeout(hintTimer);
    S.tracks[kind] = cues;
    choose();
  }

  function choose() {
    const want = S.settings.svSource;
    const pick = S.tracks[want] ? want : Object.keys(S.tracks)[0];
    if (!pick || pick === S.active) return;
    S.active = pick;
    S.key = `${S.videoId}:${pick}`;
    S.cues = S.tracks[pick].map(c => ({ ...c, en: null }));
    restart();
  }

  function sourceNote() {
    const want = S.settings.svSource;
    const note = `Swedish: ${SOURCE_LABEL[S.active]}`;
    return S.active === want ? note : `${note} (no ${SOURCE_LABEL[want]} track yet)`;
  }

  const cacheKey = () => `yds:${S.key}:${S.settings.model}`;

  async function restart() {
    const gen = ++S.gen;
    S.shown = -2;
    for (const c of S.cues) c.en = null;
    if (!S.settings.enabled) {
      player()?.classList.remove('yds-active');
      overlay?.classList.add('yds-none');
      hideStatus();
      return;
    }
    ensureUi()?.classList.add('yds-active');
    try {
      const k = cacheKey();
      const cached = (await chrome.storage.local.get(k))[k];
      if (gen !== S.gen) return;
      if (Array.isArray(cached) && cached.length === S.cues.length) cached.forEach((en, i) => { S.cues[i].en = en; });
    } catch (e) {}
    translateLoop(gen);
  }

  function nextIndex() {
    const t = (video()?.currentTime ?? 0) * 1000;
    const i = S.cues.findIndex(c => c.en === null && c.end >= t - 1000);
    return i >= 0 ? i : S.cues.findIndex(c => c.en === null);
  }

  async function saveCache() {
    try {
      await chrome.storage.local.set({ [cacheKey()]: S.cues.map(c => c.en) });
    } catch (e) {}
  }

  async function translateLoop(gen) {
    const total = S.cues.length;
    while (gen === S.gen) {
      const idx = nextIndex();
      if (idx < 0) break;
      const batch = [];
      for (let i = idx; i < S.cues.length && batch.length < 10 && S.cues[i].en === null; i++) batch.push(i);
      const done = S.cues.filter(c => c.en !== null).length;
      status(`${sourceNote()} · translating ${done}/${total} (${S.settings.model})…`);
      let res;
      try {
        res = await chrome.runtime.sendMessage({
          type: 'translate',
          lines: batch.map(i => S.cues[i].sv),
          context: S.cues.slice(Math.max(0, idx - 3), idx).map(c => c.sv),
        });
      } catch (e) {
        status('YT Dual Subs was reloaded. Refresh this page.', { error: true });
        return;
      }
      if (gen !== S.gen) return;
      if (!res?.ok) {
        const hint = res?.status === 403
          ? 'Ollama refused the request (403). Run: launchctl setenv OLLAMA_ORIGINS "chrome-extension://*" and restart Ollama.'
          : res?.status === 404 ? `Model "${S.settings.model}" not found in Ollama. Pick another in the extension popup.`
          : `Ollama error: ${res?.error ?? 'unknown'}. Is Ollama running?`;
        status(hint, { error: true });
        await sleep(res?.status === 403 ? 20000 : 5000);
        continue;
      }
      batch.forEach((i, k) => { S.cues[i].en = res.translations[k] || '—'; });
      S.shown = -2;
      saveCache();
    }
    if (gen === S.gen) status(`${sourceNote()} · ${total} lines translated`, { hideAfter: 3000 });
  }

  function render() {
    requestAnimationFrame(render);
    if (!S.cues.length || !S.settings.enabled) return;
    const p = ensureUi();
    const v = video();
    if (!p || !v) return;
    const h = p.clientHeight;
    const px = Math.round(Math.max(14, h * 0.042) * S.settings.scale);
    if (px !== S.fontPx) {
      S.fontPx = px;
      overlay.style.fontSize = `${px}px`;
    }
    const idx = YDS.cueAt(S.cues, v.currentTime * 1000);
    if (idx === S.shown) return;
    S.shown = idx;
    if (idx < 0) {
      overlay.classList.add('yds-none');
      return;
    }
    const cue = S.cues[idx];
    overlay.classList.remove('yds-none');
    svEl.textContent = cue.sv;
    enEl.textContent = cue.en ?? 'translating…';
    enEl.classList.toggle('yds-pending', cue.en === null);
  }
  requestAnimationFrame(render);

  document.addEventListener('keydown', e => {
    if (e.key !== 'e' || e.ctrlKey || e.metaKey || e.altKey || !S.cues.length) return;
    const t = e.target;
    if (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)) return;
    const next = EN_MODES[(EN_MODES.indexOf(S.settings.enMode) + 1) % EN_MODES.length];
    chrome.storage.sync.set({ enMode: next });
    status(`English: ${next}`, { hideAfter: 1200 });
  }, true);

  document.addEventListener('yt-navigate-finish', () => {
    const v = new URLSearchParams(location.search).get('v');
    if (v !== S.videoId) reset(v);
    clearTimeout(hintTimer);
    if (!v || !S.settings.enabled) return;
    hintTimer = setTimeout(() => {
      if (!S.cues.length && S.videoId === v) {
        status('YT Dual Subs: turn on subtitles (CC) and choose Swedish', { hideAfter: 8000 });
      }
    }, 5000);
  });
})();
