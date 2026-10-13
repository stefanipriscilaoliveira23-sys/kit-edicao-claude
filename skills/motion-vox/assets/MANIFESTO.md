# Manifesto dos assets

O kit tem 16 objetos. **9 já vêm prontos** nesta pasta. **7 são gerados sob demanda**:
quando uma cena precisar de um deles, a IA gera (ou te entrega o prompt para colar no
ChatGPT/Gemini), recorta e salva aqui, seguindo `SKILL.md`, seção "Quando faltar um
objeto". Não é instalação quebrada: é o kit crescendo conforme o uso.

Origem dos prontos: gerados no ChatGPT em 13/10/2026 com os prompts do kit
(`referencias/prompts-asset.md`) e recortados localmente com `lib/cutout.py`.
Podem ser repassados junto com a skill.

## Prontos

| Arquivo | O que é | Tamanho | Como foi tratado |
| --- | --- | --- | --- |
| `BG_PAPER.png` | fundo de mesa: papel marfim pontilhado | 1080×1920 | sem recorte; ajustado de 1024×1536 para 1080×1920 por escala 1,25 e corte central (sem distorcer). No projeto vai para `07_assets/raw/` |
| `A02_CLOCK.png` | despertador de dois sinos, mostrador só com tracinhos, sem ponteiros | 768×1015 | `tol=12`, vão entre a alça e os sinos limpo por `seeds`. Mostrador medido em `kit.py` (`DIAL_CX/CY/R` = 0,5039 / 0,6102 / 0,3685) |
| `A03_TAPE.png` | 4 tiras de fita crepe | 1007×887 | `tol=16`; `piece()` separa as 4 |
| `A04_CLIPS.png` | 3 clipes de papel de aço | 802×851 | `tol=12`, `grad=16`, `trim=2`, `punch_bg` (miolo dos clipes); `piece()` separa os 3 |
| `A05_CARD.png` | folha de papel aquarela com borda rasgada | 908×1228 | `tol=16`; também é o cartão da foto noturna em `photo_card()` |
| `A06_CAVE.png` | gravura antiga de uma caverna em papel envelhecido | 1029×1006 | `tol=16` |
| `A07_IDEA.png` | papel amassado com rabisco abstrato (sem letras) | 908×886 | `tol=12` |
| `A08_BOX.png` | caixa de papelão branca, fechada, sem marca | 836×777 | `tol=16` |
| `A09_STACK.png` | pilha de fichas brancas | 807×579 | `tol=16` |

Conferidos um a um: sem texto, sem número, sem sombra embutida, borda limpa, sem buraco.

## Gerados sob demanda

O prompt de cada um está pronto em `referencias/prompts-asset.md`.

| Arquivo | O que é | Tratamento depois de gerar |
| --- | --- | --- |
| `A10_SCRAPS.png` | 4 retalhos de papel rasgado | `cutout.py` |
| `A11_NIGHT.png` | foto noturna, pessoa no notebook, tela como única luz | `night_photo.py` (não usa `cutout.py`); recalibrar `CROP` e `SCREEN`/`SCREEN_WH` no `kit.py` |
| `A12_KEYBOARD.png` | teclado escuro com teclas gastas | `cutout.py` com fundo claro `#D8D8D8` e `dark_floor` |
| `A13_EMPTY.png` | a mesma mesa, horas depois, vazia e apagada | `night_photo.py`; recalibrar `CROP_EMPTY` e `LAPTOP`/`LAPTOP_WH` |
| `A14_CRT.png` + `A14_CRT_screen.npy` | monitor CRT bege em três-quartos | `cutout.py`; medir o quadrilátero da tela e salvar o `.npy` (frações TL, TR, BR, BL) |
| `A15_MONEY_STACK.png` | maço alto de cédulas genéricas | `cutout.py` |
| `A17_MONEY_FEW.png` | três cédulas genéricas em leque | `cutout.py` |

## Objetos novos

Todo objeto que a IA gerar para uma cena entra aqui, com uma linha nesta tabela.

| Arquivo | O que é | Origem e data | Tratamento |
| --- | --- | --- | --- |
