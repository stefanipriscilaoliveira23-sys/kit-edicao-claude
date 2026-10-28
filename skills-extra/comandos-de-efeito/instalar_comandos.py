#!/usr/bin/env python3
"""Instala os comandos de efeito (/tier-list, /vidro, /figurinha...) por cima da skill /effects da Vibha.

uso: python3 instalar_comandos.py      (de novo depois de cada "atualiza meu kit")
- gera ~/.claude/skills/effects/scripts/fx_pt.py: o fx.py da Vibha com os textos em português (o fx.py dela fica intacto, então o git pull continua funcionando)
- copia fx_private.py (3 efeitos do kit), aplicar.py e COMO-USAR-COMANDOS.md pra skill /effects
- copia cada comando de comandos/ pra ~/.claude/skills/<comando>/ (pasta com o mesmo nome que não seja de comando vai pro backup antes)
"""
import datetime, json, os, shutil, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SK = os.path.expanduser('~/.claude/skills')
E = os.path.join(SK, 'effects')
if not os.path.isfile(os.path.join(E, 'scripts', 'fx.py')):
    sys.exit('FALTA a skill /effects da Vibha em ~/.claude/skills/effects (INSTALAR.md, etapa 3.5).')

try: marca = json.load(open(os.path.expanduser('~/minha-marca/marca.json'), encoding='utf-8'))
except Exception: marca = {}
arroba = marca.get('arroba') or '@seu.perfil'; nome = marca.get('nome') or 'Seu Nome'
sys.path.insert(0, AQUI); from traducao_pares import PARES

fx = open(os.path.join(E, 'scripts', 'fx.py'), encoding='utf-8').read(); faltou = 0
for velho, novo in PARES:
    novo = novo.replace('{ARROBA}', arroba).replace('{ARROBA_SEM}', arroba.lstrip('@')).replace('{NOME}', nome)
    if velho in fx: fx = fx.replace(velho, novo)
    else: faltou += 1
open(os.path.join(E, 'scripts', 'fx_pt.py'), 'w', encoding='utf-8').write(fx)
for f in ('fx_private.py', 'aplicar.py'): shutil.copy2(os.path.join(AQUI, f), os.path.join(E, 'scripts', f))
shutil.copy2(os.path.join(AQUI, 'COMO-USAR-COMANDOS.md'), os.path.join(E, 'COMO-USAR-COMANDOS.md'))

hoje = datetime.date.today().isoformat(); n = 0
for cmd in sorted(os.listdir(os.path.join(AQUI, 'comandos'))):
    dst = os.path.join(SK, cmd)
    if os.path.isdir(dst) and not os.path.exists(os.path.join(dst, '.comando-efeito')):
        bk = os.path.expanduser(f'~/.claude/skills-backup/{cmd}-{hoje}'); os.makedirs(os.path.dirname(bk), exist_ok=True)
        shutil.move(dst, bk); print('backup:', cmd, '->', bk)
    shutil.copytree(os.path.join(AQUI, 'comandos', cmd), dst, dirs_exist_ok=True); n += 1
print(f'OK: {n} comandos instalados; textos traduzidos: {len(PARES) - faltou} de {len(PARES)}'
      + (' (o fx.py da Vibha mudou; o que não bateu fica em inglês)' if faltou else ''))
