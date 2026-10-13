#!/usr/bin/env python3
"""
Gera as lâminas do formato "Conteúdo amarelinho" em PNG 1080x1350.

Uso:
  python3 gerar.py copy.json                 -> gera todas as lâminas
  python3 gerar.py copy.json --so 1,2        -> só a capa e a lâmina 2 (pra aprovar)
  python3 gerar.py copy.json --saida /pasta  -> muda a pasta de saída

Pasta padrão: ~/Carrosseis-Claude/amarelinho-<tema>/
Precisa só do Google Chrome instalado (usa o modo sem janela dele).
O formato do copy.json está no SKILL.md e em exemplo-copy.json.
"""
from concurrent.futures import ThreadPoolExecutor
import argparse, html, json, os, re, shutil, subprocess, sys, tempfile, unicodedata
from pathlib import Path
from urllib.parse import quote

PASTA = Path(__file__).resolve().parent
MODELO = PASTA / "modelo.html"

# Onde procurar a SF Pro Display (fonte da Apple: usar só no próprio Mac, nunca empacotar pra outras pessoas)
PASTAS_FONTE = [
    PASTA / "fontes",
    Path.home() / "Library/Fonts",
    Path("/Library/Fonts"),
]
GOOGLE_FONTS = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                '<link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300..800'
                '&family=Playpen+Sans:wght@300..600&family=Mynerve&display=block" rel="stylesheet">')

CHROMES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def achar_chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for c in CHROMES:
        if Path(c).exists():
            return c
    for nome in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge"):
        p = shutil.which(nome)
        if p:
            return p
    sys.exit("Não achei o Google Chrome. Instale o Chrome (google.com/chrome) e rode de novo.")


def achar_arquivo(nomes):
    for pasta in PASTAS_FONTE:
        for n in nomes:
            f = pasta / n
            if f.exists():
                return f
    return None


def url_arquivo(p):
    return "file://" + quote(str(Path(p).expanduser().resolve()))


def montar_fontes(escolha):
    """Devolve (html das fontes, nome da família principal, descrição)."""
    partes = [GOOGLE_FONTS]
    familia = '"Inter"'
    desc = "Inter (fonte livre, parecida com a SF Pro)"
    if escolha in ("sf", "auto"):
        pesos = {
            300: ["SFProDisplay-Light.otf", "SF-Pro-Display-Light.otf"],
            400: ["SFProDisplay-Regular.otf", "SF-Pro-Display-Regular.otf"],
            500: ["SFProDisplay-Medium.otf", "SF-Pro-Display-Medium.otf"],
            600: ["SFProDisplay-Semibold.otf", "SF-Pro-Display-Semibold.otf"],
            700: ["SFProDisplay-Bold.otf", "SF-Pro-Display-Bold.otf"],
            800: ["SFProDisplay-Heavy.otf", "SF-Pro-Display-Heavy.otf"],
        }
        faces = []
        for peso, nomes in pesos.items():
            f = achar_arquivo(nomes)
            if f:
                faces.append(f'@font-face{{font-family:"SF Pro Display";src:url("{url_arquivo(f)}");font-weight:{peso}}}')
        if any("font-weight:700" in x for x in faces):
            partes.append("<style>" + "".join(faces) + "</style>")
            familia = '"SF Pro Display"'
            desc = "SF Pro Display (arquivos do próprio Mac)"
        elif escolha == "sf":
            print("Aviso: SF Pro Display não encontrada neste computador. Usando Inter no lugar.")
    mao = achar_arquivo(["Mynerve-Regular.ttf"])
    if mao:
        partes.append(f'<style>@font-face{{font-family:"Mynerve";src:url("{url_arquivo(mao)}")}}</style>')
    pilha = f'{familia}, "Inter", -apple-system, "Helvetica Neue", Arial, sans-serif'
    partes.append(f"<style>:root{{--fonte:{pilha}}}</style>")
    return "\n".join(partes), desc


