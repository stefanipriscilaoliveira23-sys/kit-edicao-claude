#!/usr/bin/env python3
"""
Checagem de instalacao. Rode ANTES do primeiro projeto:

    python3 ~/.claude/skills/motion-vox/verificar.py

Verifica o que a skill precisa e o que ela carrega junto. Sai com codigo != 0 se algo
essencial faltar, para nao descobrir no meio de um render de 20 minutos.
"""
import importlib
import shutil
import subprocess
import sys
from pathlib import Path

S = Path(__file__).resolve().parent
falhas, avisos = [], []


def ok(t):
    print(f"  \033[32mok\033[0m    {t}")


def erro(t):
    print(f"  \033[31mFALTA\033[0m {t}")
    falhas.append(t)


def aviso(t):
    print(f"  \033[33maviso\033[0m {t}")
    avisos.append(t)


print(f"MOTION VOX — verificacao\n  skill em {S}\n")

print("python")
if sys.version_info < (3, 8):
    erro(f"python {sys.version_info.major}.{sys.version_info.minor} — precisa 3.8+")
else:
    ok(f"python {sys.version_info.major}.{sys.version_info.minor}")

print("\nbibliotecas")
for mod, pip in [("PIL", "Pillow"), ("numpy", "numpy"), ("cv2", "opencv-python")]:
    try:
        importlib.import_module(mod)
        ok(pip)
    except ImportError:
        erro(f"{pip}   ->  pip install {pip}")
try:
    importlib.import_module("faster_whisper")
    ok("faster-whisper")
except ImportError:
    erro("faster-whisper   ->  pip install faster-whisper")

print("\nferramentas")
for exe in ("ffmpeg", "ffprobe"):
    if shutil.which(exe):
        v = subprocess.run([exe, "-version"], capture_output=True, text=True)
        ok(f"{exe}  {v.stdout.splitlines()[0].split(' version ')[-1][:24]}")
    else:
        erro(f"{exe}   ->  brew install ffmpeg  |  apt install ffmpeg")

print("\nkit que viaja com a skill")
fontes = sorted((S / "fontes").glob("*.ttf"))
(ok if len(fontes) >= 9 else erro)(f"{len(fontes)} fontes em fontes/ (esperado 9)")
# 9 objetos vem prontos; 7 sao gerados sob demanda, na primeira cena que pedir cada um
# (SKILL.md, "Quando faltar um objeto"). Faltar um desses 7 NAO e instalacao quebrada.
PRONTOS = ["BG_PAPER", "A02_CLOCK", "A03_TAPE", "A04_CLIPS", "A05_CARD", "A06_CAVE",
           "A07_IDEA", "A08_BOX", "A09_STACK"]
SOB_DEMANDA = ["A10_SCRAPS", "A11_NIGHT", "A12_KEYBOARD", "A13_EMPTY", "A14_CRT",
               "A15_MONEY_STACK", "A17_MONEY_FEW"]
A = S / "assets"
falta = [n for n in PRONTOS if not (A / f"{n}.png").exists()]
(ok if not falta else erro)(f"{len(PRONTOS) - len(falta)} de {len(PRONTOS)} objetos prontos em assets/"
                            + (f"  (faltando: {', '.join(falta)})" if falta else ""))
pend = [n for n in SOB_DEMANDA if not (A / f"{n}.png").exists()]
if pend:
    aviso(f"{len(pend)} objeto(s) gerado(s) sob demanda ainda nao criado(s): {', '.join(pend)}")
    print("        -> normal: a IA gera na primeira cena que pedir (SKILL.md, 'Quando faltar um objeto')")
else:
    ok(f"os {len(SOB_DEMANDA)} objetos sob demanda ja foram gerados")
extras = sorted(f.stem for f in A.glob("*.png") if f.stem not in PRONTOS + SOB_DEMANDA)
if extras:
    ok(f"{len(extras)} objeto(s) novo(s) no kit: {', '.join(extras)}")
(ok if (A / "MANIFESTO.md").exists() else aviso)("assets/MANIFESTO.md")
for f in ("lib/voxlab.py", "lib/captions.py", "lib/cutout.py", "lib/crt.py",
          "lib/night_photo.py", "lib/render_template.py", "lib/compose_template.py",
          "lib/transcrever.py", "lib/gerar_asset.py", "lib/marca.py", "referencias/legenda.md", "referencias/armadilhas.md",
          "IDENTIDADE.md"):
    (ok if (S / f).exists() else erro)(f)

print("\nmotor")
sys.path.insert(0, str(S / "lib"))
try:
    import voxlab as V
    f = V.font(V.F_BLACK, 80)
    w = V.text_width("MOTION", V.F_BLACK, 80, -1.8)
    ok(f"voxlab carrega e mede tipo ({w:.0f}px para 'MOTION' em 80px)")
    im = V.boil_full(V.text_layer((400, 200), "vox", V.F_BLACK, 90, (200, 100),
                                  anchor="mm"), 0.0, **V.BOIL_PRESETS["print"])
    ok(f"boil preset 'print' aplica ({im.size[0]}x{im.size[1]})")
except Exception as e:
    erro(f"voxlab: {type(e).__name__}: {e}")
try:
    import captions as CAP
    CAP.blocos()
    erro("captions deveria exigir configurar() e nao exigiu")
except RuntimeError:
    ok("captions exige configurar() antes de rodar")
except Exception as e:
    erro(f"captions: {type(e).__name__}: {e}")

try:
    import marca as M
    c1, c2, origem = M.acentos()
    ok(f"cores de acento #{c1[0]:02X}{c1[1]:02X}{c1[2]:02X} e #{c2[0]:02X}{c2[1]:02X}{c2[2]:02X} ({origem})")
except Exception as e:
    erro(f"marca: {type(e).__name__}: {e}")

print("\nmodelo de transcricao")
try:
    from huggingface_hub import scan_cache_dir
    nomes = [r.repo_id for r in scan_cache_dir().repos]
    if any("large-v3-turbo" in n for n in nomes):
        ok("large-v3-turbo em cache")
    else:
        aviso("large-v3-turbo nao esta em cache — baixa ~1,5 GB no primeiro uso")
except Exception:
    aviso("nao deu para checar o cache do modelo (baixa no primeiro uso)")

print()
if falhas:
    print(f"\033[31m{len(falhas)} item(ns) faltando.\033[0m Resolva antes de comecar.")
    sys.exit(1)
print("\033[32mTudo pronto.\033[0m Comece por SKILL.md, secao 'Ordem de execucao'."
      + (f"  ({len(avisos)} aviso(s))" if avisos else ""))
