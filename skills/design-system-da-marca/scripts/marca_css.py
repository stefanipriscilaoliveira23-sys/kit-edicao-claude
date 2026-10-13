# -*- coding: utf-8 -*-
"""
Transforma o Manual da Marca (~/minha-marca/marca.json) no CSS que os slides usam.

  python3 marca_css.py --conferir
      -> diz se o manual está completo (sai com erro 1 se faltar algo: hora da entrevista da marca)
  python3 marca_css.py --saida <pasta-do-carrossel>
      -> copia as fontes pra <pasta>/fonts/ e grava <pasta>/marca.css (@font-face + variáveis :root)
         No HTML de cada slide: <link rel="stylesheet" href="marca.css">
  python3 marca_css.py --aplicar <arquivo.html>
      -> troca os @font-face e o bloco :root de um modelo (ex.: references/design-system-visual.html)
         pelos da marca, gravando <arquivo>-marca.html ao lado (as fontes vão pra fonts/ ao lado)

Variáveis geradas (as mesmas dos modelos):
  --cor-principal --cor-destaque --cor-fundo --cor-fundo-2 --cor-texto --cor-claro --cor-escuro --cor-raro
  --cor-principal-escura (calculada) --fonte-titulo --fonte-corpo --fonte-manuscrita
  --assinatura (texto) e --max-cores (número) ficam como comentário pra consulta
"""
import json
import os
import re
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTES_SKILL = os.path.join(AQUI, "..", "assets", "fonts")
PASTA_MARCA = os.path.expanduser(os.environ.get("MINHA_MARCA", "~/minha-marca"))
ARQ = os.path.join(PASTA_MARCA, "marca.json")

PADRAO_CORES = {"principal": "#222222", "destaque": "#4A4A4A", "fundo": "#F5F5F5", "fundo_2": "#E9E9E9",
                "texto": "#1A1A1A", "claro": "#FFFFFF", "escuro": "#111111", "raro": "#8C8C8C"}
PADRAO_FONTES = {"titulo": "InstrumentSerif-Regular.ttf", "titulo_italico": "InstrumentSerif-Italic.ttf",
                 "legenda": "Inter-Bold.woff2", "legenda_media": "Inter-Medium.woff2", "manuscrita": "Mynerve-Regular.ttf"}


def carregar():
    m = json.load(open(ARQ, encoding="utf-8")) if os.path.exists(ARQ) else {}
    cores = dict(PADRAO_CORES)
    cores.update({k: v for k, v in (m.get("cores") or {}).items() if str(v).startswith("#")})
    cores.setdefault("fundo_2", cores["fundo"])
    fontes = dict(PADRAO_FONTES)
    fontes.update({k: v for k, v in (m.get("fontes") or {}).items() if v})
    return m, cores, fontes


def faltando():
    if not os.path.exists(ARQ):
        return ["marca.json inteiro (pasta ~/minha-marca)"]
    m = json.load(open(ARQ, encoding="utf-8"))
    falta = [c for c in ("nome", "arroba") if not m.get(c)]
    falta += [f"cores.{c}" for c in ("principal", "destaque", "fundo", "texto") if not str((m.get("cores") or {}).get(c, "")).startswith("#")]
    if not (m.get("carrossel") or {}).get("assinatura"):
        falta.append("carrossel.assinatura")
    if not os.path.exists(os.path.join(PASTA_MARCA, "MINHA-MARCA.md")):
        falta.append("MINHA-MARCA.md")
    return falta


def achar_fonte(nome, papel):
    for p in (os.path.join(PASTA_MARCA, "fontes", nome), os.path.join(PASTA_MARCA, nome), os.path.join(FONTES_SKILL, nome)):
        if os.path.exists(p):
            return p
    reserva = os.path.join(FONTES_SKILL, PADRAO_FONTES[papel])
    print(f"[marca] fonte {nome} ({papel}) não encontrada; usando {os.path.basename(reserva)}", file=sys.stderr)
    return reserva


def fmt(arq):
    return {"ttf": "truetype", "otf": "opentype", "woff2": "woff2", "woff": "woff"}.get(arq.rsplit(".", 1)[-1].lower(), "truetype")


def css(destino_fontes, prefixo="fonts/"):
    m, cores, fontes = carregar()
    os.makedirs(destino_fontes, exist_ok=True)
    arqs = {}
    for papel in PADRAO_FONTES:
        src = achar_fonte(fontes.get(papel, PADRAO_FONTES[papel]), papel)
        shutil.copy2(src, os.path.join(destino_fontes, os.path.basename(src)))
        arqs[papel] = prefixo + os.path.basename(src)
    face = lambda fam, url, extra="": f'  @font-face {{ font-family: "{fam}"; src: url("{url}") format("{fmt(url)}");{extra} }}'
    linhas = [
        face("Titulo", arqs["titulo"], " font-style: normal;"),
        face("Titulo", arqs["titulo_italico"], " font-style: italic;"),
        face("Corpo", arqs["legenda_media"], " font-weight: 400;"),
        face("Corpo", arqs["legenda_media"], " font-weight: 500;"),
        face("Corpo", arqs["legenda"], " font-weight: 600;"),
        face("Corpo", arqs["legenda"], " font-weight: 700;"),
        face("Manuscrita", arqs["manuscrita"]),
        "  :root {",
        f"    /* marca: {m.get('nome', '')} {m.get('arroba', '')} · assinatura: {(m.get('carrossel') or {}).get('assinatura', '')} · máximo de cores por peça: {(m.get('carrossel') or {}).get('max_cores', 4)} */",
    ]
    for k in ("principal", "destaque", "fundo", "fundo_2", "texto", "claro", "escuro", "raro"):
        linhas.append(f"    --cor-{k.replace('_', '-')}: {cores.get(k, PADRAO_CORES[k])};")
    linhas += [
        "    --cor-principal-escura: color-mix(in srgb, var(--cor-principal) 60%, black);",
        '    --fonte-titulo: "Titulo", Georgia, serif;',
        '    --fonte-corpo: "Corpo", system-ui, sans-serif;',
        '    --fonte-manuscrita: "Manuscrita", cursive;',
        "  }",
    ]
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--conferir":
        f = faltando()
        print("manual completo" if not f else "falta: " + ", ".join(f) + "  -> fazer a ENTREVISTA-DA-MARCA.md")
        sys.exit(1 if f else 0)
    if a[0] == "--saida":
        pasta = a[1]
        os.makedirs(pasta, exist_ok=True)
        open(os.path.join(pasta, "marca.css"), "w", encoding="utf-8").write(css(os.path.join(pasta, "fonts")))
        print("ok", os.path.join(pasta, "marca.css"))
    elif a[0] == "--aplicar":
        arq = a[1]
        s = open(arq, encoding="utf-8").read()
        ini = s.index("  @font-face")
        fim = s.index("}", s.index(":root {")) + 1
        novo = s[:ini] + css(os.path.join(os.path.dirname(os.path.abspath(arq)), "fonts")) + s[fim:]
        saida = arq[:-5] + "-marca.html"
        open(saida, "w", encoding="utf-8").write(novo)
        print("ok", saida)
    else:
        print(__doc__)
