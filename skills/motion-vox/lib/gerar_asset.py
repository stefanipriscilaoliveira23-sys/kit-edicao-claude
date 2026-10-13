#!/usr/bin/env python3
"""
Gera (ou importa) um objeto que o kit nao tem. Ver SKILL.md, "Quando faltar um objeto".

O prompt sai SEMPRE do esqueleto de `referencias/prompts-asset.md`: objeto isolado,
de cima, fundo cinza liso, sem texto, sem sombra. O PNG cru vai para
`07_assets/raw/NOME.png`; depois e so recortar com `cutout.py`.

  # 1. so montar o prompt (para colar no ChatGPT ou no app do Gemini, ate no celular)
  python3 gerar_asset.py A20_CANECA --objeto "One white ceramic coffee mug" \
      --material "Matte glaze, small chip on the rim" --fundo claro --so-prompt

  # 2. gerar direto, se houver chave na variavel de ambiente
  #    GEMINI_API_KEY (modelos de imagem do Gemini) ou OPENAI_API_KEY (gpt-image)
  python3 gerar_asset.py A20_CANECA --objeto "..." --material "..." --fundo claro

  # 3. importar a imagem que a pessoa mandou de volta (jpg, png, webp, heic do celular)
  python3 gerar_asset.py A20_CANECA --importar ~/Downloads/caneca.jpg

Depois:  python3 cutout.py --sweep A20_CANECA   (escolha o PLATO)
         acrescente A20_CANECA ao CFG do cutout.py e rode  python3 cutout.py A20_CANECA

A chave NUNCA vai para arquivo: so a variavel de ambiente, durante o comando.
fundo claro = objeto claro (papel, cartao, metal claro) -> cinza medio #8A8A8A
fundo escuro = objeto escuro (teclado, plastico preto)  -> cinza claro #D8D8D8
"""
import argparse, base64, io, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "07_assets" / "raw"

ESQUELETO = (
    "Single isolated object centered on a completely flat plain neutral {cor} backdrop "
    "hex {hex}. {objeto}, photographed straight from directly overhead, perfect top-down "
    "view. {material}. Even soft diffuse light, no cast shadow on the backdrop, object "
    "fully within frame with clear separation from background. Muted desaturated color, "
    "matte finish, no glossy highlights. Documentary object photograph. No text, no "
    "letters, no numbers, no symbols, no brand, no logo anywhere. No glossy 3D render, "
    "no neon, no glow, no gradients, no HDR, no AI-polished look.")
FUNDOS = {"claro": ("medium gray", "#8A8A8A"), "escuro": ("light gray", "#D8D8D8")}


def montar(objeto, material, fundo):
    cor, hx = FUNDOS[fundo]
    return ESQUELETO.format(cor=cor, hex=hx, objeto=objeto.rstrip("."),
                            material=material.rstrip("."))


def _gemini(prompt, chave, aspecto):
    for modelo in ("gemini-3-pro-image", "gemini-3.1-flash-image", "gemini-2.5-flash-image"):
        body = {"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseModalities": ["IMAGE"],
                                     "imageConfig": {"aspectRatio": aspecto}}}
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": chave})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=300))
        except urllib.error.HTTPError as e:
            print(f"  {modelo}: HTTP {e.code} — tentando o proximo")
            continue
        for c in r.get("candidates", []):
            for p in c.get("content", {}).get("parts", []):
                d = p.get("inlineData") or p.get("inline_data")
                if d:
                    return base64.b64decode(d["data"]), modelo
    return None, None


def _openai(prompt, chave, aspecto):
    size = {"1:1": "1024x1024", "9:16": "1024x1536", "3:4": "1024x1536",
            "16:9": "1536x1024"}.get(aspecto, "1024x1024")
    for modelo in ("gpt-image-2", "gpt-image-1"):
        req = urllib.request.Request(
            "https://api.openai.com/v1/images/generations",
            data=json.dumps({"model": modelo, "prompt": prompt, "size": size,
                             "quality": "high", "n": 1}).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + chave})
        try:
            r = json.load(urllib.request.urlopen(req, timeout=600))
            return base64.b64decode(r["data"][0]["b64_json"]), modelo
        except urllib.error.HTTPError as e:
            print(f"  {modelo}: HTTP {e.code} — tentando o proximo")
    return None, None


def salvar(nome, dados_ou_caminho):
    RAW.mkdir(parents=True, exist_ok=True)
    src = dados_ou_caminho
    im = Image.open(io.BytesIO(src) if isinstance(src, bytes) else src)
    im = im.convert("RGB")                   # sem alfa: o recorte e feito pelo cutout.py
    dst = RAW / f"{nome}.png"
    if dst.exists():                         # nunca sobrescreve: guarda a anterior
        dst.rename(RAW / f"{nome}_anterior_{time.strftime('%Y%m%d%H%M%S')}.png")
    im.save(dst)
    print(f"  salvo: {dst}  {im.width}x{im.height}")
    return dst


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("nome", help="nome do asset, ex. A20_CANECA")
    ap.add_argument("--objeto", help="objeto e estado, em ingles")
    ap.add_argument("--material", default="Natural light wear", help="material e desgaste")
    ap.add_argument("--fundo", choices=FUNDOS, default="claro")
    ap.add_argument("--prompt", help="prompt completo pronto (ignora --objeto/--material)")
    ap.add_argument("--aspecto", default="1:1", help="1:1, 3:4, 9:16, 16:9")
    ap.add_argument("--so-prompt", action="store_true", help="so imprime o prompt")
    ap.add_argument("--importar", help="imagem que a pessoa mandou de volta")
    a = ap.parse_args()

    if a.importar:
        salvar(a.nome, a.importar)
        print(f"  proximo passo: python3 cutout.py --sweep {a.nome}")
        return

    if not (a.prompt or a.objeto):
        sys.exit("informe --objeto (ou --prompt)")
    prompt = a.prompt or montar(a.objeto, a.material, a.fundo)
    print("PROMPT:\n" + prompt + "\n")
    if a.so_prompt:
        return

    g, o = os.environ.get("GEMINI_API_KEY"), os.environ.get("OPENAI_API_KEY")
    dados = modelo = None
    if g:
        dados, modelo = _gemini(prompt, g, a.aspecto)
    if not dados and o:
        dados, modelo = _openai(prompt, o, a.aspecto)
    if not dados:
        print("Nenhum gerador respondeu (sem chave, ou chave sem credito/cota de imagem).\n"
              "Plano B: cole o PROMPT acima no ChatGPT ou no app do Gemini, peca a imagem\n"
              f"quadrada, e depois rode:  python3 gerar_asset.py {a.nome} --importar ARQUIVO")
        sys.exit(2)
    salvar(a.nome, dados)
    print(f"  modelo: {modelo}")
    print(f"  proximo passo: python3 cutout.py --sweep {a.nome}")


if __name__ == "__main__":
    main()
