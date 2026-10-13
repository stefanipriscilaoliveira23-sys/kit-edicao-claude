#!/usr/bin/env python3
"""
Sanfoninha: cada cena entra com um "soquinho" de zoom, segue com zoom lento e
sai com zoom pra dentro (atravessa), zoom pra fora (sanfona), giro ou corte
seco, sempre cortando na batida. Desfoque de movimento real (media de
subquadros), so quando o movimento e rapido. Bordas do giro espelhadas.

Jeito principal (plano em json, feito pelo montar_plano.py e revisado pelo Claude):
  python3 -I zoom_transicao.py --plano plano.json --saida previa.mp4 --previa --folha folha.jpg
  python3 -I zoom_transicao.py --plano plano.json --saida final.mp4 --folha folha-final.jpg

Jeitos rapidos (sem plano):
  --trecho arquivo@inicio@batidas (repetir) ou --pasta ./brutos (videos 01, 02...)

Precisa: ffmpeg (~/.local/bin ou no PATH), python com numpy e opencv.
Pillow so e usado se houver texto no gancho.
"""
import argparse, json, os, re, shutil, subprocess, sys
import numpy as np
import cv2

FPS = 30
OUT_W, OUT_H = 1080, 1920
WORK_W, WORK_H = 1440, 2560          # trabalha maior pra o zoom nao borrar


def achar_ff(nome="ffmpeg"):
    exe = nome + (".exe" if os.name == "nt" else "")
    for c in [os.path.expanduser(f"~/.local/bin/{exe}"), shutil.which(nome),
              f"/opt/homebrew/bin/{nome}", f"/usr/local/bin/{nome}"]:
        if c and os.path.isfile(c):
            return c
    sys.exit(f"Nao achei o {nome}. Veja o INSTALAR.md da skill sanfoninha.")


FF = achar_ff("ffmpeg")
FFPROBE = achar_ff("ffprobe")

# ---------------- parametros medidos no reel de referencia ----------------
P = dict(
    soco_dur=0.22,  soco_de=1.00, soco_ate=1.25,     # entrada: zoom in rapido, desacelera
    hook_dur=0.40,  hook_ate=1.45,                   # gancho: soco maior
    flash_dur=0.17, flash_ate=1.35,                  # flash: soco curto e forte
    deriva=0.12,                                     # zoom lento continuo: +12% por segundo
    deriva_resultado=0.05,                           # resultado: zoom lento mais calmo
    atravessa_dur=0.13, atravessa_extra=0.18,        # saida: acelera zoom in +18% no fim
    sanfona_dur=0.30,                                # saida: zoom out ate quadro cheio (1.0)
    giro_saida_dur=0.17, giro_saida_graus=20, giro_saida_zoom=0.08,
    giro_entrada_dur=0.30, giro_entrada_graus=-15, giro_entrada_de=1.35, giro_entrada_ate=1.20,
    seco_zoom=1.10, seco_zoom_resultado=1.02,        # corte seco: so zoom lento
    fade_final=0.6,                                  # fim: escurece pro preto
    sub=7, obturador=0.5,                            # desfoque: 7 subquadros, 180 graus
)


def ease_out(p): return 1 - (1 - p) ** 3          # rapido no comeco, suave no fim
def ease_in(p):  return p ** 3                    # suave no comeco, rapido no fim


def curva(u, D, c):
    """(zoom, giro_em_graus) no tempo u (s) da cena c com duracao D."""
    rot = 0.0
    entrada, saida, deriva = c["entrada"], c["saida"], c["deriva"]
    if entrada in ("soco", "gancho", "flash"):
        dur, ate = {"soco": (P["soco_dur"], P["soco_ate"]), "gancho": (P["hook_dur"], P["hook_ate"]),
                    "flash": (P["flash_dur"], P["flash_ate"])}[entrada]
        p = min(u / dur, 1.0); z0 = P["soco_de"] + (ate - P["soco_de"]) * ease_out(p)
    elif entrada == "giro":
        dur = P["giro_entrada_dur"]; p = min(u / dur, 1.0)
        z0 = P["giro_entrada_de"] + (P["giro_entrada_ate"] - P["giro_entrada_de"]) * ease_out(p)
        rot = P["giro_entrada_graus"] * (1 - ease_out(p))
    else:  # seco
        dur = 0.0; z0 = c["zoom_base"]
    z = z0 * (1 + deriva * max(0.0, u - dur))
    rest = D - u
    if saida == "atravessa" and rest < P["atravessa_dur"]:
        p = 1 - rest / P["atravessa_dur"]; z *= 1 + P["atravessa_extra"] * ease_in(p)
    elif saida == "sanfona" and rest < P["sanfona_dur"]:
        zi = z0 * (1 + deriva * max(0.0, D - P["sanfona_dur"] - dur))
        p = 1 - rest / P["sanfona_dur"]; z = zi + (1.0 - zi) * ease_in(p)
    elif saida == "giro" and rest < P["giro_saida_dur"]:
        p = 1 - rest / P["giro_saida_dur"]
        rot += P["giro_saida_graus"] * ease_in(p); z *= 1 + P["giro_saida_zoom"] * ease_in(p)
    return z, rot


