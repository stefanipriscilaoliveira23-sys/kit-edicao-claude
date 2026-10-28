---
name: tier-list
description: "Efeito de vídeo /tier-list: ranking S a D cai na tela e o item voa pro S. Use quando a aluna digitar /tier-list com um vídeo."
---

# /tier-list

**O que faz:** ranking S a D cai na tela e o item voa pro S.
**Onde combina:** comparação, "o que mais vende".
**Opções:** `title=<o que está sendo ranqueado>`, `item=<o que voa pro S>`, `others=B|C|D` (nomes com |).

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py tier-list <video> --start S --end E chave=valor ...
```
