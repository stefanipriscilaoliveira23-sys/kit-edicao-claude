# Modelo de edicao dos cortes (composicao HyperFrames: titulo, legenda palavra por palavra, emojis, rotulos, itens a giz)
# Uso: python3 gerar_clip.py <pasta-do-corte>   -> gera <pasta>/index.html
# A pasta precisa de: source.mp4, transcript.json, config.json
# Cores, fontes, posicao e estilo da legenda e emojis sim/nao vem do Manual da Marca (~/minha-marca/marca.json, via marca.py).
import json, html, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marca
M = marca.carregar()
DEST = marca.cor("destaque"); CLARO = marca.cor("claro"); CAPCOR = M["legenda"].get("cor") or "#FFFFFF"
ESC = lambda a: marca.rgba("escuro", a)

D = sys.argv[1]
cfg = json.load(open(os.path.join(D, "config.json")))
words = json.load(open(os.path.join(D, "transcript.json")))
DUR = cfg["dur"]
CUTS = cfg["cuts"]          # inicio de cada trecho na timeline final (emendas)

# junta "100" + "%" numa palavra so
w = []
for x in words:
    if w and (x["text"] == "%" or re.match(r"^[\$\.,]\d", x["text"]) or (x["text"] == "R" )):
        if x["text"] == "R": w.append(dict(x)); continue
        w[-1]["text"] += x["text"]; w[-1]["end"] = x["end"]; continue
    if x["start"] > DUR - 0.3: continue
    if x["text"] == "%" and w:
        w[-1]["text"] += "%"; w[-1]["end"] = x["end"]
    else:
        w.append(dict(x))

def norm(t): return re.sub(r"[^\wÀ-ÿ%]", "", t.lower())
KEY = {norm(k) for k in cfg.get("key", [])}
FALA = cfg.get("fala", [])
def na_fala(t): return any(a <= t < b for a, b in FALA)

# ---- legenda: ate N palavras (manual da marca, padrao 3), quebra em pontuacao, pausa > 0.35s ou troca fala/explicacao ----
NPAL = int(M["legenda"].get("palavras_por_vez") or 3)
groups, cur = [], []
for x in w:
    if cur and (len(cur) == NPAL or x["start"] - cur[-1]["end"] > 0.35 or na_fala(x["start"]) != na_fala(cur[0]["start"])):
        groups.append(cur); cur = []
    cur.append(x)
    if x["text"][-1] in ".,?!":
        groups.append(cur); cur = []
if cur: groups.append(cur)

cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    t_in = g[0]["start"]
    t_out = groups[gi + 1][0]["start"] if gi + 1 < len(groups) else DUR
    t_out = max(min(t_out, g[-1]["end"] + 0.6), t_in + 0.5)
    if gi + 1 < len(groups): t_out = min(t_out, groups[gi + 1][0]["start"])
    used_key, spans = False, []
    for wi, x in enumerate(g):
        txt = x["text"].rstrip(".,")
        is_key = norm(x["text"]) in KEY and not used_key
        used_key = used_key or is_key
        wid = f"g{gi}w{wi}"
        spans.append(f'<span id="{wid}" class="{"w key" if is_key else "w"}">{html.escape(txt)}</span>')
        cap_js.append(f'tl.set("#{wid}",{{display:"none"}},0);tl.set("#{wid}",{{display:"inline-block"}},{x["start"]:.3f});')
        if is_key:
            cap_js.append(f'tl.fromTo("#{wid}",{{opacity:0,y:18,scale:0.8}},{{opacity:1,y:0,scale:1,duration:0.24,ease:"back.out(2.6)"}},{x["start"]:.3f});')
        else:
            cap_js.append(f'tl.fromTo("#{wid}",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.12,ease:"power2.out"}},{x["start"]:.3f});')
    cap_html.append(f'<div id="g{gi}" class="cap{" fala" if na_fala(t_in) else ""}">{" ".join(spans)}</div>')
    cap_js.append(f'tl.set("#g{gi}",{{opacity:1}},{t_in:.3f});tl.set("#g{gi}",{{opacity:0}},{t_out:.3f});')

