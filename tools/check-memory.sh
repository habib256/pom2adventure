#!/usr/bin/env bash
#
# check-memory.sh - Vérifie qu'un binaire cc65 tient réellement en mémoire
#
# Un link réussi ne prouve PAS qu'un binaire tient. Le segment BSS (variables
# non initialisées) n'est pas dans le .BIN : il est alloué au lancement, juste
# après DATA. Un binaire de taille acceptable peut donc déborder à l'exécution.
#
# Pire, ld65 peut ne rien signaler. La zone BSS est définie ainsi :
#     BSS: start = __ONCE_RUN__, size = __HIMEM__ - __STACKSIZE__ - __ONCE_RUN__
# Si __ONCE_RUN__ dépasse déjà le plafond, la taille se calcule en négatif,
# déborde en non signé vers ~4 Go, et le contrôle d'overflow est neutralisé :
# le link réussit en silence et la BSS écrase ProDOS 8.
#
# Ce script lit le fichier .map et tranche.
#
# Il contrôle aussi le placement du tas. Dans cc65, le tas n'est pas un segment :
# _heap.o n'importe que sp, __STACKSIZE__, __BSS_SIZE__ et __BSS_RUN__, d'où
#     __heaporg = __BSS_RUN__ + __BSS_SIZE__      (juste après la BSS)
#     __heapend = sp - __STACKSIZE__
# Le tas SUIT donc la BSS, où qu'elle soit. Reloger la BSS en RAM basse pour
# gagner de la place l'y entraîne, et malloc() — utilisé par fopen() pour le
# buffer ProDOS de 1 Ko — rend alors des pointeurs dans HGR page 1 puis dans le
# code. Ce script refuse cette configuration.
#
# Usage :
#   ./tools/check-memory.sh build.map [--himem 0xBF00]
#
# Options :
#   --himem <adr>   Plafond RAM. Défaut 0x9600 (BASIC.SYSTEM résident, ]BRUN).
#                   Passer 0xBF00 pour un binaire qui sacrifie BASIC.SYSTEM et
#                   quitte par l'appel MLI QUIT (voir DOCS/MEMOIRE.md).
#   --min-free <n>  Marge principale minimale en octets (defaut 0).
#
# Code de sortie : 0 = tient en mémoire, 1 = déborde.
#
# Auteur  : Arnaud VERHILLE (@habib256)
# Licence : GNU GPL v3.0

set -uo pipefail

MAP=""
# Valeur par defaut cc65 : BASIC.SYSTEM occupe $9600-$BEFF. Elle n'est qu'un
# repli -- si le programme a ete lie avec un autre __HIMEM__, la carte memoire
# le dit, et c'est elle qui fait foi. Sans cette lecture, un binaire lie a
# $BF00 (celui de SCOSWAMP depuis le moteur de combat) declenchait a tort
# l'alerte de debordement.
HIMEM=""
HIMEM_DEFAUT=0x9600
MEMORY_MIN_FREE=0

