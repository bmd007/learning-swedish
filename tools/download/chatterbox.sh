#!/usr/bin/env bash
# Downloads the Chatterbox multilingual TTS weights (~3 GB) for networks where huggingface.co is blocked
# on the main machine. Run on any machine (Raspberry Pi OS, Linux, macOS), then copy the folder to
# <repo>/models/chatterbox/ on the Mac.   Usage: ./chatterbox.sh [target-dir]
set -euo pipefail
dir="${1:-models/chatterbox}"
base="https://huggingface.co/ResembleAI/chatterbox/resolve/main"
mkdir -p "$dir"
for f in ve.pt t3_mtl23ls_v2.safetensors s3gen.pt grapheme_mtl_merged_expanded_v1.json conds.pt Cangjie5_TC.json; do
  echo "== $f"
  curl -fL --retry 5 -C - -o "$dir/$f" "$base/$f"
done
ls -lh "$dir"
echo "Done. Copy $dir to <repo>/models/chatterbox/ on the Mac."
