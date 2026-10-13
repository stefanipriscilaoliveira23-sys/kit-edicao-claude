# Tira falas da entrevistadora e frases soltas que sobraram nas bordas (ou que o 2º Whisper revelou: "deixa eu ver
# o que tenho que falar", "não muda ainda", "tchau"): corta o trecho do source.mp4, reajusta transcript.json,
# as perguntas/emendas do meta-plano.json (se existir) e grava as emendas novas em cortes-extras.json.
# Uso: python3 limpar.py <frases-tirar.json>      (modelo: exemplo-frases-tirar.json)
#   {"NOME": ["frase exata como está no transcript", {"frase": "...", "ocorrencia": "ultima"}, {"frase": "Perfeito. Com certeza.", "so_primeiras": 1}]}
#   "ocorrencia": "ultima" -> corta a última vez que a frase aparece (padrão: a primeira livre)
#   "so_primeiras": N      -> corta só as N primeiras palavras da frase (ex.: tira "Perfeito." e mantém "Com certeza.")
# O source antigo fica em <nome>/_tmp/source-sujo.mp4 (o cortes_reais.py usa pra achar o deslocamento).
import json, os, re, subprocess, sys, unicodedata
def n(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
CORTAR = {k: v for k, v in json.load(open(sys.argv[1])).items() if not k.startswith("_")}   # chaves com _ = explicação
meta = json.load(open("meta-plano.json")) if os.path.exists("meta-plano.json") else {}
cortes_extras = {}
for nome, frases in CORTAR.items():
    ws = json.load(open(f"{nome}/transcript.json"))
    toks = [n(w["text"]) for w in ws]
    dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{nome}/source.mp4"],capture_output=True,text=True).stdout)
    faixas = []
    for item in frases:
        fr = item["frase"] if isinstance(item, dict) else item
        ultima = isinstance(item, dict) and item.get("ocorrencia") == "ultima"
        alvo = [n(t) for t in fr.split() if n(t)]
        so = item.get("so_primeiras", len(alvo)) if isinstance(item, dict) else len(alvo)
        ja = {k for f in faixas for k in range(f[2], f[3] + 1)}
        cand = [i for i in range(len(toks) - len(alvo) + 1) if toks[i:i+len(alvo)] == alvo and not (set(range(i, i+len(alvo))) & ja)]
        if ultima: cand = cand[-1:]
        achou = False
        for i in cand[:1]:
            j = i + so - 1
            ini = (ws[i-1]["end"] + ws[i]["start"]) / 2 if i > 0 else 0
            fim = (ws[j]["end"] + ws[j+1]["start"]) / 2 if j + 1 < len(ws) else dur
            faixas.append((round(ini, 3), round(fim, 3), i, j)); achou = True
        print(nome, "OK " if achou else "NAO ACHOU", fr)
    if not faixas: continue
    faixas.sort()
    manter, cur = [], 0.0
    for a, b, i, j in faixas:
        if a - cur > 0.1: manter.append((cur, a))
        cur = b
    if dur - cur > 0.1: manter.append((cur, dur))
    os.makedirs(f"{nome}/_tmp", exist_ok=True)
    os.replace(f"{nome}/source.mp4", f"{nome}/_tmp/source-sujo.mp4")
    fc = []
    for k, (a, b) in enumerate(manter):
        fc.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(0,b-a-0.03)}:d=0.03[a{k}]")
    fc.append("".join(f"[v{k}][a{k}]" for k in range(len(manter))) + f"concat=n={len(manter)}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",f"{nome}/_tmp/source-sujo.mp4","-filter_complex",";".join(fc),"-map","[v]","-map","[a]",
                    "-c:v","libx264","-crf","17","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{nome}/source.mp4"], check=True)
    # tempo antigo -> novo
    def novo(t):
        s = 0.0
        for a, b in manter:
            if t < a: return round(s, 3)
            if t <= b: return round(s + t - a, 3)
            s += b - a
        return round(s, 3)
    tirar = {k for a, b, i, j in faixas for k in range(i, j + 1)}
    ws2 = [dict(w, start=novo(w["start"]), end=novo(w["end"])) for k, w in enumerate(ws) if k not in tirar]
    json.dump(ws2, open(f"{nome}/transcript.json", "w"), ensure_ascii=False, indent=1)
    extras = [round(sum(b - a for a, b in manter[:k]), 3) for k in range(1, len(manter))]
    cortes_extras[nome] = extras
    if nome in meta:
        m = meta[nome]
        m["perguntas"] = [[novo(q) if q is not None else None, t] for q, t in m.get("perguntas", [])]
        m["cuts"] = sorted(set([novo(c) for c in m.get("cuts", [])] + extras))
if meta: json.dump(meta, open("meta-plano.json", "w"), ensure_ascii=False, indent=1)
ce = json.load(open("cortes-extras.json")) if os.path.exists("cortes-extras.json") else {}
ce.update(cortes_extras); json.dump(ce, open("cortes-extras.json", "w"))
