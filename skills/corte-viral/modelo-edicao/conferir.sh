#!/usr/bin/env bash
# Folha de conferência: 5 quadros espalhados do final.mp4 lado a lado + o texto final da legenda.
# Uso (de dentro da pasta ed/): ./conferir.sh <nome>   -> ../conferencia/folha-<nome>.jpg
cd "$(dirname "$0")"
PY3="$(command -v python3 || command -v python)"
CONF="$(cd .. && pwd)/conferencia"; mkdir -p "$CONF"
cd "$1" || exit 1
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 final.mp4); ins=""
for k in 0 1 2 3 4; do t=$("$PY3" -c "print([2,0.2,0.4,0.6,0.85][$k]*($D if $k else 1))"); ffmpeg -v error -y -ss $t -i final.mp4 -frames:v 1 -vf scale=300:-1 "$CONF/q$k.jpg"; ins="$ins -i $CONF/q$k.jpg"; done
ffmpeg -v error -y $ins -filter_complex hstack=5 "$CONF/folha-$1.jpg" && echo "folha: $CONF/folha-$1.jpg"
"$PY3" -c "import json;print(' '.join(w['text'] for w in json.load(open('transcript.json'))))"
