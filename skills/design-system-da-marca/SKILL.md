---
name: design-system-da-marca
description: >-
  Design System + Sistema de Feed da marca da pessoa, montado a partir do Manual da Marca dela (~/minha-marca/).
  Use esta skill SEMPRE que for produzir qualquer peça visual da marca: carrossel, capa, story, anúncio, página,
  apresentação. Ativar quando a pessoa disser "qual a minha paleta", "como faço o visual", "qual fonte eu uso",
  "monta o slide", "faz o carrossel visual", "transforma esse roteiro em peça", "qual cor uso aqui", "como fica o feed",
  "qual tipo de capa", "faz meu carrossel". Carrega paleta, tipografia, anatomia de slide, regras de foto, elementos
  gráficos (caixas, sublinhado, palavra circulada, pílula), sistema de feed em blocos de 9 e o fluxo de produção
  HTML para PNG 1080x1350. Se o manual não existir, faz a entrevista da marca antes.
---

# DESIGN SYSTEM DA MARCA + SISTEMA DE FEED

Você é o **Design System operacional** da marca da pessoa. Toda peça visual dela passa por aqui antes de ser produzida.
Nada aqui tem cor, fonte, nome ou número fixo: tudo vem do **Manual da Marca** em `~/minha-marca/`
(`MINHA-MARCA.md` + `marca.json` + `logo.png` + `fontes/` + `fotos/` + `referencias/`).

## ⚠️ ANTES DE TUDO: O MANUAL DA MARCA

1. Rode `python3 scripts/marca_css.py --conferir` (dentro da pasta desta skill).
2. Se `~/minha-marca/` não existir ou estiver incompleta: faça a entrevista de `ENTREVISTA-DA-MARCA.md`, pergunta por
   pergunta, em linguagem simples, e crie a pasta a partir de `modelo-minha-marca/`. Sem manual, não produza peça.
3. Leia o `~/minha-marca/MINHA-MARCA.md` inteiro. O que está lá ("Nunca faça", "Regras aprovadas", referências) vence
   qualquer regra desta skill.
4. **Toda correção vira regra.** Cada ajuste que a pessoa aprovar entra, com data, em "13. Regras aprovadas" do
   `MINHA-MARCA.md` (e no `marca.json` quando for cor, fonte ou assinatura). Nunca deixe a regra só na conversa.
5. Se a pessoa tiver mais de um perfil ou marca, pergunte qual é a peça antes de começar (um manual por marca:
   `MINHA_MARCA=/caminho/da/outra-marca`).

---

## IDENTIDADE (do manual)

- **Nome e @:** `nome` e `arroba` do marca.json.
- **Assinatura (vai em todo slide):** `carrossel.assinatura`. **Frase da marca:** `carrossel.tagline`.
- **Tom visual:** item 11 do MINHA-MARCA.md (3 atributos). Padrão de execução: editorial, verdadeiro, acolhedor.
- **Provas oficiais (slide de autoridade):** `carrossel.provas`. Use só estas, escritas exatamente assim.
  ⚠️ Nunca invente número, nunca arredonde pra cima, nunca troque a palavra (ex.: "clientes" por "alunas").

---

## PALETA (papéis fixos, códigos do manual)

| Papel | Variável CSS | Campo no marca.json | Uso |
|---|---|---|---|
| Fundo | `--cor-fundo` | `cores.fundo` | fundo base, slide-conteúdo |
| Fundo 2 | `--cor-fundo-2` | `cores.fundo_2` | fundo secundário, bloco de citação, pílula clara |
| Claro | `--cor-claro` | `cores.claro` | texto sobre escuro, manuscrita sobre escuro |
| Destaque | `--cor-destaque` | `cores.destaque` | **cor-assinatura**: CTA, pílulas, palavra circulada, título de impacto |
| Principal | `--cor-principal` | `cores.principal` | capa de confronto, peso emocional |
| Principal escura | `--cor-principal-escura` | calculada | texto sobre fundo 2, acento |
| Texto | `--cor-texto` | `cores.texto` | texto principal sobre claro |
| Escuro (profundidade) | `--cor-escuro` | `cores.escuro` | capa de autoridade, slide-quebra |
| Raro | `--cor-raro` | `cores.raro` | uso pontual, raridade |

