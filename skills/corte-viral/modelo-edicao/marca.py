# -*- coding: utf-8 -*-
"""
Lê o Manual da Marca da aluna e entrega os valores que os scripts de edição usam.

Onde mora o manual: ~/minha-marca/marca.json  (dá pra trocar com a variável MINHA_MARCA=/outra/pasta)
Se o arquivo ou algum campo faltar, usa padrões NEUTROS (preto, branco e cinza; fontes livres que vêm
com a skill) e avisa no terminal. Antes de editar, o Claude roda `python3 marca.py conferir`: se faltar
coisa, ele faz a entrevista da marca (ver ../ENTREVISTA-DA-MARCA.md) e completa o manual.

Uso direto no terminal:
  python3 marca.py                 -> resumo da marca (o que está preenchido e o que falta)
  python3 marca.py conferir        -> sai com erro (código 1) se o manual estiver incompleto
  python3 marca.py pasta trabalho  -> imprime a pasta de trabalho (cria se não existir)
  python3 marca.py pasta entrega   -> imprime a pasta de entrega (cria se não existir)
  python3 marca.py cor destaque    -> imprime a cor (#RRGGBB)
  python3 marca.py python          -> imprime o Python certo pra rodar os scripts (o da venv da skill)

Dentro de um script:
  import marca
  M = marca.carregar()
  marca.cor("destaque"), marca.rgba("escuro", 0.7), marca.copiar_fontes(pasta), marca.som("pop", pasta_sfx)
"""
import copy
import json
import os
import shutil
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA_MARCA = os.path.expanduser(os.environ.get("MINHA_MARCA", "~/minha-marca"))
ARQ_MARCA = os.path.join(PASTA_MARCA, "marca.json")
# Raiz da skill corte-viral: a pasta acima desta (quando roda de dentro da skill) ou a instalada em ~/.claude/skills
# (quando os scripts foram copiados pra pasta de trabalho pelo preparar_pasta.py).
SKILL_RAIZ = next((p for p in (os.path.dirname(AQUI), os.path.expanduser("~/.claude/skills/corte-viral"))
                   if os.path.exists(os.path.join(p, "vch"))), os.path.dirname(AQUI))
_ASSETS = next((p for p in (os.path.join(AQUI, "assets"), os.path.join(SKILL_RAIZ, "modelo-edicao", "assets"))
                if os.path.isdir(os.path.join(p, "fonts"))), os.path.join(AQUI, "assets"))
FONTES_SKILL = os.path.join(_ASSETS, "fonts")
SONS_SKILL = os.path.join(_ASSETS, "sfx")

# Padrões neutros: nada de identidade de ninguém. Servem só pra o script não quebrar.
PADRAO = {
    "nome": "",
    "arroba": "",
    "cores": {
        "principal": "#222222",   # cor mais forte da marca
        "destaque": "#4A4A4A",    # caixa/sublinhado da palavra-chave, pílulas, riscos
        "fundo": "#F5F5F5",       # fundo claro (cartões, slides)
        "texto": "#1A1A1A",       # texto escuro em cima de fundo claro
        "claro": "#FFFFFF",       # texto claro em cima de vídeo/fundo escuro
        "escuro": "#000000",      # sombras e degradês por cima do vídeo
    },
    "fontes": {
        "titulo": "InstrumentSerif-Regular.ttf",
        "titulo_italico": "InstrumentSerif-Italic.ttf",
        "legenda": "Inter-Bold.woff2",
        "legenda_media": "Inter-Medium.woff2",
        "manuscrita": "Mynerve-Regular.ttf",
        "giz": "PermanentMarker-Regular.woff2",
    },
    "legenda": {
        "posicao": "baixo",          # baixo | meio | alto (ou use topo_px)
        "topo_px": None,             # altura exata em pixels (1080x1920); vence a posicao
        "cor": "#FFFFFF",
        "destaque": "caixa",         # caixa | sublinhado | italico | cor
        "palavras_por_vez": 3,
        "tamanho_px": 74,
    },
    "emojis": True,
    "efeitos": {"volume_db": 0},
    "trilha": {"usar": False, "arquivo": "", "volume_db": -13},
    "pastas": {"trabalho": "~/Videos-Claude/_trabalho", "entrega": "~/Videos-Claude/PRONTOS"},
    "transcricao": {"vocabulario": "", "trocas": {}},
    "nomes_proprios": [],
}
# Fonte livre que vem com a skill, usada quando a fonte do manual não é encontrada.
FONTE_RESERVA = dict(PADRAO["fontes"])
POSICAO_TOPO = {"baixo": 1150, "meio": 900, "alto": 640}
# Som que falta (não pôde ir no pacote por licença) -> som parecido do pacote Pixabay.
SOM_SUBSTITUTO = {
    "maquina": "typing", "escrita": "typing", "typing1": "typing", "typing1-alto": "typing",
    "pagina": "whoosh", "pagina-alto": "whoosh-short", "giz": "typing", "giz1": "typing",
    "giz1-alto": "typing", "error-alto": "error", "toque": "click-soft",
}
_cache = None
_avisos = set()


