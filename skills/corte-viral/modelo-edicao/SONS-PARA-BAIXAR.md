# Sons para baixar (grátis)

Os sons que já vêm na pasta `assets/sfx/` são do pacote Pixabay (licença Pixabay: uso livre, inclusive comercial, sem
precisar dar crédito): chime, click, click-alto, click-soft, click-soft-alto, error, key-press, ping, ping-alto, pop,
pop-alto, sparkle, typing, whoosh, whoosh-short.

Os sons abaixo são usados pelos scripts, mas NÃO podem ir soltos no pacote (a licença do Mixkit permite usar nos seus
vídeos, mas não permite redistribuir o arquivo de som). Cada aluna baixa os dela, grátis.

**Enquanto não baixar, tudo funciona:** o `marca.py` troca o som que falta por um parecido do pacote Pixabay
(máquina e escrita viram `typing`, página vira `whoosh`, giz vira `typing`, erro-alto vira `error`, toque vira `click-soft`)
e avisa no terminal.

## Como instalar um som baixado
1. Baixe o arquivo (mp3 ou wav).
2. Renomeie com o nome da coluna "Salvar como" (pode ser .mp3 ou .wav).
3. Coloque em `~/minha-marca/sons/` (vale pra todos os vídeos) ou em `assets/sfx/` da pasta de trabalho.
4. Se preferir, peça: "Claude, baixa os sons do SONS-PARA-BAIXAR.md pra mim e coloca em ~/minha-marca/sons".

| Salvar como | O que é | Onde baixar (grátis) |
| --- | --- | --- |
| `maquina.wav` | máquina de escrever (título letra por letra) | Mixkit, som nº 1376 · https://mixkit.co/free-sound-effects/typewriter/ (link direto: https://assets.mixkit.co/active_storage/sfx/1376/1376-preview.mp3) |
| `giz.wav` | giz riscando no quadro (itens de lista) | Mixkit, som nº 2372 · https://mixkit.co/free-sound-effects/chalk/ (link direto: https://assets.mixkit.co/active_storage/sfx/2372/2372-preview.mp3) |
| `giz1.wav` e `giz1-alto.wav` | o mesmo giz, cortado em 1 segundo | o `giz.wav` acima, cortado: peça "Claude, corta 1 segundo do giz.wav e salva como giz1.wav e giz1-alto.wav" |
| `pagina.wav` e `pagina-alto.wav` | página virando (rótulos e perguntas em pílula) | Mixkit, som nº 1101 · https://mixkit.co/free-sound-effects/page/ (link direto: https://assets.mixkit.co/active_storage/sfx/1101/1101-preview.mp3) |
| `escrita.wav` | caneta escrevendo no papel (anotações à mão) | Pixabay ou Mixkit, buscar "pen writing" / "caneta escrevendo" · https://pixabay.com/sound-effects/search/pen%20writing/ |
| `toque.wav` | toque curto de interface | Pixabay, buscar "tap" · https://pixabay.com/sound-effects/search/tap/ |
| `typing1.wav` e `typing1-alto.wav` | digitação curta (1,2 s) | o `typing.wav` do pacote serve; ou Pixabay "keyboard typing" |
| `error-alto.wav` | erro curto (0,4 s) | o `error.wav` do pacote cortado: peça "Claude, corta os primeiros 0,4 s de voz do error.wav e salva como error-alto.wav" |
| trilha (ex.: `trilha.wav`) | música de fundo baixinha (técnica S1), só se o manual pedir | Pixabay Music, buscar "lofi" · https://pixabay.com/music/search/lofi/ (licença Pixabay). Depois coloque o nome em `marca.json` → `trilha.arquivo` |

Os links diretos do Mixkit seguem o padrão do site; se algum mudar, abra a página da categoria e procure o som pelo número.
Sons que a aluna odeia (lista no MINHA-MARCA.md) não entram em nenhum vídeo, mesmo que estejam instalados.
