---
name: pilha-de-reels
description: "Efeito de vídeo /pilha-de-reels: reels empilhando atrás da cabeça, um a cada quarto de segundo. Use quando a aluna digitar /pilha-de-reels com um vídeo."
---

# /pilha-de-reels

**O que faz:** reels empilhando atrás da cabeça, um a cada quarto de segundo.
**Onde combina:** "todo dia sai um vídeo", volume de conteúdo.
**Opções:** `images=<pasta com capas ou vídeos dela>` (sem pasta usa quadros do próprio vídeo), `size` (0.34).

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py pilha-de-reels <video> --start S --end E chave=valor ...
```
