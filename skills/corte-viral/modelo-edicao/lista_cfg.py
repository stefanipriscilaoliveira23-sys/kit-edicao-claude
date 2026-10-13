# Passo 2 do vídeo de lista: depois de cortar os silêncios pelo áudio e transcrever de novo o source.mp4,
# monta o config (itens a giz, emojis, sons) a partir da transcrição nova. Uso: python3 lista_cfg.py <receita.json>
import json, os, re, subprocess, sys, unicodedata
R = json.load(open(sys.argv[1])); N = R["nome"]
_NUM = {"1": "um", "2": "dois", "3": "tres", "4": "quatro", "5": "cinco", "6": "seis", "100": "cem"}
_nz0 = lambda s: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
nz = lambda s: _NUM.get(_nz0(s), _nz0(s))   # "Número 1" = "Número um"
out = json.load(open(f"{N}/transcript.json"))
for k, v in R.get("trocas", {}).items():
    for w in out:
        if w["text"] == k: w["text"] = v
for i, w in enumerate(out):
    if (i == 0 or out[i - 1]["text"][-1:] in ".?!") and w["text"][:1].islower(): w["text"] = w["text"][0].upper() + w["text"][1:]
json.dump(out, open(f"{N}/transcript.json", "w"), ensure_ascii=False, indent=1)
tok = [nz(w["text"]) for w in out]
def at(fr, depois=-1.0):
    alvo = [nz(x) for x in fr.split() if nz(x)]
    for i in range(len(tok) - len(alvo) + 1):
        if out[i]["start"] > depois and tok[i:i + len(alvo)] == alvo: return out[i]["start"]
    raise SystemExit(f"nao achei: {fr}")
D = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{N}/source.mp4"], capture_output=True, text=True).stdout), 2)
ini, d = [], -1.0
for t, fr in R["itens"]: d = at(fr, d); ini.append(max(3.9, d - 0.12))
fim = at(R["fim_lista"], d) - 0.1
itens = [dict(texto=t, start=round(ini[q], 2), end=round((ini[q + 1] - 0.05) if q + 1 < len(ini) else fim, 2)) for q, (t, _) in enumerate(R["itens"])]
cuts = json.load(open(f"{N}/cortes-novos.json"))
cfg = dict(dur=D, cuts=cuts, t1=R["t1"], t2=R["t2"], whoosh=False, key=R["key"], itens=itens, zooms=[], cap_top=R.get("cap_top", 1180))
cfg["emo"] = [[e, round(at(f), 2), 1.3, (760 if q % 2 == 0 else 200), R.get("emo_y", 1400)] for q, (e, f) in enumerate(R["emo"])]
cfg["sfx"] = [[f, round(max(0, at(p) - (0.3 if f == "ping-alto" else 0)), 2), g] for f, p, g in R["sfx"]]
for q, it in enumerate(itens):
    txt = it["texto"]; passo = min(0.045, 1.4 / max(1, len(txt))); nome = f"giz-{N[-24:]}-{q}"
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "giz_letras.py"), txt, str(passo), f"assets/sfx/{nome}.wav"], check=True)
    cfg["sfx"].append([nome, round(it["start"] + 0.15, 3), -10])
json.dump(cfg, open(f"{N}/config.json", "w"), ensure_ascii=False, indent=1)
print(N, "dur", D, [(i["texto"][:16], i["start"], i["end"]) for i in itens])
