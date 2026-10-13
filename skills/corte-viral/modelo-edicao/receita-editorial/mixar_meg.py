# voz (do source.mp4) + efeitos do meta.json + trilha baixinha (se o manual da marca pedir). Uso: python mixar_meg.py <nome>
# Trilha: marca.json -> "trilha": {"usar": true, "arquivo": "trilha.wav" (em assets/ ou ~/minha-marca/sons/), "volume_db": -13}
# Som que faltar (ver SONS-PARA-BAIXAR.md) é trocado por um parecido do pacote Pixabay.
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.expanduser("~/.claude/skills/corte-viral/modelo-edicao"))   # se a receita foi copiada pra outra pasta
import marca
D = sys.argv[1]; M = json.load(open(f"{D}/meta.json")); DUR = M["dur"]
T = marca.carregar()["trilha"]; VOL = marca.volume_efeitos()
trilha = None
if T.get("usar") and T.get("arquivo"):
    for c in (os.path.join("assets", T["arquivo"]), os.path.join(marca.PASTA_MARCA, "sons", T["arquivo"]), os.path.expanduser(T["arquivo"])):
        if os.path.exists(c): trilha = c; break
    if not trilha: print("AVISO: trilha", T["arquivo"], "não encontrada; vai sem trilha")
FX = []
for fx in M["sfx"]:
    p = marca.som(fx[0], "assets")
    if p: FX.append([p] + list(fx[1:]))
args = ["ffmpeg","-nostdin","-v","error","-y","-i",f"{D}/frente/render.mp4","-i",f"{D}/source.mp4"]; fc = []; base = 2
if trilha:
    args += ["-i", trilha]; base = 3
    fc.append(f"[2:a]atrim=0:{DUR},volume={T.get('volume_db', -13)}dB,afade=t=out:st={max(0,DUR-2.5):.2f}:d=2.5[tr]")
for i, fx in enumerate(FX):
    f, t, g = fx[:3]; d = fx[3] if len(fx) > 3 else None
    cut = f"atrim=0:{d},afade=t=out:st={max(0,d-0.08):.3f}:d=0.08," if d else ""
    args += ["-i", f]; ms = int(t * 1000); fc.append(f"[{i+base}:a]aresample=48000,{cut}volume={g + VOL}dB,adelay={ms}|{ms}[f{i}]")
fc.append("[1:a]" + ("[tr]" if trilha else "") + "".join(f"[f{i}]" for i in range(len(FX))) + f"amix=inputs={len(FX)+base-1}:normalize=0:duration=first,alimiter=limit=0.89[a]")
subprocess.run(args + ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{D}/final.mp4"], check=True)
print("ok", D)