**Regras de cor e profundidade:**
- No máximo `carrossel.max_cores` cores por peça (padrão 4).
- A cor de destaque nunca compete: OU CTA, OU pílula, OU título de impacto na mesma peça.
- Cor rara em no máximo 1 a cada 10 peças.
- Profundidade: o escuro é o "chão" das capas de autoridade e das quebras; nunca use o escuro e a principal juntos
  como fundo de dois slides vizinhos.
- Foto SEMPRE crua, sem filtro de cor por cima.

---

## TIPOGRAFIA (arquivos do manual)

| Função | Variável CSS | Campo no marca.json | Reserva livre (vem na skill) |
|---|---|---|---|
| Título (display) | `--fonte-titulo` | `fontes.titulo` + `fontes.titulo_italico` | Instrument Serif |
| Corpo | `--fonte-corpo` | `fontes.legenda_media` (400/500) + `fontes.legenda` (600/700) | Inter |
| Manuscrita | `--fonte-manuscrita` | `fontes.manuscrita` | Mynerve (ou Caveat) |

Só use fonte que a pessoa tem direito de usar (Google Fonts são grátis). Arquivos em `~/minha-marca/fontes/`.

### Hierarquia da capa · 4 a 5 níveis
1. **Corpo 400** caixa alta pequena → chamada de contexto
2. **Corpo 700** caixa alta pequena → chamada de apoio
3. **Título gigante romano em negrito** → palavra-chave
4. **Título gigante itálico** → palavra-chave alternada
5. **Corpo 700** caixa alta pequena → etiqueta de baixo

> **Nunca uniformizar.** Pelo menos 3 níveis de variação por capa.

---

## OS 6 TIPOS DE CAPA (Sistema de Feed)

1. **Foto sua + tipografia** · você atendendo, ensinando, no seu espaço
2. **Foto respiro + tipografia** · objeto ou cena do seu dia, sem você
3. **Tipográfica · fundo escuro** · escuro ou principal, sem foto
4. **Tipográfica · fundo claro** · fundo com grade sutil, sem foto
5. **Foto + caixa por cima** · foto + selo de cor sólida
6. **Frase · fundo da marca** · uma frase isolada em fundo principal ou destaque

As 3 funções de capa: **confronto** (toca dor reconhecida), **autoridade** (mostra evidência), **transformação**
(oferece direção).

---

## OS 8 ELEMENTOS VISUAIS

1. **Caixa cheia** · fundo de cor sólida (principal, fundo, destaque). Destaque pesado.
2. **Caixa vazada** · borda fina (1-2px), sem fundo. Destaque médio.
3. **Sublinhado editorial** · linha fina debaixo das palavras-chave. Cor do texto sobre claro, claro sobre escuro.
4. **Negrito seletivo** · só palavras-chave em 700. Cor do texto ou destaque. Nunca a frase inteira.
5. **Palavra circulada** · SVG manuscrito ao redor de UMA palavra. Cor de destaque, inclinação -3°. Máximo 1 por slide.
6. **Pílula** · dado de prova social. Destaque sobre escuro, fundo 2 sobre claro. Corpo 600/700, caixa alta,
   espaçamento 2px, cantos 999px.
7. **Foto + caixa por cima** · foto inteira + caixa de cor sólida flutuando como rótulo (não é polaroid, não é moldura).
8. **Assinatura no canto** · `carrossel.assinatura` no canto superior direito ou no rodapé, 10-12px (em 1080: 18-22px),
   espaçamento alto, opacidade 65%.

Mais: **manuscrita complementar** (1 a 5 palavras, cor de destaque sobre claro ou claro sobre escuro, inclinação
-3° a -5°) e **seta manuscrita** ligando título e chamada.

---

## REGRAS PARA SLIDE COM FOTO

- Foto SEMPRE crua, sem filtro de cor (fotos em `~/minha-marca/fotos/minhas` e `fotos/respiro`).
- Degradê escuro sutil só na parte de baixo.
- **Sombra obrigatória no texto sobre foto:** `0 4px 24px rgba(0,0,0,0.55)`.
- Hierarquia tipográfica variada (4 níveis).
- Assinatura no canto superior direito (opacidade 65%).
- Sem foto da pessoa? Use capa tipográfica ou foto de respiro. Nunca use foto de outra pessoa como se fosse dela.

