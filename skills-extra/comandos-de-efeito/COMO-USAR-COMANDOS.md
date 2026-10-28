# Comandos de efeito (/nome), o jeito dos reels de "Claude edita meu vídeo"

Cada efeito tem um comando próprio, igual nos reels de "Claude edita meu vídeo": a aluna anexa o vídeo, digita
`/tier-list` (ou `/vidro`, `/figurinha`...) e recebe o vídeo editado. Cada comando é uma skill curta em
`~/.claude/skills/<comando>/SKILL.md` que manda pra cá. Lista completa: tabela no fim deste arquivo.
Instalados pelo Kit de Edição (`~/kit-edicao-claude/skills-extra/comandos-de-efeito/`). A maioria dos efeitos é da
skill gratuita da @vibha.in.progress (licença MIT); /figurinha, /particulas e /colagem são do kit.

A aluna não é técnica: não pedir pra ela rodar nada, responder curto e em português.

`<PY>` = `~/.claude/skills/effects/.venv/bin/python` (no Windows: `~/.claude/skills/effects/.venv/Scripts/python.exe`).
Se a `.venv` ainda não existir, rodar antes `bash ~/.claude/skills/effects/scripts/setup.sh` (a skill /effects explica).

## Passo a passo quando a aluna digitar um comando

1. **Vídeo.** O que a aluna anexou ou o caminho que deu. Sem vídeo: perguntar qual (uma pergunta curta). Vídeo vertical é o ideal.
2. **Onde entra.** Vídeo de até 6 s: o efeito no vídeo inteiro. Mais longo: tempo de cada palavra com
   `<PY> ~/.claude/skills/effects/scripts/words.py <video>`
   e escolher o trecho em que a fala combina com o efeito (dica na skill do comando), 1,5 a 4 s. Se ela disser "na palavra X", usar a palavra.
3. **Textos.** Sempre em português e tirados do que ela fala no vídeo. Nunca inventar número (visualizações, faturamento,
   porcentagem): se o efeito pede número e ela não disse, perguntar.
   Nome e @ entram sozinhos, lidos de `~/minha-marca/marca.json`. Cor: `color=<cores.destaque do marca.json>` onde o efeito tem cor de destaque.
4. **Conferir antes de renderizar.**
   `<PY> ~/.claude/skills/effects/scripts/aplicar.py <comando> <video> --start S --end E chave=valor ... --still t1,t2`
   e abrir os PNGs. Nada cobrindo o rosto, texto inteiro na tela, tudo em português.
5. **Renderizar.** O mesmo comando sem `--still`. Sai `<video>-<comando>.mp4` ao lado do original, com o áudio original.
   Rodar com `run_in_background` se o vídeo passar de 20 s.
6. **Entregar.** Copiar o vídeo pronto pra `~/Videos-Claude/PRONTOS/`, dizer onde está e, em uma linha, o que foi feito.
   Ela pode emendar outro comando no resultado (`/figurinha` e depois `/vidro`): aplicar no vídeo que acabou de sair.

Vários comandos de uma vez ("põe /vidro no começo e /letreiro no fim"): montar um `plano.json` com os efeitos
(`{"effects":[{"fx":"liquid-glass-graph","start":1,"end":3.5,...},{"fx":"led-sign",...}]}`, o nome do `fx` está na tabela)
e rodar `<PY> ~/.claude/skills/effects/scripts/fx_pt.py --plan plano.json <video> <saida>.mp4` uma vez só. Efeitos de câmera (`/por-cima-do-ombro`, `/mira`, `/aproximar`) primeiro na lista.

Os efeitos não põem som nem legenda. Num vídeo pra postar, isso entra depois, no modelo de edição
(`~/.claude/skills/corte-viral/modelo-edicao/`). O efeito vai no vídeo base ANTES das camadas.

## Os comandos

