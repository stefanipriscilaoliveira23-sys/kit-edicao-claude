#!/usr/bin/env python3
"""
Acha a batida da musica: BPM e o ponto exato pra comecar a musica em cima de uma batida.

  python3 -I batidas.py musica.mp3 --inicio 12 [--dur 25] [--bpm 128] [--json batidas.json]

  --inicio  segundo em que a pessoa quer que a musica comece
  --bpm     se a pessoa souber o BPM (ou se o calculado sair o dobro/metade), forca esse valor
  Mostra: BPM, "musica_inicio" ajustado (primeira batida forte a partir do --inicio),
  picos fortes, graves (bumbo) e o volume a cada meio segundo (pra achar pausa e "drop").

Gerar uma batida de teste (quando nao tem musica ou pra ouvir o ritmo):
  python3 -I batidas.py --gerar-batida batida.mp3 --bpm 128 --dur 25 [--atraso 0.3]
"""
import argparse, json, os, shutil, subprocess, sys
import numpy as np


def achar_ff(nome):
    exe = nome + (".exe" if os.name == "nt" else "")
    for c in [os.path.expanduser(f"~/.local/bin/{exe}"), shutil.which(nome),
              f"/opt/homebrew/bin/{nome}", f"/usr/local/bin/{nome}"]:
        if c and os.path.isfile(c):
            return c
    sys.exit(f"Nao achei o {nome}. Veja o INSTALAR.md da skill sanfoninha.")


FF = achar_ff("ffmpeg")
SR, HOP, WIN = 22050, 256, 1024


