#!/usr/bin/env python3
"""Aplica UM efeito pelo nome do comando (/tier-list, /vidro...) e devolve o vídeo editado ao lado do original.

uso:  aplicar.py <comando> <video> [--start S --end E] [--still 2.1,3.0] [chave=valor ...]
      sem --start/--end: vídeo de até 6 s leva o efeito inteiro; mais longo, do 0,5 s aos 3,5 s (melhor passar o trecho).
saída: <video>-<comando>.mp4 (ou -2, -3... se já existir); com --still, PNGs de conferência <video>-<comando>-conf_<t>.png
Os comandos ficam em COMANDOS (nome em português -> efeito do fx.py e opções fixas).
"""
import argparse, json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
VENV = os.path.join(os.path.dirname(AQUI), '.venv')
PY = os.path.join(VENV, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(VENV, 'bin', 'python')
COMANDOS = {
    'pilha-de-reels': ('noise', {}), 'leque-numerado': ('lineup', {}), 'mira': ('locked-on', {}), 'orbita': ('orbit', {}),
    'zoom-rapido': ('lean-in', {}), 'palavra-atras': ('backdrop-word', {}), 'holofote': ('spotlight', {}),
    'brilho-dourado': ('spotlight', {'look': 'sparkle'}), 'recibo-impresso': ('the-bill', {}), 'cor-de-cinema': ('moody', {}),
    'antes-depois': ('swipe', {}), 'lista-de-tarefas': ('todo', {}), 'comentario': ('comment-box', {}), 'seguir': ('tap', {}),
    'pausa-seta': ('pause-point', {}), 'desinstalar': ('uninstall', {}), 'vira-reel': ('reel-frame', {}),
    'chuva-de-teclas': ('shortcut-rain', {}), 'carimbo': ('reject-stamp', {}), 'contagem': ('countdown-flip', {}),
    'tunel': ('rabbit-hole', {}), 'capa-de-revista': ('cover-star', {}), 'capa-editorial': ('cover-star', {'look': 'editorial'}),
    'rabiscos': ('scribble', {}), 'widgets-de-vidro': ('glass-widgets', {}), 'colagem-vermelha': ('red-collage', {}),
    'manchete-dividida': ('split-headline', {}), 'sala-lilas': ('pastel-word', {}), 'pilulas': ('check-pills', {}),
    'linha-do-tempo': ('timeline', {}), 'manchete-caixa': ('headline-box', {}), 'parede-de-reels': ('profile-wall', {}),
    'tier-list': ('tier-list', {}), 'imagem-de-apoio': ('broll-split', {}), 'leque-de-celulares': ('phone-fan', {}),
    'pontinhos': ('dot-reveal', {}), 'parede-de-manchetes': ('headline-wall', {}), 'checklist': ('checklist', {}),
    'vidro': ('liquid-glass-graph', {}), 'vidro-bento': ('liquid-glass-graph', {'look': 'bento'}), 'carrossel-3d': ('carousel-spin', {}),
    'trava': ('match-cut', {}), 'ajustes-iphone': ('apple-toggles', {}), 'letreiro': ('led-sign', {}), 'aproximar': ('slow-push', {}),
    'por-cima-do-ombro': ('over-the-shoulder-zoom', {}), 'mensagens': ('messages', {}), 'grade-do-perfil': ('place-in-grid', {}),
    'figurinha': ('figurinha', {}), 'particulas': ('particulas-celular', {}), 'colagem': ('colagem-mesa', {}),
}
try: _m = json.load(open(os.path.expanduser('~/minha-marca/marca.json'), encoding='utf-8'))
except Exception: _m = {}
PADRAO = {k: v for k, v in (('handle', _m.get('arroba')), ('name', _m.get('nome'))) if v}  # @ e nome da aluna


def dur(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                capture_output=True, text=True, check=True).stdout.strip())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('comando'); ap.add_argument('video'); ap.add_argument('opcoes', nargs='*', help='chave=valor')
    ap.add_argument('--start', type=float); ap.add_argument('--end', type=float); ap.add_argument('--still')
    ap.add_argument('--width', default='1080')
    a = ap.parse_args()
    nome = a.comando.lstrip('/').lower()
    if nome not in COMANDOS: sys.exit(f'Comando /{nome} não existe. Comandos: ' + ' '.join('/' + k for k in sorted(COMANDOS)))
    fx, fixas = COMANDOS[nome]
    d = dur(a.video)
    ini = a.start if a.start is not None else (0.0 if d <= 6 else 0.5)
    fim = a.end if a.end is not None else (d if d <= 6 else min(d, ini + 3.0))
    ef = {'fx': fx, 'start': ini, 'end': fim, **PADRAO, **fixas}
    for kv in a.opcoes:
        k, v = kv.split('=', 1); ef[k] = v
    if fx == 'pastel-word' and ef.get('handle') and '·' not in ef['handle']: ef['handle'] += '  ·  '  # o cargo vem colado depois do @
    base = os.path.splitext(a.video)[0]
    plano = f'{base}-{nome}.json'; json.dump({'effects': [ef]}, open(plano, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if a.still:
        saida = f'{base}-{nome}-conf.png'
    else:
        saida, n = f'{base}-{nome}.mp4', 2
        while os.path.exists(saida): saida = f'{base}-{nome}-{n}.mp4'; n += 1
    cmd = [PY, os.path.join(AQUI, 'fx_pt.py'), '--plan', plano, a.video, saida, '--width', a.width]
    if a.still: cmd += ['--still', a.still]
    r = subprocess.run(cmd)
    if r.returncode == 0 and not a.still: print('PRONTO:', saida)
    sys.exit(r.returncode)


if __name__ == '__main__':
    main()
