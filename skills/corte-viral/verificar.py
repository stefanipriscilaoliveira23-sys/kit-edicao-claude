#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checagem de instalacao da skill corte-viral.

Roda antes do primeiro projeto. E mais barato descobrir aqui do que no meio de
uma run que ja gastou a transcricao.

    python3 ~/.claude/skills/corte-viral/verificar.py
    python3 ~/.claude/skills/corte-viral/verificar.py --testar-recorte   (testa de verdade o recorte da pessoa)
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# O python3 do PATH pode ser o 3.9 do sistema. Diagnosticar com ele daria um
# retrato do interpretador errado, entao reentra na venv da skill quando existe.
_VENV_PY = ROOT / ".venv" / "bin" / "python"
if not _VENV_PY.exists():
    _VENV_PY = ROOT / ".venv" / "Scripts" / "python.exe"   # Windows
if _VENV_PY.exists() and Path(sys.executable).resolve() != _VENV_PY.resolve():
    import os
    os.execv(str(_VENV_PY), [str(_VENV_PY), str(Path(__file__).resolve()), *sys.argv[1:]])

AGENTS_HOME = Path.home() / ".claude" / "agents"
OK, FALHA, AVISO = "  ok  ", " FALTA", " aviso"

problemas: list[str] = []
avisos: list[str] = []


def linha(estado: str, texto: str, detalhe: str = "") -> None:
    print(f"[{estado}] {texto}" + (f"  — {detalhe}" if detalhe else ""))


def secao(titulo: str) -> None:
    print(f"\n{titulo}")
    print("-" * len(titulo))


def _checar_libass(ffmpeg: str) -> None:
    """
    Queimar legenda usa o filtro `ass` do ffmpeg. Sem libass ele nao existe.
    So importa se `make_captioned_version` for ligado no config - o padrao desta
    skill e entregar o vertical limpo, e a motion-vox queima por conta propria.
    """
    import re
    try:
        proc = subprocess.run([ffmpeg, "-hide_banner", "-filters"],
                              capture_output=True, text=True, timeout=30)
    except Exception:
        return
    saida = (proc.stdout or "") + (proc.stderr or "")
    # Palavra inteira: "ass" como substring casa com lowpass/highpass/bass/allpass.
    tem = bool(re.search(r"^\s*\S*\s+(subtitles|ass)\s", saida, re.MULTILINE))
    if tem:
        linha(OK, "filtro ass/subtitles", "queima de legenda disponivel se voce ligar")
    else:
        linha(AVISO, "filtro ass/subtitles ausente",
              "ffmpeg sem libass: NAO ligue make_captioned_version. "
              "O padrao (vertical limpo -> motion-vox) nao e afetado.")
        avisos.append("ffmpeg sem libass (queima de legenda indisponivel)")


def checar_binarios() -> None:
    secao("Binarios")
    for nome, obrigatorio, como in [
        ("ffmpeg", True, "brew install ffmpeg"),
        ("ffprobe", True, "brew install ffmpeg"),
        ("yt-dlp", False, "brew install yt-dlp — so para puxar legenda do YouTube"),
    ]:
        caminho = shutil.which(nome)
        if caminho:
            linha(OK, nome, caminho)
            if nome == "ffmpeg":
                _checar_libass(caminho)
        elif obrigatorio:
            linha(FALHA, nome, como)
            problemas.append(f"{nome} ausente")
        else:
            linha(AVISO, nome, como)
            avisos.append(f"{nome} ausente (opcional)")


def checar_python() -> None:
    secao("Python")
    versao = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        linha(OK, f"Python {versao}", sys.executable)
    else:
        linha(FALHA, f"Python {versao}", "precisa de 3.10+")
        problemas.append("Python < 3.10")

    for modulo, obrigatorio, para_que in [
        ("yaml", True, "ler config e perfis"),
        ("jsonschema", True, "validar os artefatos — e o que segura a qualidade"),
        ("faster_whisper", False, "transcrever sem legenda pronta"),
        ("cv2", False, "enquadramento por locutor ativo"),
        ("numpy", False, "enquadramento por locutor ativo"),
        ("PIL", False, "utilidades de imagem"),
    ]:
        existe = importlib.util.find_spec(modulo) is not None
        if existe:
            linha(OK, modulo, para_que)
        elif obrigatorio:
            linha(FALHA, modulo, f"{para_que} — pip3 install -r {ROOT}/requirements.txt")
            problemas.append(f"modulo {modulo} ausente")
        else:
            linha(AVISO, modulo, f"opcional: {para_que}")
            avisos.append(f"modulo {modulo} ausente (opcional)")


