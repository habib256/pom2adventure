#!/bin/sh
# Construit le moteur SPACE EXPLORER TRIP et, au passage, verifie l'analyseur
# de page sur la machine hote.
#
# Le binaire demarre a $4000 : la page HGR 1 occupe $2000-$3FFF et le
# programme ne doit pas s'y coucher dessus. __EXEHDR__=0 donne un binaire nu,
# sans en-tete, tel que ProDOS l'attend d'un BRUN.
#
#     sh build.sh          compile SPACETRIP.BIN
#     sh build.sh test     ne fait tourner que le banc hote
set -e
cd "$(dirname "$0")"

# Le banc hote d'abord : page.h se compile des deux cotes, et une seconde ici
# vaut une partie entiere rejouee dans l'emulateur.
cc -Wall -Wextra -O2 -o /tmp/spacetrip_test_parse test_parse.c
/tmp/spacetrip_test_parse
[ "$1" = "test" ] && exit 0

cl65 -t apple2enh -O -Oirs -Wl -D,__EXEHDR__=0 -Wl -S,0x4000 \
     -o SPACETRIP.BIN spacetrip.c paths.c

rm -f spacetrip.o paths.o
ls -l SPACETRIP.BIN
