---
name: motion-vox
description: Insere motion graphics no estilo editorial da Vox e legenda queimada dentro de um clipe vertical ja cortado (podcast, entrevista, talking head). Use quando o pedido for adicionar motion, ilustrar palavras-chave, animar trechos, "colocar uns motions nesse corte", "ilustrar essa fala", queimar legenda no clipe, ou melhorar e estender motions ja feitos. Cobre o processo inteiro: escolher as frases pelo transcript, gerar e recortar assets PNG, compor as cenas em camadas com registros visuais variados, legendar, revisar com rubrica, e montar o master sem tocar no audio. NAO use para video gerado do zero por IA de video.
---

# Motion editorial sobre footage

Insere cenas de motion no estilo `VOX-EXPLAINER-LABS` dentro de um clipe vertical que
**já existe**. O áudio é congelado: não dá para reescrever a fala, então tudo se ancora
no que foi dito e em quando foi dito.

## A identidade viaja junto

Esta skill é um **kit fechado**, não só um método. Ver `IDENTIDADE.md`.

| | |
| --- | --- |
| `fontes/` | as 5 fontes da identidade, licenças livres, com os arquivos de licença |
| `assets/` | 9 objetos recortados prontos, mais o manifesto; os outros 7 do kit são gerados sob demanda (ver "Quando faltar um objeto") |
| `lib/` | o motor, o recorte, o CRT, a legenda, a transcrição, os dois templates, `gerar_asset.py` (objeto novo) e `marca.py` (cores) |
| `exemplo/` | o bloco de configuração de um clipe real, com o motivo de cada escolha |
| `verificar.py` | checagem de instalação — rode antes do primeiro projeto |
| `referencias/` | identidade, registros, transições, legenda, armadilhas, rubricas, prompts |

Quem instalar reproduz **este** visual, não um parecido.

**Cores da sua marca.** Os dois acentos (amarelo `#DBD653` e azul `#2E82F7`) podem ser
trocados sem mexer no código: crie `~/minha-marca/marca.json` com
`{"cor_destaque_1": "#RRGGBB", "cor_destaque_2": "#RRGGBB"}` — o 1 substitui o amarelo
(sublinhado de marcador), o 2 substitui o azul (linha de continuidade e foto noturna).
Sem o arquivo, valem as originais. `python3 lib/marca.py` mostra quais estão valendo.
Papel, tinta, sombras e fontes não mudam.

## Requisitos de máquina

| | | Se faltar |
| --- | --- | --- |
| `python3` + `Pillow`, `numpy`, `opencv-python` | composição e recorte | nada roda |
| `ffmpeg` | montagem do master | os frames saem, o vídeo não |
| `faster-whisper` | transcript palavra a palavra | sem ancoragem e sem legenda |
| gerador de imagem | **só** para objeto que o kit não tem | sem ele, a usuária gera pelo ChatGPT/Gemini com o prompt pronto — ver "Quando faltar um objeto" |

**Antes do primeiro projeto:** `python3 verificar.py`. Ver `INSTALAR.md`.

**Transcript.** Insumo sem substituto — motion ancorado e legenda em corte seco dependem
de saber em que frame cada palavra foi dita. Gere com:

```bash
python3 lib/transcrever.py 00_brief/fonte.mp4 00_brief/transcript_palavras.json
```

Formato: `[{"w": "palavra", "t": 12.28, "e": 12.54}, ...]`, em segundos **do clipe**.
Já tem transcript em outro formato? Converta para este — não reescreva o motor.

**`night_photo.py` e `crt.py` trazem constantes calibradas** para as fotos do kit
(recorte, curva de cor, quadrilátero da tela). Ao gerar fotografia nova, recalibre — os
dois scripts dizem onde.

## Regra-mãe

> **Mostrar uma prova, apontar o detalhe, concluir — nesta ordem.**
> Movimento acompanha raciocínio. Nada se mexe só para "dar dinâmica".

## O que NÃO usar

Não gere vídeo com IA de vídeo. A composição por camadas em PIL dá controle exato de
posição, tempo e grafia, e produz o mesmo resultado com custo muito menor. IA de imagem
entra **só** para gerar objetos físicos e fotografias.