def _aviso(txt):
    if txt not in _avisos:
        _avisos.add(txt)
        print(f"[marca] {txt}", file=sys.stderr)


def _mescla(base, extra):
    for k, v in (extra or {}).items():
        if k.startswith("_"):
            continue                      # campos de explicação no json
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _mescla(base[k], v)
        elif v not in (None, ""):
            base[k] = v
    return base


def carregar(recarregar=False):
    """Manual da marca já misturado com os padrões neutros."""
    global _cache
    if _cache is not None and not recarregar:
        return _cache
    m = copy.deepcopy(PADRAO)
    if os.path.exists(ARQ_MARCA):
        try:
            _mescla(m, json.load(open(ARQ_MARCA, encoding="utf-8")))
        except Exception as e:  # json com erro de digitação
            _aviso(f"não consegui ler {ARQ_MARCA} ({e}). Usando padrões neutros.")
    else:
        _aviso(f"{ARQ_MARCA} não existe. Usando padrões neutros. Faça a entrevista da marca antes de entregar.")
    _cache = m
    return m


def faltando():
    """Lista do que o manual ainda não tem (pra decidir se precisa da entrevista)."""
    falta = []
    if not os.path.exists(ARQ_MARCA):
        return ["marca.json inteiro"]
    bruto = json.load(open(ARQ_MARCA, encoding="utf-8"))
    for campo in ("nome", "arroba"):
        if not bruto.get(campo):
            falta.append(campo)
    cores = bruto.get("cores") or {}
    for c in ("principal", "destaque", "fundo", "texto"):
        if not str(cores.get(c, "")).startswith("#"):
            falta.append(f"cores.{c}")
    if not os.path.exists(os.path.join(PASTA_MARCA, "MINHA-MARCA.md")):
        falta.append("MINHA-MARCA.md")
    return falta


def cor(nome):
    return carregar()["cores"].get(nome) or PADRAO["cores"].get(nome, "#000000")


def rgba(nome, alfa):
    h = cor(nome).lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alfa})"


def fonte_arquivo(papel):
    """Caminho do arquivo da fonte: primeiro em ~/minha-marca/fontes, depois nas fontes livres da skill."""
    nome = carregar()["fontes"].get(papel) or FONTE_RESERVA.get(papel)
    for pasta in (os.path.join(PASTA_MARCA, "fontes"), PASTA_MARCA, FONTES_SKILL):
        p = os.path.join(pasta, nome)
        if os.path.exists(p):
            return p
    reserva = os.path.join(FONTES_SKILL, FONTE_RESERVA.get(papel, "Inter-Medium.woff2"))
    _aviso(f"fonte '{nome}' ({papel}) não encontrada em {PASTA_MARCA}/fontes. Usando {os.path.basename(reserva)}.")
    return reserva


def copiar_fontes(destino):
    """Copia as fontes da marca pra dentro do projeto (o render só enxerga arquivos do projeto).
    Devolve {papel: nome_do_arquivo} pra montar o @font-face com url relativa."""
    os.makedirs(destino, exist_ok=True)
    mapa = {}
    for papel in PADRAO["fontes"]:
        src = fonte_arquivo(papel)
        alvo = os.path.join(destino, os.path.basename(src))
        if not os.path.exists(alvo) or os.path.getsize(alvo) != os.path.getsize(src):
            shutil.copy2(src, alvo)
        mapa[papel] = os.path.basename(src)
    return mapa


def _formato(arq):
    ext = arq.rsplit(".", 1)[-1].lower()
    return {"ttf": "truetype", "otf": "opentype", "woff2": "woff2", "woff": "woff"}.get(ext, "truetype")


def font_face(familia, url, peso=None):
    p = f" font-weight: {peso};" if peso else ""
    return f'@font-face {{ font-family: "{familia}"; src: url("{url}") format("{_formato(url)}");{p} }}'


def legenda_topo():
    L = carregar()["legenda"]
    if L.get("topo_px"):
        return int(L["topo_px"])
    return POSICAO_TOPO.get(str(L.get("posicao", "baixo")).lower(), 1150)


