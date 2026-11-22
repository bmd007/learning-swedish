# Downloaded sources (history)

What we downloaded, from where, under which licence, where it lives locally, and how to get it again.
Everything here is in gitignored folders (`materials/`, `models/`). Only the code that fetches it is in git.

## Voices / TTS

| What | Source | Licence | Local path | How to get it again |
|---|---|---|---|---|
| **Chatterbox multilingual TTS** weights (6 files, ~3.2 GB: `ve.pt`, `t3_mtl23ls_v2.safetensors`, `s3gen.pt`, `grapheme_mtl_merged_expanded_v1.json`, `conds.pt`, `Cangjie5_TC.json`) | huggingface.co/ResembleAI/chatterbox | MIT | `models/chatterbox/` | `tools/download/chatterbox.sh` (Linux/Pi) or `.ps1` (Windows). huggingface.co is blocked on the Mac's network → download elsewhere, copy over (2026-11-18 via external disk). Python: `.venv-tts` (python 3.11, `pip install chatterbox-tts`). |
| Spacy pkuseg model (auto-downloaded by chatterbox on first run, only for Chinese) | github.com/explosion/spacy-pkuseg | MIT | `~/.pkuseg/` | automatic |
| **LibriVox Swedish audiobooks** (chapter 1–2 of each, 64 kb mp3) | archive.org (`<id>_64kb.mp3`) | Public domain | `materials/voices/librivox/` | see table below |
| **NST svensk ATG-database 16 kHz** (Nordisk Språkteknologi, 1999–2000): 1012 speakers, age 16–77, sex, region of youth (10 regions), read sentences | nb.no/sprakbanken/ressurskatalog/oai-nb-no-sbr-56/ → `https://www.nb.no/sbfil/talegjenkjenning/16kHz_2020/se_2020/` (`metadata_se_csv.zip` 20 MB, `lydfiler_16_1.tar.gz` 32 GB = channel 1/head mic, `lydfiler_16_2` = channel 2) | CC0 | `materials/voices/nst/` (`NST_se.csv`, `picked.json`, `clips/`) | `tools/nst_voices.py pick / fetch / refs`. Streaming the 32 GB tar breaks; download it with `curl -C -` first, extract, then delete the tar. |
| Reference clips for voice cloning (~12 s per speaker) | cut from LibriVox + NST; `kid-*` = adult female ref raised in pitch/formant (asetrate ×1.25/×1.4) | as source | `materials/voices/refs/` | `tools/nst_voices.py refs`; LibriVox cuts: ffmpeg `-ss 90 -t 12` (see log 2026-11-18) |
| NOK/Rivstart actors as references (7 actors: 4 f, 3 m) | cut from `materials/nok/audio/` by speaker clustering | © licensed to the learner → outputs stay private (`materials/tts/`) | `materials/voices/refs/nok-*.wav`, `materials/voices/nok_speakers.json` | `.venv-tts/bin/python tools/nok_voices.py` |
| Generated lesson audio (human voices) | Chatterbox + `tools/voice_cast.json` | private | `materials/tts/<lessonId>/` | `build_audio.py --chatterbox` |

LibriVox items used (archive.org identifiers, reader):

| Identifier | Title | Reader |
|---|---|---|
| goteborgsflickor_1005_librivox | Göteborgsflickor (Strömberg) | Lars Rolander (m) |
| baronolson_1309_librivox | Baron Olson och andra historier | Lars Rolander (m) |
| nyckfull_kvinna_del1_1111_librivox | En nyckfull kvinna del 1 (Flygare-Carlén) | Lars Rolander + Cecilia (f) |
| jordens_inre_p_librivox | Jordens inre (Witt) | Petra (f) |
| fran_barnaar_mb_librivox | Från barnaår till silfverhår (Ramsay) | Måns Broo (m, Finland-Swedish, Roslax) |
| valda_berattelser_2304_librivox | Valda berättelser (Lagerlöf) | Anna Sofia Anderson (f) |

Other Swedish LibriVox items found (not downloaded): nyckfull_kvinna_3/4, nyckfull_kvinna_del2, walthers_aftventyr (Måns Broo), sockerpullor_pepparkorn_petra (Petra), vandrande_draeknarne (Lars Rolander).

Rule: Chatterbox audio is never committed (`materials/tts/`, private). Public `audio/` stays edge-tts.
Voices: LibriVox (public domain), NST (CC0, anonymous), NOK actors (licensed to the learner, private use only).
Never clone SR/Klartext speakers or other real, named people.

Checked and not usable (2026-11-18): Gemini TTS via the work gateway (404), Wikimedia Commons Swedish audio
(single words only), Mozilla Common Voice sv-SE (good: CC0, age-tagged, but needs a login on Mozilla Data Collective).
No free Swedish child speakers found.

## Video / photo memory cues

| What | Source | Licence | Local path | How |
|---|---|---|---|---|
| Short stock videos/photos as word cues (2026-11-22 →) | pixabay.com API (key in `materials/.pixabay_key`; Pexels key issuance was paused) | Pixabay Content License: free use, no redistribution of raw files → private | `materials/video/<lessonId>/` | `python3 -I tools/pixabay.py search "<query>"` → look at thumbs → `get <id> <lessonId> <name>` |

## Real audio for listening

| What | Source | Licence | Local path | How |
|---|---|---|---|---|
| SR Klartext clips (~70, 2026-11) + `index.json` | sverigesradio.se (Klartext) | © Sveriges Radio – private study use only, never commit | `materials/sr/klartext/` | `tools/fetch_klartext.py`; cut parts via `clip: [start, end]` → `materials/clips/` |
| Scene sounds (car, café, vacuum …) | Wikimedia Commons | see `sounds/CREDITS.md` | `sounds/` (in git) | – |
| Rivstart B1/B2 extramaterial | Folkuniversitetet / book | © – private | `materials/nok/` | see its README |
| Rivstart B1/B2 Ordlista (textbook word list, sv + forms + en, ch. 1–18, 68 p.) | Natur & Kultur (learner's copy, 2026-11-20; same as `materials/nok/docs/Ordkort_ordlista_verblista__01…`) | © – private | `materials/swedex-a2b1/Rivstart B1B2 Ordlista.pdf` → `materials/ordlista/rivstart-b1b2.json` | `python3 -I tools/parse_ordlista.py <pdf> <json>` |
| Swedex A2B1 model test | Folkuniversitetet | © – private | `materials/swedex-a2b1/` | – |
| Old Swedex B1 + A2 model tests (pre-2022): B1 listening 4 mp3 (~37 min) + `b1hf.pdf` questions + `swedex_b1_facit_hf_transkription.pdf`, B1 reading, writing, oral (topics, picture prompt, script, assessment form), A2 reading/listening, A2B1 oral task, B2C1 format | folkuniversitetet.se `/globalassets/dokumentbanken/lokala-dokument/dokument_region_vast/goteborg/swedex/` (`modelltest-b1/…`, list via web.archive.org CDX; see docs/research.md 2026-11-18) | © – private | `materials/swedex-old/` | curl the direct links (2026-11-18) |
