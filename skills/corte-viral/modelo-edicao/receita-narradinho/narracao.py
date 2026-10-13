# -*- coding: utf-8 -*-
"""Narradinho, passo da NARRAÇÃO: limpa o áudio gravado à parte, tira as frases erradas e emenda uma frase na outra.

Uso:
  python3 narracao.py transcrever <projeto> <arquivo-da-narracao>
      -> narracao/bruta.wav (48 kHz mono), narracao/ia.wav (DeepFilterNet + depof),
         narracao/frases.json (cada frase com "manter": true/false e o motivo) e a lista na tela.
      O Claude confere a lista (e a pessoa confere os nomes de produto). Pra tirar uma frase: "manter": false.
      Pra aproveitar só um pedaço: muda "start"/"end" da frase. Frase com palavra esticada (>0,9 s) = conferir: o Whisper
      esconde repetição assim.
  python3 narracao.py emendar <projeto> [--acelerar 1.08] [--pausa-frase 0.10] [--pausa-interna 0.06]
      -> narracao/voz.wav (emendada, tratada, -14 LUFS) + narracao/transcript.json (palavras com tempo NA VOZ FINAL)
         + narracao/emendas.json (de onde veio cada pedaço).
O corte é pelo SOM (energia), não pela palavra do Whisper (ele dá fim de palavra cedo e come o final).
"""
import json, os, re, subprocess, sys, wave
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import identidade as I

HOP = 0.01   # 10 ms


def run(cmd):
    subprocess.run(cmd, check=True)


def ler_wav(p):
    w = wave.open(p); sr = w.getframerate(); ch = w.getnchannels()
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1: x = x.reshape(-1, ch).mean(1)
    return sr, x


def gravar_wav(p, sr, x):
    y = np.clip(x, -1, 1)
    o = wave.open(p, "wb"); o.setnchannels(1); o.setsampwidth(2); o.setframerate(sr)
    o.writeframes((y * 32767).astype(np.int16).tobytes()); o.close()


def energia(x, sr):
    h = int(sr * HOP); n = len(x) // h
    rms = np.sqrt(np.mean(x[:n * h].reshape(n, h) ** 2, 1))
    rms = np.convolve(rms, [0.5, 0.5], "same")
    db = 20 * np.log10(rms + 1e-9)
    thr = min(max(np.percentile(db, 30) + 12, np.percentile(db, 95) - 40), np.percentile(db, 95) - 15)
    return db, thr


def corrige(t):
    base = re.sub(r"[^\wÀ-ÿ]", "", t).lower()
    if I.TROCAS.get(base):
        t = re.sub(r"[\wÀ-ÿ]+", I.TROCAS[base], t, count=1)
    return t


def whisper(path):
    from faster_whisper import WhisperModel
    m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(path, language="pt", word_timestamps=True, vad_filter=False, beam_size=5,
                           condition_on_previous_text=False, initial_prompt=I.VOCAB or None)
    ws = []
    for s in segs:
        for w in s.words:
            t = w.word.strip()
            if t and t.startswith("-") and ws:      # "Bem -vinda" -> "Bem-vinda"
                ws[-1]["text"] += t; ws[-1]["end"] = round(w.end, 3)
            elif t:
                ws.append({"text": corrige(t), "start": round(w.start, 3), "end": round(w.end, 3)})
    return ws


def norm(t):
    return re.sub(r"[^\wÀ-ÿ]", "", t.lower())


ENCHIMENTO = {"é", "éé", "ééé", "eh", "hum", "hm", "ah", "ahn", "tá", "então", "né", "uhum", "aham", "oi"}


def em_frases(ws):
    """Quebra as palavras em frases: ponto final/interrogação/exclamação ou silêncio > 0,6 s."""
    fr, cur = [], []
    for i, w in enumerate(ws):
        if cur and w["start"] - cur[-1]["end"] > 0.6:
            fr.append(cur); cur = []
        cur.append(w)
        if w["text"][-1:] in ".?!":
            fr.append(cur); cur = []
    if cur: fr.append(cur)
    return fr


