# Jeito da marca de editar Reels

Guia único do estilo e do processo de edição. Os scripts ficam nesta pasta (`modelo-edicao/`).
As escolhas visuais (cores, fontes, legenda, emojis, sons, o que a pessoa ama e o que odeia) NÃO estão aqui:
estão no Manual da Marca da aluna, em `~/minha-marca/` (`MINHA-MARCA.md` + `marca.json`). Os scripts leem
o `marca.json` sozinhos pelo `marca.py`. Aqui ficam as regras técnicas e o processo, que valem pra qualquer marca.
Falar com a aluna sempre em português simples, sem termo técnico.

## Antes de editar (sempre)
1. Rodar `python3 modelo-edicao/marca.py conferir`. Se faltar o manual ou algum campo, fazer a ENTREVISTA DA MARCA
   (`ENTREVISTA-DA-MARCA.md`, na raiz da skill) com a aluna, pergunta por pergunta, e criar/completar `~/minha-marca/`.
   Não editar vídeo com o manual vazio: sai com a cara de ninguém.
2. Ler `~/minha-marca/MINHA-MARCA.md` inteiro, principalmente "Nunca faça", "Palavras que a IA erra" e "Regras aprovadas".
   O que está lá vence o que está aqui.
3. Rodar `python3 modelo-edicao/preparar_pasta.py` na primeira vez (cria a pasta de trabalho, copia scripts, sons e fontes,
   instala o HyperFrames fixo).
4. **Toda correção vira regra.** Cada vez que a aluna aprovar um ajuste ("agora sim", "ficou perfeito", "assim mesmo"),
   acrescentar a regra, com data, na seção "Regras aprovadas" do `MINHA-MARCA.md` (e no `marca.json` se for valor de script:
   cor, fonte, posição da legenda, volume). Nunca guardar só na conversa.

## Onde trabalhar e entregar
- Pasta de trabalho: a do `marca.json` (`pastas.trabalho`, padrão `~/Videos-Claude/_trabalho/`), com `ed/`, `trans/`, `hf/`,
  `prontos/`, `versoes-anteriores/`, `conferencia/`. `python3 marca.py pasta trabalho` mostra qual é.
- NUNCA trabalhar em pasta temporária (`/tmp`, scratchpad): se o computador reiniciar, apaga todas as bases de edição.
- Entrega: a pasta `pastas.entrega` (padrão `~/Videos-Claude/PRONTOS/`), com `entregar.sh`. Versão antiga vai pra
  `versoes-anteriores/`; nada é apagado antes de a aluna aprovar o lote todo.
- Cada pasta de corte tem o link `assets` pros sons e fontes: `ln -s ../assets assets` (pasta nova com link quebrado
  some com fonte e som SEM dar erro no render).

## Visual (vale pra todos)
- Vertical 1080x1920, voz ORIGINAL (sem EQ/compressor de "voz de rádio": realça o eco da sala). Só tirar ruído de fundo:
  `highpass=f=70,afftdn=nr=12:nf=-40:tn=1` + loudnorm -14.
- Luz leve: `eq=brightness=0.02:contrast=1.04:saturation=1.05:gamma=1.04`. Sem desfoque de fundo (fica artificial).
- Título no começo, sempre deixando claro o assunto: linha de cima na fonte de TÍTULO do manual, branca e grande; linha de baixo
  na fonte MANUSCRITA do manual, em máquina de escrever (letra por letra, com som de máquina) e sublinhado na cor de DESTAQUE.
- Legenda palavra por palavra na fonte de LEGENDA do manual, na cor da legenda, até N palavras por vez (manual, padrão 3);
  palavra-chave com o destaque do manual (caixa, sublinhado, itálico ou cor). Legenda nunca em cima de área branca (TV,
  parede clara): usar `cap_top` no config.
- Emojis como elementos (pop), se o manual disser que pode. Sons: clique, pop, página, erro (baixo), ping no fecho; respeitar
  os sons que a aluna odeia (manual). Capa = quadro com o título inteiro.
- Grafias: as da lista "Palavras que a IA erra" do manual (vão também no `marca.json` em `transcricao.trocas`). Revisar a
  legenda inteira antes de renderizar. Começo de frase com maiúscula. Whisper troca "stories/story" por "stores/store",
  "insights" por coisas parecidas e separa "e-book" ("e -book"): conferir sempre.

