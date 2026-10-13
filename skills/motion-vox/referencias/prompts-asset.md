# Prompts de asset

Um objeto por prompt. Sempre isolado, sempre fotográfico, nunca ilustração genérica.

## Esqueleto — objeto isolado

```
Single isolated object centered on a completely flat plain neutral <COR DO FUNDO>
backdrop hex <HEX>. <OBJETO E ESTADO>, photographed straight from directly overhead,
perfect top-down view. <MATERIAL E DESGASTE>. Even soft diffuse light, no cast shadow
on the backdrop, object fully within frame with clear separation from background.
Muted desaturated color, matte finish, no glossy highlights. Documentary object
photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere.
No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

Fundo: `#8A8A8A` para objeto claro · `#D8D8D8` para objeto escuro.

## Esqueleto — fundo de mesa (1080×1920)

```
Background plate only, nothing on it. Flat straight-down photograph of warm ivory
dotted grid paper filling the entire vertical frame edge to edge. Fine regular light
warm-gray dot grid. Subtle paper fiber texture, matte uncoated surface, very slight
uneven aging. Even soft diffuse light, completely flat lighting. Absolutely empty:
no objects, no props, no writing, no text, no border, no frame, no shadow, no vignette.
Muted desaturated warm neutral palette around hex D9D8D1. Fine film grain.
```

## Esqueleto — fotografia noturna (fonte única de luz)

```
Documentary reportage photograph, dark room at night. <SUJEITO E POSTURA>. <A FONTE>
is the single light source in the entire frame: cool light falls on <O QUE RECEBE LUZ>,
and everything else drops into deep near-black shadow. No lamp, no window, no second
source. Coarse 35mm film grain, very high contrast, crushed matte blacks, heavily
desaturated. Natural photographic light only: no glow effect, no bloom, no halation,
no lens flare, no neon, no rim light, no volumetric light rays, no particles. <A TELA>
shows only an indistinct pale field with no readable interface, no text, no letters,
no numbers, no icons, no logo. Editorial reportage on pushed black and white film.
```

Depois trate com mapa de gradiente (`night_photo.py`) — ver armadilha 18.

## Regras que não podem faltar

| Sempre | Por quê |
| --- | --- |
| `no cast shadow on the backdrop` | sombra é camada |
| `no text, no letters, no numbers, no logo, no brand` | texto de IA é BLOCKER |
| `no glow, no bloom, no neon, no gradients, no HDR` | proibições da identidade |
| `matte finish, no glossy highlights` | material fosco |
| `muted desaturated` | 80% neutros |

## Casos especiais

**Mostrador (relógio, medidor):** peça `plain unmarked dial with only twelve small thin
tick marks, absolutely no numbers, no numerals, no digits`. Redesenhe os ponteiros em
PIL a partir de um total em minutos com fração — a hora vira dado controlado e animável.

**Teclado, teclas, botões:** peça `legends worn away to the point of being illegible
smudges`. Impede letra de IA sem impedir o objeto.

**Papel amassado com rabisco:** peça `a pure abstract tangle of looping lines only:
no letters, no words, no numbers, no diagram, no recognizable shape`.

**Embalagem, caixa:** `completely unbranded and blank: no printing, no label, no tape,
no barcode, no logo, no arrows, no symbols`.

## Variantes

Gere 2–3 variantes de qualquer asset que seja herói de cena. Barato, e a rejeitada
costuma ensinar algo — uma das variantes de teclado voltou com "1993" no canto, texto
de IA que teria passado se fosse a única.

## Prompts prontos dos 16 objetos do kit

Cada objeto do kit, o que ele é, e o prompt exato para gerar de novo (ou para trocar por
uma versão sua). Copie o bloco inteiro. Funciona no ChatGPT, no app do Gemini, ou pelo
`lib/gerar_asset.py NOME --prompt "..."`. Os nomes de arquivo são exatos: o código procura
por eles. O A16 não existe no kit (numeração herdada).

### BG_PAPER

**O que é:** fundo de mesa: papel marfim pontilhado, chão de toda cena de mesa.  
**Como:** 9:16 (vai para 07_assets/raw/, redimensionar para 1080x1920; não recorta).

```
Background plate only, nothing on it. Flat straight-down photograph of warm ivory dotted grid paper filling the entire vertical frame edge to edge. Fine regular light warm-gray dot grid. Subtle paper fiber texture, matte uncoated surface, very slight uneven aging. Even soft diffuse light, completely flat lighting. Absolutely empty: no objects, no props, no writing, no text, no border, no frame, no shadow, no vignette. Muted desaturated warm neutral palette around hex D9D8D1. Fine film grain.
```

### A02_CLOCK

