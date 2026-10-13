# Corta trechos (tempo do source.mp4) de um corte já montado e ajusta tudo: source.mp4, transcript.json e config.json
# (emendas, emojis, sons, push). Uso: python3 tirar_trechos.py <pasta> '<json [[ini,fim],...]>'
import json, os, subprocess, sys
D_, tir = sys.argv[1], sorted(json.loads(sys.argv[2]))
src = f"{D_}/source.mp4"
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
fr = lambda t: round(round(t * 30) / 30, 4)
# junta trechos encostados
m = []
for a, b in tir:
    if m and a <= m[-1][1] + 0.02: m[-1][1] = max(m[-1][1], b)
    else: m.append([a, b])
keep, cur = [], 0.0
for a, b in m: keep.append((cur, fr(a))); cur = fr(b)
keep.append((cur, dur))
keep = [(a, b) for a, b in keep if b - a > 0.03]
def novo(t):
    s = 0.0
    for a, b in keep:
        if t < a: return round(s, 3)
        if t <= b: return round(s + t - a, 3)
        s += b - a
    return round(s, 3)
dentro = lambda t: any(a <= t < b for a, b in m)
fc = [f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(0, b - a - 0.025):.3f}:d=0.025[a{k}]" for k, (a, b) in enumerate(keep)]
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[v][a]")
os.makedirs(f"{D_}/_tmp", exist_ok=True)
os.replace(src, f"{D_}/_tmp/source-antes-trechos.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{D_}/_tmp/source-antes-trechos.mp4", "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "17",
                "-preset", "medium", "-g", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", src], check=True)
ws = json.load(open(f"{D_}/transcript.json"))
def frac_dentro(w):
    d = max(1e-3, w["end"] - w["start"])
    return sum(max(0, min(b, w["end"]) - max(a, w["start"])) for a, b in m) / d
ws2 = [dict(w, start=novo(w["start"]), end=novo(w["end"])) for w in ws if frac_dentro(w) < 0.7]   # palavra só some se ~toda dentro do corte
for i, w in enumerate(ws2):
    if (i == 0 or ws2[i - 1]["text"][-1:] in ".?!") and w["text"][:1].islower(): w["text"] = w["text"][0].upper() + w["text"][1:]
json.dump(ws2, open(f"{D_}/transcript.json", "w"), ensure_ascii=False, indent=1)
if not os.path.exists(f"{D_}/config.json"): print(D_, f"{dur:.2f}s -> {round(sum(b - a for a, b in keep), 2)}s (sem config)"); sys.exit(0)
c = json.load(open(f"{D_}/config.json"))
D2 = round(sum(b - a for a, b in keep), 2); c["dur"] = D2
cuts = sorted({novo(t) for t in c["cuts"]} | {round(sum(b - a for a, b in keep[:k]), 3) for k in range(1, len(keep))})
c["cuts"] = [t for i, t in enumerate(cuts) if i == 0 or t - cuts[i - 1] > 0.4]
c["emo"] = [[e[0], novo(e[1])] + e[2:] for e in c.get("emo", []) if not dentro(e[1])]
c["sfx"] = [[s[0], novo(s[1]), s[2]] for s in c.get("sfx", []) if not dentro(s[1])]
if c.get("push"): c["push"] = [novo(c["push"][0]), c["push"][1]]
for it in c.get("itens", []): it["start"], it["end"] = novo(it["start"]), novo(it["end"])
c["zooms"] = [[novo(z[0]), novo(z[1])] + z[2:] for z in c.get("zooms", []) if novo(z[1]) - novo(z[0]) > 0.3]
json.dump(c, open(f"{D_}/config.json", "w"), ensure_ascii=False, indent=1)
print(D_, f"{dur:.2f}s -> {D2}s;", len(m), "trechos tirados")
