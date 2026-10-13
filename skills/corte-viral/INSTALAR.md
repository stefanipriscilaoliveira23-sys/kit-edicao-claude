# Instalar a corte-viral (Mac e Windows)

## O jeito mais fácil

Abra o Claude Code e escreva:

> Claude, instala a corte-viral pra mim seguindo o INSTALAR.md

Ele faz tudo abaixo sozinho e te avisa quando precisar de você (por exemplo, pra digitar a senha do computador numa
instalação). Leva uns 20 a 40 minutos, quase tudo é download.

O resto deste arquivo é o passo a passo que o Claude segue.

---

## 0. Onde a skill mora

Copie a pasta `corte-viral` inteira para a pasta de skills do Claude:

- Mac: `~/.claude/skills/corte-viral/`
- Windows: `C:\Users\SEU-NOME\.claude\skills\corte-viral\`

No Windows, o Claude Code usa o Git Bash pros comandos (`.sh`). Se o Git não estiver instalado:
`winget install Git.Git`.

## 1. Programas do computador

| Programa | Pra quê | Mac | Windows (PowerShell) |
| --- | --- | --- | --- |
| Python 3.11 | roda os scripts | `brew install python@3.11` (ou o instalador de python.org) | `winget install Python.Python.3.11` |
| ffmpeg + ffprobe | corta, junta, mede e trata o áudio | `brew install ffmpeg` | `winget install Gyan.FFmpeg` |
| Node 22 | roda o HyperFrames (render da edição) | `brew install node@22` (ou o instalador de nodejs.org) | `winget install OpenJS.NodeJS.LTS` |

Sem Homebrew no Mac: instale em https://brew.sh ou use os instaladores dos sites oficiais (python.org, nodejs.org) e o
ffmpeg estático de https://evermeet.cx/ffmpeg/ (ffmpeg e ffprobe em `~/.local/bin`, que precisa estar no PATH).

Confira: `python3.11 --version` (Windows: `py -3.11 --version`), `ffmpeg -version`, `ffprobe -version`, `node --version`.

## 2. Python da skill (venv) com faster-whisper e o resto

Mac:
```bash
python3.11 -m venv ~/.claude/skills/corte-viral/.venv
~/.claude/skills/corte-viral/.venv/bin/python -m pip install -r ~/.claude/skills/corte-viral/requirements.txt
```

Windows (PowerShell):
```powershell
py -3.11 -m venv $env:USERPROFILE\.claude\skills\corte-viral\.venv
& $env:USERPROFILE\.claude\skills\corte-viral\.venv\Scripts\python.exe -m pip install -r $env:USERPROFILE\.claude\skills\corte-viral\requirements.txt
```

Isso instala: pyyaml, jsonschema, faster-whisper (transcrição local com tempo por palavra), av (versão fixa),
opencv-contrib-python 4.10.0.84 (versão fixa), numpy, Pillow e scipy.
Na primeira transcrição, o faster-whisper baixa o modelo `large-v3-turbo` (~1,6 GB). É uma vez só.

Use sempre o lançador `~/.claude/skills/corte-viral/vch <comando>`: ele acha o Python certo (a venv) sozinho.

## 3. Os 8 subagentes

Eles só existem para o Claude Code quando estão em `~/.claude/agents/`:

```bash
mkdir -p ~/.claude/agents && cp ~/.claude/skills/corte-viral/agentes/*.md ~/.claude/agents/
```

Os 8: `context-mapper`, `clip-hunter`, `clip-builder`, `feed-psychologist`, `blind-reviewer`, `clip-deduplicator`,
`edit-director`, `quality-controller`. Rode de novo sempre que atualizar a skill.

## 4. Limpeza de voz por IA (DeepFilterNet)

Baixe o `deep-filter` certo pro seu computador seguindo `bin/COMO-BAIXAR.md` (GitHub oficial, release v0.5.6).
Sem ele tudo funciona, só pula a limpeza de ruído por IA.

## 5. Rosto e recorte da pessoa (Windows e Mac)

- **Recorte da pessoa** (texto ATRÁS da pessoa e o close do `retrato.py`): `modelo-edicao/mascara.py`, igual no Windows e
  no Mac. Usa o recorte do próprio HyperFrames (`remove-background`, modelo u2net_human_seg, licença Apache 2.0). Não
  precisa instalar nada além do que já está aqui: Node 22 (passo 1), ffmpeg (passo 1), a venv com numpy (passo 2) e o
  HyperFrames fixo (passo 8). Na primeira vez ele baixa sozinho o modelo (~168 MB, fica em `~/.cache/hyperframes`) e o
  `onnxruntime-node`. Precisa de internet só nessa primeira vez. Não precisa de placa de vídeo.
  Pra já deixar baixado e testar: `verificar.py --testar-recorte` (passo 9).
- **Mac (opcional, mais rápido):** `modelo-edicao/mascara-pessoa/mascara-pessoa` usa o Vision do macOS. Só entra se
  pedir: `MASCARA_MOTOR=vision` (ou `mascara.py ... --motor vision`).
- `modelo-edicao/olhar/olhar` (mede rosto e olhar, Vision) vem pronto pra Mac com chip Apple (M1 em diante). No Windows ele
  é trocado sozinho pelo `olhar/olhar.py` (OpenCV, usa o modelo da pasta `models/`).
- Mac com Intel: recompile os dois binários do Mac (precisa das ferramentas do Xcode: `xcode-select --install`):
  ```bash
  cd ~/.claude/skills/corte-viral/modelo-edicao/olhar && swiftc -O main.swift -o olhar
  cd ../mascara-pessoa && swiftc -O main.swift -o mascara-pessoa
  ```

## 6. HyperFrames (render da edição)

- Instale o plugin seguindo `hyperframes-e-media-use/COMO-INSTALAR.md` do pacote (skills de vídeo do HyperFrames e o media-use).
- A cópia FIXA usada no render (`hyperframes@0.8.107`) é instalada pelo passo 8. Nunca renderizar com `npx` em paralelo:
  ele se atualiza no meio e quebra.

## 7. Manual da Marca

A edição lê tudo da pasta `~/minha-marca/` (Windows: `C:\Users\SEU-NOME\minha-marca\`). Se ela não existir:

> Claude, faz a entrevista da minha marca

O roteiro da entrevista está em `ENTREVISTA-DA-MARCA.md` e o modelo da pasta em `modelo-minha-marca/`.

## 8. Pasta de trabalho, sons e fontes

```bash
~/.claude/skills/corte-viral/.venv/bin/python ~/.claude/skills/corte-viral/modelo-edicao/preparar_pasta.py
```
(Windows: `.venv\Scripts\python.exe` no lugar de `.venv/bin/python`.)

Cria `~/Videos-Claude/_trabalho/` (ou a pasta do seu `marca.json`), copia scripts, sons e fontes, e instala o
HyperFrames fixo. Sons extras grátis (máquina de escrever, giz, página): `modelo-edicao/SONS-PARA-BAIXAR.md`.

## 9. Conferir

```bash
~/.claude/skills/corte-viral/verificar.py
```
(Windows: `.venv\Scripts\python.exe verificar.py` dentro da pasta da skill.)

Verde em tudo que é obrigatório = pronto. Os avisos (deep-filter, manual da marca) não travam, mas resolva antes de
entregar vídeo.

Pra testar de verdade o recorte da pessoa (e já baixar o modelo dele): `verificar.py --testar-recorte`.

## Testes (opcional)

```bash
cd ~/.claude/skills/corte-viral && .venv/bin/python -m unittest discover -s tests -t . -q
```

---

## Notas técnicas (pro Claude)

- **O pin do OpenCV não é capricho:** sem versão, o pip instala a 5.x, que removeu `cv2.dnn.readNetFromCaffe` e não
  empacota os haarcascades. Se precisar consertar:
  `pip uninstall -y opencv-python opencv-python-headless opencv-contrib-python && pip install "opencv-contrib-python==4.10.0.84"`.
- **av==17.0.1:** a 19.x quebra o faster-whisper 1.2.1 (metadata_errors).
- **mediapipe foi testado e descartado** (trava ao inicializar no Mac). Não insista.
- **libass:** muitos ffmpeg não têm o filtro `ass`/`subtitles`. Não faz falta: a legenda é queimada pelo HyperFrames
  (`modelo-edicao/`), nunca pelo ffmpeg. Só não ligue `make_captioned_version` no config esperando que funcione.
- **Sem `jsonschema` a validação de artefato passa vazia** e é ela que segura a qualidade do pipeline de cortes.
- **Sempre `--workspace <pasta-do-projeto>/runs` no `init`**, senão a run é gravada dentro de `~/.claude/skills/`.
- **Se instalar em outro caminho:** muda só o bloco `allowed-tools` do `SKILL.md`. O código Python resolve o próprio
  caminho sozinho.
- **Efeito sonoro dentro do HyperFrames sai ~17 dB abaixo da voz:** os sons entram depois, no `mixar_clip.py`/`mixar_meg.py`.
- **Render solto com nohup numa chamada comum é cancelado:** renderizar com run_in_background.
- **Recorte da pessoa:** `mascara.py` acha o HyperFrames em `<trabalho>/hf/` (ou `HYPERFRAMES_CLI=<caminho do
  hyperframes.mjs>`); sem a cópia fixa cai no `npx -y hyperframes@0.8.107`. O modelo vê a imagem em 320x320, então o
  vídeo vai reduzido pra 360 de largura antes (mais rápido, mesma qualidade) e a máscara volta na largura pedida.
  Conta de tempo: o HyperFrames é bem mais lento que o Vision do Mac (teste de 13/10/2026 num M1 com o computador muito
  ocupado: 5 s de vídeo em 11 s no Vision, ~7 min no HyperFrames com CoreML, ~13 min só no processador; com o computador
  livre é bem menos). A máscara é igual pelo CoreML e pelo processador. No Windows roda no processador: rodar em
  segundo plano e só nos trechos que vão ter texto atrás (o `source.mp4` do corte, nunca o bruto inteiro).
  `MASCARA_DEVICE=cpu` força o processador se o CoreML der problema no Mac.
