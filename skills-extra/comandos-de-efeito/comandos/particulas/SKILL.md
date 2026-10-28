---
name: particulas
description: "Efeito de vídeo /particulas: celular enchendo de grãos com a porcentagem e virando o reel pronto. Use quando a aluna digitar /particulas com um vídeo."
---

# /particulas

**O que faz:** celular enchendo de grãos com a porcentagem e virando o reel pronto.
**Onde combina:** "o Claude edita sozinho", vídeo pronto.
**Opções:** `text=editando…`, `done=Reel|pronto`, `color=<cor de destaque>`, `cols`.

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py particulas <video> --start S --end E chave=valor ...
```