def gerar_batida(caminho, bpm, dur, atraso):
    sr = 44100; y = np.zeros(int(sr * dur)); b = 60 / bpm; rng = np.random.default_rng(1)
    k = 0
    while atraso + k * b < dur:
        s = int((atraso + k * b) * sr); L = int(0.25 * sr); tt = np.arange(L) / sr
        forte = 1.0 if k % 4 == 0 else 0.8
        kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * 0.9 * forte
        y[s:s + L] += kick[:len(y[s:s + L])]
        if k % 2 == 1:                                         # caixa nos tempos 2 e 4
            L2 = int(0.12 * sr); sn = rng.standard_normal(L2) * np.exp(-np.arange(L2) / sr * 35) * 0.35
            y[s:s + L2] += sn[:len(y[s:s + L2])]
        for h in (0, 0.5):                                     # chimbal em colcheias
            s2 = int((atraso + (k + h) * b) * sr); L3 = int(0.04 * sr)
            hat = rng.standard_normal(L3) * np.exp(-np.arange(L3) / sr * 120) * 0.12
            y[s2:s2 + L3] += hat[:len(y[s2:s2 + L3])]
        k += 1
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run([FF, "-v", "error", "-y", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                    "-b:a", "192k", caminho], input=pcm, check=True)
    print(f"batida de teste: {caminho}  {bpm:g} BPM, {dur:g}s, primeira batida em {atraso:.2f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("musica", nargs="?")
    ap.add_argument("--inicio", type=float, default=0.0)
    ap.add_argument("--dur", type=float, default=25.0)
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--json")
    ap.add_argument("--gerar-batida"); ap.add_argument("--atraso", type=float, default=0.0)
    a = ap.parse_args()

    if a.gerar_batida:
        gerar_batida(a.gerar_batida, a.bpm or 128, a.dur, a.atraso); return
    if not a.musica: sys.exit("faltou o arquivo da musica")

    raw = subprocess.run([FF, "-v", "error", "-ss", str(a.inicio), "-t", str(a.dur), "-i", a.musica,
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) < SR * 3: sys.exit("musica curta demais (ou nao consegui ler) a partir desse inicio")
    frames = np.lib.stride_tricks.sliding_window_view(x, WIN)[::HOP] * np.hanning(WIN)
    S = np.abs(np.fft.rfft(frames, axis=1)); logS = np.log1p(10 * S)
    flux = np.r_[0, np.maximum(0, np.diff(logS, axis=0)).sum(1)]
    lo = np.fft.rfftfreq(WIN, 1 / SR) < 150
    lflux = np.r_[0, np.maximum(0, np.diff(logS[:, lo], axis=0)).sum(1)]
    t = (np.arange(len(flux)) * HOP + WIN / 2) / SR          # tempo do centro da janela
    rms = np.sqrt((frames ** 2).mean(1))
    env = flux / (flux.max() + 1e-9) + 0.7 * lflux / (lflux.max() + 1e-9)

    # BPM: autocorrelacao do envelope (faixa 75 a 170 BPM)
    f = env - env.mean(); ac = np.correlate(f, f, "full")[len(f) - 1:]
    lags = np.arange(len(ac)) * HOP / SR
    sel = (lags >= 60 / 170) & (lags <= 60 / 75)

    def nota_grade(b, fase):
        g = np.arange(fase, t[-1], b)
        return np.interp(g, t, env).mean()

    if a.bpm:
        bpm = a.bpm
    else:
        b0 = lags[sel][np.argmax(ac[sel])]
        cand = []
        for b in np.linspace(b0 * 0.97, b0 * 1.03, 61):        # refina o periodo
            fases = np.arange(0, b, 0.005)
            cand.append((max(nota_grade(b, ph) for ph in fases), b))
        bpm = round(60 / max(cand)[1], 1)
    b = 60 / bpm
    fases = np.arange(0, b, 0.002)
    notas = [nota_grade(b, ph) for ph in fases]
    fase = float(fases[int(np.argmax(notas))])
    mus_ini = round(a.inicio + fase, 3)

    def picos(e, k=1.5, mind=0.12):
        m = np.convolve(e, np.ones(15) / 15, "same"); out = []; p70 = np.percentile(e, 70)
        for i in range(1, len(e) - 1):
            if e[i] > e[i - 1] and e[i] >= e[i + 1] and e[i] > m[i] * k and e[i] > p70:
                if not out or t[i] - out[-1][0] > mind: out.append((t[i], e[i]))
                elif e[i] > out[-1][1]: out[-1] = (t[i], e[i])
        return [round(p[0], 2) for p in out]

    fortes = picos(flux); graves = picos(lflux, 1.8)
    print(f"BPM: {bpm:g}  (uma batida a cada {b:.3f}s)")
    print(f"musica_inicio ajustado: {mus_ini:.3f}s  (pediu {a.inicio:g}s; a 1a batida forte fica no 0,00 do video)")
    print("picos fortes (s, contando do inicio pedido):", " ".join("%.2f" % v for v in fortes[:40]))
    print("graves/bumbo (s):", " ".join("%.2f" % v for v in graves[:40]))
    print("volume (dB) a cada 0,5 s:")
    vol = []
    for k in np.arange(0, t[-1], 0.5):
        s = (t >= k) & (t < k + 0.5); v = 20 * np.log10(rms[s].mean() + 1e-9); vol.append(round(float(v), 1))
        print("%.1f:%.0f" % (k, v), end="  ")
    print()
    # pausa seguida de volta forte ("drop"): maior salto de volume de 0,5 s pro seguinte
    if len(vol) > 3:
        saltos = np.diff(vol); k = int(np.argmax(saltos))
        if saltos[k] > 6: print(f"possivel 'drop' (volta forte da musica) perto de {0.5 * (k + 1):.1f}s do inicio pedido")
    if a.json:
        json.dump(dict(musica=os.path.abspath(a.musica), bpm=bpm, batida_s=round(b, 4),
                       inicio_pedido=a.inicio, musica_inicio=mus_ini, picos=fortes, graves=graves,
                       volume_meio_segundo=vol), open(a.json, "w", encoding="utf-8"), indent=1)
        print("salvo:", a.json)


if __name__ == "__main__":
    main()
