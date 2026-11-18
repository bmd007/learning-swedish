# Downloads the Chatterbox multilingual TTS weights (~3 GB) on Windows 11.
# Run in PowerShell:  powershell -ExecutionPolicy Bypass -File chatterbox.ps1 [target-dir]
# Then copy the folder to <repo>/models/chatterbox/ on the Mac.
param([string]$Dir = "models\chatterbox")
$ErrorActionPreference = "Stop"
$base = "https://huggingface.co/ResembleAI/chatterbox/resolve/main"
$files = "ve.pt", "t3_mtl23ls_v2.safetensors", "s3gen.pt", "grapheme_mtl_merged_expanded_v1.json", "conds.pt", "Cangjie5_TC.json"
New-Item -ItemType Directory -Force -Path $Dir | Out-Null
foreach ($f in $files) {
    Write-Host "== $f"
    # curl.exe ships with Windows 11 and can resume (-C -), unlike Invoke-WebRequest
    curl.exe -fL --retry 5 -C - -o (Join-Path $Dir $f) "$base/$f"
    if ($LASTEXITCODE -ne 0) { throw "download failed: $f" }
}
Get-ChildItem $Dir | Format-Table Name, Length
Write-Host "Done. Copy $Dir to <repo>/models/chatterbox/ on the Mac."
