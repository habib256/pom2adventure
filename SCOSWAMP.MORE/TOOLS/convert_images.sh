#!/bin/sh
# Convertit les PNG de SCOSWAMP.MORE/GENERATED en flux DHGR RLE pour le disque.
#
#   N<id>.png -> SCOSWAMP/DHGR/N<bucket>/N<id>.RLE.BIN   l'illustration de la clairiere
#   B<id>.png -> SCOSWAMP/DHGR/N<bucket>/B<id>.RLE.BIN   l'illustration de bataille
#
# Le bucket est celui du moteur : (id / 50) * 50. Un PNG plus recent que son
# RLE est reconverti, les autres sont laisses tranquilles -- la conversion des
# 400 scenes prend plusieurs minutes.
#
# RESAMPLE=area reduit le master par moyenne de zone avant la quantification
# (voir ADVKIT/IMAGES.md) ; bilinear, le defaut, reproduit les RLE a l'octet.
# Apres le lot, les dix pires conversions sont imprimees
# (ADVKIT/TOOLS/image_quality.py, dE moyen contre le master) : on ne relit pas
# 450 apercus, on relit ceux que la mesure denonce.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DHGR="$(dirname "$0")/../../ADVKIT/TOOLS/build/scoswamp_dhgr"

[ -x "$DHGR" ] || {
    echo "Absent : $DHGR"
    echo "  cmake -S $(dirname "$0") -B $(dirname "$0")/build"
    echo "  cmake --build $(dirname "$0")/../../ADVKIT/TOOLS/build --target scoswamp_dhgr"
    exit 1
}

resample="${RESAMPLE:-bilinear}"
case "$resample" in
    bilinear) resample_opt="" ;;
    area) resample_opt="--resample area" ;;
    *) echo "RESAMPLE : bilinear ou area, pas $resample"; exit 1 ;;
esac

converted=0
skipped=0
lot=$(mktemp)
trap 'rm -f "$lot"' EXIT
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
            python3 "$ROOT/ADVKIT/image_workshop.py" --replay SCOSWAMP "$name" --resample "$resample"
            echo "$name" >> "$lot"
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
    # $resample_opt est vide ou deux mots : non cite expres.
    "$DHGR" convert $resample_opt "$png" "$out" \
        "$ROOT/SCOSWAMP.MORE/HGR-PREVIEW/$name.png" \
        "$ROOT/SCOSWAMP.MORE/CHATMAUVE-PREVIEW/$name.png"
    echo "  $name -> $bucket/$name.RLE.BIN"
    echo "$name" >> "$lot"
    converted=$((converted + 1))
done
echo "==> $converted converti(s), $skipped a jour"

# La mesure veut numpy et Pillow, que le python3 de Homebrew n'a pas toujours.
[ -s "$lot" ] || exit 0
for py in ${IMAGE_QUALITY_PYTHON:-} python3 /usr/bin/python3; do
    if "$py" -c 'import numpy, PIL' 2>/dev/null; then
        echo "== 10 pires conversions du lot (dE moyen contre le master 140x192) =="
        # shellcheck disable=SC2046
        "$py" "$ROOT/ADVKIT/TOOLS/image_quality.py" worst --count 10 $(cat "$lot") || true
        exit 0
    fi
done
echo "(rapport des pires saute : numpy et Pillow introuvables, voir IMAGE_QUALITY_PYTHON)"