def checar_agentes() -> None:
    secao("Subagentes em ~/.claude/agents/")
    fontes = sorted((ROOT / "agentes").glob("*.md"))
    if not fontes:
        linha(FALHA, "agentes/", "pacote sem agentes — instalacao corrompida")
        problemas.append("pacote sem agentes")
        return
    faltando, defasados = [], []
    for fonte in fontes:
        destino = AGENTS_HOME / fonte.name
        if not destino.exists():
            faltando.append(fonte.name)
        elif destino.read_bytes() != fonte.read_bytes():
            defasados.append(fonte.name)
    instalados = len(fontes) - len(faltando)
    if not faltando and not defasados:
        linha(OK, f"{len(fontes)} agentes instalados e em dia")
    else:
        if faltando:
            linha(FALHA, f"{len(faltando)} nao instalado(s)", ", ".join(faltando))
            problemas.append("agentes nao instalados")
        if defasados:
            linha(FALHA, f"{len(defasados)} defasado(s)", ", ".join(defasados))
            problemas.append("agentes defasados")
        linha(AVISO, f"{instalados}/{len(fontes)} presentes",
              f"corrija com: cp {ROOT}/agentes/*.md {AGENTS_HOME}/")


def checar_pacote() -> None:
    secao("Pacote")
    for relativo in ["SKILL.md", "REGRAS.md", "INSTALAR.md", "config/default.yaml",
                     "scripts/vch.py", "models/face_detection_yunet_2023mar.onnx"]:
        caminho = ROOT / relativo
        if caminho.exists():
            linha(OK, relativo)
        else:
            linha(FALHA, relativo, "arquivo ausente")
            problemas.append(f"{relativo} ausente")

    for pasta, minimo in [("schemas", 15), ("agentes", 8), ("docs", 13),
                          ("scripts", 17), ("config/profiles", 12)]:
        padrao = "*.json" if pasta == "schemas" else ("*.py" if pasta == "scripts" else "*.*")
        n = len(list((ROOT / pasta).glob(padrao)))
        if n >= minimo:
            linha(OK, f"{pasta}/", f"{n} arquivos")
        else:
            linha(FALHA, f"{pasta}/", f"{n} arquivos, esperado >= {minimo}")
            problemas.append(f"{pasta} incompleto")


def checar_fronteira() -> None:
    secao("Fronteira com a motion-vox")
    motion = Path.home() / ".claude" / "skills" / "motion-vox"
    if motion.exists():
        linha(OK, "motion-vox instalada", "recebe o vertical limpo desta skill")
    else:
        linha(AVISO, "motion-vox nao encontrada", "esta skill entrega vertical sem legenda queimada")
        avisos.append("motion-vox ausente")
    invasores = list((ROOT / "scripts").glob("*motion*")) + list((ROOT / "schemas").glob("motion-*"))
    if invasores:
        linha(FALHA, "arquivo de motion dentro desta skill",
              ", ".join(p.name for p in invasores))
        problemas.append("escopo de motion vazou para ca")
    else:
        linha(OK, "nenhum arquivo de motion aqui", "escopo limpo")


def checar_validacao_interna() -> None:
    secao("Validacao interna do pacote")
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "vch.py"), "validate-project"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=120,
        )
    except Exception as exc:  # pragma: no cover
        linha(FALHA, "validate-project", str(exc)[:80])
        problemas.append("validate-project nao executou")
        return
    if proc.returncode == 0:
        linha(OK, "validate-project", "schemas, agentes, YAML e Python validos")
    else:
        primeira = (proc.stderr or proc.stdout or "").strip().splitlines()
        linha(FALHA, "validate-project", (primeira[0][:100] if primeira else f"saida {proc.returncode}"))
        problemas.append("validate-project reprovou")
        print(f"        detalhe: python3 {ROOT}/scripts/vch.py validate-project")


def checar_edicao() -> None:
    """Modelo de edição no jeito da marca (modelo-edicao/): avisos, não bloqueia o pipeline de cortes."""
    secao("Edicao no jeito da marca (modelo-edicao/)")
    df = next((p for p in (ROOT / "bin" / "deep-filter", ROOT / "bin" / "deep-filter.exe") if p.exists()), None)
    if df:
        linha(OK, "deep-filter", str(df.name))
    else:
        linha(AVISO, "deep-filter ausente", "ver bin/COMO-BAIXAR.md (sem ele pula so a limpeza de voz por IA)")
        avisos.append("deep-filter ausente")
    for mod in ("faster_whisper", "scipy"):
        if importlib.util.find_spec(mod):
            linha(OK, mod)
        else:
            linha(AVISO, f"{mod} ausente", "pip install -r requirements.txt")
            avisos.append(f"{mod} ausente")
    if shutil.which("node") or shutil.which("node.exe"):
        linha(OK, "node", "pro HyperFrames")
    else:
        linha(AVISO, "node ausente", "instale o Node 22 (INSTALAR.md) pra renderizar com o HyperFrames")
        avisos.append("node ausente")
    sys.path.insert(0, str(ROOT / "modelo-edicao"))
    checar_recorte()
    try:
        import marca  # noqa: E402
        falta = marca.faltando()
        if falta:
            linha(AVISO, "manual da marca incompleto", ", ".join(falta) + " -> fazer a ENTREVISTA-DA-MARCA.md")
            avisos.append("manual da marca incompleto (~/minha-marca)")
        else:
            linha(OK, "manual da marca", str(marca.ARQ_MARCA))
    except Exception as exc:  # pragma: no cover
        linha(AVISO, "marca.py", str(exc)[:80])


