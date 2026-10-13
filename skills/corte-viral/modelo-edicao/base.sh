#!/usr/bin/env bash
# Monta a base de um vídeo: source enquadrado -> corta silêncio pelo áudio -> transcreve de novo.
# Rodar de dentro da pasta ed/ do trabalho (onde ficam os scripts copiados pelo preparar_pasta.py).
# Uso: ./base.sh <nome> fixo|seguir|lista [transcricao.json | receita.json]
#   fixo   = close da cintura pra cima (retrato.py; recorte da pessoa pelo mascara.py, Windows e Mac)
#   seguir = close que acompanha o rosto (retrato_seguir.py, qualquer sistema; precisa do csv do olhar em ../trans/<arquivo>)
#   lista  = vídeo de lista com slide na TV (lista_tv.py <receita.json>)
cd "$(dirname "$0")"
PY3="$(command -v python3 || command -v python)"
PY="$("$PY3" marca.py python 2>/dev/null || echo "$PY3")"
n=$1; tipo=$2
mkdir -p $n/_tmp; [ -e $n/assets ] || ln -s ../assets $n/assets
case $tipo in
  fixo)   "$PY" retrato.py $n ;;
  seguir) "$PY" retrato_seguir.py $n ../trans/$3 0.62 ;;
  lista)  "$PY" lista_tv.py $3 ;;
esac || { echo "FALHOU source $n"; exit 1; }
mv $n/source.mp4 $n/_tmp/source-bruto.mp4 && "$PY" tirar_silencios.py $n/_tmp/source-bruto.mp4 $n/source.mp4 0.3 0 0.1 && mv $n/source.mp4.cortes.json $n/cortes-novos.json || { echo "FALHOU silencio $n"; exit 1; }
"$PY" transcrever_v2.py $n > $n/_tmp/transc.log 2>&1 && echo "base pronta $n $(date +%H:%M)" || echo "FALHOU transc $n"
