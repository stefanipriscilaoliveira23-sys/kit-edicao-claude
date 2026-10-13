# 11. Operação no Claude Code

## Onde a skill mora

```text
~/.claude/skills/corte-viral/     a skill (kit fechado, roda de qualquer pasta)
~/.claude/agents/                 os 8 subagentes — é daqui que o Claude Code os lê
```

A pasta `agentes/` dentro da skill é a **fonte**; `~/.claude/agents/` é o local de
registro. Depois de atualizar a skill, recopie:

```bash
cp ~/.claude/skills/corte-viral/agentes/*.md ~/.claude/agents/
```

`verificar.py` acusa cópia ausente ou defasada. Ao criar a pasta de agentes pela
primeira vez numa sessão já aberta, reinicie o Claude Code para garantir a
detecção; versões recentes observam alterações em diretórios já existentes.

## Como chamar

A skill é invocável pelo modelo — "corta esse podcast", "o que vira Short disso",
"deixa vertical". Diretamente:

```text
/corte-viral /Users/paul/Videos/podcast.mp4 --mode full
```

## Onde as runs ficam

Sempre no projeto, nunca dentro da skill:

```bash
~/.claude/skills/corte-viral/vch init VIDEO.mp4 LEGENDA.vtt \
  --mode full --workspace /Users/paul/Downloads/Canal/PROJETO/runs
```

Sem `--workspace`, a run cai em `~/.claude/skills/corte-viral/workspace/runs/` e
some da vista do projeto.

## Modos

| Modo | Faz |
| --- | --- |
| `analyze` | decupagem + seleção, sem render |
| `verify` | acrescenta auditoria técnica e revisão cega |
| `render` | corta e renderiza o vertical |
| `full` | tudo |

## O lanchador

Todo comando passa por `~/.claude/skills/corte-viral/vch`. Ele escolhe o
interpretador correto (a venv da skill, Python 3.11) — o `python3` do PATH neste
Mac é o 3.9 do sistema e não roda o pacote.

## Retomar uma run

```bash
~/.claude/skills/corte-viral/vch init --run <run-dir>
```

Os artefatos numerados `00`–`16` dizem onde parou. Não recomece do zero: a
transcrição e o índice visual são a parte cara.
