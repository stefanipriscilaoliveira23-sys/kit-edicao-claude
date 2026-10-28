---
name: letreiro
description: "Efeito de vídeo /letreiro: luz cai e um letreiro de LED se escreve atrás. Use quando a aluna digitar /letreiro com um vídeo."
---

# /letreiro

**O que faz:** luz cai e um letreiro de LED se escreve atrás.
**Onde combina:** nome de evento/produto, frase curta.
**Opções:** `text=linha 1|linha 2` (palavras do LED), `color`, `push`.

Seguir o passo a passo de `~/.claude/skills/effects/COMO-USAR-COMANDOS.md` (vídeo, trecho, textos em português, conferir, renderizar, entregar).
Comando direto:

```
~/.claude/skills/effects/.venv/bin/python ~/.claude/skills/effects/scripts/aplicar.py letreiro <video> --start S --end E chave=valor ...
```
