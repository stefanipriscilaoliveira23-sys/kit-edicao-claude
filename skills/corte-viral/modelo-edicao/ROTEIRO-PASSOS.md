# Roteiro antes de gravar · passos 0 a 4 (método Jessica Carter)

A aluna escreve só "passo 0", "passo 1" etc. e você segue o que está aqui, sem ela colar prompt.
Base de tudo: `~/minha-marca/roteiros/` (abreviado como BASE abaixo). Se a pasta não existir, crie a partir do modelo
`modelo-minha-marca/roteiros/` desta skill (ou do `minha-marca-MODELO/roteiros/` que veio no pacote) antes de começar.
Leia também `~/minha-marca/MINHA-MARCA.md` (quem ela é, o que vende, pra quem fala, saudação, "Nunca faça").

Sempre em português, em linguagem simples.

## Atalhos que ela usa

| Ela escreve | Você faz |
|---|---|
| `passo 0` | Passo 0 |
| `passo 1` + áudio/texto, ou `roteiro novo` | Passo 1 |
| `passo 2` | Passo 2 sobre o despejo mais recente |
| `passo 3` | Passo 3 |
| `passo 4` + versão final | Passo 4 |
| `perguntas do vídeo sobre X` | Lista de perguntas no formato de `BASE/06 Perguntas pra responder falando.md`, acrescentada nesse arquivo |

Se ela pular um passo, siga mesmo assim e avise numa linha o que ficou faltando.

## Passo 0 · Psicologia (uma vez só)

Rode por conta própria este pedido (tradução do prompt da Jessica, já no contexto da aluna; o nicho e o público vêm do
MINHA-MARCA.md):

> Aja como um doutor em psicologia humana e marketing. Ensine os 10 a 15 principais princípios psicológicos e técnicas de persuasão usados em vídeo curto e em copy (efeito Zeigarnik, reciprocidade, prova social, quebra de padrão etc.). Pra cada um: o nome, uma explicação de uma frase em linguagem simples e um exemplo de como soaria num roteiro casual de Reels de [o que a aluna faz] falando com [o público dela]. Explique como pra uma amiga inteligente, nada de livro didático.

Grave o resultado em `BASE/02 Psicologia.md`, na seção "Do passo 0" (substitui o que tiver lá). Mostre a ela um resumo curto.
Se a seção já estiver preenchida, pergunte se quer refazer.

## Passo 1 · Despejo

Entrada: texto bagunçado, áudio (transcrever local: `mlx_whisper --model mlx-community/whisper-large-v3-turbo --language pt`
no Mac com chip M, ou faster-whisper com o Python da skill em qualquer computador) ou respostas às perguntas do arquivo 06.

Não arrume o texto. Devolva só:
1. **Mensagem central**, numa frase.
2. **3 opções de gancho falado** no jeito DELA (ver "Como eu escrevo gancho" em `03 Minha voz.md`; se estiver vazio: nomear
   o assunto na primeira frase, benefício ou dor de quem assiste, contraste no fim). Evite gancho de cena ou historinha
   longa: o assunto tem que estar claro em 3 segundos.
3. **Prova disponível**: que print, número ou conversa ela tem pra mostrar no segundo da frase. Se faltar, diga qual buscar.
4. **Molde sugerido** de `BASE/05 Molde do roteiro.md` (A a E) e por quê, em uma linha.
5. **O que está faltando** no despejo, em até 3 perguntas.

Guarde o despejo em `BASE/Roteiros/AAAA-MM-DD <tema>.md` (seção "Despejo").

## Passo 2 · Roteiro

Antes de escrever, leia: `03 Minha voz.md`, `04 Kit fixo de todo vídeo.md`, `05 Molde do roteiro.md`, `02 Psicologia.md`,
`07 Quem eu sou.md` e `08 Copy leve.md`. Use histórias, crenças e vulnerabilidades do arquivo 07 só se ela tiver liberado lá.

Entregue, nesta ordem:
1. **Título na tela** em duas linhas: em cima o resultado ou assunto (se explica sozinho), embaixo a linha manuscrita.
   Ela NÃO precisa ser sempre a premissa: dê 3 opções (a premissa, um detalhe do episódio, uma brincadeira).
   Em série, selinho manuscrito "Episódio N".
2. **Roteiro falado** em blocos curtos, cada bloco com a função entre colchetes antes (ex.: `[gancho]`, `[cartão de identidade]`,
   `[prova: print X]`, `[próximo episódio]`, `[palavra-chave]`, `[fecho]`). Mantenha a voz dela: casual, de conversa,
   nada corporativo.
3. **Tamanho**: diga quantas palavras e a duração estimada a 240 palavras por minuto (alvo 60 a 120 s).
4. **Legenda do post**, com o bloco "Se você é nova aqui..." (ou o cartão de identidade dela) e a palavra-chave.
   Hashtag só se o manual disser que ela usa.
5. **Psicologia usada**: lista de cada técnica e em qual bloco está. Aponte onde ficou fraca.
6. **Conferência do kit fixo**: os itens de `04 Kit fixo`, marcando o que entrou e o que ficou de fora de propósito.
7. **Checagem de copy leve** (`08 Copy leve.md`): cena, contraste, metáfora, loop aberto e quebra de expectativa, cada um com
   onde entrou. Se faltar, no máximo 2 sugestões pontuais tiradas da vida dela, marcadas como opção.

Antes de mostrar, varra o texto e corrija:
- tudo da lista "Nunca faça" e "Palavras que eu não uso" do MINHA-MARCA.md e do `03 Minha voz.md`;
- os tiques que deixam texto com cara de IA (padrão, a menos que o manual libere): travessão, "não é X, é Y",
  "parece X mas é Y", pares paralelos ("não pra A, não pra B, pra C"), frase de moral redondinha no fim de bloco;
- saudação: a que está no manual.

Salve no arquivo do roteiro (seção "Versão do Claude").

## Passo 3 · Ler em voz alta (é com ela)

Não reescreva. Mostre só o checklist:
- Leia em voz alta, de pé, como se fosse gravar.
- Risque o que você não falaria assim.
- Troque as palavras pelas suas, ponha suas expressões.
- Corte a frase que ficou explicando demais.
- Use o teleprompter como lembrete, não pra ler palavra por palavra.
Depois, mande a versão final com `passo 4`.

## Passo 4 · Ensinar a voz dela

Entrada: a versão final dela.
1. Compare com a "Versão do Claude" do mesmo roteiro: o que ela cortou, trocou e acrescentou, palavra por palavra.
2. Atualize `BASE/03 Minha voz.md`: "Palavras e expressões que eu uso", "Ritmo das minhas frases", "O que eu sempre corto da
   versão do Claude". Acrescente, não apague o que já existe. Se uma anotação nova contradiz uma antiga, troque a antiga e avise.
3. Acrescente uma linha em "Histórico de comparações": data, tema, as 2 ou 3 mudanças principais.
4. Salve a versão final no arquivo do roteiro (seção "Versão final").
5. Diga a ela, em até 4 linhas, o que aprendeu.

## Depois de gravar

O vídeo segue o pipeline normal de edição (`JEITO-DA-MARCA.md`). Use o arquivo do roteiro pra conferir grafias da legenda,
o título na tela e onde entra cada print (os blocos `[prova: ...]` viram cartões).
