# -*- coding: utf-8 -*-
"""Narradinho, passo da MONTAGEM LIMPA (portão 1): cada cena entra em cima do trecho da fala que fala dela.

Uso: python3 montar.py <projeto> [plano.json]
Lê narracao/voz.wav + narracao/transcript.json + quadros/cenas.json + plano.json (o Claude escreve depois de olhar as folhas).
Gera montagem/video.mp4 (só imagem), montagem/limpa.mp4 (imagem + narração, SEM legenda e SEM música),
montagem/linha.json (a linha do tempo, usada pela edição completa), montagem/tabela.md (cena x trecho da fala)
e montagem/folha-cortes.jpg (o primeiro quadro de cada troca, com o número da cena e o segundo).

plano.json (modelo em exemplo-plano.json):
  {"trocas": [
     {"cena": "00", "em": 0},                          <- a primeira sempre em 0 (abertura)
     {"cena": "01", "palavra": "Vocês"},               <- entra NA palavra (1ª vez depois da troca anterior; "vez": 2 pra 2ª)
     {"cena": "02", "n": 23, "in": 1.5},               <- ou pelo número da palavra no transcript.json; "in" = segundo da cena onde começa
     {"cena": "03", "em": 9.4, "vel": 1.5}             <- ou no segundo exato; "vel" 1.5 = cena acelerada (padrão 1, velocidade normal)
   ],
   "resultado": [{"cena": "09", "dur": 2.0}, {"cena": "10", "dur": 4.5, "in": 0.5}],   <- depois da narração, só música
   "luz": true}                                        <- luz leve do jeito da marca (false = cor original)
Regras: cena entre 1 e 5 s (avisa fora disso); se a cena gravada for menor que o trecho, puxa o começo pra trás, depois
deixa em câmera lenta leve (até 0,7x) e, se nem assim der, avisa pra dividir o trecho em duas cenas. Som original sai sempre.
"""
import json, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import identidade as I
from cenas import folha

FPS = 30


def fr(t):
    return round(round(t * FPS) / FPS, 4)


def norm(t):
    return re.sub(r"[^\wÀ-ÿ]", "", t.lower())


