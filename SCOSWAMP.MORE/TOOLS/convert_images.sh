#!/bin/sh
# Convertit les PNG de SCOSWAMP.MORE/GENERATED en flux DHGR RLE pour le disque.
#
#   N<id>.png -> SCOSWAMP/DHGR/N<bucket>/N<id>.RLE.BIN   l'illustration de la clairiere
#   B<id>.png -> SCOSWAMP/DHGR/N<bucket>/B<id>.RLE.BIN   l'illustration de bataille
#
# Le bucket est celui du moteur : (id / 50) * 50. Un PNG plus recent que son
# RLE est reconverti, les autres sont laisses tranquilles -- la conversion des
# 400 scenes prend plusieurs minutes.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DHGR="$(dirname "$0")/build/scoswamp_dhgr"

[ -x "$DHGR" ] || {
    echo "Absent : $DHGR"
    echo "  cmake -S $(dirname "$0") -B $(dirname "$0")/build"
    echo "  cmake --build $(dirname "$0")/build --target scoswamp_dhgr"
    exit 1
}

converted=0
skipped=0
for png in "$ROOT"/SCOSWAMP.MORE/GENERATED/[NB][0-9][0-9][0-9].png; do
    [ -e "$png" ] || continue
    name=$(basename "$png" .png)
    id=$(echo "$name" | cut -c2-4)
    # 10#$id force la base 10 : sans lui "008" est lu comme de l'octal et
    # l'arithmetique du shell s'arrete sur "value too great for base".
    bucket=$(printf 'N%03d' $(( 10#$id / 50 * 50 )))
    out="$ROOT/SCOSWAMP/DHGR/$bucket/$name.RLE.BIN"
    recipe="$ROOT/SCOSWAMP.MORE/IMAGE-RECIPES/$name.json"
    if [ -e "$recipe" ]; then
        if [ ! -e "$out" ] || [ "$png" -nt "$out" ] || [ "$recipe" -nt "$out" ]; then
            python3 "$ROOT/SCOSWAMP.MORE/TOOLS/interpreter/image_workshop.py" --replay SCOSWAMP "$name"
            converted=$((converted + 1))
        else
            skipped=$((skipped + 1))
        fi
        continue
    fi
    if [ -e "$out" ] && [ ! "$png" -nt "$out" ]; then
        skipped=$((skipped + 1))
        continue
    fi
    mkdir -p "$(dirname "$out")" "$ROOT/SCOSWAMP.MORE/HGR-PREVIEW" \
        "$ROOT/SCOSWAMP.MORE/CHATMAUVE-PREVIEW"
    "$DHGR" convert "$png" "$out" \
        "$ROOT/SCOSWAMP.MORE/HGR-PREVIEW/$name.png" \
        "$ROOT/SCOSWAMP.MORE/CHATMAUVE-PREVIEW/$name.png"
    echo "  $name -> $bucket/$name.RLE.BIN"
    converted=$((converted + 1))
done
echo "==> $converted converti(s), $skipped a jour"
