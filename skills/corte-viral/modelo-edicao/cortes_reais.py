# Emendas reais na timeline final = emendas do plano (mapeadas pelo que o limpar tirou) + emendas do limpar.
# O deslocamento de cada pedaço é achado por correlação de áudio entre source-sujo.mp4 (o limpar.py guarda em _tmp/) e source.mp4.
# Uso: python3 cortes_reais.py <nome> [<nome> ...]   (ou importado: from cortes_reais import cortes)
import json, math, os, subprocess, numpy as np
pl = json.load(open("plano-cortes.json")); ce = json.load(open("cortes-extras.json"))
SR = 8000
def audio(f):
    r = subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(r, np.float32)
def plano_cuts(n):
    t, out = 0, [0.0]
    for a, b in pl[n][:-1]:
        t += math.ceil((b - a) * 30) / 30; out.append(round(t, 3))
    return out
def cortes(n):
    base = plano_cuts(n)
    ex = ce.get(n, [])
    sujo = f"{n}/_tmp/source-sujo.mp4" if os.path.exists(f"{n}/_tmp/source-sujo.mp4") else f"{n}/source-sujo.mp4"
    if not ex or not os.path.exists(sujo): return base
    old, new = audio(sujo), audio(f"{n}/source.mp4")
    offs = [0.0]                                  # old = new + off  (por pedaço)
    for c in ex:
        i = int((c + 0.3) * SR); q = new[i:i + 2 * SR]
        lo = int((c + 0.3 + offs[-1]) * SR); hi = min(len(old) - 2 * SR - 16, lo + 20 * SR)
        best, bo = -1, 0
        for o in range(lo, hi, 8):
            w = old[o:o + 2 * SR]; v = float(np.dot(w, q)) / (np.linalg.norm(w) * np.linalg.norm(q) + 1e-9)
            if v > best: best, bo = v, o
        # refina
        for o in range(max(lo, bo - 8), bo + 9):
            w = old[o:o + 2 * SR]; v = float(np.dot(w, q)) / (np.linalg.norm(w) * np.linalg.norm(q) + 1e-9)
            if v > best: best, bo = v, o
        offs.append(bo / SR - (c + 0.3)); 
        if best < 0.1: print("  !! correlação baixa", n, c, round(best, 2))
    seg = [0.0] + ex
    out = []
    for t in base:
        for k in range(len(seg)):
            ini_old = seg[k] + offs[k]; fim_old = (seg[k + 1] + offs[k]) if k + 1 < len(seg) else 1e9
            if ini_old - 0.01 <= t < fim_old:
                out.append(round(t - offs[k], 3)); break
    allc = sorted(set(out + ex))
    res = []
    for t in allc:
        if res and t - res[-1] < 0.5: continue
        res.append(t)
    return res
if __name__ == "__main__":
    import sys
    for n in sys.argv[1:]: print(n, cortes(n))