**O que é:** despertador de duas campainhas, mostrador sem números (só tracinhos) e sem ponteiros: os ponteiros são desenhados em PIL.  
**Como:** 1:1, fundo #8A8A8A. Depois medir DIAL_CX/DIAL_CY/DIAL_R no recorte e atualizar kit.py.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. A vintage cream-white mechanical twin-bell alarm clock lying flat on its back, round face up, with a plain unmarked dial with only twelve small thin tick marks, absolutely no numbers, no numerals, no digits, and no hands at all, only the small bare center pin, photographed straight from directly overhead, perfect top-down view. Off-white enamel dial, brushed pale steel bezel and bells, light scuffs and age marks on the metal. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A03_TAPE

**O que é:** tiras de fita crepe com ponta rasgada (etiquetas; kit.piece() separa cada tira).  
**Como:** 1:1, fundo #8A8A8A.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. Four separate short strips of beige crepe masking tape with torn ends, laid flat and well apart from each other, not touching, each a different length, photographed straight from directly overhead, perfect top-down view. Matte crinkled crepe paper texture, slightly translucent, irregular torn fibrous ends, plain blank tape. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A04_CLIPS

**O que é:** clipes de papel soltos, separados.  
**Como:** 1:1, fundo #8A8A8A, CFG com punch_bg=True (miolo do clipe).

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. Three separate classic silver steel paper clips lying flat, well apart from each other, not touching, slightly different angles, photographed straight from directly overhead, perfect top-down view. Matte brushed steel wire, slightly worn, one clip a little bent. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A05_CARD

**O que é:** cartão de papel de algodão branco-frio, retrato ~5x7, bordas rasgadas: vira moldura da foto noturna e a folha do wipe.  
**Como:** 3:4, fundo #8A8A8A.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. One blank rectangular sheet of thick cool-white cotton watercolor paper in portrait orientation, proportion about five wide by seven tall, lying perfectly flat, photographed straight from directly overhead, perfect top-down view. Soft deckled hand-torn edges on all four sides, visible cotton fiber texture, completely blank and empty, no marks, no drawing. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A06_CAVE

**O que é:** gravura antiga impressa de uma caverna (traço de buril), em folha rasgada. A IDENTIDADE.md registra que como metáfora foi reprovada: use só se a fala citar caverna.  
**Como:** 1:1, fundo #8A8A8A.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. One old loose antique printed engraving on an off-white paper sheet, depicting the dark interior mouth of a rocky cave rendered entirely in fine black ink cross-hatching lines, no people, no caption, no border lettering, photographed straight from directly overhead, perfect top-down view. Aged ivory rag paper with torn deckled edges, fine etched line work, slight foxing spots, no title, no signature, no plate number. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A07_IDEA

**O que é:** folha amassada e desamassada com rabisco abstrato a lápis: a IDEIA crua (par de 'ideia -> produto' com A08_BOX).  
**Como:** 1:1, fundo #8A8A8A.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. One sheet of plain white paper that was crumpled into a ball and then flattened again, with a quick pencil scribble on it that is a pure abstract tangle of looping lines only: no letters, no words, no numbers, no diagram, no recognizable shape, photographed straight from directly overhead, perfect top-down view. Deep crumple creases and folds catching soft light, matte uncoated paper, graphite gray loose lines. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A08_BOX

**O que é:** caixa de papelão branca fechada, sem marca: o PRODUTO pronto.  
**Como:** 1:1, fundo #8A8A8A.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. One closed plain white cardboard product box, rectangular, seen from above with a slight angle so the top face and one side face are visible, completely unbranded and blank: no printing, no label, no tape, no barcode, no logo, no arrows, no symbols, photographed straight from directly overhead, perfect top-down view. Matte uncoated white board with slightly soft corners, faint handling wear on the edges. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A09_STACK

**O que é:** pilha de fichas/cartões em branco (volume, acúmulo). IDENTIDADE.md: como 'produto' sumiu sob o rótulo.  
**Como:** 1:1, fundo #8A8A8A, CFG min_area=0.004.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. One neat but imperfect stack of about thirty blank white index cards seen from above at a slight angle so the layered edges are visible, the cards slightly misaligned, photographed straight from directly overhead, perfect top-down view. Matte card stock, plain blank cards without lines, soft worn corners. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A10_SCRAPS

**O que é:** retalhos de papel rasgado, separados (props periféricos cortados pela borda).  
**Como:** 1:1, fundo #8A8A8A.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. Four separate scraps of torn ivory paper of different sizes and irregular shapes, lying flat and well apart from each other, not touching, photographed straight from directly overhead, perfect top-down view. Rough torn fibrous edges showing paper fibers, matte uncoated paper, completely blank, no writing. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A11_NIGHT

