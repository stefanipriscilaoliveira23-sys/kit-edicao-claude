# Vídeos de lista (olhando pra câmera): corte firme (pausa > 0,25 s), sem frase quebrada e
# cortando ANTES de a pessoa desviar o olhar da câmera (csv do `olhar`).
# Uso: python3 plano_lista.py <plano-entrada.json> <lista-olhar.json>
#   lista-olhar.json: {"NOME": ["caminho/do/olhar-do-bruto.csv", ["frase a tirar", ...]]}
import csv, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plano import carregar_entrada
P = carregar_entrada(sys.argv[1])
TR = "../trans/"
def n(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
L = {k: (os.path.expanduser(v[0]), v[1]) for k, v in json.load(open(sys.argv[2])).items() if not k.startswith("_")}
def fora_do_olhar(arq):
    r = list(csv.DictReader(open(arq))); fx = []
    for x in r:
        t = float(x["tempo"])
        fora = x["tem_rosto"] == "0" or abs(float(x["yaw"])) > 32 or abs(float(x["pitch"])) > 30
        if fora:
            if fx and t - fx[-1][1] < 0.35: fx[-1][1] = t
            else: fx.append([t, t])
    return [(a - 0.12, b + 0.12) for a, b in fx if b - a >= 0.6]   # ignora piscada / ruído de 1 quadro
plano = json.load(open("plano-cortes.json")); fontes = json.load(open("fontes.json"))
for nome, (olh, tirar) in L.items():
    src, tr, segs, _ = P[nome]
    todas = [w for sg in json.load(open(TR + tr + ".json")) for w in sg["words"]]
    usar = [w for w in todas if any(a - 1.0 <= w["start"] and w["end"] <= b + 1.0 for a, b in segs)]
    tok = [n(w["text"]) for w in usar]; fora = set()
    for fr in tirar:
        alvo = [n(t) for t in fr.split() if n(t)]
        for i in range(len(tok) - len(alvo) + 1):
            if tok[i:i+len(alvo)] == alvo: fora.update(range(i, i + len(alvo))); break
    olhar = fora_do_olhar(olh)
    tocou = {k for k, w in enumerate(usar) if any(a < w["end"] and w["start"] < b for a, b in olhar)}
    # frase inteira sai (do sinal de pontuação anterior até o próximo), pra não sobrar frase pela metade
    frase, ids, cur = {}, 0, []
    for k, w in enumerate(usar):
        frase[k] = ids
        if w["text"][-1:] in ".?!": ids += 1
    ruins = {frase[k] for k in tocou}
    desviou = {k for k in range(len(usar)) if frase[k] in ruins}
    ws = [w for k, w in enumerate(usar) if k not in fora and k not in desviou]
    tl = []; ini, prev = ws[0]["start"] - 0.10, ws[0]
    for w in ws[1:]:
        quebra = w["start"] - prev["end"] > 0.25 or any(prev["end"] <= a < w["start"] for a, b in olhar)
        if quebra:
            fim = prev["end"] + 0.12
            fim = min([fim] + [a for a, b in olhar if prev["end"] <= a < fim])
            tl.append((ini, fim)); ini = max(w["start"] - 0.10, max([b for a, b in olhar if a < w["start"] <= b + 0.1] or [0]))
        prev = w
    tl.append((ini, prev["end"] + 0.25))
    tl = [(round(x, 3), round(y, 3)) for x, y in tl if y - x > 0.12]
    novo = nome + "-v2"; plano[novo] = [[x, y] for x, y in tl]; fontes[novo] = fontes[nome]
    print(f"{novo}: {sum(y-x for x,y in tl):.0f}s em {len(tl)} trechos")
    for f in sorted(ruins): print("   saiu:", " ".join(usar[k]["text"] for k in range(len(usar)) if frase[k] == f))
json.dump(plano, open("plano-cortes.json", "w"), indent=1); json.dump(fontes, open("fontes.json", "w"), indent=1)