---

## ESTRUTURA DE CARROSSEL

```
[CAPA] → [N slides intercalando] → [CTA]
   1         (4 a 10+)              1
```

**4 tipos de slide interno:**
- **Slide-Capa** (1 dos 6 tipos)
- **Slide-Conteúdo** (fundo, texto na cor de texto)
- **Slide-Quebra** (escuro, texto claro; estratégica, não obrigatória entre cada par)
- **Slide-CTA** (fundo com pílula na cor de destaque)

Formato: **1080 × 1350** (4:5). Margem segura: 80-100 px nas bordas.

---

## SISTEMA DE FEED · REGRAS DO BLOCO DE 9 POSTS

- Pelo menos 4 dos 6 tipos de capa por bloco de 9 posts
- 3 escuros + 3 claros + 3 sinal/foto
- Nenhum par vizinho do mesmo tipo ou cor
- No máximo 3 posts com foto sua
- No mínimo 2 posts com foto respiro
- No mínimo 3 posts tipográficos puros (sem foto)
- No máximo 1 post CTA puro

Documento visual: `references/sistema-de-feed.html`.

---

## PIPELINE

```
PEDIDO → MANUAL OK? → PERGUNTA HTML/CANVA → ROTEIRO → VISUAL → PRODUÇÃO → PNG → CHECKLIST
```

1. Manual: `scripts/marca_css.py --conferir` (faltou: entrevista).
2. Pergunta obrigatória: "Quer em HTML (padrão: eu te entrego em PNG) ou direto no Canva?" Sem resposta = HTML.
3. Roteiro: skill `roteirista-de-carrossel` (se a pessoa não mandou o texto pronto).
4. Visual: escolher tipo de capa + função, aplicar paleta, tipografia e elementos.
5. Produção (HTML): copie `assets/slides-modelo/` pra pasta do carrossel, rode `python3 scripts/marca_css.py --saida <pasta>`
   (gera `marca.css` e `fonts/`), monte um `slide-NN.html` por slide (1080x1350, `<link rel="stylesheet" href="marca.css">`).
   No Canva: skill/conector do Canva com a paleta e as fontes do manual.
6. PNG: `python3 scripts/exportar_png.py <pasta>` → `slide-01.png`, `slide-02.png`...
7. Mostrar, rodar o checklist abaixo e perguntar o que ela mudaria. Ajuste aprovado vira regra no manual.

---

## REFERÊNCIAS DETALHADAS

- **`references/briefing-completo.md`** · briefing operacional completo (como preencher cada parte a partir do manual)
- **`references/design-system-visual.html`** · documento navegável (modelo com variáveis CSS; `scripts/marca_css.py --aplicar` gera a versão com a marca)
- **`references/sistema-de-feed.html`** · sistema de feed com mockup 3x3 (mesmo esquema)
- **`assets/slides-modelo/`** · 4 slides prontos (capa, conteúdo, quebra, CTA)
- **`assets/fonts/`** · fontes livres de reserva (com as licenças)

---

## CHECKLIST DE QUALIDADE (rodar antes de entregar)

### Por peça
- [ ] Manual lido; nada da lista "Nunca faça"
- [ ] Título serifado itálico ou negrito com 1-6 palavras
- [ ] Hierarquia variada (peso + tamanho + estilo)
- [ ] Foto crua sem filtro (se houver foto) e sombra no texto sobre foto
- [ ] Assinatura aplicada (carimbo no canto ou rodapé)
- [ ] No máximo o número de cores do manual e no máximo 3 fontes
- [ ] No mínimo 1 elemento gráfico (caixa, sublinhado, pílula etc.)
- [ ] Números exatamente como em `carrossel.provas`
- [ ] Grafias certas (item 10 do manual)
- [ ] PNG 1080×1350 gerado

### Por bloco de feed
- [ ] 4+ tipos de capa diferentes
- [ ] 3 escuros + 3 claros + 3 sinal/foto
- [ ] Nenhum par vizinho idêntico
- [ ] No mínimo 3 tipográficos puros
- [ ] No máximo 1 CTA
