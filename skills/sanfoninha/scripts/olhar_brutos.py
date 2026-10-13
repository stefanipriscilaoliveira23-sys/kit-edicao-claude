#!/usr/bin/env python3
"""
Olha os brutos numerados (01, 02...) e prepara a escolha do melhor pedacinho de cada um.

  python3 -I olhar_brutos.py PASTA_DOS_BRUTOS PASTA_DE_TRABALHO [--resultados 1] [--janela 0.9]

Gera em PASTA_DE_TRABALHO:
  folhas/visao-geral.jpg  um quadro do meio de cada video, com o numero (confere ordem e assunto)
  folhas/NN.jpg           quadros a cada 0,25 s do video NN, com o segundo escrito em cima e uma
                          barrinha de movimento embaixo (vermelha = mexe muito, cinza = parado)
  brutos.json             lista dos videos com duracao, tamanho e "inicio" sugerido
                          (o Claude olha as folhas e corrige o "inicio" de cada um)

Sugestao automatica: no processo, a janela com mais movimento e nitidez; no resultado
(os ultimos N videos), a janela mais parada e nitida (pose). E so um ponto de partida.
"""
import argparse, json, os, re, shutil, subprocess, sys
import numpy as np
import cv2

TW, TH = 144, 256           # tamanho de cada quadrinho da folha
QPS = 4                      # quadros por segundo analisados (video de ate 12 s)


def achar_ff(nome):
    exe = nome + (".exe" if os.name == "nt" else "")
    for c in [os.path.expanduser(f"~/.local/bin/{exe}"), shutil.which(nome),
              f"/opt/homebrew/bin/{nome}", f"/usr/local/bin/{nome}"]:
        if c and os.path.isfile(c):
            return c
    sys.exit(f"Nao achei o {nome}. Veja o INSTALAR.md da skill sanfoninha.")


FF, FFPROBE = achar_ff("ffmpeg"), achar_ff("ffprobe")


def info(arq):
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "format=duration:stream=width,height:stream_tags=rotate:stream_side_data=rotation",
                        "-of", "json", arq], capture_output=True, text=True)
    j = json.loads(r.stdout or "{}")
    st = (j.get("streams") or [{}])[0]
    w, h = st.get("width", 0), st.get("height", 0)
    rot = 0
    try: rot = int(float((st.get("tags") or {}).get("rotate", 0)))
    except ValueError: pass
    for sd in st.get("side_data_list") or []:
        if "rotation" in sd: rot = int(sd["rotation"])
    if abs(rot) % 180 == 90: w, h = h, w
    return float((j.get("format") or {}).get("duration", 0) or 0), w, h


