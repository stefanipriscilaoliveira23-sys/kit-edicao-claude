# Receita Editorial v2 (a aprovada): textos BRANCOS, cor de destaque da marca só em sublinhado/risco/ícone, sem cartão branco,
# legenda à direita na altura do ombro, escrita letra a letra com som, emojis, som no número de cada passo,
# print real (do seu sistema/app) quando citar, troca de enquadramento em TODA emenda.
# Uso: python etapa_b2.py <nome> [configs.json]     (modelo do config: exemplo-config.json)
# Entra: <nome>/cortado.mov (do corte.py) e <nome>/t2/transcript.json (transcrever_v2 do cortado)
# Sai:   <nome>/source.mp4, <nome>/atras/index.html, <nome>/frente/index.html, <nome>/meta.json -> depois ./render_meg.sh <nome>
import csv, html, json, os, re, statistics as st, subprocess, sys, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.append(os.path.expanduser("~/.claude/skills/corte-viral/modelo-edicao"))   # se a receita foi copiada pra outra pasta
import marca
nome = sys.argv[1]; D = nome; C = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "configs.json"))[nome]
VINHO = marca.cor("destaque"); TINTA = marca.cor("texto")   # VINHO = cor de destaque da marca (nome mantido no código)
OLHAR = marca.cmd_olhar()
EMOJIS = marca.carregar().get("emojis", True)
# ---------- fontes e cores da marca (manual da marca, via marca.py) ----------
_FT = marca.copiar_fontes("assets")
def _css(arq):
    s = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), arq)).read()
    for chave, papel in (("FONTE_LEGENDA_MEDIA", "legenda_media"), ("FONTE_LEGENDA", "legenda"), ("FONTE_ITALICO", "titulo_italico"), ("FONTE_MANUSCRITA", "manuscrita")):
        s = s.replace(chave, "assets/" + _FT[papel])
    return s.replace("VINHO", VINHO).replace("TINTA", TINTA).replace("CLARO", marca.cor("claro"))

