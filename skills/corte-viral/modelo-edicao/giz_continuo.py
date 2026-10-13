# Gera um som de giz contínuo do tamanho pedido, emendando o trecho de risco do giz.wav com crossfade
# (cada repetição com leve variação de velocidade pra não soar robótico). Uso: giz_continuo.py <segundos> <saida.wav>
import os, subprocess, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marca
GIZ = marca.som("giz", "assets/sfx")   # giz.wav é do Mixkit (ver SONS-PARA-BAIXAR.md); sem ele usa a digitação
SR = 48000
dur, out = float(sys.argv[1]), sys.argv[2]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", GIZ, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.float32)
seg = a[int(0.03 * SR):int(0.29 * SR)]
rng = np.random.default_rng(int(dur * 1000))
xf = int(0.06 * SR); n = int(dur * SR); y = np.zeros(n + len(seg) * 2, np.float32); pos = 0
while pos < n:
    f = rng.uniform(0.93, 1.07); m = int(len(seg) / f)
    s = np.interp(np.linspace(0, len(seg) - 1, m), np.arange(len(seg)), seg).astype(np.float32) * rng.uniform(0.85, 1.0)
    env = np.ones(m, np.float32); env[:xf] = np.linspace(0, 1, xf); env[-xf:] = np.linspace(1, 0, xf)
    y[pos:pos + m] += s * env; pos += m - xf
y = y[:n]
fi, fo = int(0.02 * SR), int(0.12 * SR)
y[:fi] *= np.linspace(0, 1, fi); y[-fo:] *= np.linspace(1, 0, fo)
y = y / (np.abs(y).max() + 1e-9) * 0.89
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", out], input=y.tobytes(), check=True)