## Cortes (vale pra todos)
- Cortar respiro/pausa/silêncio entre frases pela pausa entre palavras (>0,25 s), com folga -0,08/+0,10.
- Cortar erro, gaguejo, repetição e tentativa refeita (fica a última boa).
- Cortar quando a pessoa sai de cena ou vai pro lado conferir o computador, ANTES de começar a sair.
- Depois de pronto, medir o áudio do vídeo final e caçar silêncio > 0,5 s (pessoa ouvindo pergunta) e cortar.

## Vídeos com slide na TV (listas)
- Começa no GANCHO falado, inteiro (primeira à última palavra).
- Quadro ABERTO mostrando a TV na maior parte; close na pessoa só de vez em quando (≈3 s, 1 por item), quando ela só fala e
  a TV não muda (`zooms` no config, origem no rosto via `olhar`).
- Virar pra TV NÃO é desviar o olhar: nunca cortar por isso.
- TODA fala fica, inclusive a pessoa dizendo cada item.
- Cada item vira título a giz no alto (fonte GIZ do manual, letra por letra, `itens` no config), aparecendo quando ela fala o item.
- Som de giz ACOMPANHA a escrita: risquinho por letra, emendado na palavra, pausa no espaço (`giz_letras.py`), -10 dB
  (um pouco abaixo da voz).
- Sem whoosh nas emendas (`whoosh: false`). Legenda abaixo da TV (`cap_top` ≈ 1420), emojis em y ≈ 1580.
- Script de referência: `lista_tv.py` + `lista_cfg.py` com a receita (`exemplo-receita-lista.json`).

## Depoimentos de clientes/alunas
- Close da cintura pra cima direto do 4K (`retrato.py`, Windows e Mac, acha a pessoa pelo `mascara.py`; caixa manual em
  `caixa-forcada.json` quando a pessoa está de lado ou em dupla). Quando a pessoa se mexe: `retrato_seguir.py` (recorte
  acompanha o rosto). Sem desfoque.
- Vídeo "sem interlocutor": tirar a entrevistadora, "com certeza"/"sim" que respondem pergunta e o silêncio ouvindo a
  pergunta (`plano_close.py` + `limpar.py`). A pergunta pode virar pílula "💬 pergunta" (`configs_v2.py`).
- Foco em resultado, objeção e transformação pra vender o serviço/produto da aluna; nada sobre o evento em si.
- Formato de bastidor (opcional): trecho de erro/risada em preto e branco + vinheta + selo "🎬 erros de gravação" + som de
  erro, abrindo o vídeo antes do título (`bastidores` e `title_at` no config).

## Pipeline
plano (cortes) → source.mp4 (ffmpeg, 1 passada) → transcript (Whisper local large-v3-turbo + trocas de grafia do manual) →
config.json → `gerar_clip.py` → render com HyperFrames FIXO (`npm i hyperframes@0.8.107` na pasta `hf/`, chamar o binário;
nunca npx em paralelo: ele se atualiza no meio e quebra) via run_in_background → `mixar_clip.py` (voz + efeitos) →
`conferir.sh` (folha de quadros) → `entregar.sh`.
- Efeito sonoro dentro do HyperFrames sai ~17 dB abaixo da voz (inaudível): por isso os sons entram DEPOIS, no `mixar_clip.py`
  (adelay + volume em dB + amix normalize=0 + alimiter), medindo efeito contra voz no mesmo instante.
- Render lançado com nohup numa chamada comum é cancelado: usar run_in_background. `render_lote.sh` renderiza vários.
- Arquivo > 30 MB pode não chegar no celular: gerar também uma versão leve (720p, crf 27) se a aluna for mandar pelo WhatsApp.

## Vídeo de lista a partir do bruto com várias tomadas
1. Ler a transcrição crua inteira e escolher a ÚLTIMA tomada boa de cada parte; montar a receita (`exemplo-receita-lista.json`:
   blocos de frase inicial/final, itens, fim da lista, emojis, sons, trocas).
2. `lista_tv.py receita.json` (corta pelas palavras, closes recortados do 4K) →
3. `tirar_silencios.py source-bruto.mp4 source.mp4 0.3 0 0.1`: o Whisper estica palavra por cima de silêncio (sobra até 20 s),
   então o corte final é pelo ÁUDIO (o `base.sh <nome> lista <receita>` faz 2 a 4 de uma vez) →