dur = lambda f: float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout)
def n(s): return re.sub(r"[^a-z0-9$/\-]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())

# ---------- transcrição ----------
w = [dict(x) for x in json.load(open(f"{D}/t2/transcript.json"))]
while w and w[-1]["end"] - w[-1]["start"] < 0.1: w.pop()
for de, para in C.get("fix", []):
    a = de.split(); b = para.split(); i = 0
    while i <= len(w) - len(a):
        if [x["text"].lower() for x in w[i:i + len(a)]] == [t.lower() for t in a]:
            s0, e0 = w[i]["start"], w[i + len(a) - 1]["end"]; step = (e0 - s0) / len(b)
            w[i:i + len(a)] = [{"text": t, "start": round(s0 + k * step, 3), "end": round(s0 + (k + 1) * step, 3)} for k, t in enumerate(b)]
            i += len(b)
        else: i += 1
j = []
for x in w:
    if j and x["text"].startswith("-"): j[-1]["text"] += x["text"]; j[-1]["end"] = x["end"]; continue
    j.append(x)
w = j
for q, x in enumerate(w):   # minúscula depois de vírgula ("Um, Chamar" -> "Um, chamar")
    if q and w[q - 1]["text"].endswith(",") and x["text"][:1].isupper() and x["text"].strip(".,!?") not in marca.nomes_proprios(): x["text"] = x["text"][0].lower() + x["text"][1:]
json.dump(w, open(f"{D}/transcript.json", "w"), ensure_ascii=False, indent=1)
T = [n(x["text"]) for x in w]
def acha(fr, depois=0.0, fim=False):
    alvo = [n(t) for t in fr.split() if n(t)]
    for L in range(len(alvo), 0, -1):
        for i in range(len(T) - L + 1):
            if T[i:i + L] == alvo[:L] and w[i]["start"] >= depois - 0.01:
                if L < len(alvo): print(f"  aviso: âncora parcial '{fr}'")
                return w[i + L - 1]["end"] + 0.25 if fim else w[i]["start"]
    print(f"  !! âncora não achada '{fr}'"); return None

# ---------- janelas ----------
SRC = f"{D}/cortado.mov"; DUR0 = dur(SRC)
els = C["els"]
for e in els:
    e["_a"] = acha(e["start"])
    e["_b"] = acha(e["end"], depois=e["_a"] or 0, fim=True) if e.get("end") else (e["_a"] or 0) + e.get("dur", 2.4)
    if e.get("hold"): e["_b"] = max(e["_b"], e["_a"] + e["hold"])
for k, e in enumerate(els):
    if e["t"] in ("print", "anot", "carrossel", "foto"): continue
    prox = [x["_a"] for x in els[k + 1:] if x["_a"] is not None and x["t"] not in ("print", "anot", "carrossel", "foto")]
    if prox and e["_b"] > prox[0] - 0.05: e["_b"] = prox[0] - 0.05
for e in els: e["_b"] = min(e["_b"], DUR0)
ATRAS = {"titulo", "parede", "marcador", "fluxo", "cta", "valor", "anot"}
janelas = [(e["_a"] - 0.1, e["_b"] + 0.3) for e in els if e["t"] in ATRAS and e["_a"] is not None]
janelas_masc = [(e["_a"] - 0.1, e["_b"] + 0.3) for e in els if e["t"] == "parede" and e["_a"] is not None]

# ---------- enquadramento: muda em TODA emenda (corte parece continuação) ----------
if not os.path.exists(f"{D}/rosto.csv"): subprocess.run(OLHAR + [SRC, f"{D}/rosto.csv", "3"], capture_output=True)
R = [r for r in csv.DictReader(open(f"{D}/rosto.csv")) if r["tem_rosto"] == "1"]
cuts = [0.0]; acc = 0
for a, b in json.load(open(f"{D}/plano-video.json" if os.path.exists(f"{D}/plano-video.json") else f"{D}/plano-pausas.json"))[:-1]: acc += b - a; cuts.append(round(acc, 4))
seg = []
for k, a in enumerate(cuts):
    b = cuts[k + 1] if k + 1 < len(cuts) else DUR0
    if seg and b - a < 0.7: seg[-1][1] = b; continue
    seg.append([a, b])
TIPO = {"A": (1.00, 0.30), "M": (0.84, 0.32), "F": (0.70, 0.35)}
plano = []; ci = 0
for a, b in seg:
    meio = (a + b) / 2; atras = any(x <= meio <= y for x, y in janelas)
    ops = ["A", "M"] if atras else ["M", "A", "F", "A"]
    t = ops[ci % len(ops)]; ci += 1
    if plano and plano[-1][2] == t: t = ops[ci % len(ops)]; ci += 1
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
fc.append("[0:a]highpass=f=80,adeclick=w=40:o=75:a=2:t=2.5:b=2,adeclip,deesser=i=0.5:m=0.5:f=0.5,afftdn=nr=14:nf=-40:tn=1,lowpass=f=14000,loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[a]")
open(f"{D}/filtro-base.txt", "w").write(";".join(fc)); json.dump(plano, open(f"{D}/plano-close.json", "w"))
if not os.path.exists(f"{D}/source.mp4") or os.environ.get("REFAZ_BASE"):
    subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",SRC,"-filter_complex_script",f"{D}/filtro-base.txt","-map","[v]","-map","[a]",
        *(["-c:v","h264_videotoolbox","-b:v","22M"] if sys.platform == "darwin" else ["-c:v","libx264","-crf","16","-preset","medium"]),"-pix_fmt","yuv420p","-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709",
        "-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/source.mp4"], check=True)
DUR = round(dur(f"{D}/source.mp4"), 3)

