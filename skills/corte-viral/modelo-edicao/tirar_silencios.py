# Corta do vídeo PRONTO os silêncios >= 0,5 s (pessoa ouvindo pergunta / pausa longa), deixando 0,1 s de cada lado.
# Uso: tirar_silencios.py <entrada.mp4> <saida.mp4> [min_s=0.5] [depois_de_s=4] [folga_s=0.1]
import subprocess, sys, numpy as np
src, out = sys.argv[1], sys.argv[2]
MIN = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5; DEP = float(sys.argv[4]) if len(sys.argv) > 4 else 4; FOL = float(sys.argv[5]) if len(sys.argv) > 5 else 0.1
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
w = 800; lv = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + w] ** 2)) + 1e-9) for i in range(0, len(a) - w, w)])
lim = np.percentile(lv, 60) - 22
sil, s = [], None
for k, r in enumerate(list(lv) + [0]):
    if r < lim and s is None: s = k
    if r >= lim and s is not None:
        if (k - s) * 0.05 >= MIN and s * 0.05 >= DEP: sil.append((s * 0.05 + FOL, k * 0.05 - FOL))
        s = None
D = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
fr = lambda t: round(round(t * 30) / 30, 4)
keep, cur = [], 0.0
for x, y in sil: keep.append((cur, fr(x))); cur = fr(y)
keep.append((cur, D))
fc = []
for k, (x, y) in enumerate(keep):
    fc.append(f"[0:v]trim={x}:{y},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={x}:{y},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(0, y - x - 0.025):.3f}:d=0.025[a{k}]")
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[v][a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
print(f"{src.split('/')[-1]}: {len(sil)} silêncios, {D:.1f}s -> {sum(y - x for x, y in keep):.1f}s")
import json as _j; _c, _a = [0.0], 0.0
for x, y in keep[:-1]: _a += y - x; _c.append(round(_a, 3))
_j.dump(_c, open(out + ".cortes.json", "w"))
