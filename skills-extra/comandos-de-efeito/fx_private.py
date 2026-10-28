# Efeitos extras do Kit de Edição (gratuitos). O fx_pt.py carrega este arquivo sozinho, com tudo dele em globals().
# Inspirados nos reels de "Claude edita meu vídeo" (/freeze-frame, /particulas, /colagem); código escrito do zero.
# Nome, cargo e cor saem do manual da aluna (~/minha-marca/marca.json).

def _marca():
    try: return json.load(open(os.path.expanduser('~/minha-marca/marca.json'), encoding='utf-8'))
    except Exception: return {}
MARCA = _marca()
DESTAQUE = rgb((MARCA.get('cores') or {}).get('destaque'), (147, 0, 18))  # cor de destaque da aluna
MARFIM = (246, 243, 238)
ALIASES.update({'freeze-frame': 'figurinha', 'sticker': 'figurinha', 'congela': 'figurinha',
                'particulas': 'particulas-celular', 'celular-enchendo': 'particulas-celular',
                'colagem': 'colagem-mesa', 'mesa': 'colagem-mesa'})
CARD_FX = CARD_FX + ('colagem-mesa',)


def meia_tela(c, k, frac=0.5):
    """Desce você pra metade de baixo (rosto em ~71% da altura) e devolve onde termina o painel de cima."""
    alvo = c.H * (frac + (1 - frac) * 0.42)
    if c.fy < alvo: shift(c, (alvo - c.fy) * k)
    return c.H * frac * k


def painel(c, top, frac, lay):
    comp(c, lay, 0, top - c.H * frac)


