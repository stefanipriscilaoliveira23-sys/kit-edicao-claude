# Edição estilo Meg (receita Editorial do CATALOGO-TECNICAS, 1ª versão) com a identidade da marca (cor de destaque do manual).
# A versão aprovada depois das correções é a etapa_b2.py; esta fica pra quem quiser os cartões (numcard, post, quote) e o takeover.
# Uso: python etapa_b_meg.py <nome> [configs.json]   (modelo do config: exemplo-config-meg.json; entra <nome>/cortado.mp4 do etapa_a.py)
#   -> <nome>/source.mp4 (enquadramentos pelo rosto, M1), <nome>/atras/index.html (camada de trás),
#      <nome>/frente/index.html (legenda T9 + cartões), <nome>/meta.json (janelas da máscara + sons)
import csv, html, json, os, re, statistics as st, subprocess, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.expanduser("~/.claude/skills/corte-viral/modelo-edicao"))   # se a receita foi copiada pra outra pasta
import marca
nome = sys.argv[1]; D = nome; C = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "configs.json"))[nome]
VINHO = marca.cor("destaque"); TINTA = marca.cor("texto")   # VINHO = cor de destaque da marca (nome mantido no código)
OLHAR = marca.cmd_olhar()
# ---------- fontes e cores da marca (manual da marca, via marca.py) ----------
_FT = marca.copiar_fontes("assets")
def _css(arq):
    s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), arq)).read()
    for chave, papel in (("FONTE_LEGENDA_MEDIA", "legenda_media"), ("FONTE_LEGENDA", "legenda"), ("FONTE_ITALICO", "titulo_italico"), ("FONTE_MANUSCRITA", "manuscrita")):
        s = s.replace(chave, "assets/" + _FT[papel])
    return s.replace("VINHO", VINHO).replace("TINTA", TINTA).replace("CLARO", marca.cor("claro"))

