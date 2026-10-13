# Corte preciso pelo SOM (não pela transcrição): para cada trecho mantido, acha o início e o fim reais da voz
# e tira as pausas internas deixando a fala emendada; faz CORTE EM L onde a pessoa olha pra baixo no fim da frase.
# Uso: python corte.py <pasta-saida> <bruto.mov> <keep.json>      (modelo: exemplo-keep.json)
#   keep.json: [[ini, fim], ...] trechos do bruto escolhidos lendo a fala; fica sempre a ÚLTIMA tomada boa.
#              fim NEGATIVO = usar exatamente esse tempo (sem procurar o fim da voz).
#   olha_t.json (opcional, na pasta-saida ou na pasta atual): {"<tempo do bruto do fim do pedaço>": segundos}
#              -> a imagem troca esses segundos antes (a voz termina por baixo). Guardar pelo TEMPO DO BRUTO.
# Saída: <pasta>/cortado.mov + plano-pausas.json (áudio) + plano-video.json (imagem)
import json, os, subprocess, sys, numpy as np, wave
D, SRC, KEEPF = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(D, exist_ok=True)
KEEP = [tuple(x) for x in json.load(open(KEEPF))]
VOZ = f"{D}/voz16k.wav"
if not os.path.exists(VOZ):
    subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",SRC,"-vn","-ac","1","-ar","16000","-c:a","pcm_s16le",VOZ], check=True)
x = np.frombuffer(wave.open(VOZ).readframes(10**9), dtype=np.int16).astype(np.float32) / 32768
HOP = 160; FR = 16000 / HOP
rms = np.sqrt(np.convolve(x ** 2, np.ones(320) / 320, "same"))[::HOP]; db = 20 * np.log10(rms + 1e-9)
THR = np.percentile(db, 30) + 12
voz = db > THR
it = lambda t: int(round(t * FR)); tm = lambda i: i / FR
def inicio(a):   # primeira voz a partir de a-0.25 (sem invadir o trecho anterior)
    i = it(a - 0.25)
    while i < len(voz) and not voz[i]: i += 1
    return tm(i) - 0.05
def fim(b):      # segue a voz depois de b (aceita buraco < 0,1 s), até b+0,6
    j = it(b - 0.1); lim = it(b + 0.3); ult = j
    while j < lim:
        if voz[j]: ult = j
        elif j - ult > 6: break
        j += 1
    return tm(ult) + 0.09
plano = []
for a, b in KEEP:
    s, e = inicio(a), (fim(b) if b > 0 else -b)
    # pausas internas > 0,22 s viram emenda (só se a mediana for silêncio de verdade, THR-3, senão come consoante fraca):
    # deixa 0,07 s depois da fala e 0,04 s antes da próxima
    i, cur = it(s + 0.05), s
    while i < it(e - 0.1):
        if not voz[i]:
            j = i
            while j < it(e) and not voz[j]: j += 1
            if tm(j - i) > 0.22 and np.median(db[i:j]) < THR - 3:
                plano.append([cur, tm(i) + 0.07]); cur = tm(j) - 0.04
            i = j
        else: i += 1
    plano.append([cur, e])
fr = lambda t: round(round(t * 30000 / 1001) * 1001 / 30000, 4)
plano = [[fr(a), fr(b)] for a, b in plano if b - a > 0.10]
if not plano: raise SystemExit(f"nenhuma voz encontrada nos trechos (limiar {THR:.1f} dB): confira o keep.json e o áudio do bruto")
json.dump(plano, open(f"{D}/plano-pausas.json", "w"))
# corte em L: onde a pessoa abaixa o olhar no fim da frase, a imagem troca antes (a voz termina por baixo)
arq_olha = f"{D}/olha_t.json" if os.path.exists(f"{D}/olha_t.json") else "olha_t.json"
OT = json.load(open(arq_olha)) if os.path.exists(arq_olha) else {}
OLHA = {}
for tb, dd in OT.items():
    k = min(range(len(plano) - 1), key=lambda q: abs(plano[q][1] - float(tb)))
    if abs(plano[k][1] - float(tb)) < 0.2: OLHA[k] = dd
    else: print("  !! olhar sem pedaço:", tb)
vid = [[a, b] for a, b in plano]
for k, d in OLHA.items():
    vid[k][1] = fr(vid[k][1] - d); vid[k + 1][0] = fr(vid[k + 1][0] - d)
fc = [f"[0:v]trim={va}:{vb},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(0, b - a - 0.018):.3f}:d=0.018[a{k}]" for k, ((a, b), (va, vb)) in enumerate(zip(plano, vid))]
fc.append("".join(f"[v{k}]" for k in range(len(plano))) + f"concat=n={len(plano)}:v=1:a=0[v]")
fc.append("".join(f"[a{k}]" for k in range(len(plano))) + f"concat=n={len(plano)}:v=0:a=1[a]")
json.dump(vid, open(f"{D}/plano-video.json", "w"))
open(f"{D}/fc.txt", "w").write(";".join(fc))
VENC = ["-c:v","h264_videotoolbox","-b:v","45M"] if sys.platform == "darwin" else ["-c:v","libx264","-crf","14","-preset","fast"]
subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",SRC,"-filter_complex_script",f"{D}/fc.txt","-map","[v]","-map","[a]",
    *VENC,"-pix_fmt","yuv420p","-c:a","pcm_s16le",f"{D}/cortado.mov"], check=True)
for k, (a, b) in enumerate(plano):
    for t, nome in ((a, "início"), (b, "fim")):
        w = db[max(0, it(t) - 2):it(t) + 2] if nome == "fim" else db[max(0, it(t)):it(t) + 3]
        if len(w) and w.max() > THR + 12: print(f"  !! pedaço {k} {nome} {t:.2f}s cai em voz ({w.max():.0f} dB)")
print(f"pronto: {len(plano)} pedaços, {sum(b - a for a, b in plano):.1f}s, limiar {THR:.1f} dB")
