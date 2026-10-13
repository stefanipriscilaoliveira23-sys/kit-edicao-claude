# Vídeo de lista com slide na TV, no jeito da marca (ver JEITO-DA-MARCA.md):
# gancho inteiro, quadro aberto mostrando a TV, toda fala da tomada boa, corte só nas pausas,
# close de vez em quando (recortado direto do 4K, 1 por item, quando a pessoa fala de frente e a TV não muda),
# item escrito a giz com som que acompanha as letras.
# Uso: python3 lista_tv.py <arquivo-de-receita.json>   (modelo: exemplo-receita-lista.json)
import csv, json, os, re, subprocess, sys, unicodedata
R = json.load(open(sys.argv[1]))
N, RAW = R["nome"], os.path.expanduser(R["bruto"])
os.makedirs(f"{N}/_tmp", exist_ok=True)
if not os.path.lexists(f"{N}/assets"): os.symlink("../assets", f"{N}/assets")
_NUM = {"1": "um", "2": "dois", "3": "tres", "4": "quatro", "5": "cinco", "6": "seis", "100": "cem"}
_nz0 = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
nz = lambda s: _NUM.get(_nz0(s), _nz0(s))   # "Número 1" = "Número um"
ws = [w for s in json.load(open(R["transcricao"])) for w in s["words"]]
tok = [nz(w["text"]) for w in ws]
def acha(frase, depois=-1.0, ultimo=False):
    alvo = [nz(x) for x in frase.split() if nz(x)]
    hits = [i for i in range(len(tok) - len(alvo) + 1) if ws[i]["start"] > depois and tok[i:i + len(alvo)] == alvo]
    if not hits: raise SystemExit(f"nao achei: {frase}")
    return (hits[-1] if ultimo else hits[0]), len(alvo)

# 1) palavras que ficam: blocos [frase inicial, frase final] da tomada boa, menos as frases "tirar"
fica = set()
for b in R["blocos"]:
    i, _ = acha(b[0], b[2] if len(b) > 2 else -1.0)
    j, nj = acha(b[1], ws[i]["start"] - 0.01)
    fica.update(range(i, j + nj))
for fr in R.get("tirar", []):
    t0 = fr[1] if isinstance(fr, list) else -1.0; fr = fr[0] if isinstance(fr, list) else fr
    i, n = acha(fr, t0); fica.difference_update(range(i, i + n))
ids = sorted(fica)

# 2) trechos: quebra na pausa > 0,25 s ou quando pula palavra
rosto = [r for r in csv.DictReader(open(R["rosto"])) if r["tem_rosto"] == "1"]
segs, ini, prev = [], ids[0], ids[0]
for k in ids[1:]:
    if k != prev + 1 or ws[k]["start"] - ws[prev]["end"] > 0.25:
        segs.append([ini, prev]); ini = k
    prev = k
segs.append([ini, prev])

# 3) itens (frase onde começa cada item) e escolha dos closes
itens_ini = []
d = -1.0
for txt, fr in R["itens"]:
    i, _ = acha(fr, d); itens_ini.append(i); d = ws[i]["start"]
fim_lista_i, _ = acha(R["fim_lista"], d)
limites = itens_ini + [fim_lista_i]
def de_frente(a, b):
    p = [r for r in rosto if a <= float(r["tempo"]) <= b]
    return p and sum(abs(float(r["yaw"])) < 22 for r in p) / len(p) > 0.85
closes = []   # (palavra_ini, palavra_fim, caixa)
for n_it in range(len(itens_ini)):
    a_i, b_i = limites[n_it], limites[n_it + 1]
    cand = [k for k in ids if a_i <= k < b_i and ws[k]["start"] >= ws[a_i]["start"] + 2.5 and ws[k]["end"] <= ws[b_i]["start"] - 1.0]
    melhor = None
    for s in cand:   # janela de ~2,6 a 3,6 s, de frente pra câmera, mais perto do meio do item
        e = s
        while e + 1 in fica and e + 1 < b_i and ws[e + 1]["end"] - ws[s]["start"] <= 3.6: e += 1
        dur = ws[e]["end"] - ws[s]["start"]
        if dur < 2.6 or not de_frente(ws[s]["start"], ws[e]["end"]): continue
        if s > 0 and ws[s - 1]["text"][-1:] not in ".,?!" and s - 1 in fica: continue   # começa em início de frase/vírgula
        meio = (ws[a_i]["start"] + ws[b_i]["start"]) / 2
        nota = abs((ws[s]["start"] + ws[e]["end"]) / 2 - meio)
        if melhor is None or nota < melhor[0]: melhor = (nota, s, e)
    if melhor:
        _, s, e = melhor
        p = [r for r in rosto if ws[s]["start"] <= float(r["tempo"]) <= ws[e]["end"]]
        cx = sum(float(r["cx"]) for r in p) / len(p); cy = sum(float(r["cy"]) for r in p) / len(p)
        h = R.get("close_altura", 0.42); w = h            # fração do quadro (9:16 -> 9:16)
        x = min(max(0, cx - w / 2), 1 - w); y = min(max(0, cy - 0.30 * h), 1 - h)
        closes.append((s, e, (round(x, 4), round(y, 4), w, h)))