4. `transcrever_v2.py` de novo no source cortado (aparecem falas que o 1º Whisper perdeu: "deixa eu ver o que tenho que falar",
   "não muda ainda", "tchau") → tirar essas com `limpar.py` →
5. `lista_cfg.py receita.json` (itens/emojis/sons pela transcrição nova) → `gerar_clip.py` → render → `mixar_clip.py`.
6. Conferir com grade de 2 em 2 s (`fps=1/2,tile=16x4`): TV aparecendo, 1 close por item, título a giz no item certo.
- Voz de quem grava pode vazar baixinho num "aham"/pergunta curta: o Whisper NÃO escreve, só deixa buraco entre as palavras.
  Varrer o vídeo pronto pela altura da voz (`vozes.py`: ex. voz masculina F0 95–165 Hz por ≥0,35 s quando quem fala está
  em ~200–250 Hz) e cortar o trecho (`tirar_trechos.py`). Conferir se não é a própria pessoa falando grave no meio da frase.

## Organização de um lote
- Plano dos cortes de cada vídeo: `plano.py <plano-entrada.json>` (modelo `exemplo-plano.json`). `base.sh <nome> fixo|seguir|lista`
  monta source → corta silêncio pelo áudio → transcreve.
- Lote de cortes de um vídeo longo (podcast, live): `cortar2.py` (trechos + respiros pelas runs da corte-viral) →
  `render_vertical.py` → transcrever → `montar_configs.py` → `gerar_clip.py` → render → `mixar_clip.py`.
- Depoimento: `retrato_seguir.py` (recorte desliza com o rosto, largura 0,62; se ficar aberto demais, recortar 84% do source)
  e `vozes.py` (voz fora das palavras = pergunta de quem grava / "ééé"; palavra curta esticada = vogal arrastada → cortar o meio).
  `cfg_dep.py` monta o config com emendas detectadas no próprio vídeo.
- Depois de cortar por palavra (`limpar.py`), as emendas do plano mudam: `cortes_reais.py` acha o deslocamento por correlação de áudio.
- Antes de entregar: varrer pedaços < 0,6 s entre cortes secos (flash) e olhar quadro a quadro.
- Título de item com espaço "duro" não quebra linha: palavra em bloco nowrap (o `gerar_clip.py` já faz).

## Catálogo de técnicas com código
- 62 técnicas tiradas de reels de referência, cada uma com código: T (texto), C (cartões), M (câmera), S (som), E (estrutura),
  e 3 receitas (Recibo, Editorial, Bastidor).
- Quando a aluna pedir "T2", "C6", "receita Recibo" etc., a definição está em `CATALOGO-TECNICAS.md` (nesta pasta).
- O catálogo soma a este guia: corte, voz, grafia e entrega continuam como acima. As cores das referências (limão, creme)
  só entram se a aluna quiser; o padrão é a cor de DESTAQUE do manual.

## Receita Editorial (estilo Meg Kilgore)
- Scripts em `receita-editorial/`: `corte.py` (corte pelo SOM + corte em L, a partir do bruto 4K) ou `etapa_a.py` (pelas palavras),
  `etapa_b2.py` (base + 2 camadas, a versão aprovada; config modelo `exemplo-config.json`), `etapa_b_meg.py` (1ª versão, com
  cartões; `exemplo-config-meg.json`), `render_meg.sh`, `mixar_meg.py`, `cortar_pausas.py`.
  A pasta da receita é uma cópia de `receita-editorial/` com `configs.json` e `assets/` (sons, capas, fotos, prints, slides).
- Destaque na cor de DESTAQUE do manual. Cor de destaque some em cima de roupa escura: na legenda a palavra-chave vai em
  itálico (fonte TÍTULO ITÁLICO) BRANCA com sublinhado na cor de destaque que corre; em cima da parede clara, texto na cor de
  TEXTO e itálico na cor de destaque (T10, T16, T19). Cor cheia só em etiquetas/números.
- Texto atrás da pessoa (T11/C4): renderiza a camada de trás no HyperFrames, junta com a pessoa recortada (`mascara.py`
  1080 + alphamerge) nas janelas dos elementos de trás, e renderiza a camada da frente (legenda + cartões) por cima.
  Tudo de trás fica acima da cabeça (topo 0–330 px no plano aberto). Funciona no Windows e no Mac.
