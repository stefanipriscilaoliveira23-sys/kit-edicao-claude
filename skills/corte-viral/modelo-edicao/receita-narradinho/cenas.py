# -*- coding: utf-8 -*-
"""Narradinho, passo das CENAS: lista os vídeos numerados de <projeto>/cenas/ e faz a folha de quadros de cada um.

Uso: python3 cenas.py <projeto>
  -> quadros/cenas.json (arquivo, duração, tamanho, se tem som) + quadros/cena-XX.jpg (6 quadros com o segundo)
     + quadros/todas.jpg (1 quadro do meio de cada cena, com o número)
O Claude OLHA essas folhas antes de montar o plano: é assim que ele sabe o que aparece em cada cena e onde está o melhor pedaço.
Nome dos arquivos: começando pelo número da ordem (00 abertura, 01, 02...). "03 primer.mov" vale. Foto (.jpg/.png) também vale.
"""
import json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import identidade as I

VIDEO = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp")
FOTO = (".jpg", ".jpeg", ".png", ".heic", ".webp")


def numero(nome):
    m = re.match(r"\s*(\d+)", nome)
    return int(m.group(1)) if m else None


def listar(proj):
    D = os.path.join(proj, "cenas")
    out = []
    for f in sorted(os.listdir(D)):
        if f.startswith(".") or not f.lower().endswith(VIDEO + FOTO): continue
        n = numero(f)
        if n is None:
            print("AVISO: sem número no começo do nome, fica de fora:", f); continue
        out.append((n, f))
    out.sort()
    return D, out


def sondar(p):
    r = subprocess.run([I.FFPROBE, "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height:stream_side_data=rotation",
                        "-of", "json", p], capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", 0) or 0)
    w, h = v.get("width", 0), v.get("height", 0)
    if abs(rot) in (90, 270): w, h = h, w
    return {"dur": round(float(j.get("format", {}).get("duration", 0) or 0), 3), "largura": w, "altura": h,
            "tem_som": any(s.get("codec_type") == "audio" for s in j.get("streams", []))}


def fonte(tam):
    from PIL import ImageFont
    for p in (I.FONTES.get("legenda"), "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(p, tam)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=tam)
    except Exception:
        return ImageFont.load_default()


def quadro(arq, t, alt, tmp):
    o = os.path.join(tmp, f"q{abs(hash((arq, t)))}.jpg")
    cmd = [I.FFMPEG, "-v", "error", "-y"] + (["-ss", f"{t:.3f}"] if t > 0 else []) + ["-i", arq, "-frames:v", "1", "-vf", f"scale=-2:{alt}", o]
    subprocess.run(cmd, check=False)
    return o if os.path.exists(o) else None


def folha(imgs, rotulos, saida, colunas, alt):
    from PIL import Image, ImageDraw
    ims = [Image.open(p).convert("RGB") if p else Image.new("RGB", (int(alt * 9 / 16), alt), (40, 40, 40)) for p in imgs]
    larg = max(i.width for i in ims)
    linhas = (len(ims) + colunas - 1) // colunas
    F = Image.new("RGB", (colunas * (larg + 6) + 6, linhas * (alt + 6) + 6), (12, 12, 12))
    d = ImageDraw.Draw(F); fn = fonte(max(14, alt // 14))
    for k, (im, r) in enumerate(zip(ims, rotulos)):
        x, y = 6 + (k % colunas) * (larg + 6), 6 + (k // colunas) * (alt + 6)
        F.paste(im, (x + (larg - im.width) // 2, y))
        d.rectangle([x, y, x + larg, y + alt // 9], fill=(0, 0, 0))
        d.text((x + 6, y + 3), r, fill=(255, 255, 255), font=fn)
    F.save(saida, quality=85)


def main(proj):
    D, cenas = listar(proj)
    Q = os.path.join(proj, "quadros"); os.makedirs(Q, exist_ok=True)
    info, meio, rot_meio = [], [], []
    with tempfile.TemporaryDirectory() as tmp:
        for n, f in cenas:
            p = os.path.join(D, f)
            foto = f.lower().endswith(FOTO)
            s = {"dur": 99.0, "largura": 0, "altura": 0, "tem_som": False} if foto else sondar(p)
            s.update({"cena": f"{n:02d}", "arquivo": f, "foto": foto})
            info.append(s)
            if foto:
                ts = [0.0]
            else:
                ts = [round(s["dur"] * k / 6 + 0.05, 2) for k in range(6)]
            imgs = [quadro(p, t, 320, tmp) for t in ts]
            folha(imgs, [f"{n:02d} · {t:.1f}s" for t in ts], os.path.join(Q, f"cena-{n:02d}.jpg"), 6, 320)
            meio.append(quadro(p, 0 if foto else s["dur"] / 2, 300, tmp)); rot_meio.append(f"{n:02d} · {s['dur']:.1f}s" if not foto else f"{n:02d} · foto")
        if meio:
            folha(meio, rot_meio, os.path.join(Q, "todas.jpg"), min(8, len(meio)), 300)
    json.dump(info, open(os.path.join(Q, "cenas.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(info)} cenas em {D}")
    for s in info:
        tam = f"{s['largura']}x{s['altura']}" if not s["foto"] else "foto"
        dur = "-" if s["foto"] else "%.1f s" % s["dur"]
        som = "  (tem som: vai ser tirado)" if s["tem_som"] else ""
        print(f"  {s['cena']}  {s['arquivo']:<28} {dur:>8}  {tam}{som}")
    print(f"folhas: {Q}/todas.jpg e {Q}/cena-XX.jpg")


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    main(sys.argv[1])
