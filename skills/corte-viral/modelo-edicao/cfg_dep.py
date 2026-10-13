# Config (título, emojis, sons, aproximações) dos depoimentos refeitos. As emendas vêm do próprio source.mp4
# (cortes secos detectados por diferença de quadro), porque o source já passou por corte de silêncio e de vícios.
# Uso: python3 cfg_dep.py DEP-nome-1 DEP-nome-2 ...   (os build("DEP-...") ficam no configs_v2.py)
import json, re, subprocess, sys, numpy as np
src = open("configs_v2.py").read()
defs = src[:src.index('\nbuild("')]
ns = {}; exec(defs, ns)
def emendas(n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{n}/source.mp4", "-vf", "scale=54:96,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 96, 54).astype(float)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2)); out = [0.0]
    for i in range(2, len(d) - 2):
        viz = np.median([d[i - 2], d[i - 1], d[i + 1], d[i + 2]])
        if d[i] > 6 and d[i] > 3.5 * max(viz, 1.0) and (i + 1) / 30 - out[-1] > 0.8: out.append(round((i + 1) / 30, 3))
    return out
ns["_cuts"] = emendas
chamadas = re.findall(r'\nbuild\(("DEP-[^"]+").*?\)\)(?:, t1_size=\d+)?\)?', src, re.S)
for alvo in sys.argv[1:]:
    ini = src.index(f'\nbuild("{alvo}"'); fim = src.find('\nbuild("', ini + 5); bloco = src[ini:fim if fim > 0 else len(src)]
    exec(bloco, ns)
