# config.json de um lote de depoimentos e de vídeos falados: emojis/sons/destaques apontados por palavra,
# perguntas da entrevista em pílula ("💬 pergunta"). Os nomes são os do plano + "-v2".
# Uso: edite os build() do fim e rode: python3 configs_v2.py   (o cfg_dep.py reaproveita as definições deste arquivo)
# Os build() abaixo sao EXEMPLOS com textos neutros: troque pelos vídeos do lote atual.
import json, re, subprocess, unicodedata
import math
_pl = json.load(open("plano-cortes.json"))
def _cuts(n):
    t, out = 0, [0.0]
    for a, b in _pl[n][:-1]:
        t += math.ceil((b - a) * 30) / 30; out.append(round(t, 3))
    return out
def norm(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
def dur(n): return round(float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{n}/source.mp4"],capture_output=True,text=True).stdout), 2)
GAIN = {"click-alto": -4, "click-soft-alto": -4, "pop-alto": -8, "pagina-alto": -5, "error-alto": -16, "ping-alto": -3}
LEAD = {"ping-alto": 0.3}

def build(n0, t1, t2, key, emo, sfx, push, t1_size=None):
    n = n0 + "-v2"
    ws = json.load(open(f"{n}/transcript.json")); D = dur(n)
    m = {"cuts": _cuts(n), "perguntas": []}
    def at(word, occ=1):
        k = norm(word); c = 0
        for x in ws:
            if norm(x["text"]).startswith(k):
                c += 1
                if c == occ: return round(x["start"], 2)
        print(f"  !! {n}: '{word}' ({occ}) nao achada"); return None
    cfg = dict(dur=D, cuts=m["cuts"], t1=t1, t2=t2, key=key)
    if t1_size: cfg["t1_size"] = t1_size
    cfg["emo"] = [[e, t, 1.3, (740 if i % 2 == 0 else 250), 1000] for i, (e, w, o) in enumerate(emo) if (t := at(w, o)) is not None]
    cfg["sfx"] = [[f, round(max(0, t - LEAD.get(f, 0)), 2), GAIN[f]] for f, w, o in sfx if (t := at(w, o)) is not None]
    labs, fim = [], 3.9
    for q, txt in m["perguntas"]:
        if q is None: continue
        s = round(max(q, fim), 2)
        if s > D - 3: continue
        labs.append(dict(html=f"<i>💬</i> {txt}", start=s, dur=2.8)); fim = s + 3.0
        cfg["sfx"].append(["pagina-alto", round(s - 0.05, 2), -5])
    cfg["labels"] = labs
    t = at(*push)
    if t is not None: cfg["push"] = [round(max(t - 4.5, 4.0), 2), round(min(4.5, D - t + 1), 2)]
    json.dump(cfg, open(f"{n}/config.json", "w"), ensure_ascii=False, indent=1)
    print(n, D, len(cfg["emo"]), "emojis", len(labs), "perguntas")

# ----------------- EXEMPLOS (troque pelos vídeos do lote) -----------------
build("DEP-exemplo-cliente-1", "Ela tinha medo de cobrar mais", "olha o que mudou em 3 meses",
      ["medo", "cobrar", "agenda", "resultado", "clientes"],
      [("😰", "medo", 1), ("💰", "cobrar", 1), ("📈", "resultado", 1)],
      [("error-alto", "medo", 1), ("pop-alto", "cobrar", 1), ("ping-alto", "resultado", 1)],
      push=("resultado", 1))
