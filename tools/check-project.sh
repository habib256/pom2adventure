#!/usr/bin/env bash
#
# check-project.sh - Vérification d'intégrité et statistiques du projet Apple II
#
# Deux rôles :
#   1. VALIDER   : détecte les erreurs qui cassent le jeu sur Apple IIe
#                  (images HGR != 8192 octets, scènes sans texte, trous de numérotation)
#   2. MESURER   : produit les chiffres officiels du projet, pour que le README
#                  ne dérive plus de la réalité du dépôt.
#
# Usage :
#   ./tools/check-project.sh          # rapport complet
#   ./tools/check-project.sh --quiet  # erreurs uniquement (CI)
#
# Code de sortie : 0 = tout est valide, 1 = au moins une erreur bloquante.
#
# Auteur  : Arnaud VERHILLE (gist974@gmail.com)
# Licence : GNU GPL v3.0

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1

ERRORS=0
WARNINGS=0

# Taille exacte d'une paire DHGR Apple IIe : deux pages de 8192 octets,
# banque auxiliaire puis banque principale, pour 140x192 pixels en 16 couleurs.
readonly HGR_SIZE=8192
readonly DHGR_SIZE=16384

say()  { [ "$QUIET" -eq 0 ] && echo "$@"; return 0; }
err()  { echo "  ERREUR   $*"; ERRORS=$((ERRORS + 1)); }
warn() { [ "$QUIET" -eq 0 ] && echo "  ATTENTION $*"; WARNINGS=$((WARNINGS + 1)); return 0; }

say "======================================================================"
say " Vérification du projet Apple II  ($(date +%Y-%m-%d))"
say "======================================================================"

# ---------------------------------------------------------------------------
# 1. Intégrité des images HGR
# ---------------------------------------------------------------------------
say ""
say "-- Images HGR (doivent faire exactement $HGR_SIZE octets) --"

hgr_total=0
hgr_bad=0
while IFS= read -r f; do
    hgr_total=$((hgr_total + 1))
    size=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f")
    if [ "$size" -ne "$HGR_SIZE" ]; then
        err "$f : $size octets au lieu de $HGR_SIZE"
        hgr_bad=$((hgr_bad + 1))
    fi
done < <(find SCOSWAMP SPACETRIP COMBAT -name "*.HGR" -o -name "*.HGR.BIN" 2>/dev/null | sort)

say "  $hgr_total image(s) brute(s) vérifiée(s), $hgr_bad invalide(s)"

# SCOSWAMP ne porte plus de pages brutes : ses images sont compressées (HGRR),
# donc de taille variable, et la seule question qui vaille est « est-ce que ça
# se décompresse en exactement 8192 octets ? ». C'est ce que répond le
# validateur du convertisseur ; un contrôle de taille de fichier ne dirait
# plus rien ici.
say ""
say "-- Images DHGR compressées (doivent se décoder en $DHGR_SIZE octets) --"
readonly HGRTOOL=SCOSWAMP.MORE/TOOLS/build/scoswamp_dhgr
rle_total=0
rle_bad=0
if [ -x "$HGRTOOL" ]; then
    while IFS= read -r f; do
        rle_total=$((rle_total + 1))
        if ! "$HGRTOOL" validate "$f" >/dev/null 2>&1; then
            err "$f : flux HGRR invalide"
            rle_bad=$((rle_bad + 1))
        fi
    done < <(find SCOSWAMP -name "*.RLE.BIN" 2>/dev/null | sort)
    say "  $rle_total image(s) compressée(s) vérifiée(s), $rle_bad invalide(s)"
else
    warn "$HGRTOOL absent : images compressées non vérifiées"
    say "    cmake -S SCOSWAMP.MORE/TOOLS -B SCOSWAMP.MORE/TOOLS/build"
fi

# ---------------------------------------------------------------------------
# 2. Cohérence des scènes SCOSWAMP
# ---------------------------------------------------------------------------
say ""
say "-- SCOSWAMP : cohérence des scènes --"

