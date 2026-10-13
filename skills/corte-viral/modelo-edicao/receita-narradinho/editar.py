# -*- coding: utf-8 -*-
"""Narradinho, passo da EDIÇÃO COMPLETA (portão 2): legenda pequena, títulos grandes, clarão de luz e escurecer.

Uso: python3 editar.py <projeto> [edicao.json]
Lê montagem/linha.json + montagem/video.mp4 + narracao/transcript.json + edicao.json e monta o projeto HyperFrames em
<projeto>/hf/ (index.html + base.mp4 + fontes). O render e a música ficam no render.sh / mixar.py.

edicao.json (modelo em exemplo-edicao.json). Todo tempo pode ser "de": segundos OU "palavra": "texto" (entra na palavra).
  "legenda":   {"top": 1180, "tamanho": 50, "palavras": 3, "minusculas": true}   (2 a 3 palavras, branca, sem fundo)
  "titulos":   [{"pequeno": "vem comigo fazer um", "grande": "Efeito Fox", "de": 0, "ate": 3.0, "top": 800}]
               pequeno = letra pequena aparecendo palavra por palavra junto com a fala; grande = letra elegante inclinada
  "destaques": [{"texto": "Simétrico & harmônico", "palavra": "simétrico", "ate": 14.2, "estilo": "elegante" | "forte"}]
  "listas":    [{"itens": [{"texto": "técnica *natural*", "palavra": "natural"}, {"texto": "combinar com o cabelo", "palavra": "cabelo"}],
                 "ate": 14.0}]      (*palavra* = itálico elegante; lista no alto, item por item conforme a fala)
  "flashes":   "auto" (saída da abertura + entrada do resultado) ou lista de segundos. Clarão SÓ nesses 2 lugares.
  "escurecer": "auto" (entre as cenas do resultado) ou [{"em": 17.0, "dur": 0.5}]
  "fim_escuro": 0.8             (escurece até o preto no fim)
  "trocas_texto": {"leste": "Lash"}   (conserto de grafia só na legenda)
Durante título/destaque a legenda some (o texto grande entra NO LUGAR da legenda, como na referência).
"""
import html, json, os, re, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import identidade as I


def norm(t):
    return re.sub(r"[^\wÀ-ÿ]", "", t.lower())


def achar(ws, palavra, depois=0.0):
    alvo = [norm(x) for x in palavra.split()]
    for i in range(len(ws)):
        if ws[i]["start"] < depois - 0.01: continue
        if [norm(w["text"]) for w in ws[i:i + len(alvo)]] == alvo:
            return i
    return None


def tempo(el, ws, chave="de", padrao=0.0, depois=0.0):
    if "palavra" in el and chave == "de":
        i = achar(ws, el["palavra"], depois)
        if i is None: sys.exit(f"ERRO: palavra '{el['palavra']}' não achada na narração")
        return max(0.0, ws[i]["start"] - 0.03)
    return float(el.get(chave, padrao))


def italico(txt):
    """*palavra* -> span itálico elegante"""
    partes = re.split(r"(\*[^*]+\*)", txt)
    return "".join(f'<span class="it">{html.escape(p[1:-1])}</span>' if p.startswith("*") else html.escape(p) for p in partes)


