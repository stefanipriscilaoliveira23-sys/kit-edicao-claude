#!/usr/bin/env bash
# fundo (HyperFrames) -> máscara da pessoa -> junta (pessoa por cima do fundo nas janelas) -> frente (HyperFrames) -> mixa
# Uso (de dentro da pasta da receita, onde ficam configs.json e assets/): ./render_meg.sh <nome>
# A máscara da pessoa (texto ATRÁS da pessoa, T11/C4) só existe no Mac. Nos outros sistemas o fundo vai sem recorte:
# nesse caso não use elementos de trás por cima do rosto (ou use a skill embedded-captions do HyperFrames).
set -e
n=$1; cd "$(dirname "$0")"
PY3="$(command -v python3 || command -v python)"
MARCA=../marca.py; [ -f "$MARCA" ] || MARCA="$HOME/.claude/skills/corte-viral/modelo-edicao/marca.py"
PY="$("$PY3" "$MARCA" python 2>/dev/null || echo "$PY3")"
TRAB="$("$PY3" "$MARCA" pasta trabalho)"
HF="$TRAB/hf/node_modules/.bin/hyperframes"; [ -x "$HF" ] || HF="$HF.cmd"
MASC="$("$PY3" "$MARCA" mascara)"
[ -f $n/atras/render.mp4 ] || (cd $n/atras && "$HF" render -o render.mp4 > render.log 2>&1)
echo "fundo ok $(date +%H:%M)"
if [ -n "$MASC" ]; then
  [ -f $n/mask.mp4 ] || "$MASC" $n/source.mp4 $n/mask.mp4 1080
  echo "mascara ok $(date +%H:%M)"
  EN=$("$PY3" -c "import json;j=json.load(open('$n/meta.json'))['janelas_mascara'];print('+'.join(f'between(t,{a:.3f},{b:.3f})' for a,b in j))")
else
  echo "sem mascara-pessoa neste computador: base = source"; EN=""
fi
if [ -z "$EN" ]; then ffmpeg -nostdin -v error -y -i $n/source.mp4 -map 0:v -c:v copy $n/frente/base.mp4; else ffmpeg -nostdin -v error -y -i $n/atras/render.mp4 -i $n/source.mp4 -i $n/mask.mp4 -filter_complex \
 "[2:v]scale=1080:1920,format=gray,gblur=sigma=1.6[m];[1:v]format=yuva420p[p0];[p0][m]alphamerge[p];[0:v][p]overlay=0:0:enable='$EN',format=yuv420p[v]" \
 -map "[v]" -c:v libx264 -crf 15 -preset fast -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 $n/frente/base.mp4; fi
echo "juncao ok $(date +%H:%M)"
rm -f $n/frente/render.mp4; (cd $n/frente && "$HF" render -o render.mp4 > render.log 2>&1)
echo "frente ok $(date +%H:%M)"
./limpar_voz.sh $n
"$PY" mixar_meg.py $n
ffmpeg -nostdin -v error -y -i $n/final.mp4 -vf "select=not(mod(n\,60)),scale=216:-2,tile=8x6" -fps_mode vfr -frames:v 1 $n/folha.jpg
echo "FIM $(date +%H:%M)"