def texto_para_html(t):
    """Quebra de linha = \\n.  _assim_ = trecho fino (peso leve). O resto fica em negrito."""
    t = html.escape(t.strip())
    t = re.sub(r"_(.+?)_", r'<span class="leve">\1</span>', t, flags=re.S)
    return t.replace("\n", "<br>")


ICONES_ABAS = [
    '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="1"/><path d="M9 3v18M15 3v18M3 9h18M3 15h18"/></svg>',
    '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="5"/><path d="M10 8.5v7l5.5-3.5z" stroke-linejoin="round"/></svg>',
    '<svg viewBox="0 0 24 24"><path d="M5 9.5V8a3 3 0 0 1 3-3h10M15 2l3 3-3 3M19 14.5V16a3 3 0 0 1-3 3H6M9 22l-3-3 3-3" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="4"/><circle cx="12" cy="10" r="3"/><path d="M6.5 19c1-2.6 3-4 5.5-4s4.5 1.4 5.5 4"/></svg>',
]


def veu_automatico(foto):
    """Foto clara pede película mais escura. Mira um fundo final com brilho médio ~85 (como a referência)."""
    try:
        from PIL import Image, ImageOps
        im = ImageOps.exif_transpose(Image.open(Path(foto).expanduser())).convert("L").resize((64, 80))
        brilho = sum(im.getdata()) / (64 * 80)
        return round(min(.75, max(.30, (brilho - 85) / max(brilho - 20, 1))), 2)
    except Exception:
        return None  # sem a biblioteca PIL: fica o padrão do modelo (.50)