dur = lambda f: float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout)
def n(s): return re.sub(r"[^a-z0-9$/\-]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())

# ---------- transcrição + trocas ----------
w = [dict(x) for x in json.load(open(f"{D}/t2/transcript.json"))]
while w and w[-1]["end"] - w[-1]["start"] < 0.1: w.pop()   # alucinação no fim
while w and w[-1]["text"].lower().strip(".") in ("e", "aí", "então"): w.pop()
for de, para in C.get("fix", []):
    a = de.split(); b = para.split(); i = 0
    while i <= len(w) - len(a):
        if [x["text"].lower() for x in w[i:i + len(a)]] == [t.lower() for t in a]:
            s0, e0 = w[i]["start"], w[i + len(a) - 1]["end"]; step = (e0 - s0) / len(b)
            w[i:i + len(a)] = [{"text": t, "start": round(s0 + k * step, 3), "end": round(s0 + (k + 1) * step, 3)} for k, t in enumerate(b)]
            i += len(b)
        else: i += 1
# junta "follow" + "-up" se o fix não pegou
j = []
for x in w:
    if j and x["text"].startswith("-"): j[-1]["text"] += x["text"]; j[-1]["end"] = x["end"]; continue
    j.append(x)
w = j
json.dump(w, open(f"{D}/transcript.json", "w"), ensure_ascii=False, indent=1)
T = [n(x["text"]) for x in w]
def acha(fr, depois=0.0, fim=False):
    alvo = [n(t) for t in fr.split() if n(t)]
    for L in range(len(alvo), 0, -1):
        for i in range(len(T) - L + 1):
            if T[i:i + L] == alvo[:L] and w[i]["start"] >= depois - 0.01:
                if L < len(alvo): print(f"  aviso: âncora parcial '{fr}'")
                return w[i + L - 1]["end"] + 0.3 if fim else w[i]["start"]
    print(f"  !! âncora não achada '{fr}'"); return None

# ---------- janelas dos elementos ----------
els = C["els"]; DUR0 = dur(f"{D}/cortado.mp4")
for e in els:
    e["_a"] = acha(e["start"])
    e["_b"] = acha(e["end"], depois=e["_a"] or 0, fim=True) if isinstance(e.get("end"), str) else (e["_a"] or 0) + e.get("end", 4)
    if e.get("hold"): e["_b"] = max(e["_b"], e["_a"] + e["hold"])
for k, e in enumerate(els):
    prox = [x["_a"] for x in els[k + 1:] if x["_a"] is not None]
    if prox and e["_b"] > prox[0] - 0.05 and e["t"] not in ("anot",): e["_b"] = prox[0] - 0.05
    e["_b"] = min(e["_b"], DUR0)
ATRAS = {"takeover", "parede", "marcador", "fluxo", "cta"}
janelas = [(e["_a"] - 0.1, e["_b"] + 0.35) for e in els if (e["t"] in ATRAS or (e["t"] == "anot" and not e.get("front"))) and e["_a"] is not None]
semcap = [(e["_a"] - 0.05, e["_b"]) for e in els if e["t"] in ("takeover", "post", "cta") and e["_a"] is not None]

# ---------- enquadramento pelo rosto (M1: corte seco com zoom alternado) ----------
SRC = f"{D}/cortado.mp4"
if not os.path.exists(f"{D}/rosto.csv"): subprocess.run(OLHAR + [SRC, f"{D}/rosto.csv", "3"], capture_output=True)
R = [r for r in csv.DictReader(open(f"{D}/rosto.csv")) if r["tem_rosto"] == "1"]
cuts = [0.0]; acc = 0
for a, b in json.load(open(f"{D}/plano-pausas.json"))[:-1]: acc += b - a; cuts.append(acc)
# fronteiras = emendas que caem em fim de frase (pontuação) + início/fim das janelas de trás
fim_frase = [x["end"] for x in w if x["text"][-1:] in ".?!,"]
marcas = sorted(set([0.0] + [c for c in cuts if any(abs(c - f) < 0.6 for f in fim_frase)] + [a for a, b in janelas] + [b for a, b in janelas]))
marcas = [m for m in marcas if 0 <= m < DUR0 - 0.5]
seg = []
for k, a in enumerate(marcas):
    b = marcas[k + 1] if k + 1 < len(marcas) else DUR0
    if seg and b - a < 1.3: seg[-1][1] = b; continue
    seg.append([a, b])
TIPO = {"A": (1.00, 0.30), "M": (0.80, 0.33), "F": (0.64, 0.36)}
ciclo = ["M", "A", "F", "A"]; plano = []; ci = 0
for a, b in seg:
    meio = (a + b) / 2
    atras = any(x <= meio <= y for x, y in janelas)
    t = "A" if atras else ciclo[ci % 4]
    if not atras: ci += 1
    if plano and plano[-1][2] == t and not atras: t = "M" if t != "M" else "F"
    plano.append([a, b, t])
fr = lambda t: round(round(t * 30000 / 1001) * 1001 / 30000, 4)
SW, SH = [int(v) for v in subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height","-of","csv=p=0:s=x",SRC],capture_output=True,text=True).stdout.strip().split("x")[:2]]
if SW > SH: SW, SH = SH, SW   # gravação em pé com rotação nos metadados (o ffmpeg já gira ao decodificar)
fc = []
for k, (a, b, t) in enumerate(plano):
    W, fy = TIPO[t]; wd, ht = round(SW * W / 2) * 2, round(SH * W / 2) * 2
    p = [r for r in R if a <= float(r["tempo"]) <= b] or R
    cx = st.median(float(r["cx"]) for r in p); cy = st.median(float(r["cy"]) for r in p)
    x = min(max(0, cx * SW - wd / 2), SW - wd); y = min(max(0, cy * SH - fy * ht), SH - ht)
    a2 = fr(a); b2 = fr(b) if k + 1 < len(plano) else DUR0
    plano[k] = [a2, b2, t]
    fc.append(f"[0:v]trim={a2}:{b2},setpts=PTS-STARTPTS,crop={wd}:{ht}:{int(x)}:{int(y)},scale=1080:1920:flags=lanczos,setsar=1[v{k}]")
fc.append("".join(f"[v{k}]" for k in range(len(plano))) + f"concat=n={len(plano)}:v=1:a=0,eq=brightness=0.02:contrast=1.04:saturation=1.05:gamma=1.04,format=yuv420p[v]")
fc.append("[0:a]highpass=f=70,afftdn=nr=12:nf=-40:tn=1,loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[a]")
open(f"{D}/filtro-base.txt", "w").write(";".join(fc)); json.dump(plano, open(f"{D}/plano-close.json", "w"))
if not os.path.exists(f"{D}/source.mp4") or os.environ.get("REFAZ_BASE"):
    subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",SRC,"-filter_complex_script",f"{D}/filtro-base.txt","-map","[v]","-map","[a]",
        "-c:v","libx264","-crf","16","-preset","medium","-g","30","-pix_fmt","yuv420p","-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709",
        "-bsf:v","h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/source.mp4"], check=True)
