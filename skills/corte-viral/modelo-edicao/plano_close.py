# Plano v2 dos depoimentos: vídeo "sem interlocutor".
# Mantém só a fala de quem dá o depoimento, tira respostas que dependem da pergunta ("com certeza", "sim"...),
# as falas da entrevistadora e corta pausa > 0,25 s. Gera <NOME>-v2 em plano-cortes.json / fontes.json.
# Uso: python3 plano_close.py <plano-entrada.json> <frases-tirar.json>
#   plano-entrada.json: o mesmo do plano.py (modelo: exemplo-plano.json)
#   frases-tirar.json:  {"NOME": ["frase como aparece no transcript bruto", ...]} (modelo: exemplo-frases-tirar.json)
import json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plano import carregar_entrada
P = carregar_entrada(sys.argv[1])
TIRAR = {k: [x["frase"] if isinstance(x, dict) else x for x in v] for k, v in json.load(open(sys.argv[2])).items() if not k.startswith("_")}
CORTAR = {}
TR = "../trans/"
def n(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())

plano = json.load(open("plano-cortes.json")); fontes = json.load(open("fontes.json")); meta = {}
for nome, frases in TIRAR.items():
    frases = frases + CORTAR.get(nome, [])
    src, tr, segs, _ = P[nome]
    todas = [w for sg in json.load(open(TR + tr + ".json")) for w in sg["words"]]
    usar = [w for w in todas if any(a - 1.0 <= w["start"] and w["end"] <= b + 1.0 for a, b in segs)]
    tok = [n(w["text"]) for w in usar]
    fora = set()
    for fr in frases:
        alvo = [n(t) for t in fr.split() if n(t)]
        for i in range(len(tok) - len(alvo) + 1):
            if tok[i:i+len(alvo)] == alvo and not any(k in fora for k in range(i, i+len(alvo))):
                fora.update(range(i, i + len(alvo)))
    ws = [w for k, w in enumerate(usar) if k not in fora]
    tl = []
    if ws:
        ini, prev = ws[0]["start"] - 0.10, ws[0]
        for w in ws[1:]:
            if w["start"] - prev["end"] > 0.25:
                tl.append((ini, prev["end"] + 0.12)); ini = w["start"] - 0.10
            prev = w
        tl.append((ini, prev["end"] + 0.25))
    tl = [(round(max(0, x), 3), round(y, 3)) for x, y in tl if y - x > 0.12]
    novo = nome + "-v2"
    plano[novo] = [[x, y] for x, y in tl]; fontes[novo] = fontes[nome]
    print(f"{novo}: {sum(y-x for x,y in tl):.0f}s em {len(tl)} trechos (tirei {len(fora)} palavras de resposta)")
json.dump(plano, open("plano-cortes.json", "w"), indent=1); json.dump(fontes, open("fontes.json", "w"), indent=1)
