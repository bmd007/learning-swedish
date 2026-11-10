// Turns a YouTube timedtext response into cues: [{ start, end, sv }] (ms).
// Auto-generated (ASR) tracks have no punctuation and arrive word by word, so the words are
// regrouped into sentence-like chunks; that gives the translator whole thoughts.
const YDS = (() => {
  const SPLIT_BEFORE = new Set(['och', 'men', 'så', 'eftersom', 'därför', 'alltså', 'fast', 'utan']);

  function parseJson3(body) {
    const data = JSON.parse(body);
    const lines = [];
    for (const ev of data.events ?? []) {
      if (!ev.segs) continue;
      const start = ev.tStartMs ?? 0;
      const words = ev.segs.map(s => ({ t: start + (s.tOffsetMs ?? 0), text: s.utf8 ?? '' }));
      const text = words.map(w => w.text).join('');
      if (!text.trim()) continue;
      lines.push({ start, end: start + (ev.dDurationMs ?? 0), text, words });
    }
    return lines;
  }

  function parseXml(body) {
    const doc = new DOMParser().parseFromString(body, 'text/xml');
    const lines = [];
    for (const p of doc.querySelectorAll('p')) {
      const start = Number(p.getAttribute('t') ?? 0);
      const end = start + Number(p.getAttribute('d') ?? 0);
      const segs = [...p.querySelectorAll('s')];
      const words = segs.length
        ? segs.map(s => ({ t: start + Number(s.getAttribute('t') ?? 0), text: s.textContent }))
        : [{ t: start, text: p.textContent }];
      const text = words.map(w => w.text).join('');
      if (text.trim()) lines.push({ start, end, text, words });
    }
    for (const node of doc.querySelectorAll('text')) {
      const start = Math.round(parseFloat(node.getAttribute('start') ?? '0') * 1000);
      const end = start + Math.round(parseFloat(node.getAttribute('dur') ?? '0') * 1000);
      const text = node.textContent;
      if (text.trim()) lines.push({ start, end, text, words: [{ t: start, text }] });
    }
    return lines;
  }

  function parse(body) {
    return body.trimStart().startsWith('{') ? parseJson3(body) : parseXml(body);
  }

  const clean = s => s.replace(/\s+/g, ' ').trim();

  function chunkAsr(lines) {
    const words = [];
    for (const line of lines) {
      for (const w of line.words) {
        for (const part of w.text.split(/\s+/).filter(Boolean)) words.push({ t: w.t, text: part });
      }
    }
    words.sort((a, b) => a.t - b.t);
    const chunks = [];
    let cur = [];
    const flush = () => {
      if (cur.length) chunks.push({ start: cur[0].t, last: cur.at(-1).t, sv: cur.map(w => w.text).join(' ') });
      cur = [];
    };
    for (const w of words) {
      if (cur.length) {
        const gap = w.t - cur.at(-1).t;
        const n = cur.length;
        const lower = w.text.toLowerCase();
        if (gap > 1200
          || n >= 16
          || (n >= 9 && gap > 500)
          || (n >= 6 && SPLIT_BEFORE.has(lower))
          || /[.?!]$/.test(cur.at(-1).text)) flush();
      }
      cur.push(w);
    }
    flush();
    return chunks.map((c, i) => {
      const next = chunks[i + 1];
      const end = Math.min(next ? next.start : Infinity, c.last + 2500);
      return { start: c.start, end, sv: c.sv };
    });
  }

  function toCues(body, isAsr) {
    const lines = parse(body);
    if (isAsr) return chunkAsr(lines);
    return lines
      .map(l => ({ start: l.start, end: l.end, sv: clean(l.text) }))
      .filter(c => c.sv);
  }

  function cueAt(cues, ms) {
    let lo = 0, hi = cues.length - 1, found = -1;
    while (lo <= hi) {
      const mid = (lo + hi) >> 1;
      if (cues[mid].start <= ms) { found = mid; lo = mid + 1; } else hi = mid - 1;
    }
    for (let i = found; i >= 0 && i > found - 3; i--) {
      if (cues[i].end > ms) return i;
    }
    return -1;
  }

  return { parse, toCues, chunkAsr, cueAt };
})();

if (typeof module !== 'undefined') module.exports = YDS;