## Ordem de execução

Cada etapa tem uma trava. Não avance sem ela.

| # | Etapa | Saída | Trava |
| --- | --- | --- | --- |
| 1 | **Ancorar** | tabela palavra → frame | transcript palavra-a-palavra existe |
| 2 | **Escolher frases** | tabela entra/não-entra com motivo | cada corte tem justificativa escrita |
| 3 | **Gerar assets** | PNG cru por objeto | zero texto de IA, zero sombra embutida |
| 4 | **Recortar** | PNG com alfa | laudo D1 aprovado |
| 5 | **Compor** | 4 estados por cena | laudo D2/D3 aprovado |
| 6 | **Blueprint + transições** | um .md por cena + mapa | entrada e saída definidas |
| 7 | **Legenda** | sequência RGBA de duração total | nenhuma palavra dita fica de fora |
| 8 | **Render + mux** | master | duração, cadência e MD5 do áudio batem com a fonte |

Leia `referencias/rubricas-diretor.md` antes da etapa 4 e aplique em 4, 5 e 7.
Escolha o registro de cada cena em `referencias/registros.md` **antes** de compor.
Legenda queimada: `referencias/legenda.md`. Saídas e transições: `referencias/transicoes.md`.
Boil (o objeto redesenhado a cada passo): `referencias/boil.md`.

---

## 1. Ancorar no transcript

Converta cada palavra para frame local do plano:

```
frame24 = (t_palavra − t_início_do_plano) × 24
```

**Todo evento visual se trava numa palavra**, com tolerância de ±3 frames. Um elemento
que entra fora da palavra vira enfeite: o espectador não liga uma coisa à outra.

Sem transcript com timestamp por palavra, pare e produza um antes (Whisper com
`word_timestamps`, ou legendas do YouTube).

## 2. Escolher as frases

Entra a frase que tem **objeto**. Não entra a que só tem conceito.

| Critério | Entra | Não entra |
| --- | --- | --- |
| tem substantivo concreto ou unidade de medida | ✓ | |
| é a instrução ou o payoff do clipe | ✓ | |
| número que o falante **se autocorrige** ou estima ("sei lá") | | ✗ em tipografia de dado |
| piada lateral, aparte | | ✗ |
| já ilustrado por outra cena | | ✗ |
| grandiloquência sem objeto ("primeira vez na história") | | ✗ |

**Registro de fato vs. opinião.** Número dito pelo entrevistado só vira gráfico limpo se
for verificável. Estimativa vira **marcador manual** ou não entra.

**Varie o REGISTRO, nao so o objeto.** Tres cenas seguidas de "mesa + objeto + fita"
leem como a mesma cena, por mais que os objetos mudem. Nunca repita registro em cenas
vizinhas — a tabela esta em `referencias/registros.md`.

**Densidade.** Mire em 30–40% do clipe coberto por motion. Abaixo de 20% o vídeo fica
parado; acima de 50% o rosto some. Deixe pelo menos 1,5s de rosto entre cenas.

**Escreva a tabela dos que ficaram de fora, com o motivo.** A decisão descartada é tão
útil quanto a adotada, e evita refazer a discussão depois.

## 3. Gerar os assets

Um prompt por objeto. Templates completos em `referencias/prompts-asset.md`.

**Fundo: escolha pelo maior afastamento de LUMINÂNCIA do objeto.**

| Objeto | Fundo |
| --- | --- |
| papel, cartão, objeto claro | cinza médio `#8A8A8A` |
| objeto escuro (teclado, metal escuro) | cinza claro `#D8D8D8` |
| objeto de luminância média E neutro | último recurso: chroma |

Testado: **pedir "fundo transparente" não funciona** — o modelo devolve RGB sem canal
alfa, e o pedido produz um fundo cinza sólido. **Fundo chroma** torna o recorte trivial
mas contamina ~65% dos pixels de borda com spill da cor, o que estraga justamente a
borda — que neste estilo é a matéria (fibra de papel rasgado, metal fosco).

Sempre no prompt, sem exceção:

