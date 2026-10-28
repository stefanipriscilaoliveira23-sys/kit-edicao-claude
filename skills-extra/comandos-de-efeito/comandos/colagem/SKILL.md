---
name: colagem
description: "Efeito de vídeo /colagem: seus reels caindo como fotos numa mesa, com etiqueta em cada um. Use quando a aluna digitar /colagem com um vídeo."
---

# /colagem

**O que faz:** seus reels caindo como fotos numa mesa, com etiqueta em cada um.
**Onde combina:** "são vários estilos", portfólio.
**Opções:** `images=<pasta com vídeos/capas dela>`, `text=estilo 1|estilo 2|...` (etiqueta de cada carta), `count` (5), `size`, `bg`.

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py colagem <video> --start S --end E chave=valor ...
```
