# -*- coding: utf-8 -*-
"""Narradinho, MIXAGEM: narração + música baixinha (abaixo da voz) que SOBE no resultado e some no escuro do fim.

Uso: python3 mixar.py <projeto> [edicao.json]
Lê hf/render.mp4 (imagem), narracao/voz.wav, hf/meta.json e, do edicao.json:
  "musica": "musica.mp3"     (na pasta do projeto; sem isso usa a trilha padrão da marca)
  "musica_inicio": 0          (segundo da música onde começa, pra pular introdução)
  "musica_db": -9             (quanto a música fica ABAIXO da voz durante a narração; a referência fica entre -8 e -10)
  "subida_db": 8              (quanto ela sobe quando a narração acaba e entra o resultado)
  "sfx": [["sparkle", 3.0, -12]]   (opcional: som, segundo, volume em dB; a referência não usa efeito)
Gera <projeto>/<nome-da-pasta>.mp4 e mede no fim quanto a música ficou abaixo da voz.
"""
import json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import identidade as I


def lufs(p, a, b):
    """Volume percebido (LUFS integrado) do trecho a..b."""
    r = subprocess.run([I.FFMPEG, "-nostdin", "-v", "info", "-i", p, "-af", f"atrim={a:.3f}:{b:.3f},ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    vals = [l for l in r.stderr.splitlines() if l.strip().startswith("I:")]
    return float(vals[-1].split()[1]) if vals else float("nan")


def main(proj, cfg_arq=None):
    cfg_arq = cfg_arq or os.path.join(proj, "edicao.json")
    C = json.load(open(cfg_arq)) if os.path.exists(cfg_arq) else {}
    M = json.load(open(os.path.join(proj, "hf", "meta.json")))
    DUR, FV = M["dur"], M["fim_voz"]
    voz = os.path.join(proj, "narracao", "voz.wav")
    mus = C.get("musica")
    mus = os.path.join(proj, mus) if mus and not os.path.isabs(mus) else mus
    if not mus or not os.path.exists(mus):
        mus = I.musica_padrao()
        print("música:", mus or "NENHUMA (sem trilha na marca: o vídeo sai só com a voz)")
    g1 = float(C.get("musica_db", -9)); g2 = g1 + float(C.get("subida_db", 8))
    fe = float(C.get("fim_escuro", 0.8)) + 0.4
    T, R = max(0.0, FV - 0.25), 0.6
    a1, a2 = 10 ** (g1 / 20), 10 ** (g2 / 20)
    env = f"if(lt(t,{T:.3f}),{a1:.5f},if(lt(t,{T + R:.3f}),{a1:.5f}+({a2 - a1:.5f})*(t-{T:.3f})/{R},{a2:.5f}))"
    S = os.path.join(proj, "mixagem"); os.makedirs(S, exist_ok=True)
    args = [I.FFMPEG, "-nostdin", "-v", "error", "-y", "-i", os.path.join(proj, "hf", "render.mp4"), "-i", voz]
    fc = [f"[1:a]aresample=48000,apad,atrim=0:{DUR:.3f}[v]"]
    entradas = ["[v]"]
    if mus:
        args += ["-stream_loop", "-1", "-ss", str(float(C.get("musica_inicio", 0))), "-i", mus]
        musf = (f"[2:a]aresample=48000,atrim=0:{DUR:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-2:LRA=11,aresample=48000,"
                f"volume='{env}':eval=frame,afade=t=in:d=0.3,afade=t=out:st={max(0, DUR - fe):.3f}:d={fe:.3f}")
        fc.append(musf + ",asplit=2[m][mstem]")
        entradas.append("[m]")
    base = 3 if mus else 2
    for k, fx in enumerate(C.get("sfx", [])):
        p = I.som(fx[0])
        if not p: print("AVISO: som não achado:", fx[0]); continue
        args += ["-i", p]; ms = int(float(fx[1]) * 1000)
        fc.append(f"[{base}:a]aresample=48000,volume={float(fx[2]) if len(fx) > 2 else -10}dB,adelay={ms}|{ms}[s{k}]")
        entradas.append(f"[s{k}]"); base += 1
    fc.append("".join(entradas) + f"amix=inputs={len(entradas)}:normalize=0:duration=first,alimiter=limit=0.89[a]")
    nome = os.path.basename(os.path.abspath(proj))
    saida = os.path.join(proj, f"{nome}.mp4")
    mapa = ["-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida]
    if mus:
        mapa += ["-map", "[mstem]", "-c:a", "pcm_s16le", os.path.join(S, "musica.wav")]
    subprocess.run(args + ["-filter_complex", ";".join(fc)] + mapa, check=True)
    # medida em LUFS: música x voz durante a narração e a música no resultado
    if mus:
        mstem = os.path.join(S, "musica.wav")
        lv, lm = lufs(voz, 0, FV), lufs(mstem, 0.5, FV)
        lr = lufs(mstem, FV + 0.7, max(FV + 1.2, DUR - fe))
        print(f"música {lv - lm:.1f} dB abaixo da voz na narração (alvo 8 a 10); no resultado sobe {lr - lm:+.1f} dB")
    print("pronto:", saida)


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
