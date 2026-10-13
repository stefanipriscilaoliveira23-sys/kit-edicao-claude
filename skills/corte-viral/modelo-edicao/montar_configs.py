# Monta config.json dos cortes a partir de ancoras de palavra (tempo vem do transcript.json de cada corte).
# Uso: edite os build() do fim (um por corte do lote) e rode: python3 montar_configs.py
# Os build() abaixo sao EXEMPLOS com textos neutros: troque pelos cortes do lote atual.
# build(nome, titulo_linha1, titulo_linha2_manuscrita, palavras_chave, [(emoji, palavra, ocorrencia)], [(som, palavra, ocorrencia)],
#       label=(html, palavra, ocorrencia, duracao), label2=..., push=(palavra, ocorrencia), t1_size=...)
import json, math, re, subprocess, unicodedata

plano = json.load(open("plano-cortes.json"))
def norm(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
def dur(n): return round(float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{n}/source.mp4"],capture_output=True,text=True).stdout), 2)
def cuts(n, extra=()):
    t, out = 0, [0.0]
    for a, b in plano[n][:-1]:
        t += math.ceil((b - a) * 30) / 30; out.append(round(t, 3))
    return sorted(out + list(extra))

GAIN = {"click-alto": -4, "click-soft-alto": -4, "pop-alto": -8, "pagina-alto": -5, "error-alto": -16, "ping-alto": -3, "typing1-alto": -3}
LEAD = {"ping-alto": 0.3, "pagina-alto": 0.05}

def build(n, t1, t2, key, emo, sfx, label=None, label2=None, push=None, t1_size=None, extra_cuts=()):
    ws = json.load(open(f"{n}/transcript.json"))
    def at(word, occ=1):
        k = norm(word); c = 0
        for x in ws:
            if norm(x["text"]).startswith(k):
                c += 1
                if c == occ: return round(x["start"], 2)
        raise SystemExit(f"{n}: palavra '{word}' ({occ}) nao achada")
    D = dur(n)
    cfg = dict(dur=D, cuts=cuts(n, extra_cuts), t1=t1, t2=t2, key=key)
    if t1_size: cfg["t1_size"] = t1_size
    cfg["emo"] = [[e, at(w, o), 1.3, (740 if i % 2 == 0 else 250), 1000] for i, (e, w, o) in enumerate(emo)]
    cfg["sfx"] = [[f, round(max(0, at(w, o) - LEAD.get(f, 0)), 2), GAIN[f]] for f, w, o in sfx]
    labs = []
    for L in (label, label2):
        if L:
            html, w, o, d = L; t = at(w, o); labs.append(dict(html=html, start=max(t, 4.0), dur=d))
            cfg["sfx"].append(["pagina-alto", round(max(t, 4.0) - 0.05, 2), -5])
    cfg["labels"] = labs
    if push:
        w, o = push; t = at(w, o); cfg["push"] = [round(max(t - 4.5, 4.0), 2), round(min(4.5, D - t + 1), 2)]
    json.dump(cfg, open(f"{n}/config.json", "w"), ensure_ascii=False, indent=1)
    print(n, D, "ok")

# ----------------- EXEMPLOS (troque pelos cortes do lote) -----------------
build("corte-01-exemplo", "O erro que mais afasta cliente", "e como eu resolvi",
      ["erro", "cliente", "agenda", "preço", "resolvi"],
      [("📅", "agenda", 1), ("💸", "preço", 1), ("✅", "resolvi", 1)],
      [("click-alto", "agenda", 1), ("error-alto", "erro", 1), ("ping-alto", "resolvi", 1)],
      label=("<i>1️⃣</i> <b>primeiro ponto</b>", "primeiro", 1, 2.6), push=("resolvi", 1))
