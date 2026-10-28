---
name: figurinha
description: "Efeito de vídeo /figurinha: congela e você vira figurinha recortada com borda branca e etiqueta de nome. Use quando a aluna digitar /figurinha com um vídeo."
---

# /figurinha

**O que faz:** congela e você vira figurinha recortada com borda branca e etiqueta de nome.
**Onde combina:** apresentação, "eu sou a...".
**Opções:** `text=<primeiro nome>` (padrão: nome do manual), `sub=<cargo, ex. LASH DESIGNER>`, `fundo=escuro|cor`, `color`, `angle`, `scale`.

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py figurinha <video> --start S --end E chave=valor ...
```