# ---------- ajudantes ----------
def it(s): return re.sub(r"\*(.+?)\*", r'<span class="i">\1</span>', html.escape(s))
atras, frente = {"H": [], "J": []}, {"H": [], "J": []}
SFX = []
def som(f, t, g, d=None): SFX.append((f, round(max(0, t), 3), g, d))
def sec(L, id_, a, b, inner, tr=3): L["H"].append(f'<section id="{id_}" class="clip" data-start="{a:.3f}" data-duration="{max(0.3, b - a):.3f}" data-track-index="{tr}">{inner}</section>')
def entra(L, sel, t, y=24, d=0.3): L["J"].append(f'tl.fromTo("{sel}",{{opacity:0,y:{y}}},{{opacity:1,y:0,duration:{d},ease:"power3.out"}},{t:.3f});')
def sai(L, sel, t): L["J"].append(f'tl.to("{sel}",{{opacity:0,y:-12,duration:0.22,ease:"power2.in"}},{t:.3f});')
def sublinha(L, sel, t): L["J"].append(f'tl.fromTo("{sel} .i",{{backgroundSize:"0% 0.09em"}},{{backgroundSize:"100% 0.09em",duration:0.35,ease:"power2.out"}},{t:.3f});')
def escrita(L, idd, texto, t0, t_fim=None, cls="esc", som_="maquina.wav"):
    """letra por letra (fonte manuscrita da marca) com som de escrita + sublinhado na cor de destaque no fim"""
    chars = "".join(f'<span class="ch">{html.escape(c)}</span>' for c in texto)
    dt = 0.045 if not t_fim else max(0.025, min(0.06, (t_fim - t0) / max(1, len(texto))))
    L["J"].append(f'document.querySelectorAll("#{idd} .ch").forEach((c,k)=>{{tl.set(c,{{opacity:0}},0);tl.set(c,{{opacity:1}},{t0:.3f}+k*{dt:.4f});}});')
    L["J"].append(f'tl.fromTo("#{idd} .risco",{{scaleX:0}},{{scaleX:1,duration:0.3,ease:"power2.out"}},{t0 + len(texto) * dt:.3f});')
    som(som_, t0, -11, round(len(texto) * dt + 0.05, 2))
    return f'<div id="{idd}" class="{cls}"><span class="txt">{chars}</span><span class="risco"></span></div>'

