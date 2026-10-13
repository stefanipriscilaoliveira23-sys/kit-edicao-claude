#!/usr/bin/env bash
# voz do cortado -> DeepFilterNet (IA, tira ruído) -> depof (pofs de ar no microfone) -> tratar (S, estalos, loudnorm)
# -> volta pro source.mp4 (uma vez só; marca com .voz-limpa)
# Uso (de dentro da pasta da receita): ./limpar_voz.sh <nome>
# O deep-filter fica em ~/.claude/skills/corte-viral/bin/ (o INSTALAR.md explica como baixar). Sem ele, pula só essa etapa.
set -e; n=$1; cd "$(dirname "$0")"; [ -f $n/.voz-limpa ] && exit 0
PY3="$(command -v python3 || command -v python)"
MARCA=../marca.py; [ -f "$MARCA" ] || MARCA="$HOME/.claude/skills/corte-viral/modelo-edicao/marca.py"
PY="$("$PY3" "$MARCA" python 2>/dev/null || echo "$PY3")"
DF="$("$PY3" "$MARCA" deepfilter)"
mkdir -p $n/ruido/df
VOZ_ORIGEM=$n/cortado.mov; [ -f $VOZ_ORIGEM ] || VOZ_ORIGEM=$n/cortado.mp4
ffmpeg -v error -y -i $VOZ_ORIGEM -vn -ac 1 -ar 48000 $n/ruido/voz.wav
if [ -n "$DF" ]; then "$DF" -D --pf -o $n/ruido/df $n/ruido/voz.wav > /dev/null 2>&1; else echo "AVISO: sem deep-filter, segue sem a limpeza por IA"; cp $n/ruido/voz.wav $n/ruido/df/voz.wav; fi
"$PY" depof.py $n/ruido/df/voz.wav $n/ruido/depof.wav > /dev/null
ffmpeg -v error -y -i $n/ruido/depof.wav -filter_complex "[0:a]adeclick=w=20:o=50:a=2:t=2:b=2,adynamicequalizer=dfrequency=7000:dqfactor=1.2:tfrequency=7000:tqfactor=1.2:threshold=0.008:ratio=12:attack=0.5:release=40:makeup=0:range=30:mode=cutbelow:tftype=bell,acrossover=split=4500:order=8th[lo][hi];[hi]acompressor=threshold=0.01:ratio=16:attack=0.2:release=40[hic];[lo][hic]amix=inputs=2:normalize=0,acompressor=threshold=0.1:ratio=2.5:attack=5:release=80:makeup=1.5,loudnorm=I=-14:TP=-1.5:LRA=9[o]" -map "[o]" -ar 48000 $n/ruido/final.wav
ffmpeg -v error -y -i $n/source.mp4 -i $n/ruido/final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart $n/source-limpo.mp4 && mv $n/source-limpo.mp4 $n/source.mp4 && touch $n/.voz-limpa
echo "voz limpa"
