#!/bin/sh
# serve.sh -- sert le DEPOT (et non ce repertoire) sur un port local.
#
# Le lecteur lit SCOSWAMP/TEXTFR/..., SCOSWAMP/DHGR/... et SCOSWAMP.MORE/
# GENERATED/... : sa racine est celle du depot, et les modules ES qu'il
# emploie exigent http:// -- ouvrir index.html en file:// ne marchera pas.
#
#   sh SCOSWAMP.MORE/TOOLS/interpreter/serve.sh [port]
set -e
PORT="${1:-8765}"
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
URL="http://localhost:$PORT/SCOSWAMP.MORE/TOOLS/interpreter/"
echo "racine  : $ROOT"
echo "lecteur : $URL"
command -v open >/dev/null 2>&1 && (sleep 1; open "$URL") &
exec python3 "$ROOT/SCOSWAMP.MORE/TOOLS/interpreter/image_workshop.py" --port "$PORT"