for k, e in enumerate(els):
    a, b = e["_a"], e["_b"]
    if a is None: continue
    i = f"e{k}"; tp = e["t"]
    if tp == "titulo":
        partes = ""
        if e.get("pre"): partes += f'<div id="{i}p" class="tpre">{html.escape(e["pre"])}</div>'
        partes += f'<div id="{i}l" class="t1{" t1s" if e.get("small") else ""}">{it(e["l1"])}</div>'
        esc_at = None
        if e.get("esc"):
            esc_at = max(a + 0.25, acha(e["esc_at"], depois=a - 0.1) or a + 0.5)
            t_fim = acha(e["esc_fim"], depois=esc_at, fim=True) - 0.2 if e.get("esc_fim") else None
            partes += escrita(frente, f"{i}e", e["esc"], esc_at, t_fim)
        sec(frente, i, a, b, f'<div class="topo">{partes}</div>')
        if e.get("pre"): entra(frente, f"#{i}p", a); som("whoosh-short.wav", a, -15)
        t_l = max(a, acha(e["l1_at"], depois=a - 0.1) or a) if e.get("l1_at") else a
        entra(frente, f"#{i}l", t_l, 30); som("whoosh-short.wav", t_l, -14); sublinha(frente, f"#{i}l", t_l + 0.25)
        sai(frente, f"#{i} .topo", b - 0.22)
    elif tp == "parede":
        capas = "".join(f'<img id="{i}c{q}" class="capa" src="assets/capa{q % 15 + 2:02d}.jpg">' for q in range(16))
        sec(atras, i, a, b, f'<div class="parede">{capas}</div>', 1)
        for q in range(16): atras["J"].append(f'tl.fromTo("#{i}c{q}",{{opacity:0,scale:0.6}},{{opacity:1,scale:1,duration:0.25,ease:"back.out(2)"}},{a + 0.035 * q:.3f});')
        atras["J"].append(f'tl.fromTo("#{i} .parede",{{y:0}},{{y:-160,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
        sai(atras, f"#{i} .parede", b - 0.3)
        for q in range(16): som("click-soft.wav", a + 0.035 * q, -16 if q % 2 else -12)
    elif tp == "marcador":
        t_num = max(a, acha(e["num_at"], depois=a - 0.2) or a)
        esc_at = max(t_num + 0.4, acha(e["esc_at"], depois=a - 0.2) or a + 0.5)
        inner = (f'<div class="topo"><div id="{i}r" class="mrow"><span class="msm">{html.escape(e["small"])}</span><span class="mbig"><span class="i">{html.escape(e["big"])}</span></span></div>'
                 + escrita(frente, f"{i}e", e["esc"], esc_at) + '</div>')
        sec(frente, i, a, b, inner)
        entra(frente, f"#{i}r", t_num, 30); sublinha(frente, f"#{i}r", t_num + 0.2)
        som("ping.wav", t_num, -9); som("whoosh-short.wav", t_num, -16)
        sai(frente, f"#{i} .topo", b - 0.22)
    elif tp == "fluxo":
        linhas = "".join(f'<div id="{i}f{q}" class="fl">{it(x[0])}</div>' for q, x in enumerate(e["items"]))
        sec(frente, i, a, b, f'<div class="topo">{linhas}</div>')
        for q, x in enumerate(e["items"]):
            t0 = max(a, acha(x[1], depois=a - 0.2) or a); entra(frente, f"#{i}f{q}", t0, 22); sublinha(frente, f"#{i}f{q}", t0 + 0.2); som("pop.wav", t0, -13)
        sai(frente, f"#{i} .topo", b - 0.22)
    elif tp == "anot":
        t0 = max(a, acha(e["at2"], depois=a - 0.2) or a) if e.get("at2") else a
        sec(frente, i, a, b, '<div class="topo">' + escrita(frente, f"{i}e", e["text"], t0, cls="anot", som_="escrita.wav") + '</div>')
        sai(frente, f"#{i} .topo", b - 0.22)
    elif tp == "cta":
        inner = f'<div class="topo"><div id="{i}a" class="tpre">{html.escape(e["small"])}</div><div id="{i}b" class="t1 cbig"><span class="i">{html.escape(e["big"])}</span></div>'
        t_e = max(a, acha(e["esc_at"], depois=a - 0.2) or a)
        inner += escrita(frente, f"{i}e", e["esc"], t_e) + '</div>'
        sec(frente, i, a, DUR, inner)
        ta = max(a, acha(e["small_at"], depois=a - 0.2) or a); tb = max(a, acha(e["big_at"], depois=a - 0.2) or a)
        entra(frente, f"#{i}a", ta, 26); som("whoosh-short.wav", ta, -14)
        entra(frente, f"#{i}b", tb, 30); sublinha(frente, f"#{i}b", tb + 0.25); som("sparkle.wav", tb, -13)
    elif tp == "valor":
        t1 = max(a + 0.3, acha(e["count_at"], depois=a - 0.2) or a + 0.5)
        inner = (f'<div class="topo"><div id="{i}a" class="tpre">{html.escape(e["l0"])}</div>'
                 f'<div id="{i}b" class="vbig"><span class="i"><span>{html.escape(e["pre"])}</span><span id="{i}n">0</span></span></div>'
                 + escrita(frente, f"{i}e", e["esc"], t1 + 1.2) + '</div>')
        sec(frente, i, a, b, inner)
        entra(frente, f"#{i}a", a, 22); som("whoosh-short.wav", a, -15)
        entra(frente, f"#{i}b", t1, 30); sublinha(frente, f"#{i}b", t1 + 1.1)
        frente["J"].append(f'(()=>{{const o={{v:0}};tl.to(o,{{v:{e["value"]},duration:1.1,ease:"power2.out",onUpdate:()=>{{document.getElementById("{i}n").textContent=Math.round(o.v).toLocaleString("pt-BR")}}}},{t1:.3f});}})();')
        for q in range(8): som("key-press.wav", t1 + q * 0.12, -20)
        som("chime.wav", t1 + 1.05, -11)
        sai(frente, f"#{i} .topo", b - 0.22)
    elif tp == "carrossel":   # cartas distribuídas na mesa -> galeria rolando -> somem
        ta = max(a, acha(e.get("at", e["start"]), depois=a - 0.2) or a)
        nc, Wc, G = 6, 420, 24; st_ = Wc + G
        cards = "".join(f'<img id="{i}s{q}" class="cslide" src="assets/slide{q + 1}.jpg" style="left:{40 + q * st_}px">' for q in range(nc))
        inner = f'<div class="mesa"><div id="{i}row" class="crow">{cards}</div></div><div id="{i}m" class="cmeta">❤️ {e["likes"]}   💬 {e["coms"]}   · comenta <b>{html.escape(e["palavra"])}</b></div>'
        rot = [-22, 14, -9, 18, -15, 8]
        for q in range(nc):
            t0 = ta + 0.13 * q; dx = int(540 - Wc / 2 - (40 + q * st_))
            frente["J"].append(f'tl.fromTo("#{i}s{q}",{{x:{dx},y:950,rotation:{rot[q]},opacity:0}},{{x:0,y:0,rotation:0,opacity:1,duration:0.38,ease:"power3.out"}},{t0:.3f});')
            som("click-soft.wav", t0 + 0.2, -12)
        t_g = ta + 0.13 * nc + 0.35; dist = (40 + (nc - 1) * st_) - (1080 - 40 - Wc)
        frente["J"].append(f'tl.to("#{i}row",{{x:{-dist},duration:2.3,ease:"sine.inOut"}},{t_g:.3f});')
        entra(frente, f"#{i}m", t_g, 14); som("pop.wav", t_g, -14)
        t_x = t_g + 2.4
        for q in range(nc):
            frente["J"].append(f'tl.to("#{i}s{q}",{{y:-900,rotation:{-rot[q]},opacity:0,duration:0.32,ease:"power2.in"}},{t_x + 0.05 * q:.3f});')
            if q % 2 == 0: som("click-soft.wav", t_x + 0.05 * q, -15)
        frente["J"].append(f'tl.to("#{i}m",{{opacity:0,duration:0.2}},{t_x:.3f});')
        e["_b"] = b = t_x + 0.5
        sec(frente, i, a, b, inner)
    elif tp == "lista":   # tópicos do lado esquerdo, na altura do rosto, escritos à mão
        mk = e.get("mark", "•"); itens = ""
        for q, (txt, anc) in enumerate(e["items"]):
            t0 = max(a, acha(anc, depois=a - 0.2) or a)
            itens += f'<div class="li"><span class="mk">{html.escape(mk)}</span>' + escrita(frente, f"{i}i{q}", txt, t0, cls="esc lesc") + '</div>'
        sec(frente, i, a, b, f'<div class="lista">{itens}</div>')
        sai(frente, f"#{i} .lista", b - 0.22)
    elif tp == "foto":   # fotos antigas entrando por cima do vídeo
        modo = e.get("modo", "pop"); imgs = e["imgs"]; Wf = e.get("w", 560)
        b = e["_b"] = a + e.get("dur", 2.4)
        if modo == "passa":
            sec(frente, i, a, b, f'<img class="foto" src="assets/{imgs[0]}" style="width:{Wf}px;top:{e.get("y", 1080)}px;left:0">')
            frente["J"].append(f'tl.fromTo("#{i} .foto",{{x:1120,rotation:7}},{{x:{-Wf - 80},rotation:-7,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
            som("whoosh-short.wav", a, -12)
        elif modo == "pilha":
            fs = "".join(f'<img id="{i}f{q}" class="foto" src="assets/{im}" style="width:{Wf}px;left:{e.get("x", 260) + (q % 2) * 40 - 20}px;top:{e.get("y", 1000) + q * e.get("dy", 30)}px">' for q, im in enumerate(imgs))
            sec(frente, i, a, b, fs)
            for q in range(len(imgs)):
                t0 = a + q * e.get("gap", 0.25); r = (-6 if q % 2 else 6)
                frente["J"].append(f'tl.fromTo("#{i}f{q}",{{y:-1300,rotation:{r * 3},opacity:1}},{{y:0,rotation:{r},duration:{e.get("queda", 0.34)},ease:"power3.out"}},{t0:.3f});')
                som(e.get("som", "click-soft.wav"), t0 + 0.25, -11)
            frente["J"].append(f'tl.to("#{i} .foto",{{x:1200,opacity:0,duration:0.3,stagger:0.04,ease:"power2.in"}},{b - 0.35:.3f});')
        elif modo == "tela":
            sec(frente, i, a, b, f'<div class="ftela"><img src="assets/{imgs[0]}"></div>', 2)
            frente["J"].append(f'tl.fromTo("#{i} .ftela",{{opacity:0}},{{opacity:1,duration:0.25}},{a:.3f});')
            frente["J"].append(f'tl.fromTo("#{i} .ftela img",{{scale:1.15}},{{scale:1.0,duration:{b - a:.3f},ease:"none"}},{a:.3f});')
            frente["J"].append(f'tl.to("#{i} .ftela",{{opacity:0,duration:0.22}},{b - 0.22:.3f});')
            som("whoosh-short.wav", a, -12)
        elif modo == "mosaico":
            tiles = "".join(f'<div id="{i}m{q}" class="mtile" style="left:{(q % 2) * 540}px;top:{(q // 2) * 640}px"><img src="assets/{im}"></div>' for q, im in enumerate(imgs))
            sec(frente, i, a, b, f'<div class="mosaico">{tiles}</div>', 4)
            vind = [(-700, -300), (700, -200), (-700, 0), (700, 100), (-700, 300), (700, 400)]
            for q in range(len(imgs)):
                t0 = a + q * e.get("gap", 0.25); dx, dy = vind[q % 6]
                frente["J"].append(f'tl.fromTo("#{i}m{q}",{{x:{dx},y:{dy},scale:1.3,rotation:{12 if q % 2 else -12},opacity:0}},{{x:0,y:0,scale:1,rotation:0,opacity:1,duration:0.45,ease:"power3.out"}},{t0:.3f});')
                som("ping.wav" if q % 2 else "click-soft.wav", t0 + 0.3, -12)
        else:
            sec(frente, i, a, b, f'<img class="foto" src="assets/{imgs[0]}" style="width:{Wf}px;left:{e.get("x", 60)}px;top:{e.get("y", 1080)}px">')
            frente["J"].append(f'tl.fromTo("#{i} .foto",{{opacity:0,scale:0.5,rotation:-14}},{{opacity:1,scale:1,rotation:{e.get("rot", -4)},duration:0.35,ease:"back.out(1.8)"}},{a:.3f});')
            frente["J"].append(f'tl.to("#{i} .foto",{{x:-900,rotation:-20,duration:0.3,ease:"power2.in"}},{b - 0.32:.3f});')
            som("pop.wav", a, -11); som("whoosh-short.wav", b - 0.32, -16)
    elif tp == "print":   # print real (tela do seu app/sistema/relatório), sem moldura branca nossa; "img" em assets/
        tz = max(a + 0.5, acha(e["zoom_at"], depois=a - 0.2) or a + 1)
        inner = f'<div class="print"><img src="assets/{e.get("img", "print.png")}"><div class="marca"></div></div>'
        sec(frente, i, a, b, inner)
        frente["J"].append(f'tl.fromTo("#{i} .print",{{opacity:0,x:-300,rotation:-10}},{{opacity:1,x:0,rotation:-3,duration:0.45,ease:"power3.out"}},{a:.3f});'); som("whoosh.wav", a, -11)
        frente["J"].append(f'tl.to("#{i} .print",{{scale:1.22,duration:0.6,ease:"power2.inOut"}},{tz - 0.2:.3f});')
        frente["J"].append(f'tl.fromTo("#{i} .marca",{{opacity:0,scale:1.4}},{{opacity:1,scale:1,duration:0.3,ease:"back.out(2)"}},{tz + 0.45:.3f});'); som("click-soft.wav", tz + 0.45, -9)
        sai(frente, f"#{i} .print", b - 0.25)

# ---------- inserção em tela cheia (cobre olhar pra baixo nas duas pontas da emenda) ----------
PP = json.load(open(f"{D}/plano-pausas.json")); PV = json.load(open(f"{D}/plano-video.json")) if os.path.exists(f"{D}/plano-video.json") else PP
def emenda(tb):
    k = min(range(len(PP) - 1), key=lambda q: abs(PP[q][1] - tb)); return sum(y - x for x, y in PV[:k + 1])
INS = []
for ins in C.get("insercoes", []):
    if isinstance(ins, dict):
        t = emenda(ins["bruto"]); INS.append((t - ins.get("antes", 0.15), t + ins.get("depois", 0.6), ins["txt"], ins.get("bg", "capas")))
    else: INS.append((ins[0], ins[1], ins[2], ins[3] if len(ins) > 3 else "capas"))
for q, (a0, b0, l1, bg) in enumerate(INS):
    if bg.startswith("foto:"): capas = f'<img class="ibg" src="assets/{bg[5:]}">'
    elif bg.startswith("mosaico:"):
        capas = '<div class="mosaico">' + "".join(f'<div class="mtile" style="left:{(z % 2) * 540}px;top:{(z // 2) * 640}px"><img src="assets/{im}"></div>' for z, im in enumerate(bg[8:].split(","))) + '</div>'
    elif bg.startswith("notifs:"): capas = '<div class="ngrid">' + "".join(f'<img src="assets/{im}">' for im in bg[7:].split(",")) + '</div>'
    elif bg == "carrossel": capas = '<div class="igrid">' + "".join(f'<img class="capa slide" src="assets/slide{z % 6 + 1}.jpg">' for z in range(20)) + '</div>'
    else: capas = '<div class="igrid">' + "".join(f'<img class="capa" src="assets/capa{(z * 5) % 15 + 2:02d}.jpg">' for z in range(16)) + '</div>'
    sec(frente, f"ins{q}", a0, b0, f'<div class="insert" style="z-index:50"><div class="ibox">{capas}</div><div class="ishade"></div><div class="itxt">{it(l1)}</div></div>', 6)
    frente["J"].append(f'tl.fromTo("#ins{q} .ibox",{{scale:1.12}},{{scale:1.0,duration:{b0 - a0:.3f},ease:"none"}},{a0:.3f});')
    frente["J"].append(f'tl.fromTo("#ins{q} .itxt",{{opacity:0,scale:0.8}},{{opacity:1,scale:1,duration:0.2,ease:"back.out(2)"}},{a0 + 0.05:.3f});')
    sublinha(frente, f"#ins{q} .itxt", a0 + 0.2)
    for z in range(3): som("click-soft.wav", a0 + z * 0.05, -13)
semins = [x[:2] for x in INS]
# ---------- emojis ----------
for q, (anc, emo, lado) in enumerate(C.get("emojis", []) if EMOJIS else []):
    t0 = acha(anc)
    if t0 is None or any(a0 - 0.2 <= t0 <= b0 for a0, b0 in semins): continue
    x = 150 if lado == "L" else 930; y = 1230 if lado == "L" else 820
    rot = -10 if lado == "L" else 10
    sec(frente, f"em{q}", t0, t0 + 1.4, f'<div class="emo" style="left:{x}px;top:{y}px">{emo}</div>', 4)
    frente["J"].append(f'tl.fromTo("#em{q} .emo",{{opacity:0,scale:0.2,rotation:{-rot}}},{{opacity:1,scale:1,rotation:{rot},duration:0.32,ease:"back.out(2.6)"}},{t0:.3f});')
    frente["J"].append(f'tl.to("#em{q} .emo",{{y:-30,duration:1.0,ease:"none"}},{t0 + 0.3:.3f});')
    frente["J"].append(f'tl.to("#em{q} .emo",{{opacity:0,scale:0.7,duration:0.2}},{t0 + 1.15:.3f});')
    som("pop.wav", t0, -12)

# ---------- legenda: 1 palavra, lado direito na altura do ombro, chave em itálico branco com sublinhado na cor de destaque ----------
KEY = {n(k) for k in C.get("keys", [])}
caps, capj = [], []
for q, x in enumerate(w):
    ta = x["start"]; tb = min(w[q + 1]["start"] if q + 1 < len(w) else DUR, ta + 1.0)
    if any(a0 <= ta <= b0 for a0, b0 in semins): continue
    if tb - ta < 0.06: tb = ta + 0.06
    txt = x["text"].rstrip(","); k = n(x["text"].rstrip(".,?!")) in KEY
    caps.append(f'<div id="w{q}" class="cap{" key" if k else ""}"><span>{html.escape(txt)}</span></div>')
    capj.append(f'tl.set("#w{q}",{{opacity:1}},{ta:.3f});tl.set("#w{q}",{{opacity:0}},{tb:.3f});')
    if k: capj.append(f'tl.fromTo("#w{q} span",{{backgroundSize:"0% 0.08em"}},{{backgroundSize:"100% 0.08em",duration:0.22,ease:"power2.out"}},{ta + 0.05:.3f});')

css = _css("estilo-v2.css")
def pagina(L, video, extra_h="", extra_j=""):
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
camz = []
for k, (a, b, t) in enumerate(plano):
    if b - a >= 1.8 and k % 2 == 0:
        camz.append(f'tl.fromTo("#cam",{{scale:1}},{{scale:1.07,duration:{b - a:.3f},ease:"sine.inOut"}},{a:.3f});')
    else:
        camz.append(f'tl.set("#cam",{{scale:1}},{a:.3f});')
capj = camz + capj
capsec = f'<section id="caps" class="clip" data-start="0" data-duration="{DUR}" data-track-index="5">{"".join(caps)}</section>'
open(f"{D}/frente/index.html", "w").write(pagina(frente, "base.mp4", capsec, "\n".join(capj)))
janelas_masc.sort(); jj = []
for a, b in janelas_masc:
    if jj and a <= jj[-1][1]: jj[-1][1] = max(jj[-1][1], b)
    else: jj.append([max(0, a), min(DUR, b)])
json.dump({"sfx": SFX, "janelas_mascara": jj, "dur": DUR}, open(f"{D}/meta.json", "w"), indent=1)
print(f"ok {nome}: {DUR}s, {len(plano)} enquadramentos, {len(els)} elementos, {len(SFX)} sons")
