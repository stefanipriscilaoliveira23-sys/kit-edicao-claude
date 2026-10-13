# HyperFrames e media-use · como instalar

O **HyperFrames** (da HeyGen, código aberto, licença Apache 2.0) é o que transforma HTML em vídeo: é ele que "desenha"
o título, a legenda e os efeitos por cima do seu vídeo. O **media-use** vem junto com ele e traz os sons de efeito
(pacote Pixabay, uso livre) e ferramentas de áudio.

Antes: precisa do **Node 22** e do **ffmpeg** instalados (o `INSTALAR.md` da corte-viral explica, Mac e Windows).

## Jeito oficial (recomendado): plugin do Claude Code

Dentro do Claude Code, digite um comando por vez:

```text
/plugin marketplace add heygen-com/hyperframes
/plugin install hyperframes@hyperframes
```

Ou no terminal:

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
claude plugin details hyperframes
```

Depois abra uma conversa nova (ou digite `/reload-plugins`) e teste:

```text
Usando /hyperframes:hyperframes, faz um título de 5 segundos escrito "Olá, mundo".
```

A lista do plugin deve mostrar `hyperframes`, `general-video` e `media-use`.

**Atualização automática:** digite `/plugin`, abra **Marketplaces**, escolha **hyperframes** e ligue
**Enable auto-update**. Pra atualizar na mão: `claude plugin update hyperframes@hyperframes`.

Ou simplesmente peça: "Claude, instala o plugin do HyperFrames seguindo o COMO-INSTALAR.md".

## Jeito alternativo 1: skills soltas pelo npx

```bash
npx hyperframes skills update
```
Instala o conjunto principal de skills direto do repositório oficial (github.com/heygen-com/hyperframes).

## Jeito alternativo 2: copiar as pastas (sem internet pro plugin)

A pasta `skills/` ao lado deste arquivo tem uma cópia das skills `hyperframes`, `hyperframes-animation`,
`hyperframes-audio`, `hyperframes-cli`, `hyperframes-core`, `hyperframes-creative`, `hyperframes-keyframes`,
`hyperframes-registry`, `hyperframes-studio` e `media-use`, iguais às do repositório oficial.

Copie cada uma delas para a pasta de skills do Claude:
- Mac: `~/.claude/skills/`
- Windows: `C:\Users\SEU-NOME\.claude\skills\`

Use só UM jeito (plugin OU cópia), pra não ter duas versões das mesmas skills.

## O render da edição dos Reels

A skill **corte-viral** renderiza com uma cópia FIXA do HyperFrames (`hyperframes@0.8.107`) dentro da pasta de trabalho,
instalada pelo `modelo-edicao/preparar_pasta.py`. Ela é separada do plugin de propósito: o `npx` se atualiza sozinho no
meio de um render e quebra renders em paralelo.

## Licenças

- HyperFrames: Apache 2.0 (`LICENSE-HyperFrames-Apache-2.0.txt`).
- Sons do media-use: licença Pixabay, uso comercial liberado sem crédito (`CREDITOS-SONS-Pixabay.md`).