- Recorte da pessoa (`mascara.py <entrada> <saida> [largura]`): o padrão é o `remove-background` do HyperFrames fixo da
  pasta `hf/` (modelo u2net_human_seg, Apache 2.0, roda no computador, sem internet depois da 1ª vez; na 1ª vez baixa sozinho
  ~168 MB pra `~/.cache/hyperframes`). Saída igual à do antigo binário do Mac: mp4 cinza, branco = pessoa, mesmo fps e
  número de quadros. A máscara é suavizada no tempo (borda não treme). No Mac, `MASCARA_MOTOR=vision` usa o Vision da
  Apple (`mascara-pessoa/`), bem mais rápido. Objeto grande colado na pessoa pode entrar no recorte e objeto na mão pode
  sumir: conferir 2 ou 3 quadros da junção antes do render da frente.
- Âncoras do config batem com a transcrição FINAL (números viram algarismo: "1." "O 1 e o 2"); trocar na legenda por extenso via `fix`.
- No fim, `cortar_pausas.py` tira do final.mp4 os silêncios > 0,5 s da voz. Trilha só se o manual pedir (`trilha` no marca.json),
  a -13 dB.
- Tempo de referência num Mac: corte do 4K ~30 min, base ~5 min, cada render HyperFrames ~6 min.

## Regras fixas da receita Editorial (vieram de correções aprovadas)
- CORTE PELO SOM, nunca só pela palavra do Whisper (ele dá fim de palavra cedo e come o final): `corte.py` acha início/fim
  da voz pela energia (limiar = p30 + 12 dB), deixa 0,07 s depois da fala e 0,04 s antes; avisa se emenda cai em voz.
- Frase repetida = erro: a 1ª tentativa sai, fica a que fluiu. O Whisper ESCONDE repetição esticando uma palavra (>0,9 s) ou
  pulando trecho: listar palavras esticadas e retranscrever o trecho SEM vad_filter antes de escolher os cortes.
- O vídeo começa no primeiro som de voz (nada de texto/som antes de a pessoa falar).
- Troca de enquadramento em TODA emenda (A/M/F alternando), pra parecer fala contínua.
- Títulos e legenda BRANCOS (com sombra). Cor de destaque SÓ em sublinhado, risco e ícone. Nada de letra preta em cima do vídeo.
- NADA de quadro/cartão branco com número ou citação: só texto. Print real (do sistema, app, relatório) pode (tipo `print`).
- Legenda do lado DIREITO (de quem olha), ACIMA do ombro (left 560, top 845), 1 palavra, chave em itálico com sublinhado.
- Títulos no topo menores e um pouco mais baixos (top ~175), por CIMA do cabelo (camada da frente); atrás da cabeça só a parede de capas.
- Sempre: efeito de escrita letra a letra (fonte manuscrita) com som (máquina / escrita), emojis com pop, ping no número de cada passo.
- Emoji composto (🙅‍♀️, 😮‍💨, 🤷‍♀️) quebra no render: usar só emoji simples.
- As referências (Meg, Steph, Marc, Zoe) são MODELO pra melhorar, não pra replicar: manter os efeitos que a aluna já gosta.
- Sons: clique (click-soft) e sons de interface; NÃO usar whoosh grande na parede de capas.
- Zoom em movimento: aproximação lenta 1.00→1.07 em pedaços ≥1,8 s alternados (na camada da frente, #cam).

## Olhar pra baixo
- Olhar pra baixo no fim da frase não pode aparecer. Fazer CORTE EM L (imagem troca ~0,4 s antes, a voz termina por baixo):
  `corte.py` com `olha_t.json` ({"tempo do bruto do fim do pedaço": segundos}).
- O `pitch` do rosto.csv ajuda (sobe quando a pessoa olha pra baixo), mas NÃO basta: muita gente abaixa só os olhos.
  Conferir pela IMAGEM o último quadro de cada pedaço e os dois lados de cada emenda.
- Olhar pra baixo dos DOIS lados de uma emenda: cobrir com inserção em tela cheia (`insercoes` no config, 0,6–0,8 s).
- Olhar e inserções guardados pelo TEMPO DO BRUTO (olha_t.json, insercoes.bruto), pra não sair do lugar quando o corte muda.

## Voz e microfone
- Ruído de boca no microfone: highpass 80 + adeclick + adeclip + deesser + afftdn + lowpass 14k antes do loudnorm.
- RUÍDO = S ESTOURADO (fala colada no microfone de mão): o "chiadinho" é sibilância, 10–21 dB acima da voz em "esse/isso/segue".
  O deesser do ffmpeg NÃO resolve. Usar o tratamento B de `receita-editorial/desser.py`: adynamicequalizer em 7 kHz (ratio 12,
  range 30) + acrossover 4,5 kHz com acompressor forte só no agudo + loudnorm. Medir antes/depois.
- POFS de ar (P/B/G/K com o microfone de mão colado na boca), ~45 dB acima do normal abaixo de 90 Hz. Ordem que funciona
  (igual ao "reduzir ruído" do CapCut), já pronta no `limpar_voz.sh`:
  1) `bin/deep-filter -D --pf -o saida voz.wav` (DeepFilterNet, IA, segundos pro vídeo inteiro, voz 48 kHz mono);
  2) `receita-editorial/depof.py` (corte <130 Hz 8ª ordem + -15 dB em 130–400 Hz só nos pofs fortes, limiar mediana+28 dB);
  3) `receita-editorial/tratar.py` (adeclick + controle do S + compressor leve + loudnorm -14).
  Medir com `pofs.py`: grave<90 cai ~28 dB e o agudo >9k ~15 dB, sem mexer na voz 150–400 Hz.