# ---- aproximacoes: alterna enquadramento em cada emenda ----
ZIN = [1.14, 1.12, 1.18, 1.10, 1.16, 1.20]
zoom_js, k = [], 0
# "zooms": lista [inicio, fim, escala, origem_x%, origem_y%] -> close só nesses trechos (vídeo de TV: quadro aberto no resto)
for a_, b_, z_, ox, oy in cfg.get("zooms", []):
    zoom_js.append(f'tl.set("#cam",{{scale:{z_},transformOrigin:"{ox}% {oy}%"}},{a_:.3f});tl.set("#cam",{{scale:1}},{b_:.3f});')
for i, t in enumerate(CUTS if "zooms" not in cfg else []):
    if i % 2 == 0: z = 1.0
    else: z = ZIN[k % len(ZIN)]; k += 1
    zoom_js.append(f'tl.set("#cam",{{scale:{z}}},{t:.3f});')
if cfg.get("push"):
    a, d = cfg["push"]
    zoom_js.append(f'tl.fromTo("#cam",{{scale:1.0}},{{scale:1.07,duration:{d},ease:"none"}},{a});')

# ---- titulo: serifada condensada + manuscrita em maquina de escrever ----
T2 = cfg["t2"]; TA = cfg.get("title_at", 0.0); TYPE0, STEP = TA + 0.55, 0.05
t2_spans = "".join(f'<span class="ch" id="c{i}">{"&nbsp;" if c == " " else html.escape(c)}</span>' for i, c in enumerate(T2))
typ_end = TYPE0 + len(T2) * STEP
title_out = max(TA + 3.65, typ_end + 1.4)
typ_js = "".join(f'tl.set("#c{i}",{{opacity:1}},{TYPE0 + i * STEP:.3f});' for i in range(len(T2)))

# ---- selo e rotulos ----
extra_html, extra_js = [], []
for i, (a, b) in enumerate(cfg.get("bastidores", [])):
    extra_html.append(f'<section id="bast{i}" class="clip" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="7"><div class="vinheta"></div><div class="label"><div id="bast{i}p" class="pill bast"><i>🎬</i> erros de gravação</div></div></section>')
    extra_js.append(f'tl.set("#cam",{{filter:"grayscale(1) contrast(1.15) brightness(0.95)"}},{a});tl.set("#cam",{{filter:"none"}},{b});')
    extra_js.append(f'tl.fromTo("#bast{i}p",{{opacity:0,scale:0.8,rotation:-4}},{{opacity:1,scale:1,rotation:-2,duration:0.25,ease:"back.out(2)"}},{a});')
b = cfg.get("badge")
if b:
    extra_html.append(f'<section id="badge" class="clip label" data-start="{b["start"]}" data-duration="{b["end"] - b["start"]:.2f}" data-track-index="3"><div id="badgep" class="pill"><i>{b["emoji"]}</i> {html.escape(b["text"])}</div></section>')
    extra_js.append(f'tl.fromTo("#badgep",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{b["start"]});tl.to("#badgep",{{opacity:0,duration:0.2}},{b["end"] - 0.25:.2f});')
for i, l in enumerate(cfg.get("labels", [])):
    extra_html.append(f'<section id="lab{i}" class="clip label" data-start="{l["start"]}" data-duration="{l["dur"]}" data-track-index="5"><div id="lab{i}p" class="pill">{l["html"]}</div></section>')
    extra_js.append(f'tl.fromTo("#lab{i}p",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{l["start"]});tl.to("#lab{i}p",{{opacity:0,duration:0.2}},{l["start"] + l["dur"] - 0.25:.2f});')

# ---- itens de lista: escritos a giz no alto, letra por letra, ficam enquanto ela fala do item ----
for i, it in enumerate(cfg.get("itens", [])):
    txt, a, b = it["texto"], it["start"], it["end"]
    # palavra inteira num bloco que não quebra; quebra de linha só entre palavras
    spans, j = [], 0
    for pal in txt.split(" "):
        spans.append('<span class="pal">' + "".join(f'<span class="ch" id="it{i}c{j + q}">{html.escape(c)}</span>' for q, c in enumerate(pal)) + '</span>')
        j += len(pal) + 1
    spans = " ".join(spans)
    letras = [k for k, c in enumerate(txt) if c != " "]
    extra_html.append(f'<section id="it{i}" class="clip" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="8">'
                      f'<div class="lousa"></div><div class="item"><span class="num">{i + 1}.</span> {spans}</div></section>')
    passo = min(0.045, 1.4 / max(1, len(txt)))
    extra_js.append("".join(f'tl.set("#it{i}c{j}",{{opacity:1}},{a + 0.15 + j * passo:.3f});' for j in letras))
    extra_js.append(f'tl.fromTo("#it{i} .num",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.25,ease:"back.out(2)"}},{a});')

