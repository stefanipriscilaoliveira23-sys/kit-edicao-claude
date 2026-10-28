---
name: corte-viral
description: >-
  Transforma vídeo longo bruto (podcast, entrevista, live, aula) em clipes verticais 9:16 prontos para Shorts, Reels e TikTok. Cobre as quatro etapas — decupagem com timing por palavra, identificação dos trechos que funcionam fora de contexto, corte com in/out preciso, e enquadramento vertical com locutor ativo. Use quando o pedido for cortar podcast, achar cortes, "o que vira Short disso", clipar entrevista, decupar vídeo longo, deixar vertical, enquadrar pro Reels, ou refazer cortes redundantes. Também EDITA o Reel no jeito da marca da pessoa (título, legenda palavra por palavra, emojis, sons, cortes de respiro, voz limpa) lendo o Manual da Marca em ~/minha-marca/ (use quando pedirem "edita esse vídeo", "faz meu reels", "coloca legenda", "deixa no meu estilo"). Também cuida do ROTEIRO ANTES DE GRAVAR: use SEMPRE que a pessoa escrever "passo 0", "passo 1", "passo 2", "passo 3", "passo 4", "roteiro novo" ou "perguntas do vídeo sobre X" (método dos 4 passos da Jessica Carter, em modelo-edicao/ROTEIRO-PASSOS.md).
effort: high
allowed-tools:
  - Agent
  - Read
  - Write
  - Edit
  - Bash(mlx_whisper *)
  - Grep
  - Glob
  - Bash(~/.claude/skills/corte-viral/vch *)
  - Bash(~/.claude/skills/corte-viral/verificar.py *)
  - Bash(python3 ~/.claude/skills/corte-viral/scripts/vch.py *)
  - Bash(ffprobe *)
  - Bash(ffmpeg *)
---

# Do bruto ao vertical

Quatro entregas em sequência, **cada uma com um portão**. Você para no portão,
mostra o resultado e espera o usuário dizer o que segue. Só emende as quatro numa
run só quando ele pedir explicitamente ("vai até o fim", "manda o pacote todo").

| # | Entrega | O que sai | Você lê |
| --- | --- | --- | --- |
| **1** | **MOMENTOS** | a lista dos trechos que dariam corte, com timestamp e citação | `fases/1-momentos.md` |
| **2** | **CORTES** | os trechos já cortados, em vídeo, para assistir | `fases/2-cortes.md` |
| **3** | **VERTICAL** | 9:16 com o locutor rastreado e reenquadrado | `fases/3-vertical.md` |
| **4** | **ENTREGA** | pasta final verificada, pronta para a motion-vox | `fases/4-entrega.md` |

> **Leia SÓ o arquivo da fase em que você está.** Carregar as quatro de uma vez
> era o que fazia esta skill custar ~6.800 palavras antes da primeira ação útil,
> a maior parte sobre render e enquadramento, num pedido que às vezes era só
> "quais são os bons momentos". A fase 1 sozinha precisa de ~1.200.

## A regra que decide o custo da run

**Nenhum agente lê `02-transcript.json`.** Medido num podcast de 3h: o artefato
cru custa **1.346.173 tokens** — não cabe numa janela — e 9 em cada 10 desses
tokens são `words[]`, timing por palavra que o modelo **não usa** para escolher
trecho. Timing por palavra é para os scripts.

| Quem precisa de quê | Comando | Custo |
| --- | --- | --- |
| escolher trecho (fases 1) | `vch digest --run <run>` | 62.758 tok — **21,5x menos** |
| cravar in/out (fase 2) | `vch digest --run <run> --windows "a-b,c-d"` | 2.974 tok — **452x menos** |
| in/out, legenda, autoframe | os scripts, direto no JSON | não passa por LLM |

E **você, no loop principal, não lê texto longo** — nem transcript, nem digest.
Você lê os artefatos JSON, que são compactos. Quem lê texto longo é subagente,
em contexto próprio, que morre no fim da passagem.

## A ordem é fixa

```text
TIMESTEPS  →  SELEÇÃO  →  CORTE  →  VERTICAL
    ↑ sempre        ↑ só texto      ↑ só aqui o bruto é aberto
    primeiro
```

**A skill nunca começa analisando o vídeo bruto**, e os timesteps são
pré-requisito de tudo: sem transcript com timing **por palavra**, a fase 1 não
começa — ver a decupagem em `fases/1-momentos.md`. Isso não é um modo entre
outros; é a única ordem. O que varia é **até que fase** ir.

## Sempre carregado

Só `~/.claude/skills/corte-viral/REGRAS.md` — as 11 regras invioláveis e a
missão. Tudo mais é carregado pela fase que precisa:

| Fase | Carrega além do REGRAS.md |
| --- | --- |
| 1 | `docs/05-regras-de-selecao.md` |
| 2 | `docs/06-regras-de-edicao.md`, `docs/12-erros-registrados.md` |
| 3 | `config/default.yaml`, `config/platforms/<platform>.yaml` |
| 4 | nada |

## O kit viaja junto

