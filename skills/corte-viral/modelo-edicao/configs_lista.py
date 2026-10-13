# Vídeos de lista (v2): cada item vira título escrito a giz (letra de giz + som de giz), close nas emendas.
# Uso: edite os build() do fim e rode: python3 configs_lista.py
# itens: (texto do item, frase onde o item começa[, frase onde a lista acaba]) - o último item leva a frase de fim
# Os build() abaixo sao EXEMPLOS com textos neutros: troque pelos vídeos do lote atual.
import json, re, subprocess, unicodedata
from cortes_reais import cortes
def norm(s): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())
def dur(n): return round(float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{n}/source.mp4"],capture_output=True,text=True).stdout), 2)
GAIN = {"click-alto": -4, "click-soft-alto": -4, "pop-alto": -8, "pagina-alto": -5, "error-alto": -16, "ping-alto": -3, "giz1-alto": -3}
LEAD = {"ping-alto": 0.3}
TITULO_FIM = 3.9

def build(n, t1, t2, key, itens, emo, sfx, push=None):
    ws = json.load(open(f"{n}/transcript.json")); D = dur(n)
    def at(word, occ=1, depois=0):
        k = norm(word); c = 0
        for x in ws:
            if x["start"] >= depois and norm(x["text"]).startswith(k):
                c += 1
                if c == occ: return round(x["start"], 2)
        print(f"  !! {n}: '{word}' ({occ}) nao achada"); return None
    cfg = dict(dur=D, cuts=cortes(n), t1=t1, t2=t2, key=key)
    cfg["emo"] = [[e, t, 1.3, (740 if i % 2 == 0 else 250), 1000] for i, (e, w, o) in enumerate(emo) if (t := at(w, o)) is not None]
    cfg["sfx"] = [[f, round(max(0, t - LEAD.get(f, 0)), 2), GAIN[f]] for f, w, o in sfx if (t := at(w, o)) is not None]
    toks = [norm(x["text"]) for x in ws]
    def frase(f, depois=0):
        alvo = [norm(t) for t in f.split() if norm(t)]
        for i in range(len(toks) - len(alvo) + 1):
            if ws[i]["start"] >= depois and toks[i:i + len(alvo)] == alvo: return round(ws[i]["start"], 2)
        raise SystemExit(f"  !! {n}: frase '{f}' nao achada")
    # itens: (texto, frase onde começa[, frase onde a lista acaba]); cada um fica até o próximo começar
    ini, d = [], 0
    for it in itens: d = frase(it[1], d); ini.append(max(TITULO_FIM, d - 0.12))
    fim_lista = frase(itens[-1][2], d) - 0.1 if len(itens[-1]) > 2 else D - 2
    cfg["itens"] = []
    for i, (txt, *_r) in enumerate(itens):
        a = round(ini[i], 2); b = round(ini[i + 1] - 0.05 if i + 1 < len(itens) else fim_lista, 2)
        cfg["itens"].append(dict(texto=txt, start=a, end=b))
        cfg["sfx"] += [["giz1-alto", round(a + 0.1, 2), -3], ["giz1-alto", round(a + 0.9, 2), -6]]
    if push and (t := at(*push)) is not None: cfg["push"] = [round(max(t - 4.5, 4.0), 2), round(min(4.5, D - t + 1), 2)]
    json.dump(cfg, open(f"{n}/config.json", "w"), ensure_ascii=False, indent=1)
    print(n, D, [(x["texto"][:18], x["start"], x["end"]) for x in cfg["itens"]], len(cfg["cuts"]), "emendas")

# ----------------- EXEMPLO (troque pelo vídeo do lote) -----------------
build("lista-exemplo-3-erros", "3 erros que travam sua agenda", "o segundo é o pior",
      ["erros", "agenda", "horário", "confirmação", "preço"],
      [("Não confirmar o horário", "O primeiro"), ("Deixar o preço pra depois", "O segundo"), ("Atender sem intervalo", "E o terceiro", "Então é isso")],
      [("📅", "horário", 1), ("💸", "preço", 1), ("⏳", "intervalo", 1)],
      [("click-alto", "horário", 1), ("error-alto", "preço", 1), ("ping-alto", "intervalo", 1)],
      push=("Então", 1))