**O que é:** foto noturna: pessoa no escuro iluminada só pela tela do notebook.  
**Como:** 1:1, salvar cru como 07_assets/raw/A11_NIGHT_v1.png e tratar com night_photo.py (não usa cutout.py). Recalibrar CROP e SCREEN/SCREEN_WH no kit.py.

```
Documentary reportage photograph, dark room at night. A young adult seen from the side and slightly behind, sitting at a desk, leaning toward an open laptop on the right side of the frame, absorbed in work, face turned to the screen. The laptop screen is the single light source in the entire frame: cool light falls on the face, hands and the desk surface, and everything else drops into deep near-black shadow. No lamp, no window, no second source. Coarse 35mm film grain, very high contrast, crushed matte blacks, heavily desaturated. Natural photographic light only: no glow effect, no bloom, no halation, no lens flare, no neon, no rim light, no volumetric light rays, no particles. The laptop screen shows only an indistinct pale field with no readable interface, no text, no letters, no numbers, no icons, no logo. Editorial reportage on pushed black and white film.
```

### A12_KEYBOARD

**O que é:** teclado escuro com teclas apagadas (ilegíveis).  
**Como:** 16:9, fundo #D8D8D8 (objeto escuro), CFG com dark_floor.

```
Single isolated object centered on a completely flat plain neutral light gray backdrop hex #D8D8D8. One old dark charcoal gray computer keyboard, full size, lying flat, with key legends worn away to the point of being illegible smudges, photographed straight from directly overhead, perfect top-down view. Matte dark plastic, worn shiny spots only where fingers rest, dust between the keys, no visible characters on any key. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A13_EMPTY

**O que é:** a MESMA cena da A11 com a pessoa fora e o notebook APAGADO (par de contraste).  
**Como:** 1:1, gerar passando a A11 crua como imagem de referência; salvar como raw/A13_EMPTY_v1.png e tratar com night_photo.py. Recalibrar CROP_EMPTY e LAPTOP/LAPTOP_WH no kit.py.

```
Same room, same desk, same camera position and framing as this photograph, a few hours later: the person is gone, the chair is empty, and the laptop on the desk is switched off with its screen dark and closed halfway. With the screen off there is no light source anymore: only a very faint, flat, cold ambient night light lets the shapes of the desk, the empty chair and the dark laptop be barely readable. Documentary reportage photograph, coarse 35mm film grain, high contrast, crushed matte blacks, heavily desaturated, black and white. No lamp, no window light, no glow, no bloom, no lens flare. No text, no letters, no numbers, no logo anywhere.
```

### A14_CRT

**O que é:** monitor de tubo antigo bege em três-quartos, tela desligada.  
**Como:** 1:1, fundo #8A8A8A. Depois medir o quadrilátero da tela e salvar A14_CRT_screen.npy (frações TL,TR,BR,BL).

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. One old beige CRT computer monitor from the early 1990s, standing, photographed from slightly above in three-quarter view so the deep tube body and the front screen are visible, the screen switched off showing only a uniform dark gray glass, photographed straight from directly overhead, perfect top-down view. Yellowed matte beige plastic casing with faint scuffs, rounded glass screen with no reflection of anything, completely unbranded: no logo, no buttons labels, no badge, no sticker. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A15_MONEY_STACK

**O que é:** maço grosso de cédulas genéricas (impressão ilegível, nenhuma moeda real).  
**Como:** 1:1, fundo #8A8A8A, gerar 2-3 variantes (armadilha 27).

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. One thick tall stack of generic paper banknotes held by a plain paper band, seen from above at a slight angle so the layered edges are visible; the printed design is an indistinct engraved pattern only, no readable numbers, no denomination, no portraits, no seals, not any real currency, photographed straight from directly overhead, perfect top-down view. Muted pale green-gray and cream paper, slight wear on edges, fine engraved line texture. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```

### A17_MONEY_FEW

**O que é:** poucas cédulas soltas (o 'antes' do maço).  
**Como:** 1:1, fundo #8A8A8A, gerar 2-3 variantes.

```
Single isolated object centered on a completely flat plain neutral medium gray backdrop hex #8A8A8A. Only three generic paper banknotes lying loosely fanned out flat, slightly overlapping; the printed design is an indistinct engraved pattern only, no readable numbers, no denomination, no portraits, no seals, not any real currency, photographed straight from directly overhead, perfect top-down view. Muted pale green-gray and cream paper, slightly creased and worn, fine engraved line texture. Even soft diffuse light, no cast shadow on the backdrop, object fully within frame with clear separation from background. Muted desaturated color, matte finish, no glossy highlights. Documentary object photograph. No text, no letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, no neon, no glow, no gradients, no HDR, no AI-polished look.
```
