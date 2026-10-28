#!/usr/bin/env python3
# Conferência quadro a quadro de cada corte, tirada do vídeo FINAL (a prévia do HyperFrames erra o quadro na emenda).
# Para cada corte: último quadro antes | primeiro quadro depois, lado a lado, numa folha só.
# O "depois" tem que mostrar o plano novo limpo: sem legenda velha, sem a pessoa recortada do plano anterior,
# sem cartão sobrando, sem quadro preto.
#
# Uso:
#   python3 conferir_cortes.py final.mp4                    -> acha os cortes sozinho (mudança de cena)
#   python3 conferir_cortes.py final.mp4 --cortes 3.2,7.9   -> tempos dados (s)
#   python3 conferir_cortes.py final.mp4 --cortes plano.json  (lista de [início, fim] dos trechos, como o plano-video.json;
#                                                              os cortes no final são as somas das durações)
#   --celular  também gera <final>-celular.mp4 (720p crf 27, pra mandar pro celular)
# Saída: <pasta do vídeo>/cortes-conferir.jpg
import json, os, re, subprocess, sys, tempfile


def dur(v):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v],
                                capture_output=True, text=True).stdout)


def fps(v):
    n, d = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                           '-of', 'csv=p=0', v], capture_output=True, text=True).stdout.strip().split('/')
    return float(n) / float(d)


def cortes_auto(v, limiar=0.25):
    r = subprocess.run(['ffmpeg', '-v', 'info', '-i', v, '-vf', f"scale=270:-2,select='gt(scene,{limiar})',showinfo",
                        '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r'pts_time:([\d.]+)', r)]


def cortes_de(arg):
    if os.path.exists(arg):
        trechos = json.load(open(arg, encoding='utf-8'))
        t, out = 0, []
        for a, b in trechos[:-1]:
            t += b - a
            out.append(t)
        return out
    return [float(x) for x in arg.split(',') if x]


def quadro(v, t, saida):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(t, 0):.4f}', '-i', v, '-frames:v', '1',
                    '-vf', 'scale=240:-2', saida], check=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    v = a[0]
    cortes = cortes_de(a[a.index('--cortes') + 1]) if '--cortes' in a else cortes_auto(v)
    cortes = [c for c in cortes if 0.05 < c < dur(v) - 0.05]
    if not cortes:
        sys.exit('nenhum corte encontrado')
    q = 1 / fps(v)
    tmp = tempfile.mkdtemp()
    pares = []
    for i, c in enumerate(cortes):
        antes, depois = os.path.join(tmp, f'{i}a.png'), os.path.join(tmp, f'{i}b.png')
        quadro(v, c - q, antes)
        quadro(v, c + q * 0.5, depois)
        par = os.path.join(tmp, f'{i}.png')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', antes, '-i', depois, '-filter_complex',
                        f"[0][1]hstack,pad=iw+12:ih+40:6:34:color=0x1f1517,"
                        f"drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='{i + 1}  {c:.2f}s':x=10:y=8:fontsize=22:fontcolor=white", par], check=True)
        pares.append(par)
    # folha com até 4 pares por linha
    linhas = []
    for k in range(0, len(pares), 4):
        grupo = pares[k:k + 4]
        out = os.path.join(tmp, f'l{k}.png')
        ins = sum([['-i', p] for p in grupo], [])
        junta = f'hstack={len(grupo)}' if len(grupo) > 1 else 'null'
        largura = 4 * 492 if len(pares) > 4 else len(grupo) * 492   # par = 2x240 + 12 de margem
        subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex',
                        f'{junta},pad={largura}:ih:0:0:color=0x1f1517', out], check=True)
        linhas.append(out)
    folha = os.path.join(os.path.dirname(os.path.abspath(v)), 'cortes-conferir.jpg')
    ins = sum([['-i', p] for p in linhas], [])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', f'vstack={len(linhas)}' if len(linhas) > 1 else 'null',
                    '-q:v', '3', folha], check=True)
    print(f'{len(cortes)} cortes em {folha}: ' + ', '.join(f'{c:.2f}' for c in cortes))
    if '--celular' in a:
        cel = os.path.splitext(v)[0] + '-celular.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-vf', 'scale=720:-2', '-c:v', 'libx264', '-crf', '27',
                        '-preset', 'medium', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', cel], check=True)
        print(f'cópia pro celular: {cel} ({os.path.getsize(cel) / 1e6:.1f} MB)')
