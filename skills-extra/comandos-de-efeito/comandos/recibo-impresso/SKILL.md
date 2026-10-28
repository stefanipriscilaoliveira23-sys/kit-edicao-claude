---
name: recibo-impresso
description: "Efeito de vídeo /recibo-impresso: instruções saindo impressas como recibo na parede. Use quando a aluna digitar /recibo-impresso com um vídeo."
---

# /recibo-impresso

**O que faz:** instruções saindo impressas como recibo na parede.
**Onde combina:** passo a passo.
**Opções:** `text=01 ESCOLHA O PROCEDIMENTO|02 DEFINA O PREÇO|...` (linhas com |).

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py recibo-impresso <video> --start S --end E chave=valor ...
```