# parte os trechos nas bordas dos closes
cortes_close = {}
novos = []
for a, b in segs:
    pts = sorted({a} | {s for s, e, c in closes if a < s <= b} | {e + 1 for s, e, c in closes if a <= e < b})
    for q, st in enumerate(pts):
        en = (pts[q + 1] - 1) if q + 1 < len(pts) else b
        caixa = next((c for s, e, c in closes if s <= st and en <= e), None)
        novos.append([st, en, caixa])
segs = novos

# 4) tempos crus de cada trecho (folga -0,08/+0,10; no fim de bloco +0,25) sem invadir o vizinho
tl = []
for q, (a, b, caixa) in enumerate(segs):
    t0 = ws[a]["start"] - 0.08; t1 = ws[b]["end"] + (0.10 if q + 1 < len(segs) else 0.30)
    if q + 1 < len(segs) and segs[q + 1][0] == b + 1: t1 = (ws[b]["end"] + ws[b + 1]["start"]) / 2   # emenda contínua (close)
    if q > 0 and segs[q - 1][1] == a - 1: t0 = (ws[a - 1]["end"] + ws[a]["start"]) / 2
    tl.append((round(max(0, t0), 3), round(t1, 3), caixa))
def novo(t):
    s = 0.0
    for a, b, _ in tl:
        if t < a: return round(s, 3)
        if t <= b: return round(s + t - a, 3)
        s += b - a
    return round(s, 3)

# 5) vídeo: quadro aberto 1080x1920; closes recortados do 4K
if not os.path.exists(f"{N}/source.mp4"):
    args, fc = [], []
    for k, (a, b, c) in enumerate(tl):
        args += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", RAW]
        crop = f"crop=iw*{c[2]}:ih*{c[3]}:iw*{c[0]}:ih*{c[1]}," if c else ""
        fc.append(f"[{k}:v:0]{crop}scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p[v{k}];[{k}:a:0]aresample=48000,asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(0, b - a - 0.025):.3f}:d=0.025[a{k}]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(len(tl))) + f"concat=n={len(tl)}:v=1:a=1[vc][ac];[vc]eq=brightness=0.02:contrast=1.04:saturation=1.05:gamma=1.04,format=yuv420p[v];[ac]highpass=f=70,afftdn=nr=12:nf=-40:tn=1,loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[a]")
    open(f"{N}/_tmp/filtro.txt", "w").write(";".join(fc))
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args, "-filter_complex_script", f"{N}/_tmp/filtro.txt", "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-g", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{N}/source.mp4"], check=True)
D = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{N}/source.mp4"], capture_output=True, text=True).stdout), 2)

# 6) legenda com as grafias certas
TROCA = R.get("trocas", {})
out = []
for k in ids:
    w = ws[k]; t = TROCA.get(w["text"], w["text"])
    out.append(dict(text=t, start=novo(w["start"]), end=novo(w["end"])))
for i, w in enumerate(out):     # começo de frase com maiúscula
    if (i == 0 or out[i - 1]["text"][-1:] in ".?!") and w["text"][:1].islower(): w["text"] = w["text"][0].upper() + w["text"][1:]
json.dump(out, open(f"{N}/transcript.json", "w"), ensure_ascii=False, indent=1)

# 7) config
cuts, acc = [0.0], 0.0
for a, b, _ in tl[:-1]: acc += b - a; cuts.append(round(acc, 3))
ini_it = [max(3.9, novo(ws[i]["start"]) - 0.12) for i in itens_ini]
fim = novo(ws[fim_lista_i]["start"]) - 0.1
itens = [dict(texto=t, start=round(ini_it[q], 2), end=round((ini_it[q + 1] - 0.05) if q + 1 < len(ini_it) else fim, 2)) for q, (t, _) in enumerate(R["itens"])]
tok_out = [nz(w["text"]) for w in out]
def at(fr):   # 1ª ocorrência só entre as falas que ficaram
    alvo = [nz(x) for x in fr.split() if nz(x)]
    for i in range(len(tok_out) - len(alvo) + 1):
        if tok_out[i:i + len(alvo)] == alvo: return out[i]["start"]
    raise SystemExit("nao achei na fala final: " + fr)
cfg = dict(dur=D, cuts=cuts, t1=R["t1"], t2=R["t2"], whoosh=False, key=R["key"], itens=itens, zooms=[], cap_top=R.get("cap_top", 1180))
cfg["emo"] = [[e, round(at(f), 2), 1.3, (760 if q % 2 == 0 else 200), R.get("emo_y", 1400)] for q, (e, f) in enumerate(R["emo"])]
cfg["sfx"] = [[f, round(max(0, at(p) - (0.3 if f == "ping-alto" else 0)), 2), g] for f, p, g in R["sfx"]]
for q, it in enumerate(itens):
    txt = it["texto"]; passo = min(0.045, 1.4 / max(1, len(txt))); nome = f"giz-{N[-24:]}-{q}"
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "giz_letras.py"), txt, str(passo), f"assets/sfx/{nome}.wav"], check=True)
    cfg["sfx"].append([nome, round(it["start"] + 0.15, 3), -10])
json.dump(cfg, open(f"{N}/config.json", "w"), ensure_ascii=False, indent=1)
print(N, "dur", D, "trechos", len(tl), "closes", [(round(novo(ws[s]["start"]), 1), round(novo(ws[e]["end"]), 1)) for s, e, c in closes])
print("itens", [(i["texto"][:16], i["start"], i["end"]) for i in itens])
