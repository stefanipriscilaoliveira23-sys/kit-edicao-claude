# Acha no source: (1) voz fora das palavras transcritas (pergunta de quem grava, "ééé"), com nível e altura;
# (2) palavras curtas esticadas (vogal arrastada = "ééé"). Uso: python3 vozes.py <pasta>
import json, subprocess, sys, numpy as np
n = sys.argv[1]; sr = 16000
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{n}/source.mp4", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
ws = json.load(open(f"{n}/transcript.json"))
rms = lambda t0, t1: 20 * np.log10(np.sqrt(np.mean(a[int(t0 * sr):int(t1 * sr)] ** 2)) + 1e-9) if t1 > t0 else -99
def f0(t):
    s = a[int(t * sr):int(t * sr) + 640]; s = s - s.mean()
    if np.sqrt(np.mean(s ** 2)) < 0.003: return 0
    c = np.correlate(s, s, "full")[len(s) - 1:]; lo, hi = int(sr / 400), int(sr / 70); k = lo + np.argmax(c[lo:hi])
    return sr / k if c[k] > 0.3 * c[0] else 0
fala = np.median([rms(w["start"], w["end"]) for w in ws]); f0s = [f0(t) for w in ws[::3] for t in [w["start"] + 0.05]]
f0ela = np.median([x for x in f0s if x]) if any(f0s) else 0
print(f"fala {fala:.0f} dB, altura dela ~{f0ela:.0f} Hz")
pares = [(dict(end=0.0, text="[início]"), ws[0])] + list(zip(ws, ws[1:])) + [(ws[-1], dict(start=len(a) / sr, text="[fim]"))]
for p, q in pares:
    g0, g1 = p["end"], q["start"]
    if g1 - g0 < 0.25: continue
    v = [t for t in np.arange(g0, g1 - 0.05, 0.05) if rms(t, t + 0.05) > fala - 26 and f0(t) > 0]
    if len(v) * 0.05 >= 0.2:
        print(f"voz fora das palavras {g0:6.2f}-{g1:6.2f} ({len(v)*0.05:.2f}s) nível {np.mean([rms(t,t+0.05) for t in v]):.0f} dB altura {np.median([f0(t) for t in v]):.0f} Hz | ...{p['text']} ‖ {q['text']}...")
for w in ws:
    if len(w["text"].strip(".,?!")) <= 3 and w["end"] - w["start"] > 0.5: print("palavra esticada:", w)