def dur_wav(p):
    r = subprocess.run([I.FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    return float(r.stdout.strip())


def resolve_trocas(plano, ws):
    """Tempo de cada troca na voz final. Palavra: entra 0,03 s antes do começo dela (o corte cai NA palavra)."""
    out, t_ant = [], -1.0
    for k, tr in enumerate(plano["trocas"]):
        if "em" in tr:
            t = float(tr["em"])
        elif "n" in tr:
            t = ws[int(tr["n"])]["start"] - 0.03
        elif "palavra" in tr:
            alvo = [norm(x) for x in tr["palavra"].split()]
            vez, achou = int(tr.get("vez", 1)), None
            for i in range(len(ws)):
                if ws[i]["start"] <= t_ant + 0.05: continue
                if [norm(w["text"]) for w in ws[i:i + len(alvo)]] == alvo:
                    vez -= 1
                    if vez == 0: achou = i; break
            if achou is None:
                sys.exit(f"ERRO: palavra '{tr['palavra']}' (troca {k}, cena {tr['cena']}) não achada depois de {t_ant:.2f} s")
            t = ws[achou]["start"] - 0.03
        else:
            sys.exit(f"ERRO: troca {k} sem 'em', 'n' ou 'palavra'")
        if k == 0: t = 0.0
        t = fr(max(0.0, t))
        if t <= t_ant: sys.exit(f"ERRO: troca {k} (cena {tr['cena']}) em {t:.2f} s não vem depois da anterior ({t_ant:.2f} s)")
        out.append(dict(tr, t=t)); t_ant = t
    return out


def peca(arq, foto, dur_src, t_in, dur, vel, luz, saida, avisos, rot):
    """Corta 1 pedaço: vertical 1080x1920 preenchendo a tela, 30 q/s, sem som, exatamente round(dur*30) quadros."""
    nq = max(1, int(round(dur * FPS)))
    vf = []
    if foto:
        cmd = [I.FFMPEG, "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-i", arq]
    else:
        precisa = dur * vel
        if t_in is None:   # padrão: o meio da cena
            t_in = max(0.2, (dur_src - precisa) / 2) if dur_src > precisa + 0.4 else max(0.0, dur_src - precisa - 0.05)
        if t_in + precisa > dur_src - 0.04:
            t_in = max(0.0, dur_src - precisa - 0.04)
        if precisa > dur_src - 0.04:
            nova = (dur_src - 0.08) / dur
            if nova >= 0.7:
                avisos.append(f"{rot}: cena tem {dur_src:.1f} s e o trecho {dur:.1f} s -> câmera lenta leve ({nova:.2f}x)")
                vel = nova
            else:
                avisos.append(f"{rot}: cena tem {dur_src:.1f} s e o trecho {dur:.1f} s -> CONGELA no fim. Melhor dividir o trecho em 2 cenas")
                vf.append(f"tpad=stop_mode=clone:stop_duration={dur:.2f}")
        cmd = [I.FFMPEG, "-v", "error", "-y", "-ss", f"{t_in:.3f}", "-i", arq]
        if abs(vel - 1) > 0.01:
            vf.insert(0, f"setpts=(PTS-STARTPTS)/{vel:.4f}")
    if foto:   # foto: aproximação bem lenta (1,00 -> 1,05) pra não parecer vídeo travado
        vf += ["scale=2160:3840:force_original_aspect_ratio=increase", "crop=2160:3840",
               f"zoompan=z='1+0.05*on/{nq}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps={FPS}", "setsar=1"]
    else:
        vf += [f"fps={FPS}", "scale=1080:1920:force_original_aspect_ratio=increase", "crop=1080:1920", "setsar=1"]
    if luz: vf.append(I.LUZ)
    vf.append("format=yuv420p")
    cmd += ["-an", "-vf", ",".join(vf), "-frames:v", str(nq), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
            "-r", str(FPS), "-video_track_timescale", "30000", saida]
    subprocess.run(cmd, check=True)
    return t_in, vel


def main(proj, plano_arq=None):
    plano = json.load(open(plano_arq or os.path.join(proj, "plano.json")))
    ws = json.load(open(os.path.join(proj, "narracao", "transcript.json")))
    voz = os.path.join(proj, "narracao", "voz.wav")
    cenas = {c["cena"]: c for c in json.load(open(os.path.join(proj, "quadros", "cenas.json")))}
    luz = plano.get("luz", True)
    fim_voz = fr(min(dur_wav(voz), ws[-1]["end"] + 0.15)) if ws else fr(dur_wav(voz))
    trocas = resolve_trocas(plano, ws)
    linha = []
    for k, tr in enumerate(trocas):
        t1 = trocas[k + 1]["t"] if k + 1 < len(trocas) else fim_voz
        linha.append({"cena": f"{int(tr['cena']):02d}", "t0": tr["t"], "t1": fr(t1), "in": tr.get("in"), "vel": tr.get("vel", 1.0), "resultado": False})
    t = fim_voz
    for r in plano.get("resultado", []):
        linha.append({"cena": f"{int(r['cena']):02d}", "t0": fr(t), "t1": fr(t + r["dur"]), "in": r.get("in"), "vel": r.get("vel", 1.0), "resultado": True})
        t += r["dur"]
    DUR = fr(t)
    M = os.path.join(proj, "montagem"); P = os.path.join(M, "pecas"); os.makedirs(P, exist_ok=True)
    avisos, lista = [], []
    for k, L in enumerate(linha):
        c = cenas.get(L["cena"])
        if not c: sys.exit(f"ERRO: cena {L['cena']} não está em cenas/ (rode cenas.py)")
        dur = L["t1"] - L["t0"]
        rot = f"pedaço {k} (cena {L['cena']}, {L['t0']:.2f}-{L['t1']:.2f})"
        if not L["resultado"] and dur > 5.05: avisos.append(f"{rot}: {dur:.1f} s parada (passa de 5 s): dividir ou trocar na palavra seguinte")
        if not L["resultado"] and dur < 0.95 and k > 0: avisos.append(f"{rot}: só {dur:.2f} s (pisca): conferir se é de propósito")
        saida = os.path.join(P, f"p{k:03d}.mp4")
        L["in"], L["vel"] = peca(os.path.join(proj, "cenas", c["arquivo"]), c["foto"], c["dur"], L["in"], dur, L["vel"], luz, saida, avisos, rot)
        L["in"] = round(L["in"], 3) if L["in"] is not None else None
        L["arquivo"] = c["arquivo"]
        lista.append(saida)
    with open(os.path.join(P, "lista.txt"), "w") as f:
        f.write("".join(f"file '{os.path.abspath(p)}'\n" for p in lista))
    video = os.path.join(M, "video.mp4")
    subprocess.run([I.FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(P, "lista.txt"), "-c", "copy", video], check=True)
    subprocess.run([I.FFMPEG, "-v", "error", "-y", "-i", video, "-i", voz, "-filter_complex", f"[1:a]apad,atrim=0:{DUR}[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR}", "-movflags", "+faststart",
                    os.path.join(M, "limpa.mp4")], check=True)
    # tabela cena x trecho da fala
    linhas = ["| Cena | Começa | Dura | O que está sendo falado |", "|---|---|---|---|"]
    for L in linha:
        fala = " ".join(w["text"] for w in ws if L["t0"] - 0.02 <= w["start"] < L["t1"] - 0.02)
        if L["resultado"]: fala = "(resultado, só música)"
        L["fala"] = fala
        linhas.append(f"| {L['cena']} | {L['t0']:.1f} s | {L['t1'] - L['t0']:.1f} s | {fala} |")
    open(os.path.join(M, "tabela.md"), "w").write("\n".join(linhas) + "\n")
    json.dump({"dur": DUR, "fim_voz": fim_voz, "fps": FPS, "pecas": linha}, open(os.path.join(M, "linha.json"), "w"), ensure_ascii=False, indent=1)
    # folha de cortes: primeiro quadro de cada troca
    with tempfile.TemporaryDirectory() as tmp:
        imgs = []
        for k, L in enumerate(linha):
            o = os.path.join(tmp, f"{k}.jpg")
            subprocess.run([I.FFMPEG, "-v", "error", "-y", "-ss", f"{L['t0'] + min(0.15, (L['t1'] - L['t0']) / 2):.3f}", "-i", video,
                            "-frames:v", "1", "-vf", "scale=-2:300", o], check=False)
            imgs.append(o if os.path.exists(o) else None)
        folha(imgs, [f"{L['cena']} · {L['t0']:.1f}s" for L in linha], os.path.join(M, "folha-cortes.jpg"), min(8, len(imgs)), 300)
    durs = [L["t1"] - L["t0"] for L in linha if not L["resultado"]]
    print(f"montagem limpa: {os.path.join(M, 'limpa.mp4')}  ({DUR:.1f} s, {len(linha)} pedaços, cena média {sum(durs) / max(1, len(durs)):.1f} s, narração até {fim_voz:.1f} s)\n")
    print("\n".join(linhas))
    if avisos: print("\nAVISOS:\n  " + "\n  ".join(avisos))


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
