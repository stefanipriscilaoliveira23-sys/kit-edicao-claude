#!/usr/bin/env bash
# Entrega: copia o final.mp4 de cada corte pra pasta de entrega (manual da marca: pastas.entrega).
# Se já existe uma versão com o mesmo nome, a antiga vai pra _trabalho/versoes-anteriores/ (nada é apagado).
# Uso (de dentro da pasta ed/): ./entregar.sh <nome> [<nome> ...]   (o sufixo -v2/-v3 sai do nome entregue)
cd "$(dirname "$0")"
PY3="$(command -v python3 || command -v python)"
ED="$(pwd)"
DST="$("$PY3" marca.py pasta entrega)"
VELHAS="$(cd .. && pwd)/versoes-anteriores"; mkdir -p "$VELHAS"
for n in "$@"; do
  base="${n%-v[0-9]}"; [ -s "$ED/$n/final.mp4" ] || { echo "sem final $n"; continue; }
  [ -f "$DST/$base.mp4" ] && mv "$DST/$base.mp4" "$VELHAS/$base-$(date +%Y%m%d-%H%M).mp4"
  cp "$ED/$n/final.mp4" "$DST/$base.mp4" && echo "entregue $base ($(du -h "$DST/$base.mp4" | cut -f1))"
done