def montar_lamina(modelo, dados, lam, fontes_html, n, total):
    tipo = lam.get("tipo") or ("capa" if n == 1 else ("final" if n == total else "miolo"))
    fundo = lam.get("fundo") or dados.get("fundo_padrao") or ""
    if fundo and Path(fundo).expanduser().exists():
        fundo_html = f'<div class="foto" style="background-image:url(\'{url_arquivo(fundo)}\')"></div>'
        if lam.get("veu") is None:
            lam = dict(lam, veu=veu_automatico(fundo))
    else:
        if fundo:
            print(f"Aviso: foto não encontrada ({fundo}). Usando o fundo desenhado.")
        fundo_html = '<div class="foto sem-foto"></div>'

    assin = dados.get("assinatura", "")
    assin_html = (f'<div class="assinatura topo">{html.escape(assin)}</div>'
                  f'<div class="assinatura base">{html.escape(assin)}</div>') if assin else ""

    extras = []
    perfil = dados.get("perfil") or {}
    if tipo == "capa" and lam.get("selo", True) and perfil.get("arroba"):
        foto = perfil.get("foto")
        if foto and Path(foto).expanduser().exists():
            av = f'<div style="background-image:url(\'{url_arquivo(foto)}\')"></div>'
        else:
            av = f'<div>{html.escape(perfil["arroba"].lstrip("@")[:1].upper())}</div>'
        extras.append(f'<div class="selo"><div class="anel">{av}</div><div class="nomes">'
                      f'<b>{html.escape(perfil["arroba"].lstrip("@"))}</b>'
                      f'<span>{html.escape(perfil.get("linha2", ""))}</span></div></div>')
    emojis = lam.get("emojis", ["💖", "✨"] if tipo == "capa" else [])
    for i, e in enumerate(emojis[:2]):
        extras.append(f'<div class="emoji e{i+1}">{html.escape(e)}</div>')
    if tipo == "capa" and lam.get("abas", True):
        extras.append('<div class="abas">' + "".join(f"<div>{s}</div>" for s in ICONES_ABAS) + "</div>")

    nota = lam.get("nota", "")
    nota_html = ""
    if nota:
        seta = "" if lam.get("seta", True) else ' data-seta="nao"'
        nota_html = f'<div class="nota" id="nota"{seta}>{html.escape(nota).replace(chr(10), "<br>")}</div>'

    estilo = ""
    if lam.get("tamanho"):
        estilo += f"--tamanho:{int(lam['tamanho'])}px;--tamanho-capa:{int(lam['tamanho'])}px;"
    if lam.get("veu") is not None:  # 0 = sem película, .75 = bem escuro
        estilo += f"--veu:rgba(28,16,8,{float(lam['veu'])});"
    if estilo:
        fontes_html += f"<style>:root{{{estilo}}}</style>"

    return (modelo.replace("{{FONTES}}", fontes_html)
            .replace("{{TIPO}}", tipo)
            .replace("{{FUNDO}}", fundo_html)
            .replace("{{ASSINATURA}}", assin_html)
            .replace("{{EXTRAS}}", "\n".join(extras))
            .replace("{{TEXTO}}", texto_para_html(lam["texto"]))
            .replace("{{NOTA}}", nota_html))


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "sem-tema"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("copy")
    ap.add_argument("--saida")
    ap.add_argument("--so", help="números das lâminas, ex: 1,2")
    ap.add_argument("--prefixo", default="lamina")
    a = ap.parse_args()

    dados = json.loads(Path(a.copy).read_text(encoding="utf-8"))
    laminas = dados["laminas"]
    saida = Path(a.saida).expanduser() if a.saida else Path.home() / "Carrosseis-Claude" / f"amarelinho-{slug(dados.get('tema', 'carrossel'))}"
    saida.mkdir(parents=True, exist_ok=True)
    escolhidas = {int(x) for x in a.so.split(",")} if a.so else set(range(1, len(laminas) + 1))

    modelo = MODELO.read_text(encoding="utf-8")
    fontes_html, desc = montar_fontes(dados.get("fonte", "auto"))
    chrome = achar_chrome()
    print(f"Fonte: {desc}")

    tmp = Path(tempfile.mkdtemp(prefix="amarelinho-"))
    # foto do iPhone (.heic) não abre no Chrome: converte pra .jpg (usa o sips, que já vem no Mac)
    for i, lam in enumerate(laminas, 1):
        f = lam.get("fundo") or ""
        if f.lower().endswith((".heic", ".heif")) and Path(f).expanduser().exists():
            jpg = tmp / f"foto-{i:02d}.jpg"
            subprocess.run(["sips", "-s", "format", "jpeg", str(Path(f).expanduser()), "--out", str(jpg)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if jpg.exists():
                lam["fundo"] = str(jpg)
    trabalhos = []
    for n, lam in enumerate(laminas, 1):
        if n not in escolhidas:
            continue
        pagina = tmp / f"lamina-{n:02d}.html"
        pagina.write_text(montar_lamina(modelo, dados, lam, fontes_html, n, len(laminas)), encoding="utf-8")
        png = saida / f"{a.prefixo}-{n:02d}.png"
        if png.exists():
            png.unlink()
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--disable-extensions", "--use-mock-keychain",
               "--force-device-scale-factor=1", "--window-size=1080,1350",
               "--allow-file-access-from-files", "--virtual-time-budget=8000",
               f"--user-data-dir={tmp / f'perfil-chrome-{n}'}",
               f"--screenshot={png}", url_arquivo(pagina)]
        trabalhos.append((n, png, cmd))

    def fotografar(t):
        n, png, cmd = t
        for _ in range(2):  # tenta de novo uma vez se o Chrome engasgar
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
            if png.exists():
                return n, png
        return n, None

    print(f"Gerando {len(trabalhos)} lâmina(s)... (uns 20 a 40 segundos)")
    with ThreadPoolExecutor(max_workers=6) as ex:
        resultados = sorted(ex.map(fotografar, trabalhos))
    feitos = []
    for n, png in resultados:
        if png is None:
            print(f"ERRO na lâmina {n}. Feche o Chrome e rode de novo.")
        else:
            feitos.append(png)
            print(f"ok  {png}")
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(feitos)} lâmina(s) em: {saida}")


if __name__ == "__main__":
    main()
