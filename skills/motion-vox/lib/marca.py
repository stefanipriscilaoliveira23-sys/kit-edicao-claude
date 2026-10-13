#!/usr/bin/env python3
"""
Cores de acento da marca.

A identidade MOTION-VOX tem dois acentos: amarelo #DBD653 e azul #2E82F7. Quem tem
marca propria pode trocar os dois sem mexer no codigo: basta criar o arquivo

    ~/minha-marca/marca.json

com os campos (qualquer um dos dois pode faltar):

    {
      "cor_destaque_1": "#DBD653",     substitui o AMARELO (sublinhado de marcador)
      "cor_destaque_2": "#2E82F7"      substitui o AZUL (linha de continuidade, foto noturna)
    }

Sem o arquivo, ou com valor invalido, valem as cores originais. Nada mais muda:
papel, tinta, sombras e fontes continuam os da identidade.

    python3 marca.py        # mostra quais cores estao valendo e de onde vieram
"""
import json
from pathlib import Path

ARQUIVO = Path.home() / "minha-marca" / "marca.json"

PADRAO_1 = (219, 214, 83)    # #DBD653  amarelo
PADRAO_2 = (46, 130, 247)    # #2E82F7  azul


def _hex(v):
    """'#AABBCC' ou 'AABBCC' -> (r, g, b). Devolve None se nao for uma cor valida."""
    if not isinstance(v, str):
        return None
    s = v.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    if len(s) != 6:
        return None
    try:
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def _ler():
    try:
        return json.loads(ARQUIVO.read_text(encoding="utf-8"))
    except Exception:
        return {}


def acentos():
    """(cor_destaque_1, cor_destaque_2, origem). Nunca levanta erro."""
    d = _ler()
    c1 = _hex(d.get("cor_destaque_1")) or PADRAO_1
    c2 = _hex(d.get("cor_destaque_2")) or PADRAO_2
    origem = "marca.json" if (c1 != PADRAO_1 or c2 != PADRAO_2) else "padrao"
    return c1, c2, origem


if __name__ == "__main__":
    c1, c2, o = acentos()
    print(f"arquivo: {ARQUIVO} ({'existe' if ARQUIVO.exists() else 'nao existe'})")
    print(f"cor_destaque_1 (amarelo): #{c1[0]:02X}{c1[1]:02X}{c1[2]:02X}")
    print(f"cor_destaque_2 (azul):    #{c2[0]:02X}{c2[1]:02X}{c2[2]:02X}")
    print(f"origem: {o}")
