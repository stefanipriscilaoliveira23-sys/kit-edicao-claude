# -*- coding: utf-8 -*-
"""
Prepara a pasta de trabalho da edição (uma vez, e de novo sempre que a skill for atualizada).

Cria, dentro da pasta de trabalho do manual da marca (padrão ~/Videos-Claude/_trabalho):
  ed/                 -> onde cada corte vira uma pasta; recebe uma cópia dos scripts deste modelo
  ed/assets/          -> sons (sfx/) e fontes (fonts/), já com as fontes da marca da aluna
  trans/              -> transcrições e csv do olhar dos brutos
  hf/                 -> HyperFrames FIXO (npm i hyperframes@0.8.107), nunca npx em paralelo
  prontos/, versoes-anteriores/, conferencia/
e a pasta de entrega (padrão ~/Videos-Claude/PRONTOS).

NUNCA trabalhar em pasta temporária (/tmp, scratchpad): se o computador reiniciar, apaga tudo.

Uso: python preparar_pasta.py [--sem-hyperframes]
"""
import glob
import os
import shutil
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import marca  # noqa: E402

TRAB = marca.pasta("trabalho")
ENTREGA = marca.pasta("entrega")
for sub in ("ed", "trans", "hf", "prontos", "versoes-anteriores", "conferencia"):
    os.makedirs(os.path.join(TRAB, sub), exist_ok=True)
ED = os.path.join(TRAB, "ed")

# scripts do modelo (os .py, .sh, .css e os exemplos .json) + a receita editorial
for f in glob.glob(os.path.join(AQUI, "*.py")) + glob.glob(os.path.join(AQUI, "*.sh")) + glob.glob(os.path.join(AQUI, "exemplo-*.json")):
    shutil.copy2(f, ED)
for pasta in ("receita-editorial", "olhar"):
    shutil.copytree(os.path.join(AQUI, pasta), os.path.join(ED, pasta), dirs_exist_ok=True)

# assets: sons e fontes livres da skill + fontes e sons da marca
shutil.copytree(os.path.join(AQUI, "assets"), os.path.join(ED, "assets"), dirs_exist_ok=True)
marca.copiar_fontes(os.path.join(ED, "assets", "fonts"))
sons_marca = os.path.join(marca.PASTA_MARCA, "sons")
if os.path.isdir(sons_marca):
    for f in glob.glob(os.path.join(sons_marca, "*")):
        shutil.copy2(f, os.path.join(ED, "assets", "sfx"))

# HyperFrames fixo (render estável; npx atualiza sozinho no meio e quebra renders em paralelo)
hf_bin = os.path.join(TRAB, "hf", "node_modules", ".bin", "hyperframes")
if "--sem-hyperframes" not in sys.argv and not (os.path.exists(hf_bin) or os.path.exists(hf_bin + ".cmd")):
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if npm:
        print("instalando hyperframes@0.8.107 em", os.path.join(TRAB, "hf"), "...")
        subprocess.run([npm, "i", "--save-exact", "hyperframes@0.8.107"], cwd=os.path.join(TRAB, "hf"), check=False)
    else:
        print("AVISO: npm não encontrado. Instale o Node 22 (ver INSTALAR.md) e rode de novo.")

print("pasta de trabalho:", TRAB)
print("pasta de entrega: ", ENTREGA)
f = marca.faltando()
if f:
    print("ATENÇÃO: o manual da marca está incompleto (" + ", ".join(f) + "). Faça a entrevista da marca antes de editar.")