- Tratamento "voz de rádio" (afftdn + EQ + compressor forte) realça o eco da sala: não usar.

## Fluxo completo da receita Editorial (já sai pronto)
`receita-editorial/`: `corte.py <ep> <bruto> keep.json` (+ olha_t.json) → transcrever_v2 do cortado (pasta `<ep>/t2/` com o
`source.mp4` apontando pro cortado) → `etapa_b2.py <ep>` (configs.json) → `render_meg.sh <ep>` (já chama `limpar_voz.sh` =
DeepFilterNet + depof + tratar; sem parede de capas, a base é o próprio source).
- Print de post: tipo `carrossel` = cartas distribuídas na mesa lado a lado (clique em cada uma) → galeria rolando de lado →
  somem; NÃO empilhar. Depois, print real do painel de insights do post, com zoom.
- Não deixar tudo como texto no topo: listas/tópicos do LADO ESQUERDO na altura do rosto (tipo `lista`, escrita à mão com
  marcador na cor de destaque), oposto à legenda.
- Fotos da aluna entrando por cima do vídeo (tipo `foto`: pop / passa / pilha / tela / mosaico), variando. Inserções com
  FOTO de fundo. Fotos em pilha caem DEVAGAR (gap ≥1,0 s, queda 0,5 s); foto que representa o assunto pode ir em TELA CHEIA
  com o título por cima (`modo: tela`); prints de venda/mensagem como MOSAICO se encaixando na frente da pessoa
  (`modo: mosaico`, 6 grandes, gap 0,28) e a inserção seguinte usa o mesmo mosaico de fundo com o texto.
- Pausa interna só vira corte se a mediana da energia for silêncio de verdade (THR-3): senão corta consoante fraca no meio
  da palavra.

## ÁREA SEGURA DO REELS
No feed o Instagram corta ~110 px de CADA LADO do 1080 (tela do celular é mais alta que 9:16) e a parte de baixo tem
nome/legenda/ícones. Todo texto entre x=120 e x=960: títulos .topo left/right 120; legenda left 470 right 120 (palavra com
>10 letras usa classe .longa menor); listas left 120 largura 330; emojis x 200/870; fotos com left ≥ 110.
Conferir desenhando o retângulo 110..970 sobre os snapshots antes do render.

## Conferência antes de entregar
- `conferir.sh <nome>`: folha de 5 quadros + o texto final da legenda. `render_meg.sh` já gera `folha.jpg` (1 quadro a cada 2 s).
- Olhar: grafia da legenda (lista do manual), título claro, nada em cima do rosto, área segura, sem flash entre cortes,
  sem olhar pra baixo, primeira palavra não comida, sons da lista "odeio" fora.
- Só o vídeo pronto vai pra pasta de entrega. Nada vai pro lixo antes de a aluna aprovar o lote todo.
