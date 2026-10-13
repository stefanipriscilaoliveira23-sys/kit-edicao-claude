# Plano de um lote: para cada vídeo, os trechos escolhidos (tempo do bruto) viram trechos sem respiro (silencedetect -36 dB),
# com o mapa bruto -> final (perguntas em pílula e emendas). C = conteúdo (sem respiros). Q = pergunta em pílula.
# Uso: python3 plano.py <plano-entrada.json>   (modelo: exemplo-plano.json)
#   {"NOME": {"bruto": "caminho/do/video.MOV", "transcricao": "nome-do-json-em-../trans/",
#             "trechos": [[ini, fim], ...], "perguntas": [[tempo_cru, "texto da pergunta"], ...]}}
# Gera plano-cortes.json, fontes.json e meta-plano.json na pasta atual.
import json, math, os, re, subprocess, sys
TR = "../trans/"
def carregar_entrada(arq):
    E = json.load(open(arq))
    return {n: (os.path.expanduser(v["bruto"]), v["transcricao"], [tuple(x) for x in v["trechos"]], [tuple(x) for x in v.get("perguntas", [])]) for n, v in E.items() if not n.startswith("_")}
P = carregar_entrada(sys.argv[1]) if __name__ == "__main__" else {}

def bordas(tr, a, b):
    """ajusta a/b para o inicio da 1a palavra e o fim da ultima dentro da janela (segmentos do Whisper)"""
    ws = [w for s in json.load(open(TR + tr + ".json")) for w in s["words"] if w["start"] >= a - 1.0 and w["end"] <= b + 1.0]
    if not ws: return a, b
    return max(0, ws[0]["start"] - 0.2), ws[-1]["end"] + 0.3

def silencios(f, a, b):
    out = subprocess.run(["ffmpeg","-hide_banner","-ss",str(a),"-to",str(b),"-i",f,"-af","silencedetect=noise=-36dB:d=0.40","-f","null","-"],capture_output=True,text=True).stderr
    return list(zip([a+float(x) for x in re.findall(r"silence_start: ([0-9.]+)",out)], [a+float(x) for x in re.findall(r"silence_end: ([0-9.]+)",out)]))

if __name__ == "__main__":
    plano, fontes, meta = {}, {}, {}
    for nome, (src, tr, segs, perg) in P.items():
        wav = TR + tr + ".wav"; tl = []
        for a0, b0 in segs:
            a, b = bordas(tr, a0, b0); cur = a
            for s, e in silencios(wav, a, b):
                if s <= a + 0.05: cur = max(cur, e - 0.12); continue
                if e >= b - 0.05: b = min(b, s + 0.15); break
                tl.append((cur, s + 0.10)); cur = e - 0.10
            tl.append((cur, b))
        tl = [(round(x,3), round(y,3)) for x, y in tl if y - x > 0.15]
        t = 0; mapa = []
        for x, y in tl: mapa.append((x, y, round(t,3))); t += math.ceil((y-x)*30)/30
        def final(raw):
            for x, y, f in mapa:
                if x - 1.2 <= raw <= y: return round(f + max(0, raw - x), 2)
            return None
        plano[nome] = [[x, y] for x, y in tl]; fontes[nome] = src
        meta[nome] = dict(perguntas=[[final(q), txt] for q, txt in perg], cuts=[m[2] for m in mapa], total=round(t,2))
        print(f"{nome}: {t:.0f}s, {len(tl)} trechos, perguntas {[p[0] for p in meta[nome]['perguntas']]}")
    json.dump(plano, open("plano-cortes.json","w"), indent=1); json.dump(fontes, open("fontes.json","w"), indent=1)
    json.dump(meta, open("meta-plano.json","w"), ensure_ascii=False, indent=1)