def parece_retomada(a, b):
    """True se a frase b recomeça a frase a (a pessoa errou e repetiu): fica a última."""
    na, nb = [norm(w["text"]) for w in a], [norm(w["text"]) for w in b]
    na, nb = [x for x in na if x], [x for x in nb if x]
    if not na or not nb: return False
    k = min(3, len(na), len(nb))
    if na[:k] == nb[:k]: return True
    # a ficou pela metade e b começa igual (2 primeiras palavras iguais e a é curta)
    return len(na) <= 6 and na[:2] == nb[:2]


def transcrever(proj, audio):
    N = os.path.join(proj, "narracao"); os.makedirs(N, exist_ok=True)
    bruta, ia = os.path.join(N, "bruta.wav"), os.path.join(N, "ia.wav")
    run([I.FFMPEG, "-v", "error", "-y", "-i", audio, "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", bruta])
    df_dir = os.path.join(N, "df"); os.makedirs(df_dir, exist_ok=True)
    df_out = os.path.join(df_dir, "bruta.wav")
    if I.DEEPFILTER and os.path.exists(I.DEEPFILTER):
        subprocess.run([I.DEEPFILTER, "-D", "--pf", "-o", df_dir, bruta], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(df_out):
        print("AVISO: sem DeepFilterNet; segue sem a limpeza por IA"); df_out = bruta
    if os.path.exists(I.DEPOF):
        subprocess.run([sys.executable, I.DEPOF, df_out, ia], check=True, stdout=subprocess.DEVNULL)
    else:
        run([I.FFMPEG, "-v", "error", "-y", "-i", df_out, "-af", "highpass=f=80", ia])
    ws = whisper(ia)
    fr = em_frases(ws)
    F = []
    for i, f in enumerate(fr):
        txt = " ".join(w["text"] for w in f)
        so_enchimento = all(norm(w["text"]) in ENCHIMENTO for w in f)
        esticadas = [w["text"] for w in f if w["end"] - w["start"] > 0.9]
        F.append({"i": i, "start": f[0]["start"], "end": f[-1]["end"], "text": txt, "manter": not so_enchimento,
                  "motivo": "só enchimento (éé, hum)" if so_enchimento else "", "conferir": esticadas})
    # tentativas refeitas: fica a ÚLTIMA (olha a seguinte e a de depois, pra pular um "éé" no meio)
    vivas = [f for f in F if f["manter"]]
    for a, b in zip(vivas, vivas[1:]):
        if parece_retomada(fr[a["i"]], fr[b["i"]]):
            a["manter"] = False; a["motivo"] = f"refeita na frase {b['i']}"
    json.dump(F, open(os.path.join(N, "frases.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(ws, open(os.path.join(N, "palavras-brutas.json"), "w"), ensure_ascii=False, indent=0)
    print(f"narração bruta: {len(ws)} palavras, {len(F)} frases ({sum(f['manter'] for f in F)} ficam)\n")
    for f in F:
        marca = "  " if f["manter"] else "XX"
        extra = (f"   [tirar: {f['motivo']}]" if not f["manter"] else "") + (f"   [conferir: {', '.join(f['conferir'])} esticada]" if f["conferir"] else "")
        print(f"{marca} {f['i']:>2}  {f['start']:6.2f}-{f['end']:6.2f}  {f['text']}{extra}")
    print(f"\n-> confira e ajuste {os.path.join(N, 'frases.json')} antes de emendar")


def emendar(proj, acelerar=1.0, pausa_frase=0.10, pausa_interna=0.06):
    N = os.path.join(proj, "narracao")
    sr, x = ler_wav(os.path.join(N, "ia.wav"))
    db, thr = energia(x, sr)
    F = sorted(json.load(open(os.path.join(N, "frases.json"))), key=lambda f: f["start"])
    it = lambda t: max(0, min(len(db) - 1, int(round(t / HOP))))
    tm = lambda i: i * HOP
    voz = db > thr
    pecas = []   # (inicio, fim, tipo) em segundos do áudio limpo
    for k, f in enumerate(F):
        if not f["manter"]: continue
        ant_fim = F[k - 1]["end"] if k > 0 else 0.0
        prox_ini = F[k + 1]["start"] if k + 1 < len(F) else len(x) / sr
        # começo: primeira voz a partir de start-0,25 (sem entrar na frase anterior)
        i = it(max(f["start"] - 0.25, ant_fim)); lim = it(f["start"] + 0.35)
        while i < lim and not voz[i]: i += 1
        s = tm(i) - 0.04 if i < lim else f["start"] - 0.03
        if pecas: s = max(s, pecas[-1][1])          # nunca repetir som do pedaço anterior
        # fim: segue a voz depois do fim do Whisper (aceita buraco < 0,08 s), até +0,35 s, sem entrar na próxima
        j = it(f["end"] - 0.1); lim = it(min(f["end"] + 0.35, prox_ini)); ult = j
        while j < lim:
            if voz[j]: ult = j
            elif j - ult > 8: break
            j += 1
        e = tm(ult) + 0.06
        # pausas internas viram emenda: só se for silêncio de verdade (mediana abaixo do limiar - 3 dB) e > 0,14 s
        if e - s < 0.08: continue
        cur, i = s, it(s + 0.06)
        while i < it(e - 0.06):
            if not voz[i]:
                j = i
                while j < it(e) and not voz[j]: j += 1
                if tm(j - i) > 0.14 and np.median(db[i:j]) < thr - 3:
                    pecas.append((cur, tm(i) + pausa_interna / 2, "interna"))
                    cur = tm(j) - pausa_interna / 2
                i = j
            else:
                i += 1
        pecas.append((cur, e, "frase"))
    # junta: entre frases a folga das pontas já dá ~0,10 s; acerta pro valor pedido
    out, mapa, t = [], [], 0.0
    fade = int(0.006 * sr)
    for a, b, tipo in pecas:
        seg = x[int(a * sr):int(b * sr)].copy()
        if len(seg) < 2 * fade: continue
        seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
        out.append(seg); mapa.append({"de": round(a, 3), "ate": round(b, 3), "na_voz": round(t, 3), "tipo": tipo})
        t += len(seg) / sr
        if tipo == "frase" and pausa_frase > 0.10:
            out.append(np.zeros(int((pausa_frase - 0.10) * sr), np.float32)); t += pausa_frase - 0.10
    y = np.concatenate(out)
    emendada = os.path.join(N, "emendada.wav"); gravar_wav(emendada, sr, y)
    json.dump(mapa, open(os.path.join(N, "emendas.json"), "w"), indent=0)
    af = (f"atempo={acelerar:.3f}," if abs(acelerar - 1) > 0.005 else "")
    run([I.FFMPEG, "-v", "error", "-y", "-i", emendada, "-filter_complex", f"[0:a]{af}{I.TRATAR}[o]", "-map", "[o]",
         "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le", os.path.join(N, "voz.wav")])
    ws = whisper(os.path.join(N, "voz.wav"))
    json.dump(ws, open(os.path.join(N, "transcript.json"), "w"), ensure_ascii=False, indent=1)
    dur = len(ler_wav(os.path.join(N, "voz.wav"))[1]) / 48000
    gaps = [b["start"] - a["end"] for a, b in zip(ws, ws[1:])]
    ppm = len(ws) / max(1e-6, (ws[-1]["end"] - ws[0]["start"])) * 60 if ws else 0
    print(f"voz final: {dur:.2f} s, {len(pecas)} pedaços, {len(ws)} palavras, {ppm:.0f} palavras/min, "
          f"maior pausa entre palavras {max(gaps) if gaps else 0:.2f} s (limiar {thr:.0f} dB)")
    print(" ".join(f"[{w['start']:.1f}]{w['text']}" if i % 8 == 0 else w["text"] for i, w in enumerate(ws)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "transcrever":
        transcrever(a[1], a[2])
    elif len(a) >= 2 and a[0] == "emendar":
        op = {"--acelerar": 1.0, "--pausa-frase": 0.10, "--pausa-interna": 0.06}
        for k in op:
            if k in a: op[k] = float(a[a.index(k) + 1])
        emendar(a[1], op["--acelerar"], op["--pausa-frase"], op["--pausa-interna"])
    else:
        print(__doc__)