@effect('figurinha', 'congela a imagem e você vira figurinha recortada com borda branca e etiqueta de nome')
def fx_figurinha(c, e):
    W, H = c.W, c.H
    if 'f' not in e.state:
        img, m = c.img.copy(), c.m.copy(); P = int(W * 0.06); B = max(6, int(W * float(e.o.get('borda', 0.022))))
        mp = cv2.copyMakeBorder((m > 0.5).astype(np.uint8) * 255, P, P, P, P, cv2.BORDER_CONSTANT, value=0)
        mp = cv2.morphologyEx(mp, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (B, B)))
        n_, lab, est, _ = cv2.connectedComponentsWithStats(mp)
        if n_ > 2: mp = np.where(lab == 1 + int(np.argmax(est[1:, cv2.CC_STAT_AREA])), 255, 0).astype(np.uint8)  # só você, sem pedaço de cadeira
        mp = cv2.morphologyEx(mp, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (B, B)))
        dil = cv2.dilate(mp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * B + 1, 2 * B + 1)))
        dil = cv2.GaussianBlur(dil, (0, 0), 1.2).astype(np.float32) / 255
        per = cv2.GaussianBlur(mp, (0, 0), 0.8).astype(np.float32)[..., None] / 255
        rgbp = cv2.copyMakeBorder(img, P, P, P, P, cv2.BORDER_REPLICATE)
        st = np.dstack([rgbp * per + (1 - per), dil])
        e.state['f'] = (img, m, c.fx, c.fy, c.fw, st, P)
    img, m, c.fx, c.fy, c.fw, st, P = e.state['f']
    k = ease_back(c.lt / 0.38); al = fade(c, e, 0.2)
    fundo = e.o.get('fundo', 'escuro')
    if fundo == 'cor': bg = np.ones_like(img) * np.float32(rgb(e.o.get('color'), DESTAQUE)) / 255
    else: bg = cv2.GaussianBlur(img, (0, 0), W / 90) * 0.35
    c.img = img * (1 - al) + bg * al; c.m = np.zeros_like(m)
    s = 1 - (1 - float(e.o.get('scale', 0.84))) * al; ang = float(e.o.get('angle', -3.5)) * clamp(k) * al
    cx, cy = c.fx, H * 0.58
    M = cv2.getRotationMatrix2D((cx + P, cy + P), ang, s * (0.92 + 0.08 * k)); M[0, 2] -= P; M[1, 2] -= P - H * 0.03 * al
    lay = cv2.warpAffine(st, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    sa = cv2.GaussianBlur(lay[..., 3], (0, 0), W / 70)
    sa = np.roll(sa, int(W * 0.018), 0) * 0.55
    c.img = c.img * (1 - sa[..., None])
    a = lay[..., 3:4]; c.img = c.img * (1 - a) + lay[..., :3] * a
    fl = clamp(1 - c.lt / 0.12)
    if fl > 0: c.img = c.img * (1 - fl * 0.8) + fl * 0.8
    nome = e.o.get('text', (MARCA.get('nome') or 'Seu Nome').split()[0]); sub = e.o.get('sub', MARCA.get('cargo', ''))
    def tag():
        t1 = text_img(nome, W * 0.075, 'uib', (20, 20, 22)); t1 = t1.crop(t1.getbbox())
        t2 = tracked(sub or ' ', W * 0.026, 'uib', rgb(e.o.get('color'), DESTAQUE), W * 0.006); t2 = t2.crop(t2.getbbox()) if sub else Image.new('RGBA', (1, 1))
        mx, my, gap = int(W * 0.045), int(W * 0.028), int(W * 0.014)
        w = max(t1.width, t2.width) + 2 * mx; h = t1.height + gap + t2.height + 2 * my
        im = rrect(w, h, W * 0.03, (255, 255, 255, 255))
        im.alpha_composite(t1, ((w - t1.width) // 2, my)); im.alpha_composite(t2, ((w - t2.width) // 2, my + t1.height + gap))
        return shadowed(im, 12, 6, 110)
    tg = cached(e, 'tag', tag); q = pop(c, 0.25, 0.32)
    place(c, tg, cx, min(H * 0.86, c.fy + c.fw * 3.6), 0.6 + 0.4 * q, ang + 2, clamp((c.lt - 0.25) / 0.08) * al)


@effect('particulas-celular', 'metade de cima: um celular enchendo de grãos com a porcentagem, que vira o seu reel pronto')
def fx_particulas_celular(c, e):
    W, H = c.W, c.H; frac = 0.5; k = ease_out(c.lt / 0.35) * clamp((e.d - c.lt) / 0.25)
    col = rgb(e.o.get('color'), DESTAQUE)
    thumb_src = np_thumb(c, 270, 560)
    top = meia_tela(c, k, frac)
    Hp = int(H * frac); lay = Image.new('RGBA', (W, Hp), MARFIM + (255,)); d = ImageDraw.Draw(lay)
    pw = int(W * 0.34); ph = int(pw * 2.05); bz = max(6, pw // 26); px, py = (W - pw) // 2, int(Hp * 0.44 - ph / 2)
    sw, sh = pw - 2 * bz, ph - 2 * bz; sx, sy = px + bz, py + bz
    lay.alpha_composite(shadowed(rrect(pw, ph, pw * 0.16, (16, 16, 18, 255)), 16, 10, 120), (px - 42, py - 42))
    d = ImageDraw.Draw(lay)
    t_fim = 0.3 + e.d * 0.6; p = clamp((c.lt - 0.3) / (t_fim - 0.3)); rv = ease_inout((c.lt - t_fim) / 0.35)
    tela = Image.new('RGBA', (sw, sh), (250, 248, 245, 255)); dt = ImageDraw.Draw(tela)
    cols = int(e.o.get('cols', 20)); cell = sw / cols; rows = int(sh / cell); rr = cell * 0.36
    def gera():
        rnd = random.Random(11)
        return [rnd.random() * 6.28 for _ in range(cols)], [(rnd.randrange(cols), rnd.random(), rnd.uniform(0.9, 1.6)) for _ in range(90)]
    ond, gotas = cached(e, 'g', gera)
    nivel = [min(rows, p * rows * (1 + 0.1 * math.sin(i * 1.7 + ond[i] + c.lt * 2))) for i in range(cols)]
    if rv < 1:
        for i in range(cols):
            for j in range(int(nivel[i])):
                x, y = (i + 0.5) * cell, sh - (j + 0.5) * cell
                dt.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (255,))
        if p < 1:
            for (i, ph0, v) in gotas:
                livre = rows - nivel[i]; f = (c.lt * v * 0.9 + ph0) % 1
                if f * livre < livre - 0.6:
                    x, y = (i + 0.5) * cell, (f * livre + 0.5) * cell
                    dt.ellipse([x - rr * 0.8, y - rr * 0.8, x + rr * 0.8, y + rr * 0.8], fill=col + (200,))
    if rv > 0:
        th = np_thumb_pil(thumb_src, sw, sh); th.putalpha(int(255 * rv)); tela.alpha_composite(th)
    m = Image.new('L', (sw, sh), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, sw - 1, sh - 1], int(pw * 0.13), fill=255)
    tela.putalpha(Image.fromarray(np.minimum(np.asarray(tela.split()[3]), np.asarray(m)))); lay.alpha_composite(tela, (sx, sy))
    d.rounded_rectangle([px + pw * 0.37, sy + ph * 0.018, px + pw * 0.63, sy + ph * 0.042], pw * 0.03, fill=(16, 16, 18, 255))
    ly = py + ph + int(Hp * 0.035); S = int(W * 0.04)
    if c.lt < t_fim:
        t = text_img(f"{e.o.get('text', 'editando…')}  {int(p * 100)}%", S, 'mono', (120, 116, 112))
        lay.alpha_composite(t, ((W - t.width) // 2, ly))
    else:
        q = pop(c, t_fim, 0.3)
        a, b = (e.o.get('done', 'Reel|pronto') + '|').split('|')[:2]
        t1 = text_img(a, S * 1.15, 'uib', (20, 20, 22)); t2 = text_img(b, S * 1.15, 'uib', (255, 255, 255))
        pl = rrect(t2.width + S * 0.3, t2.height * 0.92, S * 0.3, col + (255,)); pl.alpha_composite(t2, (int(S * 0.15), -int(t2.height * 0.03)))
        g = Image.new('RGBA', (t1.width + pl.width, max(t1.height, pl.height)), (0, 0, 0, 0)); g.alpha_composite(t1, (0, 0)); g.alpha_composite(pl, (t1.width, 0))
        g = g.resize((max(1, int(g.width * (0.7 + 0.3 * q))), max(1, int(g.height * (0.7 + 0.3 * q)))), Image.LANCZOS)
        lay.alpha_composite(g, ((W - g.width) // 2, ly))
    painel(c, top, frac, lay)


@effect('colagem-mesa', 'metade de cima: seus reels caindo como fotos numa mesa, com etiqueta em cada um')
def fx_colagem_mesa(c, e):
    W, H = c.W, c.H; frac = float(e.o.get('height', 0.5)); k = ease_out(c.lt / 0.35) * clamp((e.d - c.lt) / 0.25)
    col = rgb(e.o.get('color'), DESTAQUE)
    top = meia_tela(c, k, frac); Hp = int(H * frac)
    def mesa():
        rnd = np.random.default_rng(3).normal(0, 1, (Hp // 3 + 1, W // 3 + 1)).astype(np.float32)
        tex = cv2.resize(cv2.GaussianBlur(rnd, (0, 0), 0.8), (W, Hp))[..., None] * 0.012
        yy, xx = np.mgrid[0:Hp, 0:W].astype(np.float32)
        vin = 1 - 0.10 * (((xx - W / 2) / W) ** 2 + ((yy - Hp / 2) / Hp) ** 2)[..., None]
        base = np.float32(rgb(e.o.get('bg'), (238, 233, 226))) / 255
        return Image.fromarray((np.clip((base + tex) * vin, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    lay = cached(e, 'mesa', mesa).copy()
    rotulos = [s for s in e.o.get('text', '').split('|') if s]
    n = min(int(e.o.get('count', 5)), max(1, len(e.cards)))
    cw = int(W * float(e.o.get('size', 0.3)))
    def cartas():
        out = []
        for i in range(n):
            im = e.cards[i % len(e.cards)]; im = vary(im, i) if e.o.get('images') is None else im
            cd = card(im, cw, 0.06)
            if i < len(rotulos):
                t = text_img(rotulos[i], W * 0.032, 'uib', (255, 255, 255))
                pl = rrect(t.width + W * 0.012, t.height * 0.9, t.height * 0.45, col + (255,)); pl.alpha_composite(t, (int(W * 0.006), -int(t.height * 0.04)))
                cd.alpha_composite(pl, ((cd.width - pl.width) // 2, int(cd.height * 0.8)))
            out.append(cd)
        return out
    cs = cached(e, 'c', cartas)
    def pos():
        rnd = random.Random(int(e.o.get('seed', 4)))
        return [(0.16 + 0.68 * (i + 0.5) / n + rnd.uniform(-0.04, 0.04), 0.5 + rnd.uniform(-0.1, 0.1), rnd.uniform(-13, 13)) for i in range(n)]
    ps = cached(e, 'p', pos); passo = float(e.o.get('step', 0.18))
    for i, (x, y, r) in enumerate(ps):
        t0 = 0.25 + i * passo
        if c.lt < t0: break
        q = ease_out((c.lt - t0) / 0.28); im = cs[i]
        s = 1.5 - 0.5 * q
        im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR).rotate(r + (1 - q) * 18, Image.BICUBIC, expand=True)
        a = clamp((c.lt - t0) / 0.08)
        if a < 1: im2.putalpha(Image.fromarray((np.asarray(im2.split()[3]) * a).astype(np.uint8)))
        lay.alpha_composite(im2, (int(x * W - im2.width / 2), int(y * Hp - im2.height / 2)))
    painel(c, top, frac, lay)
