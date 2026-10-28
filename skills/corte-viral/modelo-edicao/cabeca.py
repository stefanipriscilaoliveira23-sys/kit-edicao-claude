#!/usr/bin/env python3
# Onde está a cabeça a cada instante, lido da máscara da pessoa (mask.mp4 do mascara-pessoa: branco = pessoa).
# Serve pra T11 (palavra atrás da cabeça), órbita (F1) e cartões que não podem cobrir o rosto.
#
# Uso:
#   python3 cabeca.py mask.mp4                      -> cabeca.json ao lado (topo da cabeça, faixa da cabeça, caixa do corpo a cada 0,1 s)
#   python3 cabeca.py mask.mp4 --de 3.2 --ate 4.1 --tamanho 220
#       -> diz o "top" CSS da palavra de 220 px atrás da cabeça nesse trecho
#
# Regra da palavra atrás da cabeça: a cabeça cobre só a base das letras (≈30% da altura do x).
# Com line-height .9: linha de base ≈ top + 0,72*S e altura do x ≈ 0,5*S, então top = topo_cabeça + 0,15*S - 0,72*S.
# Se a cabeça sobe ou desce mais que 0,3*S no trecho (ela inclina pra frente), a palavra vai pra FRENTE, no peito.
# Coordenadas sempre no quadro 1080x1920.
import json, os, subprocess, sys
import numpy as np

W, H = 1080, 1920
ESC = 4            # lê a máscara em 270x480 (rápido e suficiente)
PASSO = 0.1


def ler(mask, passo=PASSO):
    w, h = W // ESC, H // ESC
    p = subprocess.run(['ffmpeg', '-v', 'error', '-i', mask, '-vf', f'fps={1/passo},scale={w}:{h},format=gray',
                        '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    q = np.frombuffer(p, np.uint8).reshape(-1, h, w) > 128
    out = []
    for i, f in enumerate(q):
        lin = f.sum(1)
        ys = np.nonzero(lin > 2)[0]
        if not len(ys):
            out.append({'t': round(i * passo, 2), 'pessoa': False})
            continue
        topo = int(ys[0])
        # faixa da cabeça: linhas logo abaixo do topo (até ~70 px no quadro cheio)
        faixa = f[topo:topo + 18]
        xs = np.nonzero(faixa.any(0))[0]
        corpo_x = np.nonzero(f.any(0))[0]
        out.append({'t': round(i * passo, 2), 'pessoa': True,
                    'topo_cabeca': topo * ESC,
                    'cabeca_x': [int(xs[0]) * ESC, int(xs[-1]) * ESC + ESC],
                    'corpo': [int(corpo_x[0]) * ESC, topo * ESC, int(corpo_x[-1]) * ESC + ESC, int(ys[-1]) * ESC + ESC]})
    return out


def palavra(dados, de, ate, S):
    trecho = [d for d in dados if d['pessoa'] and de - PASSO / 2 <= d['t'] <= ate + PASSO / 2]
    if not trecho:
        return {'erro': 'sem pessoa nesse trecho'}
    topos = [d['topo_cabeca'] for d in trecho]
    alto = min(topos)                     # cabeça no ponto mais alto = o que mais cobre a palavra
    top = round(alto + 0.15 * S - 0.72 * S)
    mexe = max(topos) - alto
    x0 = min(d['cabeca_x'][0] for d in trecho); x1 = max(d['cabeca_x'][1] for d in trecho)
    r = {'top_css': top, 'tamanho': S, 'topo_cabeca': alto, 'cabeca_mexe_px': mexe,
         'cabeca_x': [x0, x1], 'centro_x': (x0 + x1) // 2}
    if mexe > 0.3 * S:
        r['aviso'] = 'cabeça mexe demais nesse trecho: colocar a palavra na FRENTE, no peito (y 950-1300)'
    if top < 220:
        r['aviso_zona'] = 'topo da palavra acima de 220 px (cabeçalho do Instagram): diminuir o tamanho'
    return r


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__ or 'uso: cabeca.py mask.mp4 [--de T --ate T --tamanho S]')
    mask = a[0]
    opt = {a[i][2:]: float(a[i + 1]) for i in range(1, len(a) - 1, 2) if a[i].startswith('--')}
    cache = os.path.splitext(mask)[0].replace('mask', 'cabeca') + '.json'
    if cache == os.path.splitext(mask)[0] + '.json':
        cache = os.path.join(os.path.dirname(mask) or '.', 'cabeca.json')
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(mask):
        dados = json.load(open(cache, encoding='utf-8'))
    else:
        dados = ler(mask)
        json.dump(dados, open(cache, 'w', encoding='utf-8'))
    if 'tamanho' in opt:
        print(json.dumps(palavra(dados, opt.get('de', 0), opt.get('ate', 9e9), opt['tamanho']), ensure_ascii=False, indent=1))
    else:
        com = [d for d in dados if d['pessoa']]
        print(f'{cache}: {len(dados)} amostras, pessoa em {len(com)}; topo da cabeça entre '
              f'{min(d["topo_cabeca"] for d in com)} e {max(d["topo_cabeca"] for d in com)} px')