# ---- emojis ----
emo_html, emo_js = [], []
for i, (e, t, d, x, y) in enumerate(cfg.get("emo", []) if M.get("emojis", True) else []):
    emo_html.append(f'<div id="emo{i}" class="emo" style="left:{x}px;top:{y}px">{e}</div>')
    emo_js.append(f'tl.fromTo("#emo{i}",{{opacity:0,scale:0.3,rotation:-18}},{{opacity:1,scale:1,rotation:0,duration:0.35,ease:"back.out(2.2)"}},{t});')
    emo_js.append(f'tl.to("#emo{i}",{{y:-40,opacity:0,duration:0.3,ease:"power2.in"}},{t + d});')

# ---- fontes da marca copiadas pra dentro do projeto ----
FT = marca.copiar_fontes(os.path.join(D, "assets", "fonts"))
FACES = "\n".join([marca.font_face("Titulo", "assets/fonts/" + FT["titulo"]), marca.font_face("Manuscrita", "assets/fonts/" + FT["manuscrita"]),
                   marca.font_face("Legenda", "assets/fonts/" + FT["legenda"], 700), marca.font_face("Legenda", "assets/fonts/" + FT["legenda_media"], 500),
                   marca.font_face("Giz", "assets/fonts/" + FT["giz"])])
_estilo = str(M["legenda"].get("destaque", "caixa")).lower()
KEYCSS = {"caixa": f"background: {DEST}; color: #FFFFFF; padding: 0 16px 4px; border-radius: 12px; text-shadow: none;",
          "sublinhado": f"background-image: linear-gradient({DEST},{DEST}); background-repeat: no-repeat; background-position: 50% 96%; background-size: 100% 0.1em;",
          "italico": f"font-family: \"Titulo\", serif; font-style: italic; font-weight: 400; font-size: 1.2em;",
          "cor": f"color: {DEST};"}.get(_estilo, f"background: {DEST}; color: #FFFFFF; padding: 0 16px 4px; border-radius: 12px; text-shadow: none;")
if _estilo == "italico": FACES += "\n" + marca.font_face("Titulo", "assets/fonts/" + FT["titulo_italico"]).replace(" }", " font-style: italic; }")

page = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>{html.escape(os.path.basename(D.rstrip("/")))}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{FACES}
@font-face {{ font-family: "Emoji"; src: local("Apple Color Emoji"), local("Segoe UI Emoji"), local("Noto Color Emoji"); }}
body {{ margin: 0; background: #000; }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
#cam {{ position: absolute; inset: 0; transform-origin: 57% 36%; }}
#aroll {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
#scrim {{ position: absolute; left: 0; right: 0; top: 0; height: 680px;
  background: linear-gradient(180deg, {ESC(0.70)} 0%, {ESC(0.35)} 55%, {ESC(0)} 100%); }}
#title {{ position: absolute; left: 60px; right: 60px; top: 170px; display: flex; flex-direction: column; align-items: center; text-align: center; }}
#t1 {{ font-family: "Titulo", serif; font-size: {cfg.get("t1_size", 128)}px; line-height: 0.92; letter-spacing: -1px; color: #FFFFFF; text-shadow: 0 2px 16px {ESC(0.35)}; }}
#t2 {{ font-family: "Manuscrita", cursive; font-size: 62px; color: {CLARO}; margin-top: 20px; min-height: 80px; }}
.ch {{ opacity: 0; }}
#t2u {{ display: block; height: 6px; width: 80%; margin: 4px auto 0; background: {DEST}; border-radius: 3px; transform-origin: left center; }}
.label {{ position: absolute; left: 0; right: 0; top: 250px; display: flex; justify-content: center; }}
.pill {{ font-family: "Legenda", system-ui, sans-serif; font-weight: 500; font-size: 46px; color: #FFFFFF;
  background: {DEST}; padding: 16px 34px; border-radius: 999px; box-shadow: 0 6px 18px {ESC(0.35)}; }}
