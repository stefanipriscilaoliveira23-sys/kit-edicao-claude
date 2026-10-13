# Narradinho (vídeo narrado tipo vlog)

Quando a pessoa pedir **"faz um narradinho"**, é esta receita. Vale junto com o `JEITO-DA-MARCA.md` (grafias, voz,
área segura, onde trabalhar e entregar) e com o Manual da Marca (`~/minha-marca/`): cores e fontes vêm de lá.
O que estiver aqui vence só no que for próprio do formato (legenda pequena, música, clarão).

**O que é:** várias cenas gravadas (numeradas na ordem: 00 abertura, 01, 02...) + a narração gravada à parte num áudio.
As frases da narração ficam emendadas (≈0,1 s entre uma e outra); a cena troca **na palavra que cita a coisa nova**
(fala "primer", entra a cena do primer) ou na virada da frase; o som original das cenas sai; legenda pequena branca de
2 a 3 palavras; títulos grandes em letra elegante inclinada nos momentos importantes; quase tudo corte seco, com
**clarão de luz só no gancho e na entrada do resultado**; música baixinha (8 a 10 dB abaixo da voz) que sobe no resultado;
o final escurece.

Referência: reel de procedimento de cílios narrado (https://www.instagram.com/reels/DdzNx7OR7Vt/): 38 cenas de 2,7 s em
média, narração a 222 palavras por minuto, pausa média de 0,09 s entre frases, 23 das 34 trocas caem no meio da frase,
exatamente na palavra do produto.

## Antes de tudo
1. `python3 ~/.claude/skills/corte-viral/modelo-edicao/marca.py conferir`. Faltou manual: entrevista da marca primeiro
   (`ENTREVISTA-DA-MARCA.md`). Ler o `~/minha-marca/MINHA-MARCA.md` ("Nunca faça" e "Regras aprovadas" vencem esta receita).
2. Python certo: `PY=$(python3 ~/.claude/skills/corte-viral/modelo-edicao/marca.py python)` (o da venv da skill, com o Whisper).
3. Pasta de trabalho: `python3 marca.py pasta trabalho` (nunca /tmp). Na primeira vez, `preparar_pasta.py` instala o HyperFrames fixo.

## O que a pessoa manda

1. **Cenas numeradas na ordem**: `00` = abertura (ela olhando pra câmera, sorrindo, um gesto; não precisa falar),
   `01`, `02`, `03`... na ordem do que aconteceu. Produto na mão com o rótulo virado pra câmera, detalhe, de longe, de perto.
   Os **últimos números** = resultado (cliente deitada olhando pra câmera, cliente em pé mexendo no cabelo). Foto também vale.
2. **A narração num áudio separado** (gravador do celular ou áudio do WhatsApp mandado pra ela mesma).
3. O **texto da narração**, se escreveu antes (ajuda a conferir nomes de produto).
4. A **música**, se quiser uma. Sem música: a trilha do manual (`trilha.arquivo` no `marca.json`, em `~/minha-marca/sons/`).
   Se o manual não tiver trilha, pedir uma instrumental calma (o narradinho sempre tem música).

## Como gravar a narração (passar isso pra pessoa)

- Celular a um palmo da boca, num lugar que não ecoa (carro, quarto com cortina e cama). Sem ventilador, ar, TV ou música.
- Falar **na ordem das cenas**, contando o que fez e **por que fez** (o porquê é o que prende).
- Frases inteiras. Errou? Para, respira e **repete a frase inteira**. Não precisa apagar nada: fica a última vez.
- Energia de quem conta pra uma amiga, um pouquinho mais rápido que o normal.
- **Nome dos produtos com calma e bem claro**: é neles que o corte cai.

## Passo a passo do Claude

Dentro da pasta de trabalho, uma pasta por vídeo (`P`) com `cenas/` (cópia dos vídeos numerados), o áudio da narração e,
se tiver, a música. `R=~/.claude/skills/corte-viral/modelo-edicao/receita-narradinho`.

### 1. Conferir o material (prompt 1)
```
$PY $R/cenas.py $P                              # lista as cenas, duração, e faz quadros/cena-XX.jpg + quadros/todas.jpg
$PY $R/narracao.py transcrever $P $P/narracao.m4a   # DeepFilterNet + depof + Whisper; propõe o que tirar
```
- Responder: quantas cenas, quanto tempo cada uma, quanto tempo tem a narração, e **mostrar a transcrição** pra ela
  conferir os nomes de produto. **Não editar ainda.** Palavra que o Whisper errou vai pro manual ("Palavras que a IA erra"
  e `transcricao.trocas` no `marca.json`).
- `narracao/frases.json`: cada frase com `"manter"`. O script já marca pra tirar "éé/hum" sozinhos e a tentativa
  refeita (fica a ÚLTIMA). Conferir na mão: frase com palavra esticada (>0,9 s) = o Whisper escondeu repetição; ouvir o trecho.
  Pra aproveitar só um pedaço de uma frase, mudar `start`/`end` dela.

### 2. Montagem limpa (prompt 2) = PORTÃO 1
```
$PY $R/narracao.py emendar $P [--acelerar 1.08]   # corta pelo SOM, emenda (≈0,1 s entre frases, ≈0,06 s dentro), trata a voz, retranscreve
```
- Saem `narracao/voz.wav` (-14 LUFS, sem ruído, sem pofs e sem S estourado) e `narracao/transcript.json` (palavras na voz final).
  Acelerar só se ela pedir ou se a fala estiver lenta (acima de 1,12 a voz afina).
- **O Claude decide o encaixe**: abrir `quadros/todas.jpg` e as `quadros/cena-XX.jpg`, ler a transcrição final e escrever
  `$P/plano.json` (modelo `exemplo-plano.json`): uma troca por cena, na ordem dos números.
  - A cena entra **na palavra** que cita a coisa nova (`"palavra": "primer"`), mesmo no meio da frase; quando não cita
    nada, na virada da frase.
  - Cada cena entre 1 e 5 s (média ≈2,5 s). Fala longa sem coisa nova: dividir em 2 cenas ou usar 2 pedaços da mesma cena (`"in"` diferente).
  - `"in"` = segundo da cena onde começa (olhar a folha: pular o tremido do começo, pegar o melhor pedaço). Sem `"in"`, pega o meio.
  - `resultado`: as últimas cenas, depois da narração, só com música (5 a 7 s no total).
```
$PY $R/montar.py $P
```
- Sai `montagem/limpa.mp4` (sem legenda, sem música, sem som das cenas), `montagem/tabela.md` e `montagem/folha-cortes.jpg`.
  Olhar a folha de cortes e os AVISOS (cena > 5 s, cena piscando, cena curta demais). Foto entra com aproximação bem lenta.
- **Mandar pra ela o vídeo + a tabela (cena, segundo, trecho da fala) e PARAR.** Só seguir quando ela aprovar.
  Ajuste dela = mudar `plano.json` e rodar `montar.py` de novo.

### 3. Edição completa (prompt 3) = PORTÃO 2
Escrever `$P/edicao.json` (modelo `exemplo-edicao.json`) e rodar **com run_in_background** (um render por vez):
```
bash $R/render.sh $P        # editar.py -> HyperFrames fixo -> mixar.py -> folha.jpg
```
- **Abertura**: frase do começo em letra pequena (palavra por palavra com a fala) + o nome da técnica GRANDE na fonte de
  título itálica do manual, com sublinhado na cor de DESTAQUE correndo embaixo. Depois o clarão de luz pra entrar no procedimento.
- **Legenda**: fonte de legenda do manual, cor clara, pequena (50 px), minúscula, sem fundo, 2 a 3 palavras, centralizada
  um pouco abaixo do meio (top 1180), dentro da área segura (x 120 a 960). Some quando entra texto grande.
- **Textos grandes** nos momentos-chave (1 a 3 no vídeo): o nome da técnica, o pedido da cliente em lista no alto
  (traço na cor de destaque em cada item, palavra em `*itálico*`), e uma palavra de resultado em letra elegante ("Simétrico & harmônico").
- **Transições**: corte seco. Clarão SÓ na saída da abertura e na entrada do resultado (`"flashes": "auto"`).
  Escurece entre as cenas do resultado e no fim.
- **Música**: o vídeo todo, 9 dB abaixo da voz (`musica_db`), sobe 8 dB quando a narração acaba (`subida_db`) e some
  no escuro do fim. O script mede e mostra quanto ficou. Sem efeito sonoro (a referência não usa); se ela pedir, `sfx`
  (respeitando os sons que ela odeia, no manual).
- Sai `$P/<nome>.mp4` + `$P/folha.jpg`. Conferir a folha (legenda dentro da área segura e longe do rosto, títulos no
  segundo certo, clarão nos 2 lugares, fim escuro). Legenda branca some em cena clara (print de celular, parede branca):
  nesses casos subir/descer a legenda (`legenda.top`) ou pegar outro pedaço da cena. Só então mandar pra ela com uma lista curta do que foi feito.

### 4. Entregar
Depois do "aprovado": `entregar.sh` (pasta de entrega do manual). **Toda correção aprovada vira regra** em
"Regras aprovadas" do `MINHA-MARCA.md`, com data.

## Regras do formato (da referência)
- Fala emendada: pausa entre frases ≈0,1 s (máx. 0,25), entre palavras ≈0. Nada de buraco.
- 1 troca a cada 2 a 3 s; mais rápido no meio (passos rápidos, 1,2 a 1,4 s), mais calmo no começo e no fim.
- A imagem sempre mostra o que está sendo dito naquele segundo. Não esperar a frase acabar pra trocar.
- Cenas em velocidade normal. Sem zoom, deslize ou giro. Cor igual em todas (luz leve).
- Sem CTA falado nem escrito no vídeo: o convite vai na legenda do post.

## Arquivos desta pasta
| Arquivo | O que faz |
|---|---|
| `identidade.py` | lê cores, fontes, trilha, grafias e pastas do Manual da Marca (via `marca.py`) |
| `cenas.py` | lista as cenas numeradas e faz as folhas de quadros |
| `narracao.py` | `transcrever` (limpa + Whisper + proposta do que tirar) e `emendar` (corta pelo som, emenda, trata, retranscreve) |
| `montar.py` | plano.json -> montagem limpa + tabela + folha de cortes (portão 1) |
| `editar.py` | edicao.json -> projeto HyperFrames (legenda, títulos, lista, destaque, clarão, escurecer) |
| `mixar.py` | narração + música com a subida no resultado; mede música x voz |
| `render.sh` | editar -> render -> mixar -> folha (portão 2) |
| `exemplo-plano.json`, `exemplo-edicao.json` | modelos |

## Os 3 prompts prontos

### Prompt 1: mandar o material
```
Faz um narradinho com este material.

Estou mandando:
1. Os vídeos das cenas numerados na ordem (01, 02, 03...). O vídeo 00 é a minha abertura olhando para a câmera e os últimos são o resultado da cliente.
2. A minha narração gravada em um áudio separado.
3. O texto da narração que eu usei como roteiro (se eu mandei).
4. A música (se eu mandei). Se eu não mandei, escolha uma instrumental calma.

Antes de editar, confira se está tudo certo: me diga quantos vídeos recebeu, quanto tempo tem cada um, quanto tempo tem a narração, e me mostre a transcrição da narração para eu conferir os nomes dos produtos. Não comece a edição ainda.
```

### Prompt 2: aprovar a montagem limpa do narradinho
```
A transcrição está certa. Agora faça a montagem limpa do narradinho, ainda sem legenda e sem música:

1. Limpe a narração: tire os respiros, as pausas, os "éé" e as frases que eu errei (fique sempre com a última vez que eu falei a frase). Emende uma frase na outra, sem silêncio entre elas.
2. Coloque as cenas na ordem dos números, cada uma em cima do trecho da fala que fala daquilo.
3. Quando eu falar o nome de um produto, a cena do produto tem que entrar exatamente nessa palavra, mesmo no meio da frase.
4. Corte cada cena do tamanho da fala. Nenhuma cena pode ficar parada mais de 5 segundos.
5. Tire o som original de todos os vídeos. Só fica a minha voz.

Me mande o vídeo e uma tabela com: número da cena, segundo em que começa, e o trecho da fala que ela cobre. Eu vou assistir e te falar o que mudar.
```

### Prompt 3: edição completa do narradinho
```
Aprovei a montagem do narradinho. Agora termine a edição:

1. Abertura: o meu vídeo 00 com a frase do começo escrita em cima, uma parte em letra pequena e o nome da técnica grande em letra elegante inclinada. Depois um clarão de luz para entrar no procedimento.
2. Legenda: branca, sem fundo, letra minúscula, pequena, de 2 a 3 palavras por vez, no meio da tela um pouco para baixo, acompanhando a minha fala.
3. Nos momentos mais importantes, coloque um texto maior: o nome da técnica, o pedido da cliente em lista no alto da tela, e uma palavra de resultado em letra elegante.
4. Transição: corte seco entre as cenas. Clarão de luz só na entrada do resultado. Escurecer no fim.
5. Música instrumental o vídeo todo, baixinha atrás da minha voz, e que suba no final, quando entra o resultado.
6. Resultado da cliente no final só com música, uns 6 segundos.
7. Exporte em vertical 1080x1920, pronto para postar.

Me mande o vídeo final e uma lista curta do que você fez.
```
