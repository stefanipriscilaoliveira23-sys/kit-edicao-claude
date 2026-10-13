---
name: conteudo-amarelinho
description: Formato fixo de carrossel "Conteúdo amarelinho" (apelido "amarelinho"): letra grande cor creme #FFF4C9, em negrito com espaçamento -60, por cima de foto do dia a dia escurecida com granulado, com cara de story/post nativo (low-fi). Use SEMPRE que a pessoa pedir "amarelinho", "conteúdo amarelinho", "faz no formato amarelinho", "carrossel amarelinho", "monta no amarelinho" ou mandar uma copy dizendo que é pra esse formato. Gera os PNGs 1080x1350 prontos pra postar.
---

# Conteúdo amarelinho

Formato de carrossel com aparência "low-fi", que parece nativo do Instagram (parece texto de story
digitado por cima de uma foto do celular). Formato inspirado num post público de @nutriclubdigital.

**Atenção (o erro mais comum):** o "amarelinho" #FFF4C9 é a cor da LETRA, não do fundo.
O fundo é uma foto escurecida (tom marrom quente) com granulado de filme.

## Regras do formato (medidas em px, lâmina 1080x1350)

| Item | Regra |
|---|---|
| Tamanho | 1080 x 1350 (4:5) |
| Cor da letra | #FFF4C9 |
| Fonte | SF Pro Display **Bold** (se a pessoa tiver no Mac) ou **Inter** Bold (grátis, Google Fonts). Trechos finos em Regular/Light |
| Espaçamento entre letras | -60 do Canva = `-0.06em` |
| Tamanho da letra | miolo e final: 128 px, entrelinha 0,98. Capa: 134 px, entrelinha 0,91. Muito texto: diminui até no mínimo 84 px |
| Alinhamento | tudo centralizado, na horizontal e na vertical |
| Margens | texto no máximo 800 px de largura (140 px livres de cada lado); área do texto entre y=250 e y=1100 |
| Linhas | tudo minúsculo como se digitasse no celular (maiúscula só em nome próprio ou começo de frase de chamada). Capa: 4 a 6 linhas de até ~15 letras. Miolo: até ~9 linhas |
| Fundo | foto do dia a dia (ambiente, abajur, sofá, cadeira, selfie no espelho), escurecida com película marrom (30% a 75%, automático pelo brilho da foto) + granulado de pontinhos claros. Sem foto: fundo marrom desenhado com "luz de abajur" |
| Faixa fina | em cima (y≈57) e embaixo (y≈1290): NOME • MARCA • ASSUNTO, maiúsculas, 14,5 px, espaçada, creme a 72% |
| Capa | selo de perfil estilo menção do story (foto redonda com anel colorido + @ em negrito + "siga o perfil") em y≈225; emoji 💖 ao lado do selo e ✨ no canto de baixo à direita; fileira de ícones das abas do perfil em y≈1130 |
| Miolo | só texto. Pode misturar negrito com trechos finos `_(assim)_` |
| Última lâmina | chamada em negrito + recado em letra de mão (Playpen Sans 60 px) com seta desenhada à mão saindo do fim da chamada até o recado |
| O que NÃO tem | caixa, botão, faixa colorida, sombra, contorno, foto recortada, numeração de lâmina, "arrasta pro lado" |

O que dá a cara "nativa": foto real do dia a dia sem produção, película escura + granulado (parece print
de story), letra de sistema apertada, emoji, selo de menção e ícones de perfil do próprio Instagram.

### Sobre as fontes
- **SF Pro Display** é a fonte da Apple (a do iPhone). Pode ser usada no seu próprio Mac, mas o arquivo
  NÃO pode ser repassado pra outras pessoas, por isso ela não vem junto. Se quiser usar: baixe no site
  da Apple (developer.apple.com/fonts), instale no Mac (ela vai pra `~/Library/Fonts`) ou coloque os
  arquivos `SF-Pro-Display-Bold.otf` / `SF-Pro-Display-Regular.otf` numa pasta `fontes/` dentro desta skill.
- Sem SF Pro, a skill usa **Inter** (grátis, Google Fonts), que é a mais parecida. Fica quase igual.
- Letra de mão da última lâmina: **Playpen Sans** (Google Fonts, também tem no Canva).
- No Canva: SF Pro Display (subindo o arquivo) ou Inter, negrito, espaçamento -60, cor #FFF4C9.
- As fontes do Google são carregadas pela internet na hora de gerar (precisa estar conectada).

## O que pedir antes de fazer

