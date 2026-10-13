# Junta os trechos do plano (plano-cortes.json) num vertical 1080x1920 numa passada so -> <nome>/source.mp4
# Uso: python render_vertical.py <nome>   (o bruto de cada nome fica em fontes.json)
import json, subprocess, sys, os
SRC = json.load(open("fontes.json")).get(sys.argv[1])
if not SRC: raise SystemExit(f"{sys.argv[1]} nao tem bruto em fontes.json")
nome = sys.argv[1]; tl = json.load(open("plano-cortes.json"))[nome]
os.makedirs(nome, exist_ok=True)
args = []; fc = []
for n, (a, b) in enumerate(tl):
    args += ["-ss", f"{a:.3f}", "-t", f"{b-a:.3f}", "-i", SRC]
    fc.append(f"[{n}:v:0]scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p[v{n}];[{n}:a:0]aresample=48000,asetpts=PTS-STARTPTS[a{n}]")
cat = "".join(f"[v{i}][a{i}]" for i in range(len(tl)))
fc.append(f"{cat}concat=n={len(tl)}:v=1:a=1[vc][ac];[vc]scale=in_range=pc:out_range=tv,format=yuv420p[v];[ac]loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[a]")
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-color_range", "tv", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{nome}/source.mp4"], check=True)
print("ok", nome)