.pill b {{ font-family: "Manuscrita", cursive; font-weight: 400; font-size: 52px; }}
.pill i {{ font-family: "Emoji"; font-style: normal; }}
#badge .pill {{ background: #FFFFFF; color: {DEST}; font-size: 40px; padding: 12px 28px; }}
.cap {{ position: absolute; left: 80px; right: 80px; top: {cfg.get("cap_top", marca.legenda_topo())}px; display: flex; flex-wrap: nowrap; justify-content: center; gap: 0 18px;
  font-family: "Legenda", system-ui, sans-serif; font-weight: 700; font-size: {M["legenda"].get("tamanho_px", 74)}px; font-variant-ligatures: none; line-height: 1.18; color: {CAPCOR};
  text-shadow: 0 3px 14px {ESC(0.75)}, 0 1px 3px {ESC(0.9)}; opacity: 0; }}
.cap.fala {{ color: {CLARO}; }}
.w {{ display: inline-block; }}
.w.key {{ {KEYCSS} }}
.vinheta {{ position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%); }}
.pill.bast {{ background: #FFFFFF; color: {marca.cor("texto")}; font-size: 42px; letter-spacing: 1px; }}
.lousa {{ position: absolute; left: 0; right: 0; top: 0; height: 560px; background: linear-gradient(180deg, {ESC(0.72)} 0%, {ESC(0.38)} 60%, {ESC(0)} 100%); }}
.item {{ position: absolute; left: 70px; right: 70px; top: 190px; text-align: center; font-family: "Giz", cursive; font-size: 64px; line-height: 1.22; color: #FFFFFF;
  text-shadow: 0 2px 10px {ESC(0.5)}; }}
.item .num {{ display: inline-block; color: {CLARO}; }}
.pal {{ display: inline-block; white-space: nowrap; }}
.emo {{ position: absolute; font-family: "Emoji"; font-size: 120px; line-height: 1; opacity: 0; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR}">
  <div id="cam">
    <video id="aroll" src="source.mp4" data-start="0" data-duration="{DUR}" data-track-index="0" muted playsinline></video>
  </div>
  <audio id="voz" src="source.mp4" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  <section id="titlecard" class="clip" data-start="{TA}" data-duration="{title_out - TA + 0.35:.2f}" data-track-index="2">
    <div id="scrim"></div>
    <div id="title">
      <div id="t1">{html.escape(cfg["t1"])}</div>
      <div id="t2">{t2_spans}<span id="t2u"></span></div>
    </div>
  </section>
  {"".join(extra_html)}
  <section id="caps" class="clip" data-start="0" data-duration="{DUR}" data-track-index="4">
    {"".join(cap_html)}
  </section>
  <section id="emos" class="clip" data-start="0" data-duration="{DUR}" data-track-index="6">
    {"".join(emo_html)}
  </section>
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(zoom_js)}
tl.fromTo("#scrim", {{opacity:0}}, {{opacity:1, duration:0.25}}, {TA});
tl.fromTo("#t1", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.45, ease:"power3.out"}}, {TA});
{typ_js}
tl.fromTo("#t2u", {{scaleX:0}}, {{scaleX:1, duration:0.5, ease:"power2.inOut"}}, {typ_end:.2f});
tl.to("#title", {{opacity:0, y:-20, duration:0.3, ease:"power2.in"}}, {title_out:.2f});
tl.to("#scrim", {{opacity:0, duration:0.3}}, {title_out:.2f});
{chr(10).join(extra_js)}
{chr(10).join(emo_js)}
{chr(10).join(cap_js)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
open(os.path.join(D, "index.html"), "w").write(page)
json.dump({"typ_end": typ_end, "title_out": title_out, "type0": TYPE0}, open(os.path.join(D, "titulo.json"), "w"))
print(D, len(groups), "grupos; titulo ate", round(title_out, 2), "s")