| Comando | `fx` | O que faz |
| --- | --- | --- |
| /pilha-de-reels | noise | reels empilhando atrás da cabeça, um a cada quarto de segundo |
| /leque-numerado | lineup | peças numeradas abrindo em leque acima da cabeça |
| /mira | locked-on | colchetes travam no rosto e a câmera segue |
| /orbita | orbit | seus reels girando em volta da cabeça |
| /zoom-rapido | lean-in | aproximação rápida numa palavra |
| /palavra-atras | backdrop-word | palavra gigante cai atrás de você |
| /holofote | spotlight | apaga a sala e deixa você acesa |
| /brilho-dourado | spotlight (look sparkle) | sala escura, raios dourados e palavra dourada com faíscas |
| /recibo-impresso | the-bill | instruções saindo impressas como recibo na parede |
| /cor-de-cinema | moody | cor de cinema no vídeo |
| /antes-depois | swipe | cortina de antes e depois passando por cima de você |
| /lista-de-tarefas | todo | cartão de tarefas ao lado da cabeça se marcando |
| /comentario | comment-box | barra de comentário do Instagram digita uma palavra e publica |
| /seguir | tap | botão Seguir vira Seguindo |
| /pausa-seta | pause-point | congela e uma seta à mão aponta pra você |
| /desinstalar | uninstall | barra de desinstalar com falha quebrando a imagem |
| /vira-reel | reel-frame | o vídeo encolhe e vira um cartão de reel |
| /chuva-de-teclas | shortcut-rain | teclas de teclado chovendo atrás |
| /carimbo | reject-stamp | carimbo grande batendo na tela |
| /contagem | countdown-flip | relógio de virar 3, 2, 1 acima da cabeça |
| /tunel | rabbit-hole | a imagem vira um túnel girando |
| /capa-de-revista | cover-star | você vira capa de revista, título atrás da cabeça |
| /capa-editorial | cover-star (look editorial) | capa de revista clássica, serifada e cor de filme |
| /rabiscos | scribble | rabiscos de caneta se desenhando em volta |
| /widgets-de-vidro | glass-widgets | widgets de vidro em volta da cabeça + pílula "Editado pelo Claude" |
| /colagem-vermelha | red-collage | você em preto e branco, palavra gigante colorida atrás, 3 frases batendo |
| /manchete-dividida | split-headline | manchete desce e empurra você pra metade de baixo |
| /sala-lilas | pastel-word | sala lilás, palavra gigante atrás, cartão de perfil sendo seguido |
| /pilulas | check-pills | papel quadriculado, reels pregados atrás, cursor clicando pílulas |
| /linha-do-tempo | timeline | cor vermelha de filme, linha do tempo de edição e REC |
| /manchete-caixa | headline-box | aproximação com manchete de 2 linhas, a 2ª numa caixa branca |
| /parede-de-reels | profile-wall | grade dos seus reels enche a parede e um contador sobe |
| /tier-list | tier-list | ranking S a D cai na tela e o item voa pro S |
| /imagem-de-apoio | broll-split | imagem de apoio em cima com etiqueta de preço, você embaixo |
| /leque-de-celulares | phone-fan | seus reels abrindo como um leque de celulares |
| /pontinhos | dot-reveal | a imagem se monta com pontinhos de luz |
| /parede-de-manchetes | headline-wall | suas manchetes empilham atrás da cabeça e um total aparece |
| /checklist | checklist | lista de tarefas do Claude embaixo do queixo, cada passo gira e fica verde |
| /vidro | liquid-glass-graph | cartão de vidro com gráfico subindo e número contando |
| /vidro-bento | liquid-glass-graph (look bento) | gráfico numa tela de vidro escuro atrás + blocos de vidro na frente |
| /carrossel-3d | carousel-spin | seus reels girando em carrossel 3D |
| /trava | match-cut | páginas de texto passando com uma palavra travada numa caixa |
| /ajustes-iphone | apple-toggles | cartão de ajustes do iPhone ligando os botões, um por frase |
| /letreiro | led-sign | luz cai e um letreiro de LED se escreve atrás |
| /aproximar | slow-push | aproximação lenta de cinema no rosto |
| /por-cima-do-ombro | over-the-shoulder-zoom | câmera entra num canto com gráfico de vidro ao lado da cabeça, depois no outro |
| /mensagens | messages | notificações de mensagem chegando uma atrás da outra |
| /grade-do-perfil | place-in-grid | você encolhe pro centro da grade do perfil e os reels aparecem em volta |
| /figurinha | figurinha | congela e você vira figurinha recortada com borda branca e etiqueta de nome |
| /particulas | particulas-celular | celular enchendo de grãos com a porcentagem e virando o reel pronto |
| /colagem | colagem-mesa | seus reels caindo como fotos numa mesa, com etiqueta em cada um |