def matriz(z, rot):
    M = cv2.getRotationMatrix2D((WORK_W / 2, WORK_H / 2), rot, z)
    S = np.array([[OUT_W / WORK_W, 0, 0], [0, OUT_H / WORK_H, 0], [0, 0, 1]])
    return (S @ np.vstack([M, [0, 0, 1]]))[:2]


def duracao(arq):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                       capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return None


def ler_quadros(arq, ini, dur, foco_x=0.5):
    crop_x = f"(iw-{WORK_W})*{min(max(foco_x, 0), 1):.3f}"
    cmd = [FF, "-v", "fatal", "-ss", "%.3f" % ini, "-i", arq, "-t", "%.4f" % (dur + 0.2), "-an",
           "-vf", f"fps={FPS},scale={WORK_W}:{WORK_H}:force_original_aspect_ratio=increase,"
                  f"crop={WORK_W}:{WORK_H}:{crop_x}:(ih-{WORK_H})/2,setsar=1",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    pr = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = WORK_W * WORK_H * 3
    while True:
        b = pr.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(WORK_H, WORK_W, 3)
    pr.wait()


def batida_sintetica(caminho, dur, bpm):
    sr = 44100; t = np.arange(int(sr * dur)) / sr; y = np.zeros_like(t); b = 60 / bpm
    for k in range(int(dur / b) + 1):                       # bumbo em toda batida
        s = int(k * b * sr); L = int(0.25 * sr); tt = np.arange(L) / sr
        kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9)
        y[s:s + L] += kick[:len(y[s:s + L])] * 0.9
    rng = np.random.default_rng(1)
    for k in range(int(dur / (b / 2)) + 1):                 # chimbal em colcheias
        s = int(k * b / 2 * sr); L = int(0.04 * sr)
        hat = rng.standard_normal(L) * np.exp(-np.arange(L) / sr * 120) * 0.12
        y[s:s + L] += hat[:len(y[s:s + L])]
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run([FF, "-v", "error", "-y", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                    caminho], input=pcm, check=True)


# ---------------- texto opcional do gancho (fonte e cor do Manual da Marca) ----------------
def hex_bgr(h, padrao):
    h = (h or padrao).lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h): h = padrao.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (4, 2, 0))


