# -*- coding: utf-8 -*-
"""
Exporta slides HTML em PNG 1080x1350 (ou outro tamanho) com o Chrome/Edge sem abrir janela.

  python3 exportar_png.py <pasta-com-slide-01.html...>          -> slide-01.png, slide-02.png ... na mesma pasta
  python3 exportar_png.py slide-01.html slide-02.html           -> um PNG por HTML
  python3 exportar_png.py <pasta> --tamanho 1080x1920            -> story

Cada slide é um HTML com <body> do tamanho exato (1080x1350), margem 0 e o <link rel="stylesheet" href="marca.css">.
Se o Playwright estiver instalado (pip install playwright && playwright install chromium) ele é usado;
senão, usa o Chrome (ou o Edge no Windows) instalado no computador.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

a = sys.argv[1:]
tam = "1080x1350"
if "--tamanho" in a:
    i = a.index("--tamanho"); tam = a[i + 1]; del a[i:i + 2]
W, H = (int(x) for x in tam.lower().split("x"))
arquivos = []
for x in a:
    arquivos += sorted(glob.glob(os.path.join(x, "slide-*.html"))) if os.path.isdir(x) else [x]
if not arquivos:
    print(__doc__); sys.exit(1)


def chrome():
    cands = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
    ]
    for c in cands:
        if os.path.exists(c):
            return c
    for n in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        if shutil.which(n):
            return shutil.which(n)
    return None


try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": W, "height": H})
        for f in arquivos:
            pag.goto("file://" + os.path.abspath(f).replace("\\", "/"))
            pag.wait_for_timeout(400)          # fontes carregarem
            pag.screenshot(path=f[:-5] + ".png")
            print("ok", f[:-5] + ".png")
        nav.close()
except ImportError:
    c = chrome()
    if not c:
        sys.exit("Não achei Chrome nem Edge. Instale o Chrome ou: pip install playwright && playwright install chromium")
    perfil = tempfile.mkdtemp(prefix="chrome-png-")   # perfil separado: não trava se o Chrome já estiver aberto
    for f in arquivos:
        url = "file:///" + os.path.abspath(f).replace("\\", "/").lstrip("/")
        subprocess.run([c, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={W},{H}",
                        f"--user-data-dir={perfil}", "--no-first-run", "--no-default-browser-check",
                        "--run-all-compositor-stages-before-draw", f"--screenshot={os.path.abspath(f[:-5] + '.png')}", url],
                       capture_output=True, timeout=120)
        print("ok" if os.path.exists(f[:-5] + ".png") else "FALHOU", f[:-5] + ".png")
