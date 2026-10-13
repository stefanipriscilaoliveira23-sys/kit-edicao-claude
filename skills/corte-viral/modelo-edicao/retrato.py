# Close da cintura pra cima + luz melhor (sem desfoque de fundo).
# Uso: python3 retrato.py <nome-do-corte-v2>
# 1) acha a pessoa no bruto (máscara do macOS) -> caixa do close
# 2) renderiza o corte direto do 4K já recortado (nitidez) em 1080x1920
# 3) correção de luz leve e ruído de fundo tirado
# Só no Mac (usa o recorte de pessoa do macOS). No Windows use o modo "seguir" (retrato_seguir.py), que vai pelo rosto.
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marca
MASC = marca.cmd_mascara()
if not MASC and not os.path.exists("caixa-forcada.json"):
    raise SystemExit("retrato.py precisa do mascara-pessoa (Mac). Neste computador use: base.sh <nome> seguir <transcricao> (retrato_seguir.py)")
nome = sys.argv[1]
src = json.load(open("fontes.json"))[nome]; tl = json.load(open("plano-cortes.json"))[nome]
os.makedirs(nome, exist_ok=True); tmp = f"{nome}/_tmp"; os.makedirs(tmp, exist_ok=True)
def run(*a): subprocess.run(a, check=True)

# 1) caixa do close a partir de ~20 s do bruto
a0 = tl[0][0]
_forcar0 = json.load(open("caixa-forcada.json")).get(nome) if os.path.exists("caixa-forcada.json") else None
if not MASC and not _forcar0: raise SystemExit(f"{nome}: sem mascara-pessoa neste computador; coloque a caixa em caixa-forcada.json ou use o modo seguir")
if MASC: run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(a0), "-t", "20", "-i", src, "-c", "copy", f"{tmp}/amostra.mov")
if MASC: run(MASC, f"{tmp}/amostra.mov", f"{tmp}/amostra-m.mp4", "270")
W0, H0 = 270, 480
raw = b"" if not MASC else subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", f"{tmp}/amostra-m.mp4", "-vf", f"scale={W0}:{H0},fps=5", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H0, W0) > 128
tops, bots, cxs = [], [], []
for m in fr:
    ys = np.where(m.any(1))[0]
    if len(ys) < 20: continue
    top, bot = ys[0], ys[-1]
    faixa = m[top: top + max(5, (bot - top) // 5)]   # cabeça/ombros: centro horizontal
    xs = np.where(faixa.any(0))[0]
    tops.append(top / H0); bots.append(bot / H0); cxs.append((xs[0] + xs[-1]) / 2 / W0)
cabeca, pe, cx = (float(np.median(tops)), float(np.median(bots)), float(np.median(cxs))) if tops else (0.1, 0.95, 0.5)
cintura = cabeca + 0.47 * (pe - cabeca)
ch = min(1.0, (cintura - cabeca) / 0.70)          # cabeça a 22% do topo, cintura perto do pé do quadro
topo = max(0.0, cabeca - 0.22 * ch)
if topo + ch > 1: topo = 1 - ch
cw = ch                                            # em fração: largura relativa = altura relativa (quadro já é 9:16)
x = min(max(0.0, cx - cw / 2), 1 - cw)
_forcar = json.load(open("caixa-forcada.json")).get(nome) if os.path.exists("caixa-forcada.json") else None
if _forcar: x, topo, cw, ch = _forcar["x"], _forcar["y"], _forcar["w"], _forcar["h"]
caixa = dict(x=round(x, 4), y=round(topo, 4), w=round(cw, 4), h=round(ch, 4), cabeca=round(cabeca, 3), pe=round(pe, 3))
json.dump(caixa, open(f"{nome}/caixa.json", "w"))
print(nome, "close:", caixa)

# 2) corte direto do bruto com o recorte (fração do quadro já girado)
args, fc = [], []
crop = f"crop=iw*{caixa['w']}:ih*{caixa['h']}:iw*{caixa['x']}:ih*{caixa['y']}"
for k, (a, b) in enumerate(tl):
    args += ["-ss", f"{a:.3f}", "-t", f"{b-a:.3f}", "-i", src]
    fc.append(f"[{k}:v:0]{crop},scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p[v{k}];[{k}:a:0]aresample=48000,asetpts=PTS-STARTPTS[a{k}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(len(tl))) + f"concat=n={len(tl)}:v=1:a=1[vc][ac];[vc]scale=in_range=pc:out_range=tv,format=yuv420p[v];[ac]loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[a]")
if not os.path.exists(f"{tmp}/close.mp4"): run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", f"{tmp}/close.mp4")

# 3) sem desfoque de fundo (reprovado: fica artificial): só luz suave e ruído de fundo tirado (sem mexer no timbre)
run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", f"{tmp}/close.mp4",
    "-vf", "eq=brightness=0.025:contrast=1.05:saturation=1.06:gamma=1.05,format=yuv420p",
    "-af", "highpass=f=70,afftdn=nr=12:nf=-40:tn=1",
    "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{nome}/source.mp4")
print("ok", nome)
