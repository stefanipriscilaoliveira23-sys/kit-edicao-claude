# Manual da Minha Marca

> Este é o arquivo que o Claude lê ANTES de editar qualquer vídeo ou montar qualquer carrossel seu.
> Tudo que está escrito aqui vence qualquer padrão das skills.
> Os textos entre [colchetes] são EXEMPLOS: troque pelos seus. Pode escrever do seu jeito, sem medo.
> Os valores que os programas usam (cores, fontes, posição da legenda) ficam também no `marca.json`, nesta mesma pasta.
> Não sabe preencher? Peça: "Claude, faz a entrevista da minha marca". Ele pergunta uma coisa de cada vez e preenche pra você.

## 1. Quem eu sou

- **Nome que aparece nos vídeos:** [Ana Souza]
- **Meu @:** [@anasouza.beauty]
- **O que eu vendo:** [atendimento de design de sobrancelha + curso online de sobrancelha para iniciantes]
- **Pra quem eu falo:** [mulheres de 25 a 45 anos que querem sobrancelha natural / profissionais iniciantes que querem
  aprender a técnica e cobrar mais]
- **Como eu cumprimento:** [Oi, gente!]  (o Claude usa essa saudação em roteiro e legenda)
- **Meu cartão de identidade (frase de 5 segundos pra quem me vê pela primeira vez):**
  [Se você é nova aqui, eu sou a Ana e ensino sobrancelha natural que dura.]

### Meus produtos e chamadas (CTA)

| Produto | Tipo de post que combina | Chamada que eu uso |
| --- | --- | --- |
| [Atendimento de design de sobrancelha] | [post de identificação com a cliente final] | [Me chama no direct pra agendar] |
| [Curso online para iniciantes] | [como começar do zero] | [Comenta COMEÇAR que eu te mando o link] |

### Frases reais do meu público

Frases exatas que aparecem nos comentários, no direct e nas perguntas (o Claude usa como gancho e título).
- ["Tenho medo de ficar artificial"]
- ["Quanto tempo dura?"]

## 2. Cores (com código)

O código é o que começa com # (ex.: #1F3A5F). Se você não sabe, mande o seu logo ou um print do seu perfil que o Claude
descobre pra você.

