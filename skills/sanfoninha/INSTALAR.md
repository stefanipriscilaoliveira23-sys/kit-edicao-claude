# INSTALAR.md (instruções para o Claude)

A skill Sanfoninha precisa de 3 coisas: **ffmpeg**, **Python 3.10 ou mais novo** e 3 bibliotecas do Python
(**numpy**, **opencv** e **Pillow**). Instale só o que faltar e fale com a pessoa em português simples.

## 1. ffmpeg

| Mac | Windows |
|---|---|
| `brew install ffmpeg`. Sem Homebrew: baixe os binários estáticos de `ffmpeg` e `ffprobe` (evermeet.cx) para `~/.local/bin/` e dê permissão de execução (`chmod +x`). | `winget install Gyan.FFmpeg` e feche e abra o terminal (o ffmpeg passa a ficar no PATH). |

Os scripts procuram o ffmpeg primeiro em `~/.local/bin/` e depois no PATH. Conferir: `ffmpeg -version`.

## 2. Python

| Mac | Windows |
|---|---|
| `python3 --version`. Se faltar: `brew install python@3.11` ou o instalador de python.org. | `python --version`. Se faltar: `winget install Python.Python.3.11`. |

## 3. Ambiente próprio da skill (recomendado)

Cria uma pasta `.venv` dentro da skill, assim nada mexe no Python do computador.

Mac:
```bash
cd ~/.claude/skills/sanfoninha
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install numpy opencv-python-headless pillow
```

Windows (PowerShell):
```powershell
cd $HOME\.claude\skills\sanfoninha
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install numpy opencv-python-headless pillow
```

Se o Python do computador já tiver as 3 bibliotecas, a `.venv` não é obrigatória: a skill usa o `python3`
(ou `python` no Windows) direto.

## 4. Conferir

Mac:
```bash
~/.claude/skills/sanfoninha/.venv/bin/python -I -c "import numpy, cv2, PIL; print('ok', cv2.__version__)"
~/.claude/skills/sanfoninha/.venv/bin/python -I ~/.claude/skills/sanfoninha/scripts/batidas.py --gerar-batida /tmp/teste-batida.mp3 --bpm 128 --dur 5
```

Windows:
```powershell
& "$HOME\.claude\skills\sanfoninha\.venv\Scripts\python.exe" -I -c "import numpy, cv2, PIL; print('ok', cv2.__version__)"
& "$HOME\.claude\skills\sanfoninha\.venv\Scripts\python.exe" -I "$HOME\.claude\skills\sanfoninha\scripts\batidas.py" --gerar-batida "$env:TEMP\teste-batida.mp3" --bpm 128 --dur 5
```

Se as duas linhas funcionarem, está pronto. Diga à pessoa:

> Pronto! Agora é só me mandar os vídeos numerados (01, 02, 03...) e pedir: "faz um sanfoninha".

## Problemas comuns

- `No module named cv2`: o comando rodou com outro Python. Use o caminho da `.venv` acima.
- `Nao achei o ffmpeg`: o ffmpeg não está em `~/.local/bin` nem no PATH. Refaça o passo 1 e abra um terminal novo.
- Vídeo do iPhone em HEVC (.mov) abre normalmente com o ffmpeg; não precisa converter.
- Texto do gancho sem a fonte da marca: confira se o arquivo da fonte está em `~/minha-marca/fontes/` com o
  mesmo nome que está em `marca.json` (`fontes.titulo`).
