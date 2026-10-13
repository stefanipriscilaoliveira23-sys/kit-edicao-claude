---
name: sanfoninha
description: Formato de vídeo "Sanfoninha" (zoom na batida). Reel vertical de 15 a 20 s com cenas curtas do atendimento cortadas na batida da música, cada cena entra com um soquinho de zoom e sai com zoom pra dentro, zoom pra fora (sanfona) ou giro, e termina no resultado com zoom lento escurecendo. Use SEMPRE que a pessoa pedir "sanfoninha", "faz um sanfoninha", "faz no formato sanfoninha", "meu vídeo sanfoninha", "vídeo de zoom na batida", "zoom in zoom out na batida" ou mandar vários vídeos curtos numerados pedindo esse formato.
---

# Sanfoninha (zoom na batida)

## Como é o formato (receita fixa)

Medido quadro a quadro num reel de lash designer com 52 mil curtidas. Não inventar outro estilo.

| Peça | Regra |
|---|---|
| Duração | 15 a 20 s, vertical 1080x1920, 30 quadros por segundo |
| Cenas | cerca de 0,4 a 0,9 s cada (1 ou 2 batidas), cortadas exatamente na batida da música |
| Gancho (1ª cena) | ~1,7 s, plano aberto, zoom forte 1,00 → 1,45 em 0,40 s desacelerando |
| Entrada de toda cena | "soquinho": zoom 1,00 → 1,25 em 0,22 s desacelerando, depois zoom lento +12% por segundo |
| Saídas (rodízio) | **atravessa** (+18% nos últimos 0,13 s, acelerando), **sanfona** (volta ao quadro cheio em 0,30 s), **giro** (+20° saindo; a próxima entra de -15° → 0 em 0,30 s; bordas espelhadas, nunca preto), **corte seco** |
| Desfoque | desfoque de movimento só quando o movimento é rápido (perto dos cortes) |
| Flash | antes do resultado, 4 cenas de meia batida repetindo pedacinhos do processo |
| Resultado | últimos vídeos, corte seco, zoom lento 5% por segundo, o último escurece pro preto em 0,6 s (imagem e som) |
| Texto | o original não tem. Só se a pessoa mandar o texto do gancho |
| Cor | natural, sem filtro |

## O que pedir à pessoa (antes de começar)

Pergunte só o que faltar, numa mensagem só:

1. **8 a 15 vídeos verticais curtos, numerados na ordem do atendimento** (01, 02, 03...). Cada um de 3 a 6 s
   (o resultado, de 5 a 10 s). Só meio segundo a 1 segundo de cada um vai pro vídeo; a sobra serve pra escolher.
2. **Qual é o resultado**: por padrão, o último vídeo. Se forem 2 ou 3 de resultado, ela avisa ("o 11 e o 12 são o resultado").
3. **Música**, de um destes jeitos:
   - arquivo da música (mp3, m4a ou wav) + o segundo em que quer que comece; ou
   - "vou colocar a música no Instagram": entrega SEM som, cortada no ritmo de um BPM. Pergunte o BPM se ela souber
     (dá pra ver em sites como songbpm.com); se não souber, use 128.
4. **Texto no gancho** (opcional). Se não falar nada, vai sem texto (como o original).

Dicas de gravação pra passar se ela ainda vai filmar: celular parado (tripé), plano mais ABERTO do que quer que
apareça (o zoom fecha a imagem), 4K se o celular tiver, variar ângulos (de longe, de cima, close no olho, close na
mão, cliente deitada, resultado em selfie com 2 ou 3 poses).

## Caminhos e comandos

- `S` = pasta `scripts/` desta skill (`~/.claude/skills/sanfoninha/scripts`).
- `PY` = `~/.claude/skills/sanfoninha/.venv/bin/python` se existir (Windows: `.venv\Scripts\python.exe`);
  senão `python3` (Windows: `python`). Rode sempre com `-I`. Se der erro de `cv2`/`numpy`, siga o `INSTALAR.md`.