def achar_fonte(nome):
    if nome:
        nome = os.path.expanduser(nome)
        if os.path.isfile(nome): return nome
    pastas = [os.path.expanduser("~/minha-marca/fontes"),
              os.path.expanduser("~/.claude/skills/corte-viral/modelo-edicao/assets/fonts"),
              os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fontes")]
    for nm in ([nome] if nome else []) + ["Inter-Bold.woff2", "Inter-Bold.ttf"]:
        for p in pastas:
            c = os.path.join(p, os.path.basename(nm))
            if os.path.isfile(c): return c
    for c in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.isfile(c): return c
    return None


def camada_texto(texto, plano):
    """devolve (rgb float32, alfa float32) do tamanho da saida, ou None."""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        print("AVISO: sem Pillow, o texto do gancho foi pulado (veja INSTALAR.md)."); return None
    marca = {}
    mj = os.path.expanduser("~/minha-marca/marca.json")
    if os.path.isfile(mj):
        try: marca = json.load(open(mj, encoding="utf-8"))
        except Exception: marca = {}
    cores = marca.get("cores", {}) if isinstance(marca.get("cores"), dict) else {}
    fontes = marca.get("fontes", {}) if isinstance(marca.get("fontes"), dict) else {}
    fonte = achar_fonte(plano.get("fonte_texto") or fontes.get("titulo"))
    cor = hex_bgr(plano.get("cor_texto") or cores.get("claro"), "#FFFFFF")[::-1]
    sombra = hex_bgr(cores.get("escuro"), "#000000")[::-1]
    print(f"texto do gancho: fonte={fonte}  cor=#{''.join('%02X' % v for v in cor)}"
          f"  ({'Manual da Marca' if marca else 'padrao'})")
    W, H = OUT_W, OUT_H
    tam = int(plano.get("tamanho_texto", 84) * W / 1080)
    fnt = ImageFont.truetype(fonte, tam) if fonte else ImageFont.load_default()
    d0 = ImageDraw.Draw(Image.new("L", (W, H)))
    def quebrar(par, larg):
        out, atual = [], ""
        for w in par.split():
            teste = (atual + " " + w).strip()
            if d0.textlength(teste, font=fnt) <= larg or not atual: atual = teste
            else: out.append(atual); atual = w
        return out + [atual]

    linhas = []
    for par in texto.split("\n"):                            # linhas equilibradas (sem palavra sozinha)
        n = len(quebrar(par, W * 0.84)); larg = W * 0.84
        if n > 1:
            larg = d0.textlength(par, font=fnt) / n * 1.08
            while len(quebrar(par, larg)) > n: larg += 10
        linhas += quebrar(par, larg)
    alt = int(tam * 1.12); topo = int(H * plano.get("altura_texto", 0.15)) - alt * len(linhas) // 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(sh)
    for i, ln in enumerate(linhas):
        x = (W - d.textlength(ln, font=fnt)) / 2; y = topo + i * alt
        ds.text((x, y + tam * 0.04), ln, font=fnt, fill=sombra + (200,))
        d.text((x, y), ln, font=fnt, fill=cor + (255,))
    sh = sh.filter(ImageFilter.GaussianBlur(tam * 0.12))
    comp = Image.alpha_composite(sh, img)
    a = np.asarray(comp).astype(np.float32)
    rgb = a[:, :, 2::-1].copy(); alfa = a[:, :, 3:4] / 255.0
    return rgb, alfa


# ---------------- folha de quadros ----------------
def montar_folha(tiles, caminho, colunas=3):
    if not tiles: return
    th, tw = tiles[0][1][0].shape[:2]
    gap, lab = 8, 26
    tile_w = tw * 3 + gap * 2; tile_h = th + lab
    linhas = (len(tiles) + colunas - 1) // colunas
    W = colunas * tile_w + (colunas + 1) * 16; H = linhas * tile_h + (linhas + 1) * 16
    folha = np.full((H, W, 3), 245, np.uint8)
    for i, (rot, ims) in enumerate(tiles):
        r, c = divmod(i, colunas)
        x0 = 16 + c * (tile_w + 16); y0 = 16 + r * (tile_h + 16)
        cv2.putText(folha, rot, (x0, y0 + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 1, cv2.LINE_AA)
        for j, im in enumerate(ims):
            folha[y0 + lab:y0 + lab + th, x0 + j * (tw + gap):x0 + j * (tw + gap) + tw] = im
    cv2.imwrite(caminho, folha, [cv2.IMWRITE_JPEG_QUALITY, 85])


# ---------------- montagem das cenas ----------------
ENTRADA_DE = {"atravessa": "soco", "sanfona": "soco", "giro": "giro", "seco": "seco"}


def normalizar(cenas):
    out = []
    for i, c in enumerate(cenas):
        c = dict(c); papel = c.get("papel", "gancho" if i == 0 else "processo")
        c["papel"] = papel
        c.setdefault("saida", "seco" if i == len(cenas) - 1 else "atravessa")
        if "entrada" not in c:
            if i == 0: c["entrada"] = "gancho"
            elif papel == "flash": c["entrada"] = "flash" if out[-1]["saida"] != "giro" else "giro"
            else: c["entrada"] = ENTRADA_DE[out[-1]["saida"]]
        c.setdefault("deriva", P["deriva_resultado"] if papel == "resultado" else P["deriva"])
        c.setdefault("zoom_base", P["seco_zoom_resultado"] if papel == "resultado" else P["seco_zoom"])
        c.setdefault("foco_x", 0.5)
        for k in ("entrada", "saida"):
            if c[k] not in ("soco", "gancho", "flash", "giro", "seco", "atravessa", "sanfona"):
                sys.exit(f"cena {i+1}: {k} desconhecida: {c[k]}")
        out.append(c)
    return out


def main():
    global OUT_W, OUT_H, WORK_W, WORK_H
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", required=True)
    ap.add_argument("--plano")
    ap.add_argument("--trecho", action="append", default=[])
    ap.add_argument("--pasta")
    ap.add_argument("--inicio", type=float, default=0.5, help="segundo de cada bruto (modo pasta)")
    ap.add_argument("--batidas", type=float, default=4, help="batidas por trecho (modo pasta)")
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--transicoes", default="", help="lista: atravessa,sanfona,giro,seco")
    ap.add_argument("--musica"); ap.add_argument("--musica-inicio", type=float)
    ap.add_argument("--batida-sintetica", action="store_true", help="poe uma batida de teste no lugar da musica")
    ap.add_argument("--sem-som", action="store_true")
    ap.add_argument("--previa", action="store_true", help="versao leve e rapida pra aprovar (540x960)")
    ap.add_argument("--folha", help="salva uma folha de quadros (entrada, meio e saida de cada cena)")
    a = ap.parse_args()

    plano = {}
    if a.plano:
        plano = json.load(open(a.plano, encoding="utf-8"))
        base = os.path.dirname(os.path.abspath(a.plano))
        cenas = []
        for c in plano["cenas"]:
            c = dict(c); arq = os.path.expanduser(c["arquivo"])
            c["arquivo"] = arq if os.path.isabs(arq) else os.path.join(base, arq)
            cenas.append(c)
    else:
        cenas = []
        for t in a.trecho:
            arq, ini, bt = t.rsplit("@", 2); cenas.append(dict(arquivo=arq, inicio=float(ini), batidas=float(bt)))
        if a.pasta:
            vids = [f for f in os.listdir(a.pasta) if re.match(r"^\d+.*\.(mp4|mov|m4v)$", f, re.I)]
            vids.sort(key=lambda f: int(re.match(r"^(\d+)", f).group(1)))
            cenas += [dict(arquivo=os.path.join(a.pasta, f), inicio=a.inicio, batidas=a.batidas) for f in vids]
        rodizio = ["atravessa", "sanfona", "atravessa", "giro"]
        trans = [x for x in a.transicoes.split(",") if x]
        for i, c in enumerate(cenas[:-1]):
            c["saida"] = trans[i] if i < len(trans) else rodizio[i % 4]
    if not cenas: sys.exit("nenhuma cena")
    cenas = normalizar(cenas)

    bpm = a.bpm or plano.get("bpm") or 143
    musica = a.musica or plano.get("musica")
    if musica: musica = os.path.expanduser(musica)
    if musica and not os.path.isabs(musica) and a.plano:
        musica = os.path.join(os.path.dirname(os.path.abspath(a.plano)), musica)
    mus_ini = a.musica_inicio if a.musica_inicio is not None else float(plano.get("musica_inicio", 0))
    sem_som = a.sem_som or bool(plano.get("sem_som"))
    texto = (plano.get("texto_gancho") or "").strip()

    sub = P["sub"]; crf, preset = "18", "medium"
    if a.previa:
        OUT_W, OUT_H, WORK_W, WORK_H = 540, 960, 720, 1280
        sub = 3; crf, preset = "26", "veryfast"

    # cortes exatamente na batida (em quadros)
    beat = 60 / bpm; acum = 0.0; cortes = [0]
    for c in cenas:
        acum += float(c["batidas"]); cortes.append(round(acum * beat * FPS))
    total = cortes[-1]

    txt = camada_texto(texto, plano) if texto else None

    os.makedirs(os.path.dirname(os.path.abspath(a.saida)) or ".", exist_ok=True)
    tmp = a.saida + ".video.mp4"
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", preset, "-crf", crf, "-pix_fmt", "yuv420p", tmp],
                           stdin=subprocess.PIPE)
    fade_q = int(P["fade_final"] * FPS)
    tiles = []; tw = 150; th = int(tw * 16 / 9)
    for i, c in enumerate(cenas):
        n = cortes[i + 1] - cortes[i]; D = n / FPS
        if n <= 0: sys.exit(f"cena {i+1} ficou com 0 quadros (batidas={c['batidas']})")
        ini = float(c.get("inicio", 0)); dv = duracao(c["arquivo"])
        if dv and ini + D > dv - 0.03:
            novo = max(0.0, dv - D - 0.05)
            print(f"  aviso: {os.path.basename(c['arquivo'])} e curto, inicio {ini:.2f} -> {novo:.2f}")
            ini = novo
        print(f"cena {i+1:2d} [{c['papel']:9s}] {os.path.basename(c['arquivo'])} desde {ini:.2f}s  "
              f"{D:.2f}s  entra={c['entrada']} sai={c['saida']}")
        quadros = ler_quadros(c["arquivo"], ini, D, float(c["foco_x"])); ult = None
        ultq = n - 1 if i < len(cenas) - 1 else max(0, n - 1 - fade_q)    # ultima cena: antes do fade
        marcas = {min(2, n - 1): 0, n // 2: 1, ultq: 2}; ims = [None, None, None]
        for k in range(n):
            fr = next(quadros, None); fr = ult if fr is None else fr; ult = fr
            if fr is None: sys.exit(f"nao consegui ler {c['arquivo']}")
            u = k / FPS
            amostras = [u + (j / (sub - 1) - 0.5) * P["obturador"] / FPS for j in range(sub)]
            zr = [curva(min(max(s, 0), D), D, c) for s in amostras]
            veloc = abs(zr[-1][0] - zr[0][0]) + abs(zr[-1][1] - zr[0][1]) / 30
            if veloc < 0.004:                                   # parado: 1 amostra so
                zr = [curva(u, D, c)]
            acc = np.zeros((OUT_H, OUT_W, 3), np.float32)
            for z, r in zr:
                acc += cv2.warpAffine(fr, matriz(z, r), (OUT_W, OUT_H), flags=cv2.INTER_LINEAR,
                                      borderMode=cv2.BORDER_REFLECT_101)
            img = acc / len(zr)
            if txt is not None and i == 0:
                al = txt[1] * min(1.0, u / 0.12)
                img = img * (1 - al) + txt[0] * al
            g = cortes[i] + k
            if g >= total - fade_q:                             # fade pro preto no final
                img *= max(0.0, (total - 1 - g) / fade_q)
            out = np.clip(img, 0, 255).astype(np.uint8)
            enc.stdin.write(out.tobytes())
            if a.folha and k in marcas: ims[marcas[k]] = cv2.resize(out, (tw, th), interpolation=cv2.INTER_AREA)
        if a.folha:
            ims = [x if x is not None else np.zeros((th, tw, 3), np.uint8) for x in ims]
            nome = os.path.splitext(os.path.basename(c["arquivo"]))[0][:10]
            tiles.append((f"C{i+1} {nome} {cortes[i]/FPS:.2f}s {c['entrada']}>{c['saida']}", ims))
    enc.stdin.close(); enc.wait()

    dur = total / FPS; aud = None; wav = None
    if sem_som:
        aud = None
    elif a.batida_sintetica or (not musica and plano.get("batida_sintetica")):
        wav = a.saida + ".batida.wav"; batida_sintetica(wav, dur, bpm); aud = ["-i", wav]
    elif musica:
        aud = ["-ss", "%.3f" % mus_ini, "-i", musica]
    if aud:
        subprocess.run([FF, "-v", "error", "-y", "-i", tmp] + aud +
                       ["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-af", f"afade=t=out:st={dur - P['fade_final']:.2f}:d={P['fade_final']}",
                        "-t", "%.3f" % dur, "-movflags", "+faststart", a.saida], check=True)
        os.remove(tmp)
        if wav: os.remove(wav)
    else:
        subprocess.run([FF, "-v", "error", "-y", "-i", tmp, "-c", "copy", "-movflags", "+faststart",
                        a.saida], check=True)
        os.remove(tmp)
    if a.folha:
        montar_folha(tiles, a.folha); print("folha de quadros:", a.folha)
    print(f"duracao {dur:.2f}s | {len(cenas)} cenas | {bpm:g} BPM | "
          f"{'sem som' if not aud else ('musica desde %.2fs' % mus_ini if musica and not wav else 'batida de teste')}")
    print("cortes (s):", [round(c / FPS, 3) for c in cortes], "->", a.saida)


if __name__ == "__main__":
    main()
