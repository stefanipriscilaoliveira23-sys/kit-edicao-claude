# Mixa a voz original + efeitos por cima do video renderizado
# Uso: python3 mixar_clip.py <pasta-do-corte>   (usa render.mp4 e config.json["sfx"]) -> final.mp4
# Som que faltar (ver SONS-PARA-BAIXAR.md) e trocado por um parecido do pacote Pixabay; volume geral dos efeitos vem do manual da marca.
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marca
D = sys.argv[1]
cfg = json.load(open(os.path.join(D, "config.json")))
S = os.path.join(D, "assets", "sfx") + "/"
# maquina de escrever do titulo sempre entra; o resto vem do config (arquivo, inicio s, ganho dB)
FX = [("maquina", json.load(open(os.path.join(D, "titulo.json"))).get("type0", 0.55), -6)] + [tuple(x) for x in cfg.get("sfx", [])]
# whoosh nas aproximacoes (emendas impares), longe dos outros sons, no maximo 4
ws = 0
for i, t in enumerate(cfg["cuts"] if cfg.get("whoosh", True) else []):
    if i % 2 == 1 and t > cfg.get("title_at", 0) + 4.0 and ws < 4 and all(abs(t - x[1]) > 0.8 for x in FX):
        FX.append(("whoosh-short", round(t - 0.12, 2), -7)); ws += 1
args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", os.path.join(D, "render.mp4"), "-i", os.path.join(D, "source.mp4")]
fc = []
VOL = marca.volume_efeitos()
FX = [(marca.som(f, S), t, g) for f, t, g in FX]
FX = [x for x in FX if x[0]]
for i, (f, t, g) in enumerate(FX):
    args += ["-i", f]
    ms = int(t * 1000)
    fc.append(f"[{i+2}:a]volume={g + VOL}dB,adelay={ms}|{ms}[f{i}]")
fc.append("[1:a]" + "".join(f"[f{i}]" for i in range(len(FX))) + f"amix=inputs={len(FX)+1}:normalize=0:duration=first,alimiter=limit=0.89[a]")
args += ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.join(D, "final.mp4")]
subprocess.run(args, check=True); print("ok", D)
