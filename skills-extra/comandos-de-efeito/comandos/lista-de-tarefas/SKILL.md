---
name: lista-de-tarefas
description: "Efeito de vídeo /lista-de-tarefas: cartão de tarefas ao lado da cabeça se marcando. Use quando a aluna digitar /lista-de-tarefas com um vídeo."
---

# /lista-de-tarefas

**O que faz:** cartão de tarefas ao lado da cabeça se marcando.
**Onde combina:** lista falada, cada item marcando na hora que ela fala.
**Opções:** `text=item 1|item 2|item 3`, `ticks=<segundo de cada item com |>`, `title`.

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py lista-de-tarefas <video> --start S --end E chave=valor ...
```
