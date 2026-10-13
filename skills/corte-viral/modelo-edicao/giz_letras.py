# Som de giz que acompanha a escrita: um risquinho por letra (no instante em que a letra aparece),
# risco seguido dentro da palavra e pausa curta no espaço entre palavras.
# Uso: giz_letras.py "<texto>" <passo_s> <saida.wav>   (o som começa no instante da 1ª letra)
import os, subprocess, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marca
GIZ = marca.som("giz", "assets/sfx")   # giz.wav é do Mixkit (ver SONS-PARA-BAIXAR.md); sem ele usa a digitação
SR = 48000
txt, passo, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", GIZ, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
fonte = np.frombuffer(raw, np.float32)[int(0.03 * SR):int(0.29 * SR)]
rng = np.random.default_rng(len(txt))
P = int(passo * SR); n = len(txt) * P + int(0.12 * SR)
y = np.zeros(n + SR, np.float32)
for j, ch in enumerate(txt):
    if ch == " ": continue
    junta_prox = j + 1 < len(txt) and txt[j + 1] != " "
    m = P + int(0.02 * SR) if junta_prox else int(P * 0.75)      # dentro da palavra emenda na próxima letra; antes do espaço termina cedo
    ini = int(rng.integers(0, len(fonte) - m)) if len(fonte) > m else 0
    s = np.resize(fonte[ini:ini + m], m) * rng.uniform(0.7, 1.0)
    env = np.ones(m, np.float32)
    a_ = int(0.006 * SR); r_ = min(int((0.02 if junta_prox else 0.03) * SR), m // 2)
    env[:a_] = np.linspace(0.3, 1, a_)                                 # ataque do traço
    env[-r_:] = np.linspace(1, 0, r_)
    env *= np.linspace(1.0, 0.8, m)                                   # cada traço perde um pouco de força
    y[j * P:j * P + m] += s * env
y = y[:n]
y = y / (np.abs(y).max() + 1e-9) * 0.89
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", out], input=y.tobytes(), check=True)