- `no cast shadow on the backdrop` — sombra é camada, não pixel do asset
- `no text, no letters, no numbers, no logo, no brand`
- `no glow, no bloom, no neon, no gradients, no HDR, no AI-polished look`
- objeto isolado, top-down, luz difusa uniforme

**Relógio e qualquer mostrador:** peça **sem números, só tracinhos**, e redesenhe os
ponteiros em PIL. Assim a hora vira dado controlado e animável, e não sobra texto de IA.

## 4. Recortar

Use `lib/cutout.py`. Três passes, e a ordem importa:

1. **Flood** `FIXED_RANGE` semeado nas bordas. A tolerância sai de uma **varredura**
   (`python3 cutout.py --sweep NOME`): escolha o **platô**, o ponto a partir do qual
   aumentar a tolerância não remove mais nada.
2. **Sombra.** O fundo cresce, restrito à faixa onde a sombra mora: pixel neutro, liso,
   e do lado certo em luminância. `dark_floor` inverte a regra para objeto escuro.
3. **Fundo encapsulado.** Miolo de clipe de papel tem cor de fundo mas o flood não chega.

Tolerância relativa ao vizinho foi testada e **reprovada**: escorre por gradiente liso e
come o interior de objetos chapados.

## Quando faltar um objeto

**Antes de montar qualquer cena, confira se o objeto existe em `assets/`.** Se a cena pede
uma caneca e o kit não tem caneca, a IA **gera** a caneca. Não troque por outro objeto
"parecido" e não pule a cena.

1. **Tem gerador de imagem?** (chave do Gemini ou da OpenAI na variável de ambiente
   `GEMINI_API_KEY` / `OPENAI_API_KEY`, ou uma skill de imagem instalada)
   → gere com o esqueleto de `referencias/prompts-asset.md`:
   ```bash
   python3 gerar_asset.py A20_CANECA --objeto "One white ceramic coffee mug" \
       --material "Matte glaze, small chip on the rim" --fundo claro
   ```
   → recorte com `cutout.py` (`--sweep`, escolha o platô, entre no `CFG`) → confira o
   PNG aberto (sem letra, sem número, sem sombra, borda limpa; se tiver texto, gere de
   novo) → salve em `assets/` **e** acrescente uma linha em `assets/MANIFESTO.md`.
2. **Não tem gerador** (ou a chave está sem crédito/cota — o script avisa)
   → entregue à usuária o prompt pronto (`python3 gerar_asset.py NOME --objeto "..."
   --so-prompt`) e diga, em português simples: *"Cole este texto no ChatGPT ou no app do
   Gemini (dá até pelo celular), peça a imagem quadrada e me mande a imagem de volta."*
   → quando ela mandar: `python3 gerar_asset.py NOME --importar caminho/da/imagem` → recorte,
   confira e salve igual ao passo 1.

Regras que não mudam:

- **Nunca** use imagem da internet sem licença livre. Banco de imagem, print do Google ou
  foto de produto de marca: não.
- O prompt é sempre o esqueleto (objeto isolado, de cima, fundo cinza liso, sem texto,
  sem sombra). Prompt sem as proibições volta com letra de IA e sombra embutida.
- **Todo objeto novo entra no kit** (`assets/` + `MANIFESTO.md`) — da próxima vez ele já
  existe. Nome no padrão `A##_NOME`, número livre seguinte.
- A chave **nunca** vai para arquivo da skill: só variável de ambiente, durante o comando.

## 5. Compor

**Divisão de trabalho — não negociável:**

| Camada | Origem | Motivo |
| --- | --- | --- |
| fundo, objetos físicos, fotografias | IA de imagem | materialidade |
| **todo texto** | PIL, fonte local | grafia garantida |
| **toda anotação** (círculo, seta, sublinhado, linha) | PIL procedural | precisa ser desenhável em progresso |
| sombra de contato, grão, vinheta | PIL | intensidade por camada |

Anotação procedural não é economia: é o que permite renderizar "seta 40% desenhada"
sem regerar imagem.