DUR = round(dur(f"{D}/source.mp4"), 3)

# ---------- ajudantes de HTML/GSAP ----------
def it(s, cls="i"):  # *palavra* -> itálico na cor de destaque
    return re.sub(r"\*(.+?)\*", rf'<span class="{cls}">\1</span>', html.escape(s))
def camada():
    return {"H": [], "J": []}
def sec(L, id_, a, b, inner, tr=3): L["H"].append(f'<section id="{id_}" class="clip" data-start="{a:.3f}" data-duration="{max(0.3, b - a):.3f}" data-track-index="{tr}">{inner}</section>')
def entra(L, sel, t, y=26, d=0.32): L["J"].append(f'tl.fromTo("{sel}",{{opacity:0,y:{y}}},{{opacity:1,y:0,duration:{d},ease:"power3.out"}},{t:.3f});')
def cresce(L, sel, t): L["J"].append(f'tl.fromTo("{sel}",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.26,ease:"back.out(2.2)"}},{t:.3f});')
def sai(L, sel, t): L["J"].append(f'tl.to("{sel}",{{opacity:0,y:-14,duration:0.22,ease:"power2.in"}},{t:.3f});')
SFX = []
def som(f, t, g): SFX.append((f, round(max(0, t), 3), g))
atras, frente = camada(), camada()

