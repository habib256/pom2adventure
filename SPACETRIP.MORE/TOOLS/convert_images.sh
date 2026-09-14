#!/bin/sh
# Convertit les masters de SPACETRIP.MORE/GENERATED en pages HGR brutes pour
# le volume : N012.png -> SPACETRIP/IMG/N012.HGR.BIN (8192 octets, sans
# en-tete ni compression -- le format que spacetrip.c charge d'un fread).
#
# Le convertisseur est celui de SCOSWAMP (scoswamp_hgr) : il ecrit un flux RLE
# HGRR, et son `decode` en rend la page brute. Deux passes plutot qu'un second
# outil ; l'apercu PNG part dans SPACETRIP.MORE/HGR-PREVIEW pour l'atelier.
# Un PNG plus recent que son .BIN est reconverti, les autres sont laisses.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HGR="$ROOT/ADVKIT/TOOLS/build/scoswamp_hgr"
[ -x "$HGR" ] || { echo "Absent : $HGR (cmake --build SCOSWAMP.MORE/TOOLS/build --target scoswamp_hgr)"; exit 1; }
mkdir -p "$ROOT/SPACETRIP/IMG" "$ROOT/SPACETRIP.MORE/HGR-PREVIEW"
tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
converted=0; skipped=0
for png in "$ROOT"/SPACETRIP.MORE/GENERATED/N[0-9][0-9][0-9].png; do
    [ -e "$png" ] || continue
    name=$(basename "$png" .png)
    out="$ROOT/SPACETRIP/IMG/$name.HGR.BIN"
    recipe="$ROOT/SPACETRIP.MORE/IMAGE-RECIPES/$name.json"
    if [ -e "$recipe" ]; then
        if [ ! -e "$out" ] || [ "$png" -nt "$out" ] || [ "$recipe" -nt "$out" ]; then
            python3 "$ROOT/ADVKIT/image_workshop.py" --replay SPACETRIP "$name"
            converted=$((converted + 1))
        else
            skipped=$((skipped + 1))
        fi
        continue
    fi
    if [ -e "$out" ] && [ ! "$png" -nt "$out" ]; then skipped=$((skipped + 1)); continue; fi
    "$HGR" convert "$png" "$tmp" "$ROOT/SPACETRIP.MORE/HGR-PREVIEW/$name.png" >/dev/null
    "$HGR" decode "$tmp" "$out" >/dev/null
    echo "  $name -> IMG/$name.HGR.BIN"
    converted=$((converted + 1))
done
echo "==> $converted converti(s), $skipped a jour"
