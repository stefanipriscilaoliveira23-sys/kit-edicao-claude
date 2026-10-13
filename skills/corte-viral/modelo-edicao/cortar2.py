# Plano de cortes a partir das runs da corte-viral: cada corte aponta pro seu proprio bruto/run e tira os respiros
# (silencedetect -36 dB, >= 0,40 s). Gera/atualiza plano-cortes.json e fontes.json na pasta atual.
# Uso: python3 cortar2.py [cortes-tempos.json] [cortes.json]
#   cortes-tempos.json: {"nome-do-corte": [[ini, fim], ...]}            (tempo do bruto, em segundos)
#   cortes.json:        {"nome-do-corte": ["<pasta-da-run>", "<caminho do bruto>"]}
import json, subprocess, re, os, sys
T = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "cortes-tempos.json"))
C = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "cortes.json"))
R = "../runs/"
def silencios(wav, a, b):
    out = subprocess.run(["ffmpeg","-hide_banner","-ss",str(a),"-to",str(b),"-i",wav,"-af","silencedetect=noise=-36dB:d=0.40","-f","null","-"],capture_output=True,text=True).stderr
    st=[a+float(x) for x in re.findall(r"silence_start: ([0-9.]+)",out)]; en=[a+float(x) for x in re.findall(r"silence_end: ([0-9.]+)",out)]
    return list(zip(st,en))
plano = json.load(open("plano-cortes.json")) if os.path.exists("plano-cortes.json") else {}
fontes = json.load(open("fontes.json")) if os.path.exists("fontes.json") else {}
for nome, segs in T.items():
    run = C[nome][0]; wav = R + run + "/assets/audio-analysis.wav"
    src = os.path.expanduser(C[nome][1])
    res = []
    for a, b in segs:
        a = max(a, 0); cur = a
        for s, e in silencios(wav, a, b):
            if s <= a + 0.05: cur = max(cur, e - 0.12); continue
            if e >= b - 0.05: b = min(b, s + 0.15); break
            res.append((cur, s + 0.10)); cur = e - 0.10
        res.append((cur, b))
    tl = [(round(x,3), round(y,3)) for x, y in res if y - x > 0.15]
    plano[nome] = tl; fontes[nome] = src
    print(nome, f"{sum(b-a for a,b in segs):.1f}s -> {sum(b-a for a,b in tl):.1f}s ({len(tl)} trechos)")
json.dump(plano, open("plano-cortes.json","w"), indent=1); json.dump(fontes, open("fontes.json","w"), indent=1)