def som(nome, pasta_sfx):
    """Caminho do som. Aceita 'pop' ou 'pop.wav'. Procura na pasta de sons do projeto, depois em
    ~/minha-marca/sons, depois troca por um som parecido do pacote Pixabay. None = pular o som."""
    base = os.path.basename(nome)
    base = base[:-4] if base.lower().endswith((".wav", ".mp3")) else base
    for pasta in (pasta_sfx, os.path.join(PASTA_MARCA, "sons"), SONS_SKILL):
        for ext in (".wav", ".mp3"):
            p = os.path.join(pasta, base + ext)
            if os.path.exists(p):
                return p
    sub = SOM_SUBSTITUTO.get(base)
    if sub:
        _aviso(f"som '{base}' não está instalado (ver SONS-PARA-BAIXAR.md). Usando '{sub}' no lugar.")
        return som(sub, pasta_sfx)
    _aviso(f"som '{base}' não encontrado: vai sem ele.")
    return None


def volume_efeitos():
    return float(carregar()["efeitos"].get("volume_db", 0) or 0)


def pasta(tipo):
    p = os.path.expanduser(carregar()["pastas"].get(tipo) or PADRAO["pastas"][tipo])
    os.makedirs(p, exist_ok=True)
    return p


def trocas():
    return dict(carregar()["transcricao"].get("trocas") or {})


def vocabulario():
    return carregar()["transcricao"].get("vocabulario") or ""


def nomes_proprios():
    return list(carregar().get("nomes_proprios") or [])


def python():
    """Python da venv da skill (tem numpy, faster-whisper, opencv, scipy). Se não tiver, o atual."""
    for p in (os.path.join(SKILL_RAIZ, ".venv", "bin", "python"),
              os.path.join(SKILL_RAIZ, ".venv", "Scripts", "python.exe")):
        if os.path.exists(p):
            return p
    return sys.executable


def binario(*partes):
    """Ferramenta da skill (deep-filter, olhar, mascara-pessoa). None se não existir neste computador."""
    p = os.path.join(SKILL_RAIZ, *partes)
    for c in (p, p + ".exe"):
        if os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None


def cmd_olhar():
    """Comando que mede o rosto quadro a quadro: o binário do Mac (Vision) ou, se não tiver, o olhar.py (OpenCV)."""
    b = binario("modelo-edicao", "olhar", "olhar")
    return [b] if b and sys.platform == "darwin" else [python(), os.path.join(AQUI, "olhar", "olhar.py")]


def cmd_mascara():
    """Recorte da pessoa (só Mac, Vision). None nos outros sistemas: as técnicas de 'texto atrás da pessoa' ficam de fora."""
    b = binario("modelo-edicao", "mascara-pessoa", "mascara-pessoa")
    return b if b and sys.platform == "darwin" else None


if __name__ == "__main__":
    a = sys.argv[1:]
    M = carregar()
    if not a:
        print(f"Manual da marca: {ARQ_MARCA} ({'existe' if os.path.exists(ARQ_MARCA) else 'NÃO EXISTE'})")
        print(f"  nome: {M['nome'] or '-'}   @: {M['arroba'] or '-'}")
        print("  cores:", ", ".join(f"{k} {v}" for k, v in M["cores"].items()))
        print("  fontes:", ", ".join(f"{k} {os.path.basename(fonte_arquivo(k))}" for k in M["fontes"]))
        print(f"  legenda: {M['legenda']}")
        print(f"  emojis: {'sim' if M['emojis'] else 'não'}   efeitos: {volume_efeitos():+.0f} dB   trilha: {M['trilha']}")
        print(f"  trabalho: {os.path.expanduser(M['pastas']['trabalho'])}   entrega: {os.path.expanduser(M['pastas']['entrega'])}")
        f = faltando()
        print("  falta:", ", ".join(f) if f else "nada")
    elif a[0] == "conferir":
        f = faltando()
        print("manual completo" if not f else "falta: " + ", ".join(f))
        sys.exit(1 if f else 0)
    elif a[0] == "pasta":
        print(pasta(a[1]))
    elif a[0] == "cor":
        print(cor(a[1]))
    elif a[0] == "python":
        print(python())
    elif a[0] == "mascara":
        print(cmd_mascara() or "")
    elif a[0] == "deepfilter":
        print(binario("bin", "deep-filter") or "")
    elif a[0] == "som":
        print(som(a[1], a[2] if len(a) > 2 else SONS_SKILL) or "")
    else:
        print(__doc__)
