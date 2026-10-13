#!/usr/bin/env bash
# Narradinho, edição completa: edicao.json -> HyperFrames (binário FIXO, um render por vez) -> música/mixagem -> folha de quadros
# Uso: bash render.sh <projeto>      (rodar com run_in_background; leva ~1 min a cada 5 s de vídeo)
set -e
P="$(cd "$1" && pwd)"; R="$(cd "$(dirname "$0")" && pwd)"
PY3="$(command -v python3 || command -v python)"
MARCA="$R/../marca.py"; [ -f "$MARCA" ] || MARCA="$HOME/.claude/skills/corte-viral/modelo-edicao/marca.py"
PY="${PY:-$("$PY3" "$MARCA" python 2>/dev/null || echo "$PY3")}"
HF=$("$PY" -c "import sys; sys.path.insert(0,'$R'); import identidade as I; print(I.HF)")
[ -e "$HF" ] || { echo "ERRO: HyperFrames fixo não achado em $HF (rode python3 modelo-edicao/preparar_pasta.py)"; exit 1; }
"$PY" "$R/editar.py" "$P"
echo "render começou $(date +%H:%M)"
rm -f "$P/hf/render.mp4"; (cd "$P/hf" && "$HF" render -o render.mp4 > render.log 2>&1) || { tail -20 "$P/hf/render.log"; exit 1; }
echo "render ok $(date +%H:%M)"
"$PY" "$R/mixar.py" "$P"
N="$(basename "$P")"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$P/$N.mp4")
ffmpeg -nostdin -v error -y -i "$P/$N.mp4" -vf "fps=40/$D,scale=216:-2,tile=8x5" -frames:v 1 "$P/folha.jpg"
echo "FIM $(date +%H:%M): $P/$N.mp4 e $P/folha.jpg"
