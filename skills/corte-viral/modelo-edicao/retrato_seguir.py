# Close do depoimento SEGUINDO o rosto: em cada trecho do plano o recorte acompanha o rosto de quem fala
# (desliza do começo ao fim do trecho), um pouco mais aberto que o retrato.py, pra ela nunca ficar cortada.
# Uso: python3 retrato_seguir.py <nome-v2> <rosto-do-bruto.csv> [largura_recorte=0.62]
#   o rosto-do-bruto.csv sai do `olhar` (Mac) ou do olhar/olhar.py (qualquer sistema): ver marca.cmd_olhar()
import csv, json, os, subprocess, sys
nome, rcsv = sys.argv[1], sys.argv[2]
W = float(sys.argv[3]) if len(sys.argv) > 3 else 0.62
src = json.load(open("fontes.json"))[nome]; tl = json.load(open("plano-cortes.json"))[nome]
rosto = [r for r in csv.DictReader(open(rcsv)) if r["tem_rosto"] == "1"]
tmp = f"{nome}/_tmp"; os.makedirs(tmp, exist_ok=True)
if not os.path.lexists(f"{nome}/assets"): os.symlink("../assets", f"{nome}/assets")
def med(xs): xs = sorted(xs); return xs[len(xs) // 2]
caixas, ultimo = [], None
for a, b in tl:
    p = [r for r in rosto if a - 0.2 <= float(r["tempo"]) <= b + 0.2]
    if p: cx, cy = med([float(r["cx"]) for r in p]), med([float(r["cy"]) for r in p])
    elif ultimo: cx, cy = ultimo
    else: cx, cy = 0.5, 0.3
    ultimo = (cx, cy)
    ini = [float(r["cx"]) for r in p if float(r["tempo"]) <= a + 0.6] or [cx]
    fim = [float(r["cx"]) for r in p if float(r["tempo"]) >= b - 0.6] or [cx]
    cl = lambda v: round(min(max(0.0, v - W / 2), 1 - W), 4)
    y = min(max(0.0, cy - 0.27 * W), 1 - W)   # rosto a ~27% do topo
    caixas.append((cl(med(ini)), cl(med(fim)), round(y, 4)))
json.dump(caixas, open(f"{tmp}/caixas-seguir.json", "w"))
args, fc = [], []
for k, ((a, b), (x0, x1, y)) in enumerate(zip(tl, caixas)):
    args += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", src]
    xe = f"iw*({x0}+({x1}-{x0})*min(t/{b - a:.3f}\\,1))" if abs(x1 - x0) > 0.01 else f"iw*{x0}"
    fc.append(f"[{k}:v:0]setpts=PTS-STARTPTS,crop=iw*{W}:ih*{W}:{xe}:ih*{y},scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p[v{k}];[{k}:a:0]aresample=48000,asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(0, b - a - 0.025):.3f}:d=0.025[a{k}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(len(tl))) + f"concat=n={len(tl)}:v=1:a=1[vc][ac];[vc]scale=in_range=pc:out_range=tv,eq=brightness=0.025:contrast=1.05:saturation=1.06:gamma=1.05,format=yuv420p[v];[ac]loudnorm=I=-14:TP=-1:LRA=11,aresample=48000,highpass=f=70,afftdn=nr=12:nf=-40:tn=1[a]")
open(f"{tmp}/filtro-seguir.txt", "w").write(";".join(fc))
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args, "-filter_complex_script", f"{tmp}/filtro-seguir.txt", "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-g", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{nome}/source.mp4"], check=True)
print("ok", nome, len(tl), "trechos")
