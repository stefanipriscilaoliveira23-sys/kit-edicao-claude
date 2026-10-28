---
name: checklist
description: "Efeito de vídeo /checklist: lista de tarefas do Claude embaixo do queixo, cada passo gira e fica verde. Use quando a aluna digitar /checklist com um vídeo."
---

# /checklist

**O que faz:** lista de tarefas do Claude embaixo do queixo, cada passo gira e fica verde.
**Onde combina:** Claude fazendo uma tarefa por etapas.
**Opções:** `text=passo::detalhe|...`, `title`.

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py checklist <video> --start S --end E chave=valor ...
```