- ffmpeg: os scripts procuram sozinhos em `~/.local/bin` e depois no PATH (no Windows, o ffmpeg do PATH).
- `TRAB` = pasta de trabalho: `pastas.trabalho` do `~/minha-marca/marca.json` + `/sanfoninha-<tema>/`;
  sem manual, `~/Videos-Claude/_trabalho/sanfoninha-<tema>/`. Entrega em `pastas.entrega` (ou `~/Videos-Claude/PRONTOS/`).
- Nunca apague, mova ou renomeie os vídeos originais da pessoa. Se não estiverem numerados, proponha a ordem,
  confirme e COPIE para `TRAB/brutos/` já numerados (01.mp4, 02.mov...).

## Passo a passo

### 1. Olhar os brutos e escolher o melhor pedacinho de cada um

```bash
PY -I S/olhar_brutos.py "PASTA_DOS_BRUTOS" "TRAB" --resultados 1
```

Gera `TRAB/folhas/visao-geral.jpg` (um quadro de cada vídeo), `TRAB/folhas/NN.jpg` (quadros a cada 0,25 s com o
segundo escrito e uma barrinha de movimento; a janela sugerida vem com contorno vermelho) e `TRAB/brutos.json`.

Abra a visão geral e TODAS as folhas (ferramenta Read) e escolha você mesmo o `inicio` de cada vídeo no
`brutos.json` (a sugestão automática é só um ponto de partida):

- **Gancho (01)**: plano aberto dela trabalhando, de preferência olhando ou se mexendo. Rosto e mãos no centro,
  porque o zoom fecha no meio da imagem.
- **Processo**: o trecho com AÇÃO (pinça encostando, mão aplicando, produto sendo pego, cliente piscando,
  expressão). Evite: mão tapando a câmera, imagem tremida ou fora de foco, começo e fim do vídeo (mão no botão).
- **Resultado**: pose parada, nítida, olhos abertos, sem piscar. Se tiver 2 ou 3 poses, cada vídeo de resultado
  pega uma.
- Vídeo DEITADO (horizontal): o corte vertical pega o meio; se o assunto estiver de lado, ponha `"foco_x"`
  (0 = esquerda, 1 = direita) no bruto.
- Se mais de um vídeo for resultado, troque o `"papel"` deles para `"resultado"` no `brutos.json`.

### 2. Batida da música

Com música:
```bash
PY -I S/batidas.py "musica.mp3" --inicio 12 --json "TRAB/batidas.json"
```
Use o **BPM** e o **musica_inicio ajustado** (a primeira batida forte cai no 0,00 do vídeo). Se o BPM sair o
dobro ou a metade do que se ouve (acima de 160 ou abaixo de 80, ou ela disser o BPM), rode de novo com `--bpm`.
Olhe também o volume a cada meio segundo: se houver pausa e "drop", dá pra fazer o corte do gancho cair no drop
(ajustando as batidas do gancho no plano).

Sem música (ela coloca no Instagram): não precisa desse passo, use o BPM informado (ou 128) e `--sem-som`.
Pra ela ouvir o ritmo, dá pra gerar uma batida de teste: `PY -I S/batidas.py --gerar-batida "TRAB/batida.mp3" --bpm 128 --dur 25`.

### 3. Plano

```bash
PY -I S/montar_plano.py "TRAB/brutos.json" --bpm 128 --saida "TRAB/plano.json" \
   --musica "musica.mp3" --musica-inicio 12.34          # ou --sem-som
   # opcionais: --alvo 17 (segundos) --flash 4 (0 tira o flash) --texto-gancho "texto"
```

Confira o que ele imprimiu e edite o `plano.json` se precisar. Cada cena tem:
`arquivo`, `inicio` (s), `batidas` (pode ser 0.5), `papel` (gancho, processo, flash, resultado),
`saida` (atravessa, sanfona, giro, seco) e opcionais `entrada` (gancho, soco, flash, giro, seco), `foco_x`, `deriva`
(zoom lento por segundo). No plano: `bpm`, `musica`, `musica_inicio`, `sem_som`, `texto_gancho`, `fonte_texto`,
`cor_texto`, `tamanho_texto` (84), `altura_texto` (0.15 = 15% do topo).

