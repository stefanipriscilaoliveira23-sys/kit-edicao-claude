#!/usr/bin/env python3
# Melhor tentativa de cada frase: quando ela grava a mesma frase várias vezes (não para a gravação, só repete),
# agrupa as repetições e fica com a ÚLTIMA tentativa completa de cada uma (regra: a última boa é a que fica).
# Mostra a tabela pra conferir e grava o plano de corte.
#
# Uso:
#   python3 melhor_tentativa.py transcript.json [outro.json ...]
#       transcript = lista de palavras [{"text","start","end"}] (formato do modelo; 1 por clipe)
#   python3 melhor_tentativa.py video.MOV [outro.MOV ...]
#       transcreve antes (faster-whisper large-v3-turbo local, venv do corte-viral) e salva <video>.palavras.json
#   --pausa 0.6    pausa (s) que separa uma frase da outra
#   --parecido 0.6 quão parecida a frase tem que ser pra contar como repetição (0 a 1)
# Saída: tentativas.md (tabela) e tentativas.json (trechos escolhidos, em ordem: arquivo, início, fim, texto)
import difflib, json, os, re, subprocess, sys, unicodedata

_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = next((p for p in (os.path.join(_RAIZ, '.venv', 'bin', 'python'),
                         os.path.join(_RAIZ, '.venv', 'Scripts', 'python.exe')) if os.path.exists(p)), sys.executable)
VICIOS = {'é', 'éé', 'ééé', 'hum', 'ahn', 'tipo', 'né', 'pera', 'calma', 'volta', 'de', 'novo'}
TRANSCREVER = '''
import json, sys
from faster_whisper import WhisperModel
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
seg, _ = m.transcribe(sys.argv[1], language="pt", word_timestamps=True, vad_filter=True)
json.dump([{"text": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)} for s in seg for w in s.words],
          open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
'''


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9 ]', '', s)


def palavras(arq):
    if arq.lower().endswith('.json'):
        return json.load(open(arq, encoding='utf-8')), arq
    saida = os.path.splitext(arq)[0] + '.palavras.json'
    if not os.path.exists(saida):
        print(f'transcrevendo {os.path.basename(arq)}...', flush=True)
        subprocess.run([VENV, '-c', TRANSCREVER, arq, saida], check=True)
    return json.load(open(saida, encoding='utf-8')), arq


def frases(ws, pausa):
    out, cur = [], []
    for w in ws:
        if cur and (w['start'] - cur[-1]['end'] > pausa or re.search(r'[.!?]$', cur[-1]['text'])):
            out.append(cur)
            cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return [{'ini': f[0]['start'], 'fim': f[-1]['end'], 'texto': ' '.join(w['text'] for w in f),
             'n': norm(' '.join(w['text'] for w in f))} for f in out]


def parecido(a, b):
    if not a or not b:
        return 0
    pa, pb = a.split(), b.split()
    # tentativa interrompida ou refeita: as 4 primeiras palavras iguais
    if len(pa) >= 4 and len(pb) >= 4 and pa[:4] == pb[:4]:
        return 1
    # mesma ideia com outras palavras: quase todas as palavras de conteúdo da menor estão na maior
    ca, cb = {w for w in pa if len(w) > 3}, {w for w in pb if len(w) > 3}
    menor = min(ca, cb, key=len)
    if len(menor) >= 3 and len(ca & cb) / len(menor) >= 0.7:
        return 1
    return difflib.SequenceMatcher(None, pa, pb).ratio()


def agrupar(fs, limiar):
    grupos = []
    for f in fs:
        # repetição costuma vir logo em seguida: compara com os 3 últimos grupos
        alvo = None
        for g in grupos[-3:]:
            if max(parecido(f['n'], x['n']) for x in g) >= limiar:
                alvo = g
        if alvo is not None and alvo is grupos[-1]:
            alvo.append(f)
        elif alvo is not None:
            # repetiu uma frase de antes, depois de outra: a nova tentativa vira a versão daquela frase
            alvo.append(f)
        else:
            grupos.append([f])
    return grupos


def escolher(g):
    maior = max(len(f['n'].split()) for f in g)
    boas = [f for f in g if len(f['n'].split()) >= 0.85 * maior and not (set(f['n'].split()) & {'pera', 'calma', 'volta'})]
    return (boas or g)[-1]


if __name__ == '__main__':
    a = sys.argv[1:]
    opt = {}
    for k in ('--pausa', '--parecido'):
        if k in a:
            i = a.index(k)
            opt[k] = float(a[i + 1])
            a = a[:i] + a[i + 2:]
    pausa, limiar = opt.get('--pausa', 0.6), opt.get('--parecido', 0.6)
    todas = []
    for arq in a:
        ws, nome = palavras(arq)
        for f in frases(ws, pausa):
            f['arquivo'] = nome
            todas.append(f)
    grupos = agrupar(todas, limiar)
    plano, linhas = [], ['| # | Frase escolhida | Tentativas | Ficou com | Arquivo e tempo |', '|---|---|---|---|---|']
    for i, g in enumerate(grupos, 1):
        e = escolher(g)
        so = [f for f in g if f is not e]
        if len(e['n'].split()) <= 1 and set(e['n'].split()) <= VICIOS:
            continue
        plano.append({'arquivo': e['arquivo'], 'inicio': round(max(e['ini'] - 0.06, 0), 3), 'fim': round(e['fim'] + 0.08, 3), 'texto': e['texto']})
        linhas.append(f"| {i} | {e['texto']} | {len(g)} | {'última boa' if len(g) > 1 else 'única'} "
                      f"| {os.path.basename(e['arquivo'])} {e['ini']:.1f}–{e['fim']:.1f}s |")
        for f in so:
            linhas.append(f"|  | ~~{f['texto']}~~ |  | descartada | {os.path.basename(f['arquivo'])} {f['ini']:.1f}s |")
    pasta = os.path.dirname(os.path.abspath(a[0]))
    open(os.path.join(pasta, 'tentativas.md'), 'w', encoding='utf-8').write('\n'.join(linhas) + '\n')
    json.dump(plano, open(os.path.join(pasta, 'tentativas.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rep = sum(1 for g in grupos if len(g) > 1)
    print('\n'.join(linhas))
    print(f'\n{len(plano)} frases no roteiro; {rep} tinham repetição. Plano em {pasta}/tentativas.json')