def checar_recorte() -> None:
    """Recorte da pessoa (texto ATRÁS da pessoa e close do retrato.py): mascara.py, Windows e Mac."""
    import os
    try:
        import mascara  # noqa: E402
    except Exception as exc:
        linha(AVISO, "mascara.py", f"nao carregou: {str(exc)[:80]}")
        avisos.append("recorte da pessoa indisponivel")
        return
    try:
        motor = mascara.escolher_motor()
    except SystemExit as exc:
        linha(AVISO, "recorte da pessoa indisponivel", str(exc))
        avisos.append("recorte da pessoa indisponivel (texto atras da pessoa fica de fora)")
        return
    cmd = mascara.cmd_hyperframes() or []
    if motor == "hyperframes" and any("npx" in os.path.basename(c) for c in cmd[:1]):
        linha(AVISO, "recorte da pessoa via npx",
              "funciona, mas rode o modelo-edicao/preparar_pasta.py pra instalar o HyperFrames fixo (hf/)")
        avisos.append("HyperFrames fixo ausente (recorte via npx)")
    else:
        linha(OK, f"recorte da pessoa ({motor})", " ".join(cmd[-1:]) if motor == "hyperframes" else "Vision do Mac")
    modelo = Path.home() / ".cache" / "hyperframes" / "background-removal" / "models" / "u2net_human_seg.onnx"
    if motor == "hyperframes":
        if modelo.exists():
            linha(OK, "modelo do recorte", str(modelo))
        else:
            linha(AVISO, "modelo do recorte ainda nao baixado",
                  "baixa sozinho (~168 MB) no primeiro uso; pra adiantar: verificar.py --testar-recorte")
    if "--testar-recorte" in sys.argv:
        _testar_recorte(mascara)


def _testar_recorte(mascara) -> None:
    """Teste de verdade: gera 1 s de video, recorta e confere o formato da mascara."""
    import json
    import tempfile
    import time
    ffmpeg = mascara.FFMPEG
    if not ffmpeg:
        linha(FALHA, "teste do recorte", "sem ffmpeg")
        problemas.append("teste do recorte falhou")
        return
    with tempfile.TemporaryDirectory() as tmp:
        ent, sai = str(Path(tmp) / "teste.mp4"), str(Path(tmp) / "mascara.mp4")
        subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=360x640:r=30:d=1",
                        "-pix_fmt", "yuv420p", ent], check=True)
        t0 = time.time()
        try:
            mascara.gerar(ent, sai, 270)
            info = json.loads(subprocess.run([mascara.FFPROBE, "-v", "error", "-count_frames", "-show_entries",
                                              "stream=width,height,nb_read_frames", "-of", "json", sai],
                                             capture_output=True, text=True).stdout)["streams"][0]
            ok = (info["width"], info["height"], int(info["nb_read_frames"])) == (270, 480, 30)
        except (SystemExit, Exception) as exc:
            ok, info = False, str(exc)[:120]
        if ok:
            linha(OK, "teste do recorte", f"30 quadros 270x480 em {time.time() - t0:.0f} s")
        else:
            linha(FALHA, "teste do recorte", str(info))
            problemas.append("teste do recorte falhou")


def main() -> int:
    print("Verificacao da skill corte-viral")
    print(f"Local: {ROOT}")
    print(f"Interpretador: {sys.executable}")
    checar_pacote()
    checar_binarios()
    checar_python()
    checar_agentes()
    checar_fronteira()
    checar_validacao_interna()
    checar_edicao()

    secao("Resultado")
    if problemas:
        print(f"{len(problemas)} problema(s) que impedem uma run completa:")
        for item in problemas:
            print(f"  - {item}")
        print(f"\nVer {ROOT}/INSTALAR.md")
        return 1
    if avisos:
        print(f"Pronto para rodar. {len(avisos)} recurso(s) opcional(is) ausente(s):")
        for item in avisos:
            print(f"  - {item}")
        return 0
    print("Tudo pronto.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
