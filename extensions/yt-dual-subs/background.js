const OLLAMA = 'http://localhost:11434';
const DEFAULTS = { model: 'gemma3:4b', enMode: 'show', scale: 1, enabled: true };

// Ollama rejects requests whose Origin is chrome-extension://… (403) unless OLLAMA_ORIGINS is set.
// Strip the Origin header, but only on this extension's own requests to Ollama.
async function installOriginRule() {
  await chrome.declarativeNetRequest.updateSessionRules({
    removeRuleIds: [1],
    addRules: [{
      id: 1,
      priority: 1,
      action: { type: 'modifyHeaders', requestHeaders: [{ header: 'origin', operation: 'remove' }] },
      condition: {
        regexFilter: '^http://(localhost|127\\.0\\.0\\.1):11434/',
        initiatorDomains: [chrome.runtime.id],
        resourceTypes: ['xmlhttprequest', 'other'],
      },
    }],
  });
}
chrome.runtime.onInstalled.addListener(installOriginRule);
chrome.runtime.onStartup.addListener(installOriginRule);
installOriginRule();

async function settings() {
  return { ...DEFAULTS, ...(await chrome.storage.sync.get(DEFAULTS)) };
}

async function ollama(path, body) {
  const res = await fetch(OLLAMA + path, body ? {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  } : undefined);
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    const err = new Error(`Ollama HTTP ${res.status} ${text.slice(0, 200)}`);
    err.status = res.status;
    throw err;
  }
  return res.json();
}

const SYSTEM = `You translate Swedish YouTube subtitles into natural, simple English.
The Swedish often comes from automatic speech recognition: no punctuation, sometimes misheard words.
Translate the meaning. Silently fix obvious recognition errors. Keep it short, like a subtitle.
Return JSON: {"translations": [ ... ]} with exactly one English string per numbered input line, in the same order.
Never merge or split lines. Never add notes.`;

async function translateOnce(model, lines, context) {
  const prompt = [
    context.length ? `Earlier lines, for context only (do not translate):\n${context.join('\n')}\n` : '',
    `Translate these ${lines.length} lines:`,
    ...lines.map((l, i) => `${i + 1}. ${l}`),
  ].join('\n');
  const data = await ollama('/api/chat', {
    model,
    stream: false,
    think: false,
    keep_alive: '30m',
    options: { temperature: 0.2, num_ctx: 4096 },
    format: {
      type: 'object',
      properties: {
        translations: { type: 'array', items: { type: 'string' }, minItems: lines.length, maxItems: lines.length },
      },
      required: ['translations'],
    },
    messages: [{ role: 'system', content: SYSTEM }, { role: 'user', content: prompt }],
  });
  const parsed = JSON.parse(data.message?.content ?? '{}');
  const out = parsed.translations;
  if (!Array.isArray(out) || out.length !== lines.length) throw new Error('count mismatch');
  return out.map(s => String(s).trim());
}

async function translate(model, lines, context) {
  try {
    return await translateOnce(model, lines, context);
  } catch (e) {
    if (e.status) throw e;
    if (lines.length === 1) return [''];
    const mid = Math.ceil(lines.length / 2);
    const a = await translate(model, lines.slice(0, mid), context);
    const b = await translate(model, lines.slice(mid), [...context, ...lines.slice(0, mid)].slice(-3));
    return [...a, ...b];
  }
}

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  (async () => {
    try {
      if (msg.type === 'translate') {
        const { model } = await settings();
        reply({ ok: true, translations: await translate(model, msg.lines, msg.context ?? []) });
      } else if (msg.type === 'models') {
        const data = await ollama('/api/tags');
        reply({ ok: true, models: data.models.filter(m => !m.remote_host).map(m => m.name) });
      }
    } catch (e) {
      reply({ ok: false, status: e.status ?? 0, error: String(e.message ?? e) });
    }
  })();
  return true;
});
