# Entrevista da marca (roteiro para o Claude)

Use quando `~/minha-marca/` não existir ou estiver incompleta, ou quando a
aluna pedir "faz a entrevista da minha marca". Sem o manual, NÃO edite vídeo nem monte carrossel: o resultado sai com a
cara de ninguém.

## Como conduzir
- Uma pergunta por vez. Linguagem simples, sem termo técnico. Espere a resposta antes da próxima.
- Dê sempre um exemplo curto junto da pergunta, pra ela entender o que você quer.
- Se ela não souber, ofereça 2 ou 3 opções prontas e deixe escolher. "Não sei" vira o padrão neutro, e você anota que dá
  pra mudar depois.
- Se ela já respondeu algo antes (no chat, num arquivo, num print), não pergunte de novo: confirme.
- Pode aceitar áudio, print, link e arquivo como resposta.
- No fim, mostre um resumo curto e pergunte "posso salvar assim?". Só então grave os arquivos.

## Antes de começar
Crie a pasta copiando o modelo (o `modelo-minha-marca/` desta skill, ou o `minha-marca-MODELO/` do pacote):
`~/minha-marca/` com `MINHA-MARCA.md`, `marca.json`, `fontes/`, `fotos/minhas/`, `fotos/respiro/`, `referencias/`, `sons/`,
`roteiros/`. No Windows, `~` é a pasta do usuário (ex.: `C:\Users\Nome\minha-marca`).

## As perguntas (na ordem)

| # | Pergunta (exemplo de como falar) | Onde salvar |
|---|---|---|
| 1 | "Qual nome aparece nos seus vídeos?" | MINHA-MARCA 1 · marca.json `nome` |
| 2 | "Qual é o seu @ do Instagram?" | 1 · `arroba` |
| 3 | "O que você vende? Pode ser serviço, curso, produto... E pra cada um, que chamada você usa? Ex.: Me chama no direct / Comenta QUERO" | 1 · "Meus produtos e chamadas" |
| 4 | "Pra quem você fala? Me descreve a pessoa que você quer que te assista." | 1 |
| 5 | "Como você cumprimenta quem te assiste? Ex.: Oi, gente! / Oie! / Olá, meninas!" | 1 |
| 5b | "Me manda prints de comentários e perguntas que você mais recebe." Guarde as frases exatas. | 1 · "Frases reais do meu público" |
| 6 | "Me manda o seu logo (o arquivo, de preferência com fundo transparente)." Salve como `logo.png`. | 4 · `logo.png` |
| 7 | "Quais são as cores da sua marca? Se não souber o código, me manda o logo ou um print do seu perfil." Tire as cores do logo/print (Pillow: cores mais frequentes) e mostre pra ela aprovar. Monte: principal, destaque, fundo claro, texto, claro, escuro. | 2 · `cores` |
| 8 | "Você tem fontes da marca? Me manda os arquivos." Se não tiver, ofereça 2 combinações grátis do Google Fonts (ex.: Instrument Serif + Inter + Mynerve, que já vêm com a skill; ou Playfair Display + Montserrat + Caveat). Só use fonte que ela tem direito de usar. Arquivos vão pra `fontes/`. | 3 · `fontes` |
| 9 | "Onde você gosta da legenda no vídeo: embaixo, no meio ou mais pra cima? Letra branca? A palavra importante com caixa colorida, sublinhada ou em itálico? Quantas palavras por vez?" Mostre um print de exemplo se ajudar. | 5 · `legenda` |
| 10 | "Pode usar emojis nos seus vídeos? Tem algum que você ama ou odeia?" | 6 · `emojis` |
| 11 | "Quais sons você gosta (clique, pop, máquina de escrever, página virando...) e quais você odeia? Quer música de fundo?" | 7 · `efeitos`, `trilha` |
| 12 | "Que efeitos você ama ver nos vídeos dos outros? Ex.: título escrevendo sozinho, lista aparecendo, print entrando." | 8 |
| 13 | "Tem alguma coisa que eu NUNCA posso fazer? Ex.: desfoque, letra amarela, legenda em cima do rosto." | 9 |
| 14 | "Quais palavras a IA costuma escrever errado no seu caso? Ex.: nome de técnica, seu sobrenome." Grave também em `transcricao.trocas` (chave minúscula, sem pontuação) e monte o `transcricao.vocabulario` com nome, marca e termos dela. | 10 · `transcricao` |
| 15 | "Você usa hashtag na legenda do post?" | 10 · `carrossel.hashtags` |
| 16 | "Quais números e provas são verdade sobre você? Ex.: quantas clientes atendeu, quantas alunas formou, anos de profissão." Nunca invente número. | 11 · `carrossel.provas` |
| 17 | "Qual frase pequena vai em todo slide do carrossel? Ex.: @seuarroba · O QUE VOCÊ FAZ" | 11 · `carrossel.assinatura`, `tagline` |
| 18 | "Me manda 5 Reels que você ama e me diz o que gosta em cada um." | 12 |
| 19 | "Me manda 5 carrosséis que você ama e me diz o que gosta em cada um." | 12 |
| 20 | "Tem fotos suas e fotos do seu dia (sem você) pra usar? Pode mandar." Salve em `fotos/minhas/` e `fotos/respiro/`. | 11 · `fotos/` |
| 21 | (só confirme) "Vou trabalhar em Videos-Claude/_trabalho e entregar os vídeos prontos em Videos-Claude/PRONTOS. Pode ser?" | `pastas` |

## Depois de salvar
- Confira que não falta nada: na corte-viral, `python3 modelo-edicao/marca.py conferir`; na design-system-da-marca,
  `python3 scripts/marca_css.py --conferir`.
- Na primeira edição e no primeiro carrossel, mostre o resultado e pergunte o que ela mudaria.
- **Toda correção vira regra:** cada ajuste aprovado entra, com data, em "13. Regras aprovadas" do `MINHA-MARCA.md`
  (e no `marca.json` quando for cor, fonte, posição, volume). O manual cresce a cada vídeo.