| Função | Minha cor | Código | Onde aparece |
| --- | --- | --- | --- |
| Principal | [azul marinho] | [#1F3A5F] | fundo de capa forte, títulos em cima de fundo claro |
| Destaque | [coral] | [#E07A5F] | caixa ou sublinhado da palavra-chave, pílulas, riscos, chamadas |
| Fundo claro | [creme] | [#FAF7F2] | fundo de slide de conteúdo |
| Texto | [quase preto] | [#1E1E1E] | texto em cima de fundo claro |
| Claro | [branco quente] | [#FFF8F0] | texto em cima de vídeo ou fundo escuro |
| Escuro | [grafite] | [#10141A] | sombras por cima do vídeo, slide de quebra |
| Fundo 2 (opcional) | [rosa clarinho] | [#F6E3DC] | fundo secundário |
| Cor rara (opcional) | [dourado] | [#C9A227] | detalhe especial, 1 a cada 10 peças |

**Máximo de cores por peça:** [4]

## 3. Fontes

Coloque os arquivos das fontes (.ttf, .otf ou .woff2) na pasta `fontes/`. Use só fontes que você tem direito de usar
(Google Fonts são grátis). Se não tiver nenhuma, o Claude usa as livres que vêm com a skill.

| Função | Minha fonte | Arquivo em fontes/ |
| --- | --- | --- |
| Título (grande, chama atenção) | [Instrument Serif] | [InstrumentSerif-Regular.ttf] |
| Título em itálico | [Instrument Serif Italic] | [InstrumentSerif-Italic.ttf] |
| Legenda / texto forte | [Inter Bold] | [Inter-Bold.woff2] |
| Legenda / texto normal | [Inter Medium] | [Inter-Medium.woff2] |
| Manuscrita (parece escrita à mão) | [Mynerve] | [Mynerve-Regular.ttf] |
| Giz (itens de lista em vídeo) | [Permanent Marker] | [PermanentMarker-Regular.woff2] |

## 4. Logo

- Arquivo: `logo.png` nesta pasta (de preferência com fundo transparente).
- Onde usar: [canto do último slide do carrossel; nunca em cima do rosto no vídeo]

## 5. Legenda dos vídeos

- **Posição:** [embaixo, acima dos botões do Instagram]  (opções: embaixo, meio, alto)
- **Cor da letra:** [branca]
- **Destaque da palavra-chave:** [caixa na cor de destaque]  (opções: caixa, sublinhado, itálico, só mudar a cor)
- **Quantas palavras aparecem por vez:** [3]
- **Tamanho:** [normal]  (normal = 74 px; pequena = 60; grande = 86)

## 6. Emojis

- **Uso emojis nos vídeos?** [sim]
- **Emojis que combinam comigo:** [✨ 💅 📅 💬]
- **Emojis que eu não uso:** [🔥 😂]

## 7. Sons

- **Sons que eu gosto:** [clique, pop, máquina de escrever no título, página virando]
- **Sons que eu ODEIO (nunca usar):** [whoosh alto, buzina, risada de fundo]
- **Música de fundo:** [não]  (se sim, qual arquivo e bem baixinha)
- **Volume dos efeitos:** [normal]  (mais baixo / normal / mais alto)

## 8. Elementos e efeitos que eu gosto

- [título escrito letra por letra no começo]
- [lista de itens aparecendo quando eu falo]
- [print aparecendo na hora que eu falo do resultado]
- [corte rápido, sem respiro]

## 9. Nunca faça

- [desfoque de fundo]
- [letra amarela]
- [legenda em cima do meu rosto]
- [palavrão na legenda]
- [travessão no texto]

## 10. Palavras que a IA erra (e como é o certo)

O Claude corrige sempre na legenda. Ponha também no `marca.json`, em `transcricao.trocas`, que a transcrição já sai certa.

| A IA escreve | O certo é |
| --- | --- |
| [sombrancelha] | [sobrancelha] |
| [micro pigmentação] | [micropigmentação] |
| [Ana Sousa] | [Ana Souza] |

**Palavras que eu não uso:** [cliente "VIP", "gratidão"]
**Hashtags na legenda do post:** [não]

## 11. Para carrossel

- **Assinatura que vai em todo slide:** [@anasouza.beauty · SOBRANCELHA NATURAL]
- **Frase da minha marca (tagline):** [Sobrancelha natural que dura]
- **Tom visual:** [limpo, delicado, acolhedor]
- **Fotos:** [crua, sem filtro, luz natural]  (fotos suas e de respiro ficam na pasta `fotos/`)
- **Meus números e provas oficiais (só o que é verdade):**
  - [+800 clientes atendidas]
  - [+120 alunas formadas]
  - [8 anos de profissão]

## 12. Minhas referências

Coloque prints ou vídeos na pasta `referencias/` se quiser. O link e o que você gosta em cada um é o mais importante.

**5 referências de vídeo:**
1. [link] · gosto de: [o título que aparece escrevendo]
2. [link] · gosto de: [a legenda pequena e limpa]
3. [link] · gosto de: [os prints entrando na hora certa]
4. [link] · gosto de: [o ritmo rápido]
5. [link] · gosto de: [a música baixinha]

**5 referências de carrossel:**
1. [link] · gosto de: [capa só com texto grande]
2. [link] · gosto de: [palavra circulada]
3. [link] · gosto de: [foto crua com caixa de texto]
4. [link] · gosto de: [poucos textos por slide]
5. [link] · gosto de: [último slide com chamada clara]

## 13. Regras aprovadas (toda correção vira regra)

O Claude acrescenta aqui, com a data, cada ajuste que você aprovar. Assim ele nunca mais erra a mesma coisa.

- [AAAA-MM-DD] [exemplo: legenda subiu pra não cobrir a mesa de atendimento]
