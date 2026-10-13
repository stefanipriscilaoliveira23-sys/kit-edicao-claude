# BRIEFING DE MARCA (modelo operacional)

> Documento operacional. Não é manual cerimonial. Tudo aqui é regra de execução.
> **Fonte de verdade:** `~/minha-marca/MINHA-MARCA.md` e `~/minha-marca/marca.json`. Este briefing diz COMO usar cada
> campo. Onde estiver `[do manual: ...]`, leia o valor lá; se faltar, faça a entrevista (`ENTREVISTA-DA-MARCA.md`).
> **Aplicação:** todo conteúdo visual da marca (carrossel, story, capa, anúncio, página, apresentação).

---

## 0. ANTES DE TUDO

- Um manual por marca. Se a pessoa tem mais de um perfil (ex.: um de serviço e um de curso), pergunte qual é a peça e use
  o manual certo (`MINHA_MARCA=/caminho/da/pasta`).
- Nunca misture identidades de perfis diferentes na mesma peça.

---

## 1. IDENTIDADE DA MARCA

### Assinatura e frase da marca
> **[do manual: carrossel.assinatura]** · ex.: `@seuarroba · O QUE VOCÊ FAZ`

Aplicação:
- **Carimbo superior direito** em carrosséis com vários slides (todos os slides)
- **Rodapé centralizado** em capa, peça única, story
- **Bio do Instagram:** a frase da marca ([do manual: carrossel.tagline])

### Provas oficiais (slide de autoridade)
[do manual: carrossel.provas], uma por pílula, escritas exatamente como estão.
⚠️ Nunca inventar, arredondar pra cima ou trocar palavras. Número que não está no manual não entra.

### Tom visual
> [do manual: MINHA-MARCA.md item 11, "Tom visual"]

3 atributos não negociáveis (padrão, se o manual não disser outros): **editorial · verdadeiro · acolhedor**.

---

## 2. PALETA

Os códigos vêm de `marca.json → cores`. Os papéis são fixos:

### Tons claros · acolhimento e respiro
- **Fundo** (`fundo`) · fundo base, slide-conteúdo
- **Fundo 2** (`fundo_2`) · fundo secundário
- **Claro** (`claro`) · texto sobre escuro, manuscrita sobre escuro

### Cores fortes · sinal, peso, autoridade
- **Destaque** (`destaque`) · **cor-assinatura.** CTA, pílulas, título de impacto
- **Principal** (`principal`) · capa de confronto, peso emocional
- **Principal escura** (calculada: principal 60% + preto) · texto sobre fundo 2, acento
- **Texto** (`texto`) · texto principal sobre claro

### Profundidade
- **Escuro** (`escuro`) · capa de autoridade, slide-quebra
- **Raro** (`raro`) · uso pontual, raridade

### Regras
- No máximo [do manual: carrossel.max_cores, padrão 4] cores por peça
- Destaque nunca compete (OU CTA OU pílula OU título)
- Raro em 1 a cada 10 peças no máximo
- Foto SEMPRE crua, sem filtro de cor por cima

---

## 3. TIPOGRAFIA

| Função | Do manual | Reserva livre |
|---|---|---|
| Título | `fontes.titulo` (romana) + `fontes.titulo_italico` | Instrument Serif |
| Corpo | `fontes.legenda_media` + `fontes.legenda` | Inter |
| Manuscrita | `fontes.manuscrita` | Mynerve / Caveat |

### Hierarquia tipográfica · 4 a 5 níveis por capa
A capa de impacto sempre tem variação combinada de **peso + tamanho + estilo**:
1. **Corpo 400** caixa alta pequena → chamada de contexto
2. **Corpo 700** caixa alta pequena → chamada de apoio
3. **Título gigante romano em negrito** → palavra-chave
4. **Título gigante itálico** → palavra-chave alternada
5. **Corpo 700** caixa alta pequena → etiqueta de baixo

> **Nunca uniformizar.** Se a capa tem 1 nível só (tudo em itálico), tá pobre. Pelo menos 3 níveis sempre.

---

## 4. ELEMENTOS VISUAIS · BIBLIOTECA

### 4.1 Caixas de destaque (2 tipos)
- **Caixa cheia** · palavra/expressão em fundo de cor sólida (principal, fundo, destaque). Texto contrasta. Destaque pesado.
- **Caixa vazada** · borda fina (1-2px) sem fundo. Mais leve, mais editorial. Destaque médio.

### 4.2 Sublinhado editorial
Linha fina debaixo de palavras-chave. Substitui ou complementa o negrito. Cor: texto (sobre claro) ou claro (sobre escuro).

### 4.3 Palavra circulada
SVG inline desenhando círculo manuscrito ao redor de UMA palavra (raro, máx. 1 por slide). Cor de destaque. Inclinação -3°.

### 4.4 Negrito seletivo
Em parágrafos, APENAS palavras-chave em negrito (700), nunca a frase inteira. Cor do texto ou de destaque.

### 4.5 Pílula
Dado de autoridade ou prova social. Destaque sobre escuro / fundo 2 sobre claro. Corpo 600/700, caixa alta,
espaçamento 2px, cantos 999px.

### 4.6 Foto + caixa por cima
Foto inteira de fundo + caixa de cor sólida (fundo, principal, destaque) flutuando como rótulo. NÃO é polaroid.
NÃO é moldura. É um "selo" sobre a foto.

### 4.7 Assinatura no canto superior direito
Em peças com vários slides, a assinatura pequena (18-22px em 1080), espaçamento alto, opacidade 65%.

