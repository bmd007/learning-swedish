#!/usr/bin/env bash
# Pack the private, hard-to-recreate parts of materials/ into materials.7z
# (AES-256, file names hidden). Asks for the password; nothing is stored.
# Left out on purpose (public, re-downloadable, see docs/sources.md): voices/librivox, voices/nst,
# plus logs and previews.
# Unpack: 7zz x materials.7z   (asks for the password)
set -euo pipefail
cd "$(dirname "$0")/.."
command -v 7zz >/dev/null || { echo "install sevenzip: brew install sevenzip"; exit 1; }
rm -f materials.7z
7zz a -t7z -mhe=on -mx=1 -p materials.7z materials \
  -xr!.DS_Store \
  -x!materials/voices/librivox \
  -x!materials/voices/nst \
  -x!materials/server.log \
  -x!materials/preview \
  -x!materials/.pixabay_key
ls -lh materials.7z
7zz l -pnot-the-password materials.7z >/dev/null 2>&1 && echo "warning: file names are readable" || echo "ok: file names are hidden"