| | |
| --- | --- |
| `fases/` | as quatro fases — leia uma por vez |
| `scripts/` | o motor: transcrição, métricas, enquadramento, render, QC |
| `agentes/` | os 8 subagentes — a **fonte**; precisam estar em `~/.claude/agents/` |
| `docs/` | seleção, edição, psicologia de feed, erros já cometidos |
| `config/` | default + 3 plataformas + 12 perfis narrativos |
| `schemas/` | os 15 contratos JSON de cada artefato |
| `models/` | YuNet, detecção facial do enquadramento automático |
| `verificar.py` | checagem de instalação — rode antes do primeiro projeto |
| `vch` | o lanchador: use sempre este, nunca `python3 scripts/vch.py` |
| `modelo-edicao/` | a edição no jeito da marca: guia, catálogo de técnicas, roteiro e os scripts (leem `~/minha-marca/`) |
| `modelo-minha-marca/` | modelo da pasta `~/minha-marca/` (manual da marca + base de roteiros) |
| `ENTREVISTA-DA-MARCA.md` | as perguntas pra montar o manual da marca quando ele não existe |
| `bin/` | o `deep-filter` (limpeza de voz por IA), baixado na instalação: `bin/COMO-BAIXAR.md` |

O `python3` do PATH pode ser antigo (o Mac vem com 3.9) e o pacote exige 3.10+. O
lanchador `vch` resolve sozinho o interpretador certo — a venv da própria skill.

**Nem todo subagente roda em toda fase.** São 8 no total, mas a fase 1 usa 2. Não
invoque agente de fase que você ainda não abriu.

## Antes do primeiro projeto

```bash
~/.claude/skills/corte-viral/verificar.py
```

Se acusar agente ausente ou dependência faltando, ver `INSTALAR.md`. Não comece
com instalação incompleta: o pipeline quebra no meio, depois de já ter gasto a
transcrição.

## Argumentos

Aceite vídeo com transcrição opcional; só transcrição, para análise sem render;
`--run <run-dir>` para continuar; `--max-clips N` **como teto, nunca como meta**;
`--platform cross-platform`, `tiktok` ou `instagram-reels`.

Não peça confirmação quando caminho e plataforma puderem ser inferidos — o
portão de cada fase já é o ponto de conversa.

## Onde a run mora

**`--workspace` é obrigatório no `init`.** Sem ele a run é gravada dentro de
`~/.claude/skills/` e some da vista do projeto. Aponte para a pasta do vídeo.

## Fronteira com a motion-vox

No pipeline de cortes (fases 1 a 4) esta skill entrega `clip-vertical.mp4` **limpo** — sem legenda
queimada e sem motion. A legenda, o título e os efeitos no jeito da marca entram depois, pelo `modelo-edicao/`
(composição HyperFrames). A skill `motion-vox` é opcional e não vem neste pacote.

Os `captions.srt`/`.ass` são gerados sempre: são **decupagem**, não legenda
queimada. É o timing por palavra que a motion-vox usa para ancorar cada evento
na fala. Não pule, e não queime legenda aqui antes de mandar — seriam duas.

## Edição no jeito da marca

Pra editar o vídeo da pessoa (legenda, títulos, efeitos, sons), nesta ordem:

1. **Manual da Marca primeiro.** Rode `python3 ~/.claude/skills/corte-viral/modelo-edicao/marca.py conferir`.
   Se `~/minha-marca/` não existir ou estiver incompleta, faça a entrevista de `ENTREVISTA-DA-MARCA.md` (pergunta por
   pergunta, linguagem simples) e crie a pasta a partir de `modelo-minha-marca/` ANTES de editar. Depois leia o
   `~/minha-marca/MINHA-MARCA.md` inteiro: o que está lá vence qualquer padrão desta skill.
2. Leia `modelo-edicao/JEITO-DA-MARCA.md` (regras técnicas e processo: cortes, respiros, olhar pra baixo, área segura do
   Reels, voz e pofs, limpeza da entrevistadora, conferência por quadros, pipeline) e, se ela citar um código, o catálogo
   `modelo-edicao/CATALOGO-TECNICAS.md` (118 técnicas: T, C, M, S, E, F, P, L, Q, V, as receitas Recibo, Editorial e Bastidor e os formatos com nome). A definição do código é a de lá.
3. Os scripts de `modelo-edicao/` leem cores, fontes, legenda, emojis, volume e pastas do `~/minha-marca/marca.json`
   (via `marca.py`). Na primeira vez, `python3 modelo-edicao/preparar_pasta.py` monta a pasta de trabalho.
   Texto ATRÁS da pessoa (T11/C4) e o close do `retrato.py` funcionam no Windows e no Mac: o recorte da pessoa sai do
   `modelo-edicao/mascara.py` (HyperFrames `remove-background`; no Mac, `MASCARA_MOTOR=vision` é mais rápido).
4. **Toda correção vira regra:** cada ajuste que a pessoa aprovar entra, com data, em "Regras aprovadas" do
   `MINHA-MARCA.md` (e no `marca.json` quando for valor de script). Nunca deixe a regra só na conversa.

**Formatos com nome:** Narradinho → `modelo-edicao/receita-narradinho/NARRADINHO.md` (vídeo narrado tipo vlog: cenas numeradas 00, 01, 02... + narração gravada à parte; a cena troca na palavra que cita a coisa nova). Quando a pessoa pedir "faz um narradinho", ler esse arquivo e seguir os 2 portões (montagem limpa com tabela cena x fala; depois edição completa). Os 3 prompts prontos estão no fim dele.

## Roteiro antes de gravar (passos 0 a 4)

Quando a pessoa escrever "passo 0", "passo 1", "passo 2", "passo 3", "passo 4", "roteiro novo" ou "perguntas do vídeo sobre X",
NÃO é pedido de corte: leia SÓ `modelo-edicao/ROTEIRO-PASSOS.md` e siga. Ela não cola prompt nenhum; o prompt de cada passo está lá.
Os arquivos de apoio (voz dela, psicologia, kit fixo, moldes, perguntas e os roteiros salvos) ficam em
`~/minha-marca/roteiros/` (se não existir, copie de `modelo-minha-marca/roteiros/`).