for k, e in enumerate(els):
    a, b = e["_a"], e["_b"]
    if a is None: continue
    i = f"e{k}"; tp = e["t"]
    if tp == "takeover":   # T10 + T11: frase empilhada atrás da cabeça
        linhas = "".join(f'<div id="{i}l{q}" class="tk{" tks" if l[0].startswith("~") else ""}">{it(l[0].lstrip("~"))}</div>' for q, l in enumerate(e["lines"]))
        sec(atras, i, a, b, f'<div class="takeover">{linhas}</div>')
        for q, l in enumerate(e["lines"]):
            t0 = max(a, (acha(l[1], depois=a - 0.2) or a) - 0.05); entra(atras, f"#{i}l{q}", t0, 40, 0.3); som("whoosh-short.wav", t0, -16)
        sai(atras, f"#{i} .takeover", b - 0.25)
    elif tp == "parede":   # C4: parede de capas atrás dela
        capas = "".join(f'<img id="{i}c{q}" class="capa" src="assets/capa{q % 15 + 2:02d}.jpg">' for q in range(16))
        sec(atras, i, a, b, f'<div class="parede">{capas}</div>', 1)
        for q in range(16): cresce(atras, f"#{i}c{q}", a + 0.04 * q)
        atras["J"].append(f'tl.fromTo("#{i} .parede",{{y:0}},{{y:-160,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
        sai(atras, f"#{i} .parede", b - 0.3); som("whoosh.wav", a, -12)
    elif tp == "marcador":   # T16 + T17
        chk = ""
        if e.get("check"):
            chk = '<div class="checks">' + "".join(f'<div id="{i}k{q}" class="chk"><span class="v">✓</span> {html.escape(c[0])}</div>' for q, c in enumerate(e["check"])) + "</div>"
        inner = f'<div class="marc"><div class="mrow"><span class="msm">{html.escape(e["small"])}</span><span class="mbig">{html.escape(e["big"])}</span></div><div id="{i}s" class="msub">{it(e["sub"])}</div>{chk}</div>'
        sec(atras, i, a, b, inner)
        entra(atras, f"#{i} .mrow", a, 30); som("whoosh-short.wav", a, -14)
        entra(atras, f"#{i}s", max(a + 0.35, (acha(e.get("sub_at", ""), depois=a - 0.2) or a + 0.4)), 18)
        for q, c in enumerate(e.get("check", [])):
            t0 = max(a + 0.6, acha(c[1], depois=a) or a + 0.6); entra(atras, f"#{i}k{q}", t0, 14, 0.25); som("pop.wav", t0, -14)
        sai(atras, f"#{i} .marc", b - 0.25)
    elif tp == "fluxo":
        linhas = "".join(f'<div id="{i}f{q}" class="fl">{it(x[0])}</div>' for q, x in enumerate(e["items"]))
        sec(atras, i, a, b, f'<div class="fluxo">{linhas}</div>')
        for q, x in enumerate(e["items"]):
            t0 = max(a, acha(x[1], depois=a - 0.2) or a); entra(atras, f"#{i}f{q}", t0, 24); som("pop.wav", t0, -13)
        sai(atras, f"#{i} .fluxo", b - 0.25)
    elif tp == "cta":   # T19
        inner = f'<div class="cta"><div id="{i}a" class="csm">{html.escape(e["small"])}</div><div id="{i}b" class="cbig">{html.escape(e["big"])}</div><div id="{i}c" class="csub">{it(e["sub"])}</div></div>'
        sec(atras, i, a, min(DUR, b + 1.2), inner)
        for s_, k_ in (("a", "small_at"), ("b", "big_at"), ("c", "sub_at")):
            t0 = max(a, acha(e[k_], depois=a - 0.2) or a); entra(atras, f"#{i}{s_}", t0, 30); som("whoosh-short.wav" if s_ != "b" else "sparkle.wav", t0, -14)
    elif tp == "numcard":   # T2/T3 num cartão branco + contador T15
        v = e["value"]
        inner = f'<div class="ncard" style="top:{e.get("y", 1430)}px"><div class="nlab">{html.escape(e["label"])}</div><div class="nval"><span>{html.escape(e.get("pre", ""))}</span><span id="{i}n">0</span></div><div class="nsub">{html.escape(e["sub"])}</div></div>'
        sec(frente, i, a, b, inner); cresce(frente, f"#{i} .ncard", a); som("pop.wav", a, -10)
        frente["J"].append(f'(()=>{{const o={{v:0}};tl.to(o,{{v:{v},duration:0.9,ease:"power2.out",onUpdate:()=>{{document.getElementById("{i}n").textContent=Math.round(o.v)}}}},{a + 0.15:.3f});}})();')
        som("chime.wav", a + 1.0, -14); sai(frente, f"#{i} .ncard", b - 0.25)
    elif tp == "post":   # cartão do carrossel + R$ que conta
        v = e["value"]
        inner = (f'<div class="post"><img class="pimg" src="{e["img"]}"><div class="ptag">{html.escape(e["label"])}</div></div>'
                 f'<div class="pnum"><div class="nlab">rendeu</div><div class="nval"><span>{html.escape(e["pre"])}</span><span id="{i}n">0</span></div><div class="nsub">{html.escape(e["sub"])}</div></div>')
        sec(frente, i, a, b, inner)
        frente["J"].append(f'tl.fromTo("#{i} .post",{{opacity:0,x:-260,rotation:-12}},{{opacity:1,x:0,rotation:-5,duration:0.45,ease:"power3.out"}},{a:.3f});'); som("whoosh.wav", a, -11)
        t1 = max(a + 0.4, acha(e["count_at"], depois=a - 0.2) or a + 0.6)
        cresce(frente, f"#{i} .pnum", t1); som("pop.wav", t1, -10)
        frente["J"].append(f'(()=>{{const o={{v:0}};tl.to(o,{{v:{v},duration:1.1,ease:"power2.out",onUpdate:()=>{{document.getElementById("{i}n").textContent=Math.round(o.v).toLocaleString("pt-BR")}}}},{t1 + 0.1:.3f});}})();')
        som("chime.wav", t1 + 1.2, -12)
        sai(frente, f"#{i} .post", b - 0.25); sai(frente, f"#{i} .pnum", b - 0.25)
    elif tp == "anot":   # T14
        L = frente if e.get("front") else atras
        cor = "ink" if e.get("ink") else ""
        sec(L, i, a, b, f'<div class="anotw" style="left:{e["x"]}px;top:{e["y"]}px;transform:translateX(-50%) rotate({e.get("rot", 0)}deg)"><div class="anot {cor}">{html.escape(e["text"])}</div></div>')
        t0 = max(a, acha(e["at2"], depois=a - 0.2) or a) if e.get("at2") else a
        L["J"].append(f'tl.fromTo("#{i} .anot",{{opacity:0,clipPath:"inset(0 100% 0 0)"}},{{opacity:1,clipPath:"inset(0 0% 0 0)",duration:0.6,ease:"power1.out"}},{t0:.3f});')
        som("click-soft.wav", t0, -12); sai(L, f"#{i} .anot", b - 0.25)
    elif tp == "quote":   # C13
        sec(frente, i, a, b, f'<div class="quote"><div class="qh">{html.escape(e["who"])}</div><div class="qt">{html.escape(e["text"])}</div></div>')
        cresce(frente, f"#{i} .quote", a); som("pop.wav", a, -10); sai(frente, f"#{i} .quote", b - 0.25)

# ---------- legenda T9: uma palavra por vez, palavra-chave em itálico com sublinhado na cor de destaque ----------
KEY = {n(k) for k in C.get("keys", [])}
caps, capj = [], []
for q, x in enumerate(w):
    ta = x["start"]
    if any(a <= ta <= b for a, b in semcap): continue
    tb = min(w[q + 1]["start"] if q + 1 < len(w) else DUR, ta + 1.0)
    if tb - ta < 0.06: tb = ta + 0.06
    txt = x["text"].rstrip(",")
    k = n(x["text"].rstrip(".,?!")) in KEY
    caps.append(f'<div id="w{q}" class="cap{" key" if k else ""}"><span>{html.escape(txt)}</span></div>')
    capj.append(f'tl.set("#w{q}",{{opacity:1}},{ta:.3f});tl.set("#w{q}",{{opacity:0}},{tb:.3f});')
    if k: capj.append(f'tl.fromTo("#w{q} span",{{backgroundSize:"0% 0.14em"}},{{backgroundSize:"100% 0.14em",duration:0.22,ease:"power2.out"}},{ta:.3f});')

css = _css("estilo-meg.css")
def pagina(L, video, extra_h="", extra_j="", trilha_voz=False):
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="UTF-8"><meta name="viewport" content="width=1080, height=1920">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR}">
  <div id="cam"><video id="aroll" src="{video}" data-start="0" data-duration="{DUR}" data-track-index="0" muted playsinline></video></div>
  {"".join(L["H"])}
  {extra_h}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(L["J"])}
{extra_j}
window.__timelines["main"] = tl;
</script></body></html>"""
for sub in ("atras", "frente"):
    os.makedirs(f"{D}/{sub}", exist_ok=True)
    if not os.path.lexists(f"{D}/{sub}/assets"): os.symlink("../../assets", f"{D}/{sub}/assets")
if not os.path.lexists(f"{D}/atras/source.mp4"): os.symlink("../source.mp4", f"{D}/atras/source.mp4")
open(f"{D}/atras/index.html", "w").write(pagina(atras, "source.mp4"))
capsec = f'<section id="caps" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5">{"".join(caps)}</section>'
open(f"{D}/frente/index.html", "w").write(pagina(frente, "base.mp4", capsec, "\n".join(capj)))
# junta janelas sobrepostas
janelas.sort(); jj = []
for a, b in janelas:
    if jj and a <= jj[-1][1]: jj[-1][1] = max(jj[-1][1], b)
    else: jj.append([max(0, a), min(DUR, b)])
json.dump({"sfx": SFX, "janelas_mascara": jj, "dur": DUR}, open(f"{D}/meta.json", "w"), indent=1)
print(f"ok {nome}: {DUR}s, {len(plano)} enquadramentos ({sum(1 for p in plano if p[2]=='F')} fechados), {len(els)} elementos, {len(SFX)} sons, máscara em {len(jj)} janelas")
