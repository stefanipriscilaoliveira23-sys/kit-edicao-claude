#!/usr/bin/env python3
# Folha de quadros com a zona proibida do Reels pintada de vermelho por cima (1080x1920).
# Conferir ANTES do render final: nada de texto, cartão ou legenda dentro do vermelho.
#
#   vermelho: topo 220 px (cabeçalho do Instagram), baixo a partir de y=1470 (nome, legenda, áudio),
#             35 px de cada lado, coluna direita de 100 px a partir de y=1155 (curtir, comentar, enviar)
#   linha amarela tracejada em y=330: título/capa tem que começar abaixo dela (a grade do perfil corta 3:4)
#
# Uso:
#   python3 zona_segura.py video.mp4                 -> 12 quadros espalhados
#   python3 zona_segura.py video.mp4 1.2 3.5 8.0     -> só esses instantes (ex.: onde entra cada título/cartão)
#   python3 zona_segura.py video.mp4 --n 20
# Saída: <pasta do vídeo>/zona-segura.jpg
#
# No HyperFrames dá pra ligar a mesma grade na prévia colando ZONA_HTML dentro do root (e tirar antes do render).
import os, subprocess, sys, tempfile

ZONAS = [(0, 0, 1080, 220), (0, 1470, 1080, 1920), (0, 0, 35, 1920), (1045, 0, 1080, 1920), (980, 1155, 1080, 1920)]
LINHA_GRADE = 330

ZONA_HTML = ''.join(
    f'<div class="zona-guia" style="position:absolute;left:{x0}px;top:{y0}px;width:{x1 - x0}px;height:{y1 - y0}px;'
    f'background:rgba(255,0,0,.28);z-index:9999;pointer-events:none"></div>' for x0, y0, x1, y1 in ZONAS
) + (f'<div class="zona-guia" style="position:absolute;left:0;top:{LINHA_GRADE}px;width:1080px;'
     f'border-top:4px dashed #ffd400;z-index:9999"></div>')


def filtro():
    caixas = ','.join(f'drawbox=x={x0}:y={y0}:w={x1 - x0}:h={y1 - y0}:color=red@0.32:t=fill' for x0, y0, x1, y1 in ZONAS)
    tracos = ','.join(f'drawbox=x={x}:y={LINHA_GRADE - 3}:w=40:h=6:color=0xffd400:t=fill' for x in range(0, 1080, 70))
    return f'scale=1080:1920,{caixas},{tracos}'


def dur(v):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v],
                                capture_output=True, text=True).stdout)


if __name__ == '__main__':
    a = sys.argv[1:]
    v = a[0]
    n = 12
    if '--n' in a:
        k = a.index('--n')
        n = int(a[k + 1])
        a = a[:k] + a[k + 2:]
    ts = [float(x) for x in a[1:]]
    if not ts:
        d = dur(v)
        ts = [d * (k + 0.5) / n for k in range(n)]
    tmp = tempfile.mkdtemp()
    qs = []
    for i, t in enumerate(ts):
        q = os.path.join(tmp, f'{i}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', v, '-frames:v', '1', '-vf',
                        filtro() + f",scale=216:384,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='{t:.1f}s':x=8:y=8:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.5",
                        q], check=True)
        qs.append(q)
    por = 6
    linhas = []
    for k in range(0, len(qs), por):
        g = qs[k:k + por]
        out = os.path.join(tmp, f'l{k}.png')
        junta = f'hstack={len(g)}' if len(g) > 1 else 'null'
        largura = (por if len(qs) > por else len(g)) * 216
        subprocess.run(['ffmpeg', '-v', 'error', '-y', *sum([['-i', p] for p in g], []), '-filter_complex',
                        f'{junta},pad={largura}:ih:0:0:color=0x1f1517', out], check=True)
        linhas.append(out)
    folha = os.path.join(os.path.dirname(os.path.abspath(v)), 'zona-segura.jpg')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *sum([['-i', p] for p in linhas], []), '-filter_complex',
                    f'vstack={len(linhas)}' if len(linhas) > 1 else 'null', '-q:v', '3', folha], check=True)
    print(f'{len(ts)} quadros em {folha}')