Regras do plano: total entre 15 e 20 s; cenas do processo com 1 ou 2 batidas (cerca de 0,4 a 0,95 s; a não ser de
propósito); as saídas variando (nunca 3 iguais seguidas); o flash repete cenas do processo; o resultado fica com
pelo menos 3 s no total. Com poucos vídeos (8 a 10), o `montar_plano.py` repete OUTROS momentos dos brutos do
processo (segunda passada) pra chegar no tempo; confira na folha se a repetição não ficou igual à primeira.

### 4. Prévia leve e folha de quadros (PORTÃO: não faça o final sem o "ok")

```bash
PY -I S/zoom_transicao.py --plano "TRAB/plano.json" --saida "TRAB/previa.mp4" --previa --folha "TRAB/folha-previa.jpg"
```

A prévia sai em 540x960 e leva uns 20 a 60 s. Abra a folha (Read) e confira: nenhuma cena preta ou repetida,
rosto e mãos não somem no zoom (se somem, mude o `inicio` ou o `foco_x`), giro sem borda preta, resultado nítido.
Mostre pra pessoa o caminho da prévia e a folha, explique em 2 ou 3 linhas (quantas cenas, duração, onde entra o
resultado) e ESPERE ela aprovar ou pedir ajuste.

### 5. Vídeo final

```bash
PY -I S/zoom_transicao.py --plano "TRAB/plano.json" --saida "ENTREGA/sanfoninha-<tema>.mp4" --folha "TRAB/folha-final.jpg"
```

Leva de 1 a 4 minutos. Confira a duração e se tem som (ou se está sem som, quando for o caso) e entregue o caminho.
Se for sem som, diga onde alinhar no Instagram: "escolha o trecho da música e deixe uma batida forte bem no
começo do vídeo; os cortes estão a cada X batidas de Y BPM".

### Ajustes rápidos

| Ela pediu | O que mudar |
|---|---|
| mais rápido / mais devagar | `batidas` das cenas (1 = mais rápido, 2 = mais calmo) |
| mais ou menos tempo de resultado | `batidas` das cenas de resultado, ou `--alvo` |
| sem giro | troque `giro` por `atravessa` ou `sanfona` nas `saida` |
| tirar o flash | `--flash 0` |
| zoom mais forte ou mais fraco | valores em `P` no topo do `zoom_transicao.py` (`soco_ate`, `hook_ate`, `deriva`) |
| texto no começo | `texto_gancho` no plano |

## Manual da Marca

Se existir `~/minha-marca/marca.json`, o script usa a fonte (`fontes.titulo`, procurada em `~/minha-marca/fontes/`)
e a cor (`cores.claro`, com sombra em `cores.escuro`) da pessoa **só no texto opcional do gancho**. O resto do
formato é fixo: não aplicar cores, legenda, emojis ou sons do manual neste formato. Sem manual, o texto sai branco
com sombra, em Inter Bold (ou Arial Bold).

## 2 prompts prontos (pra pessoa copiar)

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

Se ela for colocar a música no Instagram, trocar a linha da música por:
`Vou colocar a música no Instagram. Me entrega sem som, cortado no ritmo de [128] BPM.`

## Arquivos desta skill

- `scripts/olhar_brutos.py`: folhas de quadros de cada bruto + `brutos.json` com o início sugerido.
- `scripts/batidas.py`: BPM e início ajustado da música; também gera batida de teste.
- `scripts/montar_plano.py`: monta o `plano.json` (gancho, processo, flash, resultado).
- `scripts/zoom_transicao.py`: renderiza (prévia ou final) e faz a folha de quadros.
- `scripts/movimento.py`: mede zoom e giro quadro a quadro de uma referência nova (`PY -I S/movimento.py video.mp4`).
- `INSTALAR.md`: o que instalar no Mac e no Windows.