def quadros(arq, qps):
    cmd = [FF, "-v", "fatal", "-i", arq, "-an", "-vf",
           f"fps={qps},scale={TW}:{TH}:force_original_aspect_ratio=increase,crop={TW}:{TH},setsar=1",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = TW * TH * 3
    return [np.frombuffer(raw[i:i + n], np.uint8).reshape(TH, TW, 3) for i in range(0, len(raw) - n + 1, n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta"); ap.add_argument("trabalho")
    ap.add_argument("--resultados", type=int, default=1, help="quantos dos ultimos videos sao resultado")
    ap.add_argument("--janela", type=float, default=0.9, help="tamanho do pedacinho procurado (s)")
    a = ap.parse_args()

    vids = [f for f in os.listdir(a.pasta) if re.match(r"^\d+.*\.(mp4|mov|m4v|webm|mkv)$", f, re.I)]
    vids.sort(key=lambda f: int(re.match(r"^(\d+)", f).group(1)))
    if not vids: sys.exit("Nenhum video numerado (01.mp4, 02.mov...) nessa pasta.")
    os.makedirs(os.path.join(a.trabalho, "folhas"), exist_ok=True)

    lista, meios = [], []
    for idx, f in enumerate(vids):
        arq = os.path.abspath(os.path.join(a.pasta, f))
        dur, w, h = info(arq)
        qps = QPS if dur <= 12 else max(0.5, 48.0 / dur)     # video longo: menos quadros
        qs = quadros(arq, qps)
        num = re.match(r"^(\d+)", f).group(1)
        resultado = idx >= len(vids) - a.resultados
        if not qs:
            print(f"{f}: nao consegui ler"); continue
        g = [cv2.cvtColor(q, cv2.COLOR_BGR2GRAY).astype(np.float32) for q in qs]
        mov = [0.0] + [float(np.abs(g[i] - g[i - 1]).mean()) for i in range(1, len(g))]
        nit = [float(cv2.Laplacian(x, cv2.CV_32F).var()) for x in g]
        brilho = [float(x.mean()) for x in g]
        mv = np.array(mov); nt = np.array(nit) / (max(nit) + 1e-6)
        mvn = mv / (mv.max() + 1e-6)
        jan = max(1, int(round(a.janela * qps)))
        ini_min = 1 if len(g) > jan + 2 else 0                     # evita o comecinho (mao no botao)
        ini_max = max(ini_min, len(g) - jan - 1)
        melhor, nota_m = ini_min, -1e9
        for s in range(ini_min, ini_max + 1):
            m = mvn[s:s + jan].mean(); n_ = nt[s:s + jan].mean()
            escuro = 0.5 if np.mean(brilho[s:s + jan]) < 25 else 0.0
            nota = (n_ - 0.8 * m if resultado else m + 0.5 * n_) - escuro
            if nota > nota_m: melhor, nota_m = s, nota
        sug = round(melhor / qps, 2)
        orient = "vertical" if h >= w else "DEITADO (vai cortar as laterais)"
        lista.append(dict(numero=num, arquivo=arq, duracao=round(dur, 2), largura=w, altura=h,
                          papel="resultado" if resultado else ("gancho" if idx == 0 else "processo"),
                          inicio_sugerido=sug, inicio=sug, foco_x=0.5))
        print(f"{f}: {dur:.1f}s {w}x{h} {orient}  papel={lista[-1]['papel']}  sugestao: desde {sug:.2f}s")

        # folha do video: quadros a cada 1/qps s, 8 por linha
        cols = 8; pad = 6; lab = 18; bar = 6
        linhas = (len(qs) + cols - 1) // cols
        W = cols * (TW + pad) + pad; H = linhas * (TH + lab + bar + pad) + pad + 30
        folha = np.full((H, W, 3), 250, np.uint8)
        cv2.putText(folha, f"{f}  {dur:.1f}s  sugestao {sug:.2f}s  (barra: movimento)", (pad, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20, 20, 20), 1, cv2.LINE_AA)
        for i, q in enumerate(qs):
            r, c = divmod(i, cols); x = pad + c * (TW + pad); y = 30 + pad + r * (TH + lab + bar + pad)
            cor = (0, 0, 200) if melhor <= i < melhor + jan else (60, 60, 60)
            cv2.putText(folha, f"{i / qps:.2f}", (x, y + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.45, cor, 1, cv2.LINE_AA)
            folha[y + lab:y + lab + TH, x:x + TW] = q
            bw = int(TW * min(1.0, mvn[i]))
            folha[y + lab + TH + 1:y + lab + TH + bar, x:x + bw] = (40, 40, 220) if mvn[i] > 0.5 else (150, 150, 150)
            if melhor <= i < melhor + jan:
                cv2.rectangle(folha, (x - 2, y + lab - 2), (x + TW + 1, y + lab + TH + 1), (0, 0, 220), 2)
        cv2.imwrite(os.path.join(a.trabalho, "folhas", f"{num}.jpg"), folha, [cv2.IMWRITE_JPEG_QUALITY, 82])
        meios.append((f, qs[len(qs) // 2], lista[-1]["papel"]))

    # visao geral: um quadro de cada video
    cols = min(8, len(meios)); pad = 8
    linhas = (len(meios) + cols - 1) // cols
    W = cols * (TW + pad) + pad; H = linhas * (TH + 40 + pad) + pad
    vg = np.full((H, W, 3), 250, np.uint8)
    for i, (f, q, papel) in enumerate(meios):
        r, c = divmod(i, cols); x = pad + c * (TW + pad); y = pad + r * (TH + 40 + pad)
        cv2.putText(vg, f[:16], (x, y + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (20, 20, 20), 1, cv2.LINE_AA)
        cv2.putText(vg, papel, (x, y + 32), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 180), 1, cv2.LINE_AA)
        vg[y + 40:y + 40 + TH, x:x + TW] = q
    cv2.imwrite(os.path.join(a.trabalho, "folhas", "visao-geral.jpg"), vg, [cv2.IMWRITE_JPEG_QUALITY, 85])

    with open(os.path.join(a.trabalho, "brutos.json"), "w", encoding="utf-8") as fh:
        json.dump({"pasta": os.path.abspath(a.pasta), "brutos": lista}, fh, ensure_ascii=False, indent=1)
    print("ok:", os.path.join(a.trabalho, "brutos.json"), "| folhas em", os.path.join(a.trabalho, "folhas"))


if __name__ == "__main__":
    main()