fr_count=$(find SCOSWAMP/TEXTFR -name "N*.TXT" | wc -l | tr -d ' ')
en_count=$(find SCOSWAMP/TEXTEN -name "N*.TXT" | wc -l | tr -d ' ')
img_count=$(find SCOSWAMP/DHGR -name "N*.RLE.BIN" | wc -l | tr -d ' ')
# Les tableaux de bataille (B<id>) illustrent un combat, pas une page : ils se
# comptent à part, sinon le pourcentage de scènes illustrées dépasse 100 %.
bat_count=$(find SCOSWAMP/DHGR -name "B*.RLE.BIN" | wc -l | tr -d ' ')

if [ "$fr_count" -ne "$en_count" ]; then
    err "déséquilibre FR/EN : $fr_count fichiers FR vs $en_count fichiers EN"
fi

# Toute scène FR doit avoir son pendant EN (le moteur charge l'une ou l'autre
# selon la langue choisie au démarrage : un manque = plantage en cours de partie).
while IFS= read -r n; do
    [ -f "SCOSWAMP/TEXTEN/${n%/*}/${n##*/}" ] || err "scène FR sans équivalent EN : $n"
done < <(cd SCOSWAMP/TEXTFR && find . -name "N*.TXT" | sed 's|^\./||')

# Fichiers texte vides = écran blanc en jeu.
while IFS= read -r f; do
    err "fichier texte vide : $f"
done < <(find SCOSWAMP/TEXTFR SCOSWAMP/TEXTEN SPACETRIP/TXTFR SPACETRIP/TXTEN -name "*" -type f -empty 2>/dev/null)

# Continuité de la numérotation : un trou signale une scène perdue.
missing=$(cd SCOSWAMP/TEXTFR && find . -name "N*.TXT" | sed 's|.*/N||; s|\.TXT||' \
    | sort -n | awk 'NR==1{p=$1+0; next} {c=$1+0; while(p+1<c){p++; printf "%03d ", p} p=c}')
if [ -n "$missing" ]; then
    err "trou(s) dans la numérotation des scènes FR : $missing"
fi

say "  Textes  : $fr_count FR + $en_count EN = $((fr_count + en_count)) fichiers"
say "  Images  : $img_count / $fr_count scènes illustrées ($((img_count * 100 / fr_count))%)"
say "  Combats : $bat_count tableaux de bataille"

# Scènes sans image : normal à ce stade du projet, comptabilisé, pas bloquant.
say ""
say "  Répartition des images par bloc :"
for b in $(cd SCOSWAMP/DHGR && ls -d N* 2>/dev/null | sort); do
    c=$(find "SCOSWAMP/DHGR/$b" -name "N*.RLE.BIN" | wc -l | tr -d ' ')
    t=$(find "SCOSWAMP/TEXTFR/$b" -name "*.TXT" 2>/dev/null | wc -l | tr -d ' ')
    say "    $b : $c / $t"
done

# ---------------------------------------------------------------------------
# 3. Cohérence SPACETRIP
# ---------------------------------------------------------------------------
say ""
say "-- SPACETRIP : cohérence des scènes --"

