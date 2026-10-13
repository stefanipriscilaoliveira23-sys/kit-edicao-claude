# Corta trechos de um vídeo PRONTO (sem refazer render). Uso: cortar_final.py <entrada> <saida> '<json [[ini,fim],...]>'
import json, subprocess, sys
src, out, cortar = sys.argv[1], sys.argv[2], sorted(json.loads(sys.argv[3]))
D = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",src],capture_output=True,text=True).stdout)
fr = lambda t: round(round(t*30)/30, 4)
keep, cur = [], 0.0
for x, y in cortar: keep.append((cur, fr(x))); cur = fr(y)
keep.append((cur, D))
fc = [f"[0:v]trim={x}:{y},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={x}:{y},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(0,y-x-0.025):.3f}:d=0.025[a{k}]" for k,(x,y) in enumerate(keep)]
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[v][a]")
subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-filter_complex",";".join(fc),"-map","[v]","-map","[a]","-c:v","libx264","-crf","17","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",out],check=True)
print(f"{D:.1f}s -> {sum(y-x for x,y in keep):.1f}s")
