# Instalar MOTION VOX

Kit fechado: fontes, assets e motor viajam junto. Quem instala reproduz **este** visual,
não um parecido.

## 1. Colocar no lugar

```bash
unzip motion-vox.zip -d ~/.claude/skills/
```

Deve ficar `~/.claude/skills/motion-vox/SKILL.md`. Em projeto, use
`.claude/skills/motion-vox/` na raiz do repositório.

## 2. Dependências

```bash
pip install Pillow numpy opencv-python faster-whisper
```

E `ffmpeg` no sistema — `brew install ffmpeg` (macOS) ou `apt install ffmpeg` (Debian).

## 3. Conferir

```bash
python3 ~/.claude/skills/motion-vox/verificar.py
```

Checa bibliotecas, ffmpeg, as 9 fontes, os 9 objetos prontos, e carrega o motor de fato
(mede tipo, aplica o boil, confirma que a legenda exige configuração). Sai com erro se
faltar algo — melhor descobrir aqui que no meio de um render de 20 minutos. O aviso
sobre os 7 objetos "gerados sob demanda" é normal: eles são criados na primeira cena
que pedir cada um.

## 4. Usar

No Claude Code: peça motion sobre um clipe vertical que já existe. A skill é acionada
por pedidos como *"coloca uns motions nesse corte"* ou *"ilustra essa fala"*.

Estrutura mínima de projeto:

```
MEU_CLIPE/
  00_brief/fonte.mp4                    o clipe vertical já cortado
  00_brief/transcript_palavras.json     gerado no passo abaixo
```

```bash
python3 ~/.claude/skills/motion-vox/lib/transcrever.py \
    00_brief/fonte.mp4 00_brief/transcript_palavras.json
```

O modelo baixa ~1,5 GB na primeira vez. **Transcript por palavra é insumo sem
substituto**: motion ancorado e legenda em corte seco dependem de saber em que frame
cada palavra foi dita.

Depois copie `lib/render_template.py` e `lib/compose_template.py` para o projeto como
`render.py` e `compose.py`, e preencha o bloco `CLIPE`. `exemplo/clipe06_config.py` tem
um caso preenchido de verdade, com o motivo de cada escolha.

## O que a skill NÃO faz

Não gera vídeo com IA de vídeo. A composição por camadas em PIL dá controle exato de
posição, tempo e grafia — e produz o mesmo resultado com custo muito menor. IA de imagem
entra só para objeto físico que o kit ainda não tem.

## Quando faltar um objeto

O kit tem 16 objetos: 9 já vêm prontos e 7 são gerados na primeira vez que uma cena
pedir (a lista está em `assets/MANIFESTO.md`). Se a cena pedir um que não está em
`assets/`, a IA gera — não
troca por outro nem pula a cena:

1. **Com gerador de imagem** (chave do Gemini ou da OpenAI em `GEMINI_API_KEY` /
   `OPENAI_API_KEY`, ou uma skill de imagem instalada): `lib/gerar_asset.py` monta o prompt
   pelo esqueleto de `referencias/prompts-asset.md`, gera, e o `cutout.py` recorta. Depois
   de conferido, o objeto vai para `assets/` e ganha uma linha no `assets/MANIFESTO.md`.
2. **Sem gerador** (ou chave sem crédito): a IA te entrega o prompt pronto. Você cola no
   ChatGPT ou no app do Gemini (funciona pelo celular), pede a imagem quadrada e manda a
   imagem de volta no chat. A IA recorta, confere e salva no kit.

Nunca se usa imagem da internet sem licença livre. E todo objeto novo fica no kit para as
próximas vezes. A chave do gerador nunca é gravada em arquivo da skill.

## Cores da sua marca

Os dois acentos da identidade (amarelo `#DBD653` e azul `#2E82F7`) podem virar as cores
da sua marca. Crie o arquivo `~/minha-marca/marca.json`:

```json
{ "cor_destaque_1": "#7A1E3A", "cor_destaque_2": "#C9A86A" }
```

`cor_destaque_1` substitui o amarelo (sublinhado de marcador) e `cor_destaque_2` o azul
(linha de continuidade e luz da foto noturna). Sem o arquivo, ficam as cores originais.
Para conferir: `python3 ~/.claude/skills/motion-vox/lib/marca.py`.

## Recalibrar ao trocar de fotografia

`night_photo.py` e `crt.py` trazem constantes medidas para as fotos deste kit (recorte,
curva de cor, quadrilátero da tela). Fotografia nova pede recalibração — os dois scripts
dizem onde.

## Licenças

As 9 fontes são de licença livre (OFL/Apache), com os arquivos de licença em `fontes/`.
Fontes de sistema não podem ser redistribuídas — por isso a identidade foi construída
só sobre fontes abertas.
