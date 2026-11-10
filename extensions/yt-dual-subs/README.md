# YT Dual Subs (Ollama)

Chrome extension: Swedish YouTube subtitles + English translation from a local Ollama model.

## Install
1. Ollama running, model pulled: `ollama pull gemma3:4b` (default; change in the popup).
2. Chrome → `chrome://extensions` → Developer mode on → **Load unpacked** → pick this folder.
3. Open a YouTube video, turn on CC, choose Swedish (human or auto-generated).

## Use
- Swedish (white) + English (yellow) appear at the bottom; YouTube's own captions are hidden.
- Key **e**: English show → blur until hover → hidden.
- Click the Swedish line: replay it.
- Popup: on/off, model, English mode, text size.

## How it works
- `inject.js` (page world) reads the caption file the YouTube player itself downloads
  (direct requests fail without YouTube's bot token).
- `captions.js` parses it; auto-generated tracks are regrouped into sentence-like chunks.
- `content.js` translates 10 lines per request, starting at the current play position, and caches
  results per video + model in `chrome.storage.local`.
- `background.js` calls `http://localhost:11434/api/chat` with a JSON schema. Ollama returns 403
  for `chrome-extension://` origins, so a session rule strips the Origin header on this
  extension's own requests to Ollama. Fallback: `launchctl setenv OLLAMA_ORIGINS "chrome-extension://*"`
  and restart Ollama.
