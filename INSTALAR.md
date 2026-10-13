# INSTALAR.md (instruções para o Claude)

Você (Claude) está instalando o Kit de Edição para uma aluna que NÃO é técnica.
Fale com ela sempre em português simples, sem termos técnicos. Explique em uma linha o que está fazendo antes de cada etapa demorada. Nunca apague arquivos dela.

Siga as etapas em ordem. Se uma etapa falhar, tente resolver sozinho; só pergunte para ela quando precisar de uma decisão ou de uma senha do computador (nesse caso, peça que ela mesma digite no Terminal).

## 0. Descobrir o computador

- Sistema: Mac (Apple Silicon ou Intel) ou Windows.
- Já existe `~/kit-edicao-claude`? Então é ATUALIZAÇÃO: rode `git pull` lá dentro e vá direto para a etapa 2 (pule o que já estiver instalado).

## 1. Baixar o kit

```bash
git clone https://github.com/stefanipriscilaoliveira23-sys/kit-edicao-claude.git ~/kit-edicao-claude
```

Sem git no Windows: `winget install --id Git.Git -e`. No Mac, se o git pedir as ferramentas de desenvolvedor, deixe instalar.

## 2. Colocar as skills no lugar

Para cada pasta em `~/kit-edicao-claude/skills/`:
- se já existir uma pasta com o mesmo nome em `~/.claude/skills/`, mova a antiga para `~/.claude/skills-backup/<nome>-<data>/` antes;
- copie a pasta nova para `~/.claude/skills/<nome>/`.

Copie também os ajudantes da corte-viral: `~/.claude/skills/corte-viral/agentes/*.md` para `~/.claude/agents/`.

## 3. Programas que as skills usam

Instale só o que faltar (confira a versão antes):

| Programa | Mac | Windows |
|---|---|---|
| Python 3.11 ou mais novo | `brew install python@3.11`; sem Homebrew, instalador oficial de python.org | `winget install Python.Python.3.11` |
| ffmpeg e ffprobe | `brew install ffmpeg`; sem Homebrew, binários estáticos (evermeet.cx) em `~/.local/bin` e esse caminho no PATH | `winget install Gyan.FFmpeg` |
| Node.js 22 ou mais novo | `brew install node`; sem Homebrew, instalador de nodejs.org | `winget install OpenJS.NodeJS.LTS` |

Depois:
1. **corte-viral**: siga `~/.claude/skills/corte-viral/INSTALAR.md` (cria o ambiente Python próprio da skill, baixa o limpador de voz DeepFilterNet certo para o sistema dela e confere com `verificar.py`).
2. **motion-vox**: siga `~/.claude/skills/motion-vox/INSTALAR.md` e rode `verificar.py`.
3. **Transcrição**: é sempre no próprio computador, com faster-whisper (modelo `large-v3-turbo`, baixa ~1,5 GB na primeira vez). Avise a aluna que a primeira vez demora. Nunca use serviço pago de transcrição.
4. **hyperframes e media-use** (oficiais, gratuitos):
   ```bash
   claude plugin marketplace add heygen-com/hyperframes
   claude plugin install hyperframes@hyperframes
   ```
   Se o comando `claude` não existir no terminal, copie cada pasta de `~/kit-edicao-claude/skills-extra/hyperframes/skills/` para `~/.claude/skills/` (veja `skills-extra/hyperframes/COMO-INSTALAR.md`).
5. **Sons extras (opcional)**: `~/.claude/skills/corte-viral/modelo-edicao/` tem um `SONS-PARA-BAIXAR.md` com sons gratuitos que não podem vir no pacote. Sem eles, a edição usa os sons parecidos que já vêm no kit. Pergunte à aluna se ela quer baixar.

## 4. Pastas da aluna

Crie, sem apagar nada que já exista:
- `~/minha-marca/` copiando de `~/kit-edicao-claude/manual-da-marca-modelo/` SOMENTE se ainda não existir. Se já existir, NUNCA sobrescreva (é o manual dela).
- `~/Videos-Claude/_trabalho/` (rascunhos) e `~/Videos-Claude/PRONTOS/` (vídeos finais).
- `~/Carrosseis-Claude/` (lâminas prontas).

## 5. Conferir e avisar

- Rode os `verificar.py` da corte-viral e da motion-vox. Conserte o que der erro.
- Diga para a aluna, em poucas linhas e sem termos técnicos: o que foi instalado, onde ficam os vídeos prontos e qual é o próximo passo:

> Tudo instalado! Agora vamos montar o seu Manual da Marca. Me manda: "Monta meu manual da marca".

## Atualizar ("atualiza meu kit de edição")

`git pull` em `~/kit-edicao-claude`, repita as etapas 2, 3 (só o que mudou) e 5. NUNCA mexa em `~/minha-marca/`, `~/Videos-Claude/` e `~/Carrosseis-Claude/`.