while [ $# -gt 0 ]; do
    case "$1" in
        --himem) HIMEM="$2"; shift 2 ;;
        --stack) STACKSIZE=$(($2)); shift 2 ;;
        --min-free)
            if [ $# -lt 2 ] || [[ ! "$2" =~ ^[0-9]+$ ]]; then
                echo "--min-free attend un nombre entier positif ou nul" >&2
                exit 2
            fi
            MEMORY_MIN_FREE=$((10#$2)); shift 2 ;;
        -*)      echo "Option inconnue : $1" >&2; exit 2 ;;
        *)       MAP="$1"; shift ;;
    esac
done

if [ -z "$MAP" ] || [ ! -f "$MAP" ]; then
    echo "Usage : $0 <fichier.map> [--himem 0xBF00]" >&2
    echo "" >&2
    echo "Produire le .map avec :  cl65 ... -Wl -m,build.map -o PROG.BIN ..." >&2
    exit 2
fi

# Cible apple2enh sous ProDOS 8. $BF00-$BFFF est la page globale ProDOS, jamais
# disponible. En dessous, $9600-$BEFF n'est réservé que si BASIC.SYSTEM reste
# résident — ce que fait ]BRUN.
# Normalisées en décimal : [ ] ne sait pas comparer des littéraux 0x.
# Pile C : 2 Ko par defaut, mais le Makefile passe la sienne via --stack --
# le defaut ne doit donc s'appliquer QUE si l'option n'a rien dit.
: "${STACKSIZE:=$((0x0800))}"
readonly LOAD_ADDR=$((0x4000))    # -Wl -S,0x4000, préserve HGR page 1
readonly HGR1_START=$((0x2000))   # HGR page 1 : $2000-$3FFF
readonly HGR1_END=$((0x3FFF))
if [ -z "$HIMEM" ]; then
    # ld65 exporte __HIMEM__ dans la liste des symboles de la carte, en hexa
    # sur six chiffres : "__HIMEM__              00BF00 REA".
    himem_map=$(sed -n 's/.*__HIMEM__ *\([0-9A-F]\{6\}\).*/\1/p' "$MAP" | head -1)
    if [ -n "$himem_map" ]; then
        HIMEM="0x$himem_map"
    else
        HIMEM="$HIMEM_DEFAUT"
    fi
fi
readonly HIMEM_D=$((HIMEM))       # accepte 0x9600 comme 38400
readonly CEILING=$((HIMEM_D - STACKSIZE))

# Fin du segment BSS = point le plus haut occupé à l'exécution.
bss_line=$(grep -E '^BSS ' "$MAP" | head -1)
if [ -z "$bss_line" ]; then
    echo "ERREUR : segment BSS introuvable dans $MAP" >&2
    echo "Le fichier est-il bien un .map produit par ld65 ?" >&2
    exit 2
fi

bss_start=$((16#$(echo "$bss_line" | awk '{print $2}')))
bss_end=$((16#$(echo "$bss_line" | awk '{print $3}')))

# La colonne End de ld65 est INCLUSIVE. Le tas commence a Start + Size.
bss_size=$((16#$(echo "$bss_line" | awk '{print $4}')))
heap_start=$((bss_start + bss_size))

footprint=$((heap_start - LOAD_ADDR))
available=$((CEILING - LOAD_ADDR))

printf 'Analyse mémoire : %s\n' "$MAP"
printf '  Chargement    : $%04X\n' "$LOAD_ADDR"
printf '  BSS           : $%04X - $%04X\n' "$bss_start" "$bss_end"
printf '  Tas           : [$%04X, $%04X[  (%d o)\n' \
       "$heap_start" "$CEILING" "$((CEILING - heap_start))"
printf '  Plafond       : $%04X  (__HIMEM__ $%04X moins %d o de pile C)\n' \
       "$CEILING" "$HIMEM_D" "$STACKSIZE"
printf '  Empreinte     : %d o sur %d o disponibles\n' "$footprint" "$available"

# Le tas démarre juste après la BSS. Si la BSS a été relogée sous la zone de
# chargement, le tas traverse HGR page 1 puis le code : malloc() rendrait des
# pointeurs sur l'image affichée, puis sur le programme lui-même.
if [ "$bss_start" -lt "$LOAD_ADDR" ]; then
    printf '\n'
    printf 'ERREUR : la BSS est relogée en RAM basse ($%04X < $%04X).\n' \
           "$bss_start" "$LOAD_ADDR"
    printf 'Dans cc65 le tas suit la BSS (__heaporg = __BSS_RUN__ + __BSS_SIZE__).\n'
    printf 'Il démarrerait à $%04X et traverserait HGR page 1 ($%04X-$%04X)\n' \
           "$heap_start" "$HGR1_START" "$HGR1_END"
    printf "puis le code lui-même. fopen() alloue 1 Ko par fichier ouvert :\n"
    printf "l'image affichée et le programme seraient écrasés.\n"
    printf 'Gagner de la place par ce biais ne fonctionne pas.\n'
    exit 1
fi

# Détection du piège : la BSS démarre-t-elle déjà au-delà du plafond ?
# Dans ce cas ld65 n'a rien pu signaler, quel que soit le résultat.
if [ "$bss_start" -ge "$CEILING" ]; then
    printf '\n'
    printf 'ERREUR : la BSS démarre à $%04X, au-delà du plafond $%04X.\n' \
           "$bss_start" "$CEILING"
    printf 'ld65 a calculé une taille de zone négative et son contrôle\n'
    printf "d'overflow a été neutralisé : le link a réussi à tort.\n"
    printf 'La BSS écraserait ProDOS 8 dès la première ouverture de fichier.\n'
    exit 1
fi

if [ "$heap_start" -gt "$CEILING" ]; then
    printf '\n'
    printf 'ERREUR : dépassement de %d octets.\n' "$((heap_start - CEILING))"
    printf 'Réduire le code/les données, ou passer en overlay\n'
    printf '(voir /usr/share/cc65/cfg/apple2enh-overlay.cfg).\n'
    exit 1
fi

# Le segment LOWBSS (scoswamp.cfg) loge les gros tampons en RAM basse,
# $1000-$1FFF. ld65 refuse lui-meme un debordement de la zone LOWRAM ; on
# affiche seulement ce qu'il reste, pour savoir ce qu'on peut encore y mettre.
lowbss_line=$(grep -E '^LOWBSS ' "$MAP" | head -1)
if [ -n "$lowbss_line" ]; then
    lb_start=$((16#$(echo "$lowbss_line" | awk '{print $2}')))
    lb_end=$((16#$(echo "$lowbss_line" | awk '{print $3}')))
    lb_size=$((16#$(echo "$lowbss_line" | awk '{print $4}')))
    printf '  LOWBSS        : $%04X - $%04X  (%d o, reste %d o sous $2000)\n' \
           "$lb_start" "$lb_end" "$lb_size" "$((HGR1_START - lb_end - 1))"
    if [ "$lb_end" -ge "$HGR1_START" ]; then
        printf 'ERREUR : LOWBSS deborde dans HGR page 1.\n'
        exit 1
    fi
fi

# Le segment MAPBSS (scoswamp.cfg) loge les donnees du menu MAP et quelques
# tampons dans $0C00-$0FFF -- le kilo-octet que le second tampon ProDOS n'a
# jamais reclame, le jeu n'ouvrant qu'un fichier a la fois. ld65 refuse
# lui-meme un debordement ; on affiche ce qu'il reste.
mapbss_line=$(grep -E '^MAPBSS ' "$MAP" | head -1)
if [ -n "$mapbss_line" ]; then
    mb_start=$((16#$(echo "$mapbss_line" | awk '{print $2}')))
    mb_end=$((16#$(echo "$mapbss_line" | awk '{print $3}')))
    mb_size=$((16#$(echo "$mapbss_line" | awk '{print $4}')))
    printf '  MAPBSS        : $%04X - $%04X  (%d o, reste %d o sous $1000)\n' \
           "$mb_start" "$mb_end" "$mb_size" "$((0x1000 - mb_end - 1))"
    if [ "$mb_end" -ge $((0x1000)) ]; then
        printf 'ERREUR : MAPBSS deborde dans LOWRAM.\n'
        exit 1
    fi
fi

if [ "$((CEILING - heap_start))" -lt "$MEMORY_MIN_FREE" ]; then
    printf 'ERREUR : marge de %d octets inferieure au budget minimal de %d octets.\n' \
           "$((CEILING - heap_start))" "$MEMORY_MIN_FREE"
    exit 1
fi
printf '\n'
printf 'OK : tient en mémoire, marge de %d octets.\n' "$((CEILING - heap_start))"
printf '  Budget minimal : %d octets.\n' "$MEMORY_MIN_FREE"
exit 0