**Uma timeline por cena, quatro estados amostrados dela:** `START` (frame 0),
`MID` (beat DIRECT), `END` (último evento concluído), `EXIT` (fim do plano). Os estados
são coerentes por construção — nenhum pode contradizer outro sem que o código esteja
errado.

Confira que `END` cai **depois** do último evento, senão o estado mostra texto pela metade.

Detalhes de paleta, tipografia, safe zones e sombras: `referencias/identidade.md`.
Erros que já custaram retrabalho: `referencias/armadilhas.md` — **leia antes de compor**.

## 6. Entrada, saída e transição

| Tipo | Entrada | Saída |
| --- | --- | --- |
| **cutaway** (cobre o vídeo) | corte seco, herói **já em voo no frame 0** — o corte é a revelação | **três tipos alternados** — `slide`, `wipe`, `push`. Corte seco sozinho lê como tranco, e repetir a mesma saída vira tique. Ver `referencias/transicoes.md` |
| **overlay** (sobre o vídeo) | animada, com trajetória | volta por onde entrou, com fitas e anotação **presas ao objeto** |

Hold de 8–18 frames antes de qualquer saída. Melhor ponto de corte é o **silêncio** entre
palavras.

Continuidade honesta: dois elementos separados por dezenas de segundos não formam match
cut. Registre como **motivo recorrente**. O que amarra de verdade é **objeto herdado** —
o mesmo prop voltando com outro estado.

## 7. Render e montagem

Use `lib/render.py`. **Montagem por sobreposição, nunca por corte-e-concatenação.**

- cutaway = frames opacos; overlay = RGBA, e o plate nunca é reprocessado
- a timeline pode ser 24fps mesmo com o clipe em 29,97: avalie cada frame de saída no
  tempo real (`frame24 = t × 24`, com fração). Converter cadência depois gera judder.
- grão: campo **borrado** (σ≈0,9) e **"on twos"**. Ruído branco por pixel e por frame é
  incompressível e leva o bitrate a 120 Mbps.

**Verificação obrigatória do master**, contra a fonte: duração, cadência, contagem de
frames e **MD5 do áudio** (`ffmpeg -i x.mp4 -map 0:a -f md5 -`).

---

## Começar um projeto

```bash
mkdir -p PROJETO && cd PROJETO
cp -r ~/.claude/skills/motion-vox/lib/*.py .
cp -r ~/.claude/skills/motion-vox/fontes .
mkdir -p 07_assets/cutout && cp ~/.claude/skills/motion-vox/assets/*.png 07_assets/cutout/
cp ~/.claude/skills/motion-vox/assets/*.npy 07_assets/cutout/ 2>/dev/null   # só existe depois que o A14_CRT for gerado
mv 07_assets/cutout/BG_PAPER.png 07_assets/raw/ 2>/dev/null || \
  (mkdir -p 07_assets/raw && mv 07_assets/cutout/BG_PAPER.png 07_assets/raw/)
cp ~/.claude/skills/motion-vox/lib/compose_template.py compose.py
```

`fontes/` tem que ficar ao lado de `voxlab.py` — a identidade depende dela e o motor
falha com mensagem clara se não achar.

```
PROJETO/
  00_brief/PLANO_MOTION.md      frases escolhidas e recusadas, com motivo
  05_motion/M#_motion.md        blueprint por cena
  06_transitions/TRANSITION_MAP.md
  07_assets/{raw,cutout}/
  08_images/frames/             os 4 estados por cena
  09_plates/                    frames do vídeo para as cenas de overlay
  10_sequences/                 PNG por frame, por cena
  11_qa/LAUDO_*.md              laudos do Diretor
  12_master/
  voxlab.py cutout.py compose.py render.py    (copiar de lib/)
```

O `bg_paper()` do template lê `07_assets/raw/BG_PAPER.png`; os demais assets saem de
`07_assets/cutout/`. Escreva as cenas a partir de `compose_template.py`.

## Ao editar em lote

`str.replace()` devolve a string **intacta** quando o padrão não casa — patch silencioso.
Depois de qualquer rodada de patches, confirme por `grep -cF` que cada padrão crítico
entrou. Para edição que depende do contexto ao redor, use a ferramenta Edit, que **erra**
se não casar.