st_fr=$(ls SPACETRIP/TXTFR 2>/dev/null | wc -l | tr -d ' ')
st_en=$(ls SPACETRIP/TXTEN 2>/dev/null | wc -l | tr -d ' ')
st_img=$(ls SPACETRIP/IMG/*.HGR.BIN 2>/dev/null | wc -l | tr -d ' ')

[ "$st_fr" -eq "$st_en" ] || err "SPACETRIP : $st_fr fichiers FR vs $st_en EN"
[ "$st_img" -eq "$st_fr" ] || warn "SPACETRIP : $st_img images pour $st_fr scènes"

say "  Textes  : $st_fr FR + $st_en EN"
say "  Images  : $st_img / $st_fr scènes illustrées"

# ---------------------------------------------------------------------------
# 4. Taille des moteurs
# ---------------------------------------------------------------------------
say ""
say "-- Moteurs compilés --"

# Le moteur est chargé à $4000. Le plafond dépend du __HIMEM__ que son
# Makefile impose, et il n'est plus le même pour les trois :
#
#   SPACETRIP, COMBAT : __HIMEM__ = $9600, le "presumed RAM end" de cc65 sous
#     ProDOS 8, parce que $9600-$BFFF appartient à ProDOS (MLI, page globale
#     $BF00, tampons fichier de 1 Ko). Plafond : $9600 - $4000 = 22016.
#   SCOSWAMP : __HIMEM__ = $BF00 depuis le 2026-08-29 -- le moteur de combat
#     n'entrait pas sous $9600. Il prend la place de BASIC.SYSTEM, ce qui lui
#     coûte le retour au BASIC et lui vaut son propre lanceur SYS. Moins la
#     pile C de 384 octets, le plafond est $BD80, soit 32128 octets depuis
#     $4000. Chiffre unique, tenu par SCOSWAMP/SRC/Makefile.
readonly ENGINE_MAX=22016
readonly SCOSWAMP_MAX=32128

# ATTENTION : ce contrôle est NÉCESSAIRE MAIS PAS SUFFISANT.
# Le fichier .BIN ne contient pas le segment BSS (variables non initialisées),
# alloué à l'exécution juste après DATA. L'empreinte réelle est donc plus grande
# que la taille du fichier, et doit tenir sous $8E00 ($9600 moins 2 Ko de pile C),
# soit 19968 octets depuis $4000 pour CODE+RODATA+DATA+BSS.
#
# Piège connu de ld65 : si la BSS démarre déjà au-delà de $8E00, la taille de la
# zone se calcule en négatif, déborde en non signé, et le contrôle d'overflow est
# neutralisé — le link réussit en silence alors que la BSS écrase ProDOS.
# Seule l'inspection du fichier .map détecte ce cas :
#   cl65 ... -Wl -m,build.map && sed -n '/Segment list/,/^$/p' build.map
# Vérifier que la fin du segment BSS reste inférieure à $8E00.

for bin in SCOSWAMP/SCOSWAMP.BIN SPACETRIP/SPACETRIP.BIN COMBAT/COMBAT.BIN; do
    if [ -f "$bin" ]; then
        size=$(stat -c%s "$bin" 2>/dev/null || stat -f%z "$bin")
        kb=$((size / 1024))
        case "$bin" in
            SCOSWAMP/*) max=$SCOSWAMP_MAX; top='$BD80' ;;
            *)          max=$ENGINE_MAX;   top='$9600' ;;
        esac
        if [ "$size" -gt "$max" ]; then
            err "$bin : $size octets, dépasse la limite de $max (\$4000-$top)"
        else
            say "  $bin : $size octets (~$kb Ko)"
        fi
    else
        warn "$bin absent (non compilé)"
    fi
done

# ---------------------------------------------------------------------------
# 5. Hygiène du dépôt
# ---------------------------------------------------------------------------
say ""
say "-- Hygiène du dépôt --"

if git rev-parse --git-dir >/dev/null 2>&1; then
    junk=$(git ls-files | grep -E '\.(o|lst|map|DS_Store|2mg|2img|po|dsk|bak|swp)$' || true)
    if [ -n "$junk" ]; then
        while IFS= read -r f; do
            err "artefact versionné (devrait être ignoré) : $f"
        done <<< "$junk"
    else
        say "  Aucun artefact de build versionné."
    fi
else
    warn "hors dépôt Git, vérification ignorée"
fi

# ---------------------------------------------------------------------------
# Bilan
# ---------------------------------------------------------------------------
say ""
say "======================================================================"
if [ "$ERRORS" -eq 0 ]; then
    say " RÉSULTAT : OK  ($WARNINGS avertissement(s))"
    say "======================================================================"
    exit 0
else
    echo " RÉSULTAT : $ERRORS erreur(s), $WARNINGS avertissement(s)"
    echo "======================================================================"
    exit 1
fi
