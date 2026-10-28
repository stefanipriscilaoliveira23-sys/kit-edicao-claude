#!/usr/bin/env python3
# Luz e cor (catálogo L1–L3), aplicadas no vídeo base com ffmpeg, antes das camadas do HyperFrames.
#   L1 sala escura, pessoa acesa: o fundo perde luz e cor, a pessoa (máscara) fica clara e natural + vinheta.
#   L2 abertura em foco: o quadro entra borrado e claro e foca em 0,45 s (no começo e/ou em viradas de seção).
#   L3 varredura de luz: uma faixa de luz suave atravessa o quadro na diagonal em 0,8 s (abre seção, 1 por seção).
# Pele: a pessoa nunca escurece nem fica mais saturada (pele avermelha). Sem grão de filme (vira ruído no rosto).
#
# Uso:
#   python3 luz_e_cor.py base.mp4 saida.mp4 --mascara mask.mp4 --sala            (L1)
#   python3 luz_e_cor.py base.mp4 saida.mp4 --foco 0,12.4                        (L2 nos instantes dados)
#   python3 luz_e_cor.py base.mp4 saida.mp4 --varredura 12.4                     (L3)
#   dá pra juntar tudo numa chamada. --forca 0.5..1.5 regula o quanto a sala escurece (padrão 1).
# O áudio passa intacto.
import subprocess, sys


def dur(v):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', v],
                                capture_output=True, text=True).stdout)


def montar(entrada, saida, mascara=None, sala=False, foco=(), varredura=(), forca=1.0):
    ins = ['-i', entrada]
    f = []
    atual = '[0:v]'
    f.append(f'{atual}scale=1080:1920,setsar=1,format=gbrp[v0]')
    atual = '[v0]'
    if sala:
        if not mascara:
            sys.exit('--sala precisa de --mascara mask.mp4 (mascara-pessoa)')
        ins += ['-i', mascara]
        b = -0.09 * forca
        f.append(f'{atual}split[fa][pa]')
        f.append(f'[fa]eq=contrast={1 + 0.10 * forca:.3f}:saturation={1 - 0.16 * forca:.3f}:brightness={b:.3f},'
                 f'colorbalance=bs=0.03:bm=0.02:rs=-0.02[fundo]')
        f.append('[pa]eq=contrast=1.04:saturation=0.97:brightness=0.01[pessoa]')
        f.append('[1:v]scale=1080:1920,format=gray,gblur=sigma=2.5,format=gbrp[m]')
        f.append('[fundo][pessoa][m]maskedmerge,vignette=angle=PI/4.6[v1]')
        atual = '[v1]'
    f.append(f'{atual}format=yuv420p[vb]')
    atual = '[vb]'
    for k, t in enumerate(foco):
        f.append(f'{atual}split[a{k}][b{k}]')
        f.append(f'[b{k}]gblur=sigma=26,eq=brightness=0.14,format=yuva420p,'
                 f'fade=t=out:st={t:.3f}:d=0.45:alpha=1,trim=start={max(t - 0.05, 0):.3f}:end={t + 0.5:.3f},'
                 f'setpts=PTS-STARTPTS+{max(t - 0.05, 0):.3f}/TB[fb{k}]')
        f.append(f'[a{k}][fb{k}]overlay=eof_action=pass:enable=\'between(t,{t:.3f},{t + 0.46:.3f})\'[vf{k}]')
        atual = f'[vf{k}]'
    d = dur(entrada)
    for k, t in enumerate(varredura):
        # faixa diagonal suave (calculada em 270x480 e ampliada), branca a 38% no máximo
        f.append(f"color=c=black:s=270x480:r=30:d={d:.3f},format=gray,"
                 f"geq=lum='255*exp(-pow((X+Y*0.45-((T-{t:.3f})/0.8)*560+60)/22\\,2))',"
                 f"scale=1080:1920,gblur=sigma=6[lm{k}]")
        f.append(f'color=c=white:s=1080x1920:r=30:d={d:.3f},format=yuva420p[lw{k}]')
        f.append(f'[lw{k}][lm{k}]alphamerge,colorchannelmixer=aa=0.38[lz{k}]')
        f.append(f"{atual}[lz{k}]overlay=enable='between(t,{t:.3f},{t + 0.8:.3f})'[vl{k}]")
        atual = f'[vl{k}]'
    cmd = ['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(f), '-map', atual, '-map', '0:a?',
           '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'copy', saida]
    subprocess.run(cmd, check=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit('uso: luz_e_cor.py base.mp4 saida.mp4 [--mascara mask.mp4 --sala] [--foco 0,12.4] [--varredura 12.4] [--forca 1]')

    def val(k, padrao=None):
        return a[a.index(k) + 1] if k in a else padrao

    tempos = lambda s: [float(x) for x in s.split(',') if x] if s else []
    montar(a[0], a[1], mascara=val('--mascara'), sala='--sala' in a, foco=tempos(val('--foco')),
           varredura=tempos(val('--varredura')), forca=float(val('--forca', 1)))
    print(a[1])
