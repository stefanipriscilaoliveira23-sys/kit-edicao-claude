# -*- coding: utf-8 -*-
"""Identidade da marca pro Narradinho: tudo vem do Manual da Marca (~/minha-marca/marca.json) pelo marca.py.
Os outros scripts desta pasta leem daqui. Nada de cor ou fonte fixa de ninguém."""
import os, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO = os.path.dirname(AQUI)                       # modelo-edicao
for p in (MODELO, os.path.expanduser("~/.claude/skills/corte-viral/modelo-edicao")):
    if os.path.exists(os.path.join(p, "marca.py")):
        sys.path.insert(0, p); break
import marca

M = marca.carregar()
FONTES = {papel: marca.fonte_arquivo(papel) for papel in ("legenda", "legenda_media", "titulo", "titulo_italico")}
CORES = {"claro": marca.cor("claro"), "destaque": marca.cor("destaque"), "escuro": marca.cor("escuro")}
SUBLINHADO_NO_TITULO = True      # sublinhado na cor de DESTAQUE correndo embaixo do título grande

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"
DEEPFILTER = marca.binario("bin", "deep-filter")
DEPOF = os.path.join(MODELO, "receita-editorial", "depof.py")
TRABALHO = marca.pasta("trabalho")
ENTREGA = marca.pasta("entrega")
_hf = os.path.join(TRABALHO, "hf", "node_modules", ".bin", "hyperframes")   # binário FIXO (preparar_pasta.py instala)
HF = _hf if os.path.exists(_hf) or not os.path.exists(_hf + ".cmd") else _hf + ".cmd"
LUZ = "eq=brightness=0.02:contrast=1.04:saturation=1.05:gamma=1.04"     # luz leve

VOCAB = marca.vocabulario()
TROCAS = {k.lower(): v for k, v in marca.trocas().items()}

# tratamento da voz (ruído de IA + pofs + S estourado + loudnorm -14), igual ao limpar_voz.sh
TRATAR = ("adeclick=w=20:o=50:a=2:t=2:b=2,"
          "adynamicequalizer=dfrequency=7000:dqfactor=1.2:tfrequency=7000:tqfactor=1.2:threshold=0.008:ratio=12:attack=0.5:release=40:makeup=0:range=30:mode=cutbelow:tftype=bell,"
          "acrossover=split=4500:order=8th[lo][hi];[hi]acompressor=threshold=0.01:ratio=16:attack=0.2:release=40[hic];"
          "[lo][hic]amix=inputs=2:normalize=0,acompressor=threshold=0.1:ratio=2.5:attack=5:release=80:makeup=1.5,loudnorm=I=-14:TP=-1.5:LRA=9")


def musica_padrao():
    """Trilha do manual (marca.json -> trilha.arquivo, em ~/minha-marca/sons/). No narradinho a música é parte do formato,
    então usa a trilha do manual mesmo se 'usar' estiver false. Sem arquivo: None (pedir uma música pra aluna)."""
    T = M.get("trilha") or {}
    arq = T.get("arquivo")
    if arq:
        for c in (os.path.join(marca.PASTA_MARCA, "sons", arq), os.path.join(marca.PASTA_MARCA, arq), os.path.expanduser(arq)):
            if os.path.exists(c): return c
    return None


def som(nome):
    return marca.som(nome, marca.SONS_SKILL)