def main(proj, cfg_arq=None):
    cfg_arq = cfg_arq or os.path.join(proj, "edicao.json")
    C = json.load(open(cfg_arq)) if os.path.exists(cfg_arq) else {}
    L = json.load(open(os.path.join(proj, "montagem", "linha.json")))
    ws = json.load(open(os.path.join(proj, "narracao", "transcript.json")))
    DUR, FIM_VOZ, P = L["dur"], L["fim_voz"], L["pecas"]
    H = os.path.join(proj, "hf"); os.makedirs(os.path.join(H, "fonts"), exist_ok=True)
    base = os.path.join(H, "base.mp4")
    if os.path.exists(base): os.remove(base)
    try:
        os.link(os.path.join(proj, "montagem", "video.mp4"), base)
    except OSError:
        shutil.copy2(os.path.join(proj, "montagem", "video.mp4"), base)
    F = {}
    for papel in ("legenda", "legenda_media", "titulo_italico"):
        src = I.FONTES[papel]; dst = os.path.join(H, "fonts", os.path.basename(src))
        if not os.path.exists(dst): shutil.copy2(src, dst)
        F[papel] = "fonts/" + os.path.basename(src)
    CL, DE, ES = I.CORES["claro"], I.CORES["destaque"], I.CORES["escuro"]
    h = ES.lstrip("#"); esc_rgb = f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"

    js, corpo, sem_legenda = [], [], []
    # ---- títulos (abertura): pequeno palavra por palavra + grande elegante ----
    for k, t in enumerate(C.get("titulos", [])):
        de = tempo(t, ws); ate = float(t.get("ate", de + 3.0)); top = int(t.get("top", 800))
        sem_legenda.append((de, ate))
        peq = t.get("pequeno", "").split()
        spans, ult = [], de
        j0 = achar(ws, peq[0], de - 0.2) if peq else None
        for q, p in enumerate(peq):
            tq = de + 0.12 * q
            if j0 is not None and j0 + q < len(ws) and norm(ws[j0 + q]["text"]) == norm(p) and ws[j0 + q]["start"] < ate:
                tq = max(de, ws[j0 + q]["start"])
            spans.append(f'<span class="pw" id="t{k}p{q}">{html.escape(p)}</span>')
            js.append(f'tl.fromTo("#t{k}p{q}",{{opacity:0,y:10}},{{opacity:1,y:0,duration:0.14,ease:"power2.out"}},{tq:.3f});')
            ult = tq
        g = t.get("grande", "")
        jg = achar(ws, g.split()[0], ult) if g else None
        tg = t.get("grande_em", ws[jg]["start"] if jg is not None and ws[jg]["start"] < ate else ult + 0.25)
        corpo.append(f'<div class="titulo" id="t{k}" style="top:{top}px"><div class="peq">{" ".join(spans)}</div>'
                     f'<div class="grande" id="t{k}g"><span class="gtxt">{italico(g)}</span>'
                     + (f'<span class="sub" id="t{k}s"></span>' if I.SUBLINHADO_NO_TITULO else "") + '</div></div>')
        js.append(f'tl.set("#t{k}",{{opacity:1}},{de:.3f});')
        js.append(f'tl.fromTo("#t{k}g",{{opacity:0,y:24,scale:0.97}},{{opacity:1,y:0,scale:1,duration:0.6,ease:"power3.out"}},{float(tg):.3f});')
        if I.SUBLINHADO_NO_TITULO:
            js.append(f'tl.fromTo("#t{k}s",{{scaleX:0}},{{scaleX:1,duration:0.5,ease:"power2.inOut"}},{float(tg) + 0.35:.3f});')
        js.append(f'tl.to("#t{k}",{{opacity:0,duration:0.25,ease:"power2.in"}},{ate - 0.25:.3f});')

    # ---- destaques: texto grande no lugar da legenda ----
    for k, d in enumerate(C.get("destaques", [])):
        de = tempo(d, ws); ate = float(d.get("ate", de + 2.0))
        sem_legenda.append((de, ate))
        est = d.get("estilo", "elegante"); top = int(d.get("top", 860))
        corpo.append(f'<div class="dest {est}" id="d{k}" style="top:{top}px">{italico(d["texto"])}</div>')
        js.append(f'tl.fromTo("#d{k}",{{opacity:0,y:18,scale:0.96}},{{opacity:1,y:0,scale:1,duration:0.45,ease:"power3.out"}},{de:.3f});')
        js.append(f'tl.to("#d{k}",{{opacity:0,duration:0.25}},{ate - 0.25:.3f});')

    # ---- listas no alto: item por item conforme a fala ----
    for k, li in enumerate(C.get("listas", [])):
        itens, t0s = li["itens"], []
        dep = float(li.get("de", 0.0))
        for q, it in enumerate(itens):
            tq = tempo(it, ws, depois=dep); t0s.append(tq); dep = tq
        ate = float(li.get("ate", t0s[-1] + 2.5))
        corpo.append(f'<div class="lista" id="l{k}" style="top:{int(li.get("top", 210))}px">'
                     + "".join(f'<div class="item" id="l{k}i{q}"><span class="marc"></span>{italico(it["texto"])}</div>' for q, it in enumerate(itens))
                     + "</div>")
        js.append(f'tl.set("#l{k}",{{opacity:1}},{t0s[0]:.3f});')
        for q, tq in enumerate(t0s):
            js.append(f'tl.fromTo("#l{k}i{q}",{{opacity:0,x:-24}},{{opacity:1,x:0,duration:0.35,ease:"power2.out"}},{tq:.3f});')
        js.append(f'tl.to("#l{k}",{{opacity:0,duration:0.3}},{ate - 0.3:.3f});')

    # ---- legenda: 2 a 3 palavras, pequena, branca, sem fundo ----
    LG = {"top": 1180, "tamanho": 50, "palavras": 3, "minusculas": True}; LG.update(C.get("legenda", {}))
    TROC = {norm(k): v for k, v in C.get("trocas_texto", {}).items()}
    def oculta(t): return any(a - 0.05 <= t < b for a, b in sem_legenda)
    grupos, cur = [], []
    for w in ws:
        if w["start"] >= FIM_VOZ or oculta(w["start"]):
            if cur: grupos.append(cur); cur = []
            continue
        txt = TROC.get(norm(w["text"]), w["text"])
        if cur and (len(cur) >= LG["palavras"] or w["start"] - cur[-1]["end"] > 0.3 or sum(len(x["t"]) + 1 for x in cur) + len(txt) > 20):
            grupos.append(cur); cur = []
        cur.append({"t": txt, "start": w["start"], "end": w["end"]})
        if w["text"][-1:] in ".,?!:;":
            grupos.append(cur); cur = []
    if cur: grupos.append(cur)
    leg = []
    for gi, g in enumerate(grupos):
        a = g[0]["start"]
        b = grupos[gi + 1][0]["start"] if gi + 1 < len(grupos) else FIM_VOZ
        b = min(b, g[-1]["end"] + 0.5)
        for x, y in sem_legenda:
            if a < x < b: b = x
        texto = " ".join(re.sub(r"[.,!?;:]+$", "", x["t"]) for x in g)
        if LG["minusculas"]: texto = texto.lower()
        leg.append(f'<div class="cap" id="c{gi}">{html.escape(texto)}</div>')
        js.append(f'tl.fromTo("#c{gi}",{{opacity:0,y:8}},{{opacity:1,y:0,duration:0.1,ease:"power2.out"}},{a:.3f});tl.set("#c{gi}",{{opacity:0}},{b:.3f});')

    # ---- clarão de luz: saída da abertura e entrada do resultado ----
    fl = C.get("flashes", "auto")
    if fl == "auto":
        fl = []
        if len(P) > 1 and not P[1]["resultado"]: fl.append(P[1]["t0"])
        res = [p for p in P if p["resultado"]]
        if res: fl.append(res[0]["t0"])
    luzes = []
    for k, c in enumerate(fl):
        luzes.append(f'<div class="flash" id="f{k}"><div class="vaz" id="f{k}v"></div></div>')
        js.append(f'tl.fromTo("#f{k}",{{opacity:0}},{{opacity:1,duration:0.16,ease:"power2.in"}},{max(0, c - 0.16):.3f});')
        js.append(f'tl.fromTo("#f{k}v",{{xPercent:-35,rotation:-8}},{{xPercent:35,rotation:6,duration:0.75,ease:"none"}},{max(0, c - 0.3):.3f});')
        js.append(f'tl.to("#f{k}",{{opacity:0,duration:0.45,ease:"power2.out"}},{c + 0.04:.3f});')

    # ---- escurecer: entre as cenas do resultado e no fim ----
    esc = C.get("escurecer", "auto")
    if esc == "auto":
        res = [p for p in P if p["resultado"]]
        esc = [{"em": p["t0"], "dur": 0.5} for p in res[1:]]
    for e in esc:
        m, d = float(e["em"]), float(e.get("dur", 0.5))
        js.append(f'tl.to("#preto",{{opacity:1,duration:{d / 2:.3f},ease:"power1.in"}},{m - d / 2:.3f});tl.to("#preto",{{opacity:0,duration:{d / 2:.3f},ease:"power1.out"}},{m:.3f});')
    fe = float(C.get("fim_escuro", 0.8))
    if fe > 0:
        js.append(f'tl.to("#preto",{{opacity:1,duration:{fe:.3f},ease:"power1.in"}},{DUR - fe - 0.04:.3f});')

    css = f"""
@font-face {{ font-family:"LEG"; src:url("{F['legenda']}"); }}
@font-face {{ font-family:"LEGM"; src:url("{F['legenda_media']}"); }}
@font-face {{ font-family:"ELE"; src:url("{F['titulo_italico']}"); }}
body {{ margin:0; background:#000; }}
#root {{ position:relative; width:1080px; height:1920px; overflow:hidden; }}
#base {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.cap {{ position:absolute; left:120px; right:120px; top:{int(LG['top'])}px; text-align:center; opacity:0;
  font-family:"LEG"; font-size:{int(LG['tamanho'])}px; line-height:1.1; letter-spacing:-0.5px; color:{CL};
  text-shadow:0 1px 3px rgba({esc_rgb},.85), 0 2px 16px rgba({esc_rgb},.7), 0 0 30px rgba({esc_rgb},.35); }}
.titulo {{ position:absolute; left:120px; right:120px; text-align:center; opacity:0; color:{CL};
  text-shadow:0 3px 18px rgba({esc_rgb},.45), 0 1px 3px rgba({esc_rgb},.5); }}
.peq {{ font-family:"LEG"; font-size:50px; letter-spacing:-0.5px; text-transform:lowercase; margin-bottom:6px; }}
.pw {{ display:inline-block; opacity:0; margin:0 6px; }}
.grande {{ font-family:"ELE"; font-size:150px; line-height:0.95; opacity:0; display:inline-block; position:relative; }}
.sub {{ position:absolute; left:6%; right:6%; bottom:-6px; height:7px; border-radius:4px; background:{DE}; transform-origin:left center; transform:scaleX(0); }}
.it {{ font-family:"ELE"; font-size:1.18em; letter-spacing:0; }}
.dest {{ position:absolute; left:120px; right:120px; text-align:center; opacity:0; color:{CL};
  text-shadow:0 3px 18px rgba({esc_rgb},.45), 0 1px 3px rgba({esc_rgb},.5); }}
.dest.elegante {{ font-family:"ELE"; font-size:120px; line-height:1.0; }}
.dest.forte {{ font-family:"LEG"; font-size:84px; line-height:1.05; letter-spacing:-1px; }}
.lista {{ position:absolute; left:120px; right:120px; opacity:0; color:{CL}; font-family:"LEGM"; font-size:50px; line-height:1.25;
  text-shadow:0 1px 3px rgba({esc_rgb},.85), 0 2px 16px rgba({esc_rgb},.65); }}
.lista .item {{ opacity:0; display:flex; align-items:baseline; gap:18px; margin-bottom:8px; }}
.lista .marc {{ flex:0 0 34px; height:6px; border-radius:3px; background:{DE}; transform:translateY(-12px); box-shadow:0 0 0 1px rgba(255,255,255,.25); }}
.flash {{ position:absolute; inset:0; opacity:0; overflow:hidden;
  background:radial-gradient(ellipse at 50% 45%, rgba(255,252,244,.95) 0%, rgba(255,236,205,.85) 45%, rgba(255,214,160,.55) 100%); }}
.vaz {{ position:absolute; left:-20%; top:-10%; width:140%; height:120%;
  background:radial-gradient(ellipse at 50% 50%, rgba(255,255,255,1) 0%, rgba(255,226,170,.9) 30%, rgba(255,190,110,0) 70%); }}
#preto {{ position:absolute; inset:0; background:#000; opacity:0; }}
"""
    page = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<title>{html.escape(os.path.basename(os.path.abspath(proj)))}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR:.3f}">
  <video id="base" src="base.mp4" data-start="0" data-duration="{DUR:.3f}" data-track-index="0" muted playsinline></video>
  <section id="textos" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="2">
    {"".join(corpo)}
  </section>
  <section id="legendas" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="3">
    {"".join(leg)}
  </section>
  <section id="luz" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="4">
    {"".join(luzes)}
  </section>
  <section id="camada-preto" class="clip" data-start="0" data-duration="{DUR:.3f}" data-track-index="5">
    <div id="preto"></div>
  </section>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script></body></html>
"""
    open(os.path.join(H, "index.html"), "w").write(page)
    meta = {"dur": DUR, "fim_voz": FIM_VOZ, "flashes": fl, "sem_legenda": sem_legenda, "grupos_legenda": len(grupos)}
    json.dump(meta, open(os.path.join(H, "meta.json"), "w"), indent=1)
    print(f"hf/index.html pronto: {DUR:.1f} s, {len(grupos)} legendas, {len(C.get('titulos', []))} título(s), "
          f"{len(C.get('destaques', []))} destaque(s), {len(C.get('listas', []))} lista(s), clarão em {', '.join(f'{x:.1f}' for x in fl)} s")


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
