# Prompts prontos

Copie, cole no Claude (aba Code) e troque o que estiver entre [colchetes].

---

## Passo zero: montar o Manual da Marca (uma vez só)

**Separe antes:**
- Seu nome, seu @ e o que você vende
- Logo em PNG com fundo transparente (se tiver)
- 2 a 4 cores (o código, tipo #8B1E3F, ou um print de onde você tirou)
- O nome das letras (fontes) que você usa, ou um print de uma letra que você gosta
- 5 links de reels que você ama a edição, e o que gosta em cada um
- 5 prints de carrosséis que você ama o visual, e o que gosta em cada um
- Sons que você gosta e sons que você odeia
- O que você NÃO aceita de jeito nenhum nos seus vídeos e carrosséis
- Palavras que a IA costuma escrever errado (seu nome, termos da sua área)
- Uma pasta com fotos suas pra usar nos carrosséis

**Prompt:**
```
Monta meu manual da marca.
Me faz as perguntas uma por uma, em português simples.
Minhas referências de vídeo estão aqui: [links]
Minhas referências de carrossel estão nesta pasta: [arraste a pasta]
Minha logo: [arraste o arquivo]
```

---

## Vídeo

### Passo 1 e 2: mandar o vídeo e transcrever

**Vídeo longo** (live, aula, conversa, vários assuntos):
```
Esse é um vídeo bruto longo: [arraste o vídeo]
Escreve tudo o que foi falado e me traz os trechos com mais chance de viralizar.
Pra cada trecho, me dá 3 opções de gancho (o título na tela e a frase que abre o vídeo).
Ainda não corta nada.
```

**Vídeo roteirizado** (um vídeo só, já gravado pensando no post):
```
Esse vídeo já é roteirizado: [arraste o vídeo]
Escreve tudo o que foi falado e me mostra o texto antes de editar.
```

### Passo 3 e 4: escolher os cortes

```
Gostei dos cortes [1, 3 e 5].
No corte 1 quero o gancho [B].
Agora faz a edição limpa desses cortes.
```

### Passo 5: edição limpa

```
Faz a edição limpa: tira só silêncio, pausa, erro, gaguejo e repetição.
Deixa em pé (vertical) e limpa o som da minha voz.
Sem legenda, sem emoji, sem efeito. Me manda pra eu assistir.
```

### Passo 6: aprovar ou apontar o erro

```
No segundo [0:12] ainda tem um erro / uma pausa. Corta.
```
```
Aprovado. Pode ir pra edição completa.
```

### Passo 7: edição completa

```
Faz a edição completa seguindo o meu manual da marca:
título no começo, legenda, palavras de destaque, emojis e sons.
```

**Ajustes:**
```
A legenda está muito em cima do meu rosto, desce um pouco.
O som de clique está alto demais.
Gostei! Salva isso no meu manual.
```

---

## Carrossel

### Passo 1 a 3: mandar tudo

```
Quero um carrossel.
Copy (lâmina por lâmina):
Lâmina 1: [texto]
Lâmina 2: [texto]
...
Fotos: [arraste a pasta]
Referência de conteúdo: [link ou print]
Referência de visual: [print]
Segue o meu manual da marca.
Faz primeiro só a capa e uma lâmina de dentro pra eu aprovar.
```

### Passo 4 e 5: aprovar e fazer o resto

```
Aprovado o visual. Faz todas as lâminas.
```

### Passo 6: ajustes

```
Na lâmina [3], aumenta a letra e troca a foto pela [nome da foto].
Gostei! Salva isso no meu manual.
```

---

## Motion (animações de papel)

```
Coloca uns motions nesse corte: [arraste o vídeo já editado]
Ilustra as frases mais importantes.
Se faltar algum objeto, me passa o pedido pra eu gerar no ChatGPT.
```

---

## Sanfoninha (zoom na batida)

**Separe antes:** de 8 a 15 vídeos curtos em pé (3 a 6 segundos cada), numerados na ordem do atendimento
(01, 02, 03...), com o resultado por último. E a música (arquivo mp3 e o segundo em que ela começa), ou avise
que vai colocar a música no Instagram.

**Prompt 1 (rápido)**
```
Claude, faz meu vídeo no formato Sanfoninha.
Mandei 10 vídeos numerados de 01 a 10, na ordem do atendimento. O 10 é o resultado.
Pega o melhor pedacinho de cada um (meio segundo a 1 segundo), cada cena entra com zoom rápido
e sai com zoom pra dentro, zoom pra fora ou giro, sempre cortando na batida da música que eu mandei.
Começa com o plano aberto dando um zoom forte em mim e termina no resultado com zoom lento, escurecendo no final.
Vertical, até 20 segundos, sem texto na tela.
```

**Prompt 2 (completo, com música e flash antes do resultado)**
```
Claude, quero um Sanfoninha de 15 segundos com estes 12 vídeos (01 a 12, já na ordem).
Música: o arquivo musica.mp3, começando no segundo 0:12. Corta tudo na batida.
Estrutura: 2 segundos de gancho com o vídeo 01 (zoom forte no meu rosto),
processo com os vídeos 02 a 09 (1 ou 2 batidas cada, alternando zoom pra dentro, zoom pra fora e giro),
um flash bem rápido repetindo 4 cenas do processo, e os últimos 4 segundos só com o resultado (vídeos 10 a 12)
em corte seco com zoom lento e escurecendo no fim.
Coloca no começo o texto: "[texto do gancho]". Me entrega vertical 9:16 em mp4.
```

Vai colocar a música no Instagram? Troque a linha da música por:
```
Vou colocar a música no Instagram. Me entrega sem som, cortado no ritmo de [128] BPM.
```

---

## Atualizar o kit

```
Atualiza meu kit de edição.
```