### 4.8 Manuscrita complementar
Manuscrita, 1 a 5 palavras, cor de destaque (sobre claro) ou claro (sobre escuro). Inclinação -3° a -5°. Pra humanizar o título.

---

## 5. SISTEMA DE CARROSSEL

### Formato base
- **Dimensão:** 1080 × 1350 px (4:5)
- **Margem segura:** 80-100 px nas bordas
- **Assinatura:** rodapé centralizado ou canto superior direito

### Estrutura flexível
```
[CAPA] → [N slides intercalando conteúdo / quebra / imagem] → [CTA]
   1                    (4 a 10+ slides)                        1
```

### 4 tipos de slide
1. **Slide-Capa** (1 dos 6 tipos canônicos abaixo)
2. **Slide-Conteúdo** (fundo, texto na cor de texto)
3. **Slide-Quebra** (escuro, texto claro)
4. **Slide-CTA** (fundo com pílula na cor de destaque)

### Regra para slides com foto
- Foto SEMPRE crua, sem filtro de cor
- Degradê escuro sutil só na parte de baixo (pra leitura)
- **Sombra obrigatória** em todo texto sobre foto: `0 4px 24px rgba(0,0,0,0.55)`
- Hierarquia tipográfica variada (4 níveis)

---

## 6. AS 6 CAPAS CANÔNICAS

1. **Foto sua + tipografia** · você atendendo, ensinando, no seu espaço
2. **Foto respiro + tipografia** · objeto/cena (materiais, mesa, café, agenda)
3. **Tipográfica · fundo escuro** · escuro ou principal, sem foto
4. **Tipográfica · fundo claro** · fundo com grade, sem foto
5. **Foto + caixa por cima** · foto + selo de cor sólida
6. **Frase · fundo da marca** · frase isolada em fundo principal ou destaque

---

## 7. FAÇA E NÃO FAÇA

### Faça
- Foto crua sem filtro
- Hierarquia variada (peso + tamanho + estilo)
- Sombra em texto sobre foto
- Assinatura em todas as peças
- Caixinhas (cheias ou vazadas) pra destacar palavra
- Sublinhado editorial em palavras-chave
- Negrito seletivo (não a frase inteira)
- Slide-quebra estratégica
- CTA único e direto
- No mínimo 1 post sem foto a cada 3 (editorial)

### Não faça
- Foto com filtro de cor por cima
- Polaroid com rotação (use caixa retangular sem rotação)
- Mais de 3 fontes
- Título todo em caixa alta
- Mais cores que o máximo do manual
- Manuscrita em parágrafo ou CTA
- Capa sem função clara
- Número que não está nas provas do manual
- Feed com 9 posts seguidos do mesmo tipo de capa
- CTA em mais de 1 post a cada 9
- Tudo da lista "Nunca faça" do MINHA-MARCA.md

---

## 8. SISTEMA DE FEED (referência)

Feed harmônico não é 1 carrossel bonito: é regra aplicada em **blocos de 9 posts**.

### Distribuição obrigatória por bloco de 9
- Pelo menos 4 dos 6 tipos de capa
- 3 posts escuros (escuro/principal) + 3 claros (fundo/fundo 2) + 3 sinal/foto
- Nenhum par vizinho do mesmo tipo ou cor
- No máximo 3 posts com foto sua
- No mínimo 2 posts com foto respiro
- No mínimo 3 posts tipográficos puros (sem foto)
- No máximo 1 post CTA puro

Documento visual: `references/sistema-de-feed.html` (6 tipos de capa, mockup 3x3, regras, cores por bloco, checklist mensal).

---

## 9. PIPELINE DE PRODUÇÃO

```
PEDIDO → MANUAL OK? → PERGUNTAR HTML/CANVA → ROTEIRO → VISUAL → PRODUÇÃO → PNG
```

### Pergunta obrigatória ao iniciar carrossel
> "Quer em HTML (padrão: eu te entrego em PNG) ou direto no Canva?"

**Padrão:** HTML. Saída final: PNGs em 1080×1350 (`scripts/exportar_png.py`).

---

## 10. PEDIDO-MÃE · COMO O CLAUDE EXECUTA

Quando a pessoa disser **"cria um carrossel sobre X"**:

1. Confere o manual (`scripts/marca_css.py --conferir`); se faltar, entrevista
2. Lê o tema X
3. Decide a função da capa (confronto / autoridade / transformação) e 1 dos 6 tipos
4. Pergunta o canal: HTML ou Canva (padrão HTML)
5. Aciona a skill `roteirista-de-carrossel` com tema + função
6. Aplica este design system com as cores e fontes do manual
7. Aplica a regra de feed (confere se o post combina com os vizinhos do calendário)
8. Produz: HTML 1080x1350 OU Canva editável
9. Entrega: PNGs + checklist; pergunta o que mudar; ajuste aprovado vira regra no manual

### Entradas obrigatórias
- Tema
- Tipo de capa (1 dos 6)
- Canal (HTML / Canva)
- Quantidade de slides (padrão 6-9, pode ir a 10-12)
- Posição no feed (se for parte de bloco planejado)

### Saídas padrão
- Roteiro slide a slide
- HTML OU link do Canva
- PNGs nomeados slide-01.png, slide-02.png etc.
- Checklist de qualidade

---

> **O manual da marca + este briefing + sistema-de-feed.html são a régua. Peça que sai fora deles está errada, não
> importa quem produziu.**
