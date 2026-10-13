#!/usr/bin/env bash
# Renderiza vários cortes em paralelo com o HyperFrames FIXO da pasta de trabalho (../hf) e mixa voz + efeitos.
# Uso (de dentro da pasta ed/): ./render_lote.sh <nome> [<nome> ...]
# Rodar com run_in_background (render solto com nohup numa chamada comum é cancelado).
cd "$(dirname "$0")"
PY3="$(command -v python3 || command -v python)"
PY="$("$PY3" marca.py python 2>/dev/null || echo "$PY3")"
HF="$(cd .. && pwd)/hf/node_modules/.bin/hyperframes"
[ -x "$HF" ] || HF="$HF.cmd"
r(){ (cd $1 && rm -f render.mp4 final.mp4 && "$HF" render -o render.mp4 > _tmp/render.log 2>&1) && "$PY" mixar_clip.py $1 > /dev/null && echo "pronto $1 $(date +%H:%M)" || echo "FALHOU $1"; }
for n in "$@"; do r $n & done; wait
