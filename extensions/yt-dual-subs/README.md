# YT Dual Subs (Ollama)

Chrome extension: Swedish YouTube subtitles + English translation from a local Ollama model.

## Install
1. Ollama running, model pulled: `ollama pull gemma3:4b` (default; change in the popup).
2. Chrome → `chrome://extensions` → Developer mode on → **Load unpacked** → pick this folder.
3. Open a YouTube video and turn on CC (any language). The extension loads the Swedish tracks itself.

## Use
- Swedish (white) + English (yellow) appear at the bottom; YouTube's own captions are hidden.
- Key **e**: English show → blur until hover → hidden.
- Click the Swedish line: replay it.
- Popup: on/off, model, **Swedish captions** (made by people = clean / auto-generated = matches speech),
  English mode, text size. Falls back to the other track if the chosen one does not exist.

## How it works
- `inject.js` (page world) reads the caption file the YouTube player itself downloads
  (direct requests fail without YouTube's bot token), then reuses that request URL (with its token)
  to fetch all Swedish tracks of the video.
- `captions.js` parses it; auto-generated tracks are regrouped into sentence-like chunks.
- `content.js` translates 10 lines per request, starting at the current play position.
- Cache: `chrome.storage.local`, key `yds:v<CACHE_VERSION>:<videoId>:<human|asr>:<model>`, value
  `{ swedishLine: english }`. A line is re-translated only when its Swedish text is new or changed,
  the model changes, or it failed before. Bump `CACHE_VERSION` in `content.js` when the prompt changes.
- `background.js` calls `http://localhost:11434/api/chat` with a JSON schema. Ollama returns 403
  for `chrome-extension://` origins, so a session rule strips the Origin header on this
  extension's own requests to Ollama. Fallback: `launchctl setenv OLLAMA_ORIGINS "chrome-extension://*"`
  and restart Ollama.
