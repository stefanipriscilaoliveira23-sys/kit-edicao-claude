#!/usr/bin/env python3
"""
Monta o plano do Sanfoninha (plano.json) a partir do brutos.json (olhar_brutos.py).

  python3 -I montar_plano.py TRABALHO/brutos.json --bpm 128 --saida TRABALHO/plano.json \
      [--musica musica.mp3 --musica-inicio 12.34 | --sem-som | --batida-sintetica] \
      [--alvo 17] [--flash 4] [--texto-gancho "texto"]

Estrutura (igual a referencia):
  gancho     1o video, ~1,7 s, zoom forte, sai em sanfona
  processo   videos do meio, 1 ou 2 batidas cada (~0,4 a 0,95 s), saidas em rodizio:
             atravessa, sanfona, atravessa, giro
  flash      4 cenas de meia batida repetindo pedacinhos do processo (--flash 0 tira)
  resultado  os ultimos videos (papel "resultado" no brutos.json), corte seco, zoom lento,
             o ultimo escurece pro preto
O Claude pode (e deve) revisar o plano.json antes de renderizar.
"""
import argparse, json, os, sys

RODIZIO = ["atravessa", "sanfona", "atravessa", "giro"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brutos"); ap.add_argument("--saida", required=True)
    ap.add_argument("--bpm", type=float, required=True)
    ap.add_argument("--musica"); ap.add_argument("--musica-inicio", type=float, default=0.0)
    ap.add_argument("--sem-som", action="store_true"); ap.add_argument("--batida-sintetica", action="store_true")
    ap.add_argument("--alvo", type=float, default=17.0, help="duracao desejada (15 a 20 s)")
    ap.add_argument("--flash", type=int, default=4)
    ap.add_argument("--texto-gancho", default="")
    a = ap.parse_args()

    br = json.load(open(a.brutos, encoding="utf-8"))["brutos"]
    if len(br) < 3: sys.exit("precisa de pelo menos 3 videos (gancho, processo e resultado)")
    b = 60 / a.bpm
    res = [x for x in br if x["papel"] == "resultado"] or [br[-1]]
    corpo = [x for x in br if x not in res]
    gancho, processo = corpo[0], corpo[1:]

    def nb(alvo, minimo=1.0):
        return max(minimo, round(alvo / b))

    # quantas batidas por cena do processo: inteiras, entre ~0,4 e 0,95 s (a referencia usa 0,42 e 0,84)
    opcoes = [n for n in (1, 2, 3) if 0.4 <= n * b <= 0.95] or \
             [n for n in (0.5, 1.5, 2.5) if 0.4 <= n * b <= 0.95] or [min((1, 2), key=lambda n: abs(n * b - 0.7))]
    padrao = [opcoes[0]] if len(opcoes) == 1 else [opcoes[0], opcoes[1], opcoes[1]]

    def momento(p, desloc, dur):
        """outro pedacinho do mesmo bruto (pra flash ou segunda passada)."""
        ini = p["inicio"] + desloc
        if ini < 0 or ini + dur > p["duracao"] - 0.05: ini = p["inicio"] - desloc
        return round(min(max(0.0, ini), max(0.0, p["duracao"] - dur - 0.05)), 2)

    cenas = [dict(arquivo=gancho["arquivo"], inicio=gancho["inicio"], batidas=nb(1.7, 3), papel="gancho",
                  saida="sanfona")]
    for i, p in enumerate(processo):
        cenas.append(dict(arquivo=p["arquivo"], inicio=p["inicio"], batidas=padrao[i % len(padrao)],
                          papel="processo", saida=RODIZIO[i % 4], foco_x=p.get("foco_x", 0.5)))

    nflash = min(a.flash, len(processo))
    meia = 0.5 if 0.5 * b >= 0.19 else 1
    tempo = lambda: sum(c["batidas"] for c in cenas) * b
    # resultado: ~30% do alvo (minimo 3 s), limitado ao tamanho dos brutos de resultado
    dur_res_max = sum(max(0.5, r["duracao"] - 0.15) for r in res)
    dur_res = min(dur_res_max, max(3.0, 0.3 * a.alvo))
    # poucos videos? repete outros momentos dos brutos do processo (segunda passada) ate chegar no alvo
    k = 0
    while processo and tempo() + nflash * meia * b + dur_res < min(a.alvo, 20) - 0.6 and k < 2 * len(processo):
        p = processo[(k + 1) % len(processo)]                   # comeca no 2o pra nao repetir o ultimo
        bt = padrao[(len(cenas) - 1) % len(padrao)]
        cenas.append(dict(arquivo=p["arquivo"], inicio=momento(p, 1.3 if k < len(processo) else 2.2, bt * b), batidas=bt, papel="processo",
                          saida=RODIZIO[(len(cenas) - 1) % 4], foco_x=p.get("foco_x", 0.5)))
        k += 1
    if processo: cenas[-1]["saida"] = "seco"
    if k: print(f"(poucos videos: repeti {k} outros momentos dos brutos do processo pra chegar no tempo)")

    if nflash:
        passo = len(processo) / nflash
        for j in range(nflash):
            p = processo[int(j * passo + passo / 2) if passo >= 1 else j]
            c = dict(arquivo=p["arquivo"], inicio=momento(p, 0.35, meia * b), batidas=meia, papel="flash",
                     saida="seco", foco_x=p.get("foco_x", 0.5))
            if j == 2: c["entrada"] = "giro"
            cenas.append(c)

    usado = tempo()
    resto = min(dur_res_max, max(3.0, a.alvo - usado))
    if a.alvo - usado < 3.0 and nflash:                       # passou do alvo: tira o flash primeiro
        cenas = [c for c in cenas if c["papel"] != "flash"]
        usado = tempo(); resto = min(dur_res_max, max(3.0, a.alvo - usado))
    pesos = [1.0] * (len(res) - 1) + [1.6]
    for i, r in enumerate(res):
        dur = resto * pesos[i] / sum(pesos)
        cenas.append(dict(arquivo=r["arquivo"], inicio=r["inicio"], batidas=nb(dur, 2), papel="resultado",
                          saida="seco", foco_x=r.get("foco_x", 0.5)))
    # o resultado pede mais tempo do que o bruto tem? encurta e avisa
    for c in cenas:
        d = next(x["duracao"] for x in br if x["arquivo"] == c["arquivo"])
        while c["batidas"] * b > d - 0.1 and c["batidas"] > 1:
            c["batidas"] -= 1
        if c["inicio"] + c["batidas"] * b > d - 0.05:
            c["inicio"] = round(max(0.0, d - c["batidas"] * b - 0.05), 2)

    plano = dict(bpm=a.bpm, musica=os.path.abspath(a.musica) if a.musica else None,
                 musica_inicio=a.musica_inicio, sem_som=a.sem_som, batida_sintetica=a.batida_sintetica,
                 texto_gancho=a.texto_gancho, cenas=cenas)
    json.dump(plano, open(a.saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    t = 0.0
    for i, c in enumerate(cenas):
        d = c["batidas"] * b
        print(f"{i+1:2d} {c['papel']:9s} {os.path.basename(c['arquivo']):14s} desde {c['inicio']:5.2f}s  "
              f"{t:5.2f}-{t+d:5.2f}  ({c['batidas']:g} bat = {d:.2f}s)  sai={c['saida']}")
        t += d
    print(f"total {t:.2f}s  ->  {a.saida}")
    if not 15 <= t <= 20.5: print("AVISO: fora de 15 a 20 s. Ajuste --alvo, --flash ou as batidas no plano.")


if __name__ == "__main__":
    main()