1. **A copy pronta, lâmina por lâmina.** Não inventar nem reescrever a copy: só distribuir nas
   lâminas e quebrar as linhas. Se vier só o tema, perguntar:
   "Me manda a copy de cada lâmina (capa, miolo e final) que eu monto no amarelinho."
   Se a copy vier num bloco só, propor a divisão por lâmina e confirmar antes de gerar.
2. **Fotos de fundo** (opcional): uma por lâmina ou uma pra todas. Foto comum do celular serve
   (ambiente da casa, abajur, cadeira, selfie no espelho). Pode ser .heic do iPhone. Sem foto, usa o
   fundo marrom desenhado.
3. **Faixa fina** (nome • marca • assunto) e **@ do selo da capa** (+ foto de perfil, opcional).
   Perguntar uma vez e reaproveitar nas próximas.
4. O tema (vira o nome da pasta).

## Como fazer (fluxo)

1. Montar o arquivo `copy.json` (modelo em `exemplo-copy.json` desta pasta) e salvar em
   `~/Carrosseis-Claude/amarelinho-<tema>/copy.json`.
2. **Gerar só a capa e a lâmina 2 pra aprovar:**
   ```bash
   python3 ~/.claude/skills/conteudo-amarelinho/gerar.py ~/Carrosseis-Claude/amarelinho-<tema>/copy.json --so 1,2
   ```
   (no Windows, use `python` e o caminho da pasta da skill)
3. Abrir os PNGs (ferramenta Read) e conferir: nenhuma linha quebrada no meio, letra não ficou pequena
   demais (se ficou, a lâmina tem texto demais: sugerir dividir em duas), selo e emojis não encostam no
   texto. Mostrar e esperar o "ok".
4. Com o ok, gerar o resto (sem `--so`). Conferir todas de novo e entregar o caminho da pasta.

Leva uns 20 a 40 segundos. Precisa do **Google Chrome** instalado (ele gera as imagens sem abrir janela).
Saída: `~/Carrosseis-Claude/amarelinho-<tema>/lamina-01.png`, `lamina-02.png`...

## Formato do copy.json

```json
{
  "tema": "agenda da semana",
  "fonte": "auto",
  "assinatura": "NOME • MARCA • ASSUNTO",
  "perfil": { "arroba": "seu.arroba", "linha2": "siga o perfil", "foto": "/caminho/foto-perfil.jpg" },
  "laminas": [
    { "tipo": "capa",  "texto": "linha 1\nlinha 2\nlinha 3", "fundo": "/caminho/foto1.jpg", "emojis": ["💖", "✨"] },
    { "tipo": "miolo", "texto": "título:\nlinha em negrito\n_(explicação fina)_", "fundo": "" },
    { "tipo": "final", "texto": "chamada final", "nota": "Ah, e comenta “palavra”\nque eu te mando...", "fundo": "" }
  ]
}
```

- `\n` = quebra de linha. Quando a copy tem quebras, cada linha cabe inteira (a letra diminui se precisar).
- `_texto_` = trecho fino (peso leve). O resto é negrito.
- `fonte`: `"auto"` (SF Pro se estiver instalada, senão Inter), `"sf"` ou `"inter"`.
- Opcionais por lâmina: `"tamanho": 120` (força o tamanho da letra), `"veu": 0.6` (escurece mais/menos
  a foto, 0 a 0.75), `"emojis": []` (tira os emojis), `"selo": false`, `"abas": false`, `"seta": false`.
- `"assinatura": ""` tira a faixa fina. Sem `perfil.arroba`, a capa sai sem selo.

## Ajustes rápidos

| Pedido | O que mudar |
|---|---|
| letra maior/menor numa lâmina | `"tamanho"` na lâmina |
| fundo mais escuro/claro | `"veu"` na lâmina |
| outra cor de letra | `--cor-texto` no `:root` do `modelo.html` (padrão #FFF4C9) |
| menos granulado | `--granulado` no `modelo.html` (padrão .55) |
| espaçamento diferente | `--espacamento` (padrão -0.06em = -60) |

## Arquivos desta skill

- `modelo.html`: o desenho da lâmina (variáveis CSS no topo: cor, fonte, espaçamento, tamanho, margens).
- `gerar.py`: transforma o copy.json em PNGs 1080x1350 (precisa do Google Chrome; a biblioteca PIL é
  opcional, só pra escurecer a foto automaticamente).
- `exemplo-copy.json`: exemplo neutro (agenda da semana). Teste com:
  `python3 ~/.claude/skills/conteudo-amarelinho/gerar.py ~/.claude/skills/conteudo-amarelinho/exemplo-copy.json`
