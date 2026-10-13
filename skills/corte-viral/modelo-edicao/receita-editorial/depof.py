# tira os "pofs" de ar (consoantes P/B/G/K colado no microfone): corte firme <130 Hz + abaixa 130-400 Hz só no instante do pof
import numpy as np, wave, sys
from scipy.signal import butter, sosfiltfilt
src, dst = sys.argv[1], sys.argv[2]
w = wave.open(src); sr = w.getframerate(); nch = w.getnchannels()
x = np.frombuffer(w.readframes(10**9), dtype=np.int16).astype(np.float32) / 32768
if nch > 1: x = x.reshape(-1, nch).mean(1)
detect = sosfiltfilt(butter(4, [20, 90], 'bp', fs=sr, output='sos'), x)
hop = int(0.005 * sr)
L = 20 * np.log10(np.array([np.sqrt(np.mean(detect[i:i + hop] ** 2)) for i in range(0, len(x), hop)]) + 1e-7)
base = np.median(L)
pof = (L > base + 28).astype(float)
# alarga cada pof (20 ms antes, 60 ms depois) e suaviza
k = np.convolve(pof, np.ones(16), 'same') > 0
g = np.where(k, 0.18, 1.0)   # -15 dB na faixa 130-400 durante o pof
g = np.convolve(g, np.hanning(9) / np.hanning(9).sum(), 'same')
gain = np.repeat(g, hop)[:len(x)]
hp = sosfiltfilt(butter(8, 130, 'hp', fs=sr, output='sos'), x)
mid = sosfiltfilt(butter(4, [130, 400], 'bp', fs=sr, output='sos'), hp)
y = hp - mid + mid * gain
y = y / max(1e-6, np.abs(y).max()) * 0.89
out = wave.open(dst, 'wb'); out.setnchannels(1); out.setsampwidth(2); out.setframerate(sr); out.writeframes((y * 32767).astype(np.int16).tobytes()); out.close()
print("pofs tratados:", int(np.sum(np.diff(pof) > 0)))
