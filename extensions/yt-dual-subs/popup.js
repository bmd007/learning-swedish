const DEFAULTS = { model: 'gemma3:4b', enMode: 'show', scale: 1, enabled: true };
const $ = id => document.getElementById(id);

(async () => {
  const s = await chrome.storage.sync.get(DEFAULTS);
  $('enabled').checked = s.enabled;
  $('enMode').value = s.enMode;
  $('scale').value = s.scale;
  $('scaleVal').textContent = `${s.scale}×`;

  const res = await chrome.runtime.sendMessage({ type: 'models' });
  const models = res?.ok ? res.models : [];
  if (!models.includes(s.model)) models.unshift(s.model);
  for (const m of models) $('model').append(new Option(m, m, false, m === s.model));
  if (res?.ok) {
    $('status').textContent = `Ollama OK – ${res.models.length} local models`;
  } else {
    $('status').className = 'err';
    $('status').textContent = res?.status === 403
      ? 'Ollama refused (403). In Terminal:\nlaunchctl setenv OLLAMA_ORIGINS "chrome-extension://*"\nthen quit and reopen Ollama.'
      : `Cannot reach Ollama at localhost:11434.\n${res?.error ?? ''}`;
  }

  $('enabled').onchange = e => chrome.storage.sync.set({ enabled: e.target.checked });
  $('model').onchange = e => chrome.storage.sync.set({ model: e.target.value });
  $('enMode').onchange = e => chrome.storage.sync.set({ enMode: e.target.value });
  $('scale').oninput = e => {
    $('scaleVal').textContent = `${e.target.value}×`;
    chrome.storage.sync.set({ scale: Number(e.target.value) });
  };
})();
