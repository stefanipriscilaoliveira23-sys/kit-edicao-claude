# -*- coding: utf-8 -*-
"""
Recorte da pessoa (máscara) que funciona no Windows e no Mac.

Gera um vídeo de máscara: branco = pessoa, preto = fundo. É o mesmo formato que o antigo programa só de Mac
(mascara-pessoa, Vision) entregava: H.264 em .mp4, cinza, largura pedida (padrão 540), altura na proporção do vídeo
(número par), mesmo fps e mesmo número de quadros da entrada. A máscara entra depois no ffmpeg (alphamerge) pra pôr
texto ATRÁS da pessoa (render_meg.sh) e no retrato.py pra achar a caixa do close.

Uso:
  python mascara.py <entrada.mp4> <saida-mascara.mp4> [largura=540] [--motor auto|hyperframes|vision] [--sem-suavizar]
                    [--fps N]   (só pra medir, ex.: retrato.py com --fps 5: bem mais rápido, mas a máscara sai com N
                                 quadros por segundo; NÃO usar no texto atrás da pessoa)
  python mascara.py --conferir      -> diz qual motor vai ser usado (sai com erro 1 se nenhum estiver disponível)

Motores:
  hyperframes (PADRÃO, Windows e Mac): `hyperframes remove-background` da cópia fixa do HyperFrames da pasta de trabalho
      (hf/, instalada pelo preparar_pasta.py). Modelo u2net_human_seg (Apache 2.0), roda no próprio computador, sem
      internet depois da primeira vez. Na primeira vez baixa sozinho o modelo (~168 MB, em ~/.cache/hyperframes) e o
      onnxruntime-node. Sem placa de vídeo: no Windows usa o processador; no Mac com chip Apple usa o CoreML.
  vision (opcional, só Mac): o binário mascara-pessoa/mascara-pessoa (Vision da Apple). Mais rápido. Só entra se
      pedido com --motor vision ou MASCARA_MOTOR=vision.
  auto: hyperframes; se ele não existir neste computador e for Mac com o binário, vision.

MASCARA_DEVICE=cpu força o processador (o padrão escolhe sozinho: CoreML no Mac com chip Apple, CPU no Windows).
A saída do hyperframes é suavizada no tempo (mediana de 3 quadros + média leve) pra a borda não tremer.
Lê e grava quadro a quadro: vídeo longo não enche a memória.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
try:
    import marca  # noqa: E402
except Exception:  # roda solto, sem o resto da skill
    marca = None

HF_VERSAO = "0.8.107"
LARGURA_MODELO = 360  # o modelo enxerga 320x320; mandar o vídeo maior só gasta tempo


def _achar(prog):
    p = shutil.which(prog) or shutil.which(prog + ".exe") or shutil.which(prog + ".cmd")
    if p:
        return p
    extra = os.path.expanduser(os.path.join("~", ".local", "bin", prog))
    return extra if os.path.exists(extra) else None


FFMPEG, FFPROBE = _achar("ffmpeg"), _achar("ffprobe")


def _pastas_trabalho():
    """Onde pode estar a pasta hf/ com o HyperFrames fixo."""
    pastas = [os.path.dirname(AQUI)]  # scripts copiados pra <trabalho>/ed/ -> <trabalho>/hf
    if marca is not None:
        try:
            t = os.path.expanduser(marca.carregar()["pastas"].get("trabalho") or "")
            if t:
                pastas.insert(0, t)
        except Exception:
            pass
    pastas.append(os.path.expanduser(os.path.join("~", "Videos-Claude", "_trabalho")))
    return pastas


def cmd_hyperframes():
    """Comando (lista) que chama o HyperFrames fixo. None se não houver Node."""
    node = _achar("node")
    env = os.environ.get("HYPERFRAMES_CLI")
    if env and os.path.exists(env):
        return [node, env] if env.endswith((".mjs", ".js")) and node else [env]
    if node:
        for t in _pastas_trabalho():
            cli = os.path.join(t, "hf", "node_modules", "hyperframes", "bin", "hyperframes.mjs")
            if os.path.exists(cli):
                return [node, cli]
        npx = _achar("npx")
        if npx:  # sem a cópia fixa: baixa a mesma versão (uma chamada só, nunca em paralelo)
            return [npx, "-y", f"hyperframes@{HF_VERSAO}"]
    return None


def bin_vision():
    if sys.platform != "darwin":
        return None
    if marca is not None:
        b = marca.binario("modelo-edicao", "mascara-pessoa", "mascara-pessoa")
        if b:
            return b
    for p in (os.path.join(AQUI, "mascara-pessoa", "mascara-pessoa"),
              os.path.expanduser("~/.claude/skills/corte-viral/modelo-edicao/mascara-pessoa/mascara-pessoa")):
        if os.path.exists(p) and os.access(p, os.X_OK):
            return p
    return None


def escolher_motor(pedido=None):
    pedido = (pedido or os.environ.get("MASCARA_MOTOR") or "auto").lower()
    if pedido == "vision":
        if not bin_vision():
            raise SystemExit("motor vision pedido, mas o binário mascara-pessoa (só Mac) não existe aqui")
        return "vision"
    if pedido in ("auto", "hyperframes"):
        if cmd_hyperframes():
            return "hyperframes"
        if pedido == "auto" and bin_vision():
            return "vision"
        raise SystemExit("sem recorte da pessoa: instale o Node 22 e rode o preparar_pasta.py (HyperFrames fixo). Ver INSTALAR.md")
    raise SystemExit(f"motor desconhecido: {pedido} (use auto, hyperframes ou vision)")


def _sondar(caminho):
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,avg_frame_rate,r_frame_rate:stream_side_data=rotation:stream_tags=rotate",
                          "-of", "json", caminho], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    rot = 0
    for sd in s.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = rot or int(float((s.get("tags") or {}).get("rotate", 0) or 0))
    w, h = int(s["width"]), int(s["height"])
    if abs(rot) % 180 == 90:
        w, h = h, w
    taxa = s.get("avg_frame_rate") or "0/0"
    if taxa in ("0/0", "0/1"):
        taxa = s.get("r_frame_rate") or "30/1"
    return w, h, taxa


def _contar_quadros(caminho):
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                          "stream=nb_read_packets", "-of", "csv=p=0", caminho], capture_output=True, text=True).stdout
    try:
        return int(out.strip().split(",")[0])
    except ValueError:
        return 0


def suavizar3(ant, cen, dep):
    """Um quadro suavizado a partir do anterior, do atual e do seguinte (uint8 h x w).
    Mediana dos 3 (tira piscada de 1 quadro sem atrasar a máscara) e, onde a mudança é pequena (borda tremendo),
    média leve 1-2-1. Onde a pessoa se mexe de verdade fica a mediana, sem rastro."""
    import numpy as np
    a, c, d = (x.astype(np.int16) for x in (ant, cen, dep))
    med = np.maximum(np.minimum(a, c), np.minimum(np.maximum(a, c), d))
    media = (a + 2 * c + d) // 4
    return np.where(np.abs(a - d) < 48, media, med).astype(np.uint8)


def _quadros(proc, tam):
    """Lê quadros crus (bytes) do stdout de um ffmpeg, um por vez (não carrega o vídeo inteiro na memória)."""
    while True:
        b = proc.stdout.read(tam)
        if not b or len(b) < tam:
            return
        yield b


def mascara_hyperframes(entrada, saida, largura, suave=True, fps=None):
    import numpy as np
    w0, h0, taxa = _sondar(entrada)
    if fps:
        taxa = str(fps)
    W = largura
    H = int(round(W * h0 / w0 / 2.0)) * 2
    lm = min(W, LARGURA_MODELO) // 2 * 2
    hm = int(round(lm * h0 / w0 / 2.0)) * 2
    tmp = tempfile.mkdtemp(prefix=".mascara-", dir=os.path.dirname(os.path.abspath(saida)) or ".")
    try:
        pequeno = os.path.join(tmp, "entrada.mp4")
        # vídeo pequeno, já girado, fps constante (o remove-background confia no fps: fps variável desencontra)
        subprocess.run([FFMPEG, "-nostdin", "-v", "error", "-y", "-i", entrada, "-an", "-vf",
                        f"scale={lm}:{hm}:flags=area,format=yuv420p", "-fps_mode", "cfr", "-r", taxa,
                        "-c:v", "libx264", "-crf", "12", "-preset", "veryfast", pequeno], check=True)
        n_esperado = _contar_quadros(pequeno)
        mov = os.path.join(tmp, "recorte.mov")
        cache = os.path.join(os.path.expanduser("~"), ".cache", "hyperframes", "background-removal", "models",
                             "u2net_human_seg.onnx")
        if not os.path.exists(cache):
            print("[mascara] primeira vez: o HyperFrames vai baixar o modelo de recorte (~168 MB). Uma vez só.", flush=True)
        print(f"[mascara] recortando {n_esperado} quadros (o modelo leva 1 a 2 min pra carregar, sem mensagem: não travou)",
              flush=True)
        disp = os.environ.get("MASCARA_DEVICE")   # auto (padrão), cpu, coreml ou cuda
        r = subprocess.run(cmd_hyperframes() + ["remove-background", pequeno, "-o", mov] + (["--device", disp] if disp else []),
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        # o HyperFrames escreve uma barra de progresso animada: guarda só a linha final (ou o erro)
        texto = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "\n", (r.stdout or "") + "\n" + (r.stderr or ""))
        linhas = [l.strip(" ◐◓◑◒◇│") for l in texto.splitlines() if l.strip() and "Frame " not in l and "Loading model" not in l]
        if r.returncode != 0 or not os.path.exists(mov):
            print("\n".join(linhas[-12:]), file=sys.stderr)
            raise SystemExit("[mascara] o recorte do HyperFrames falhou (ver mensagem acima)")
        fim = [l for l in linhas if "Removed background" in l]
        if fim:
            print("[mascara]", fim[-1].split(" → ")[0], flush=True)
        dec = subprocess.Popen([FFMPEG, "-nostdin", "-v", "error", "-i", mov, "-vf", "alphaextract,format=gray",
                                "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
        enc = subprocess.Popen([FFMPEG, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
                                "-s", f"{lm}x{hm}", "-r", taxa, "-i", "-",
                                "-vf", f"scale={W}:{H}:flags=bicubic,format=yuv420p",
                                "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-movflags", "+faststart",
                                saida], stdin=subprocess.PIPE)
        tam = lm * hm
        n = 0

        def grava(q):
            nonlocal n
            if not n_esperado or n < n_esperado:   # nunca mais quadros que a entrada
                enc.stdin.write(q.tobytes())
                n += 1

        # janela de 3 quadros: o 1º usa ele mesmo como anterior, o último usa ele mesmo como seguinte
        ant = cen = None
        for b in _quadros(dec, tam):
            q = np.frombuffer(b, np.uint8).reshape(hm, lm)
            if cen is not None:
                grava(suavizar3(ant, cen, q) if suave else cen)
            ant, cen = (cen if cen is not None else q), q
        if cen is not None:
            grava(suavizar3(ant, cen, cen) if suave else cen)
            while n_esperado and n < n_esperado:   # mesmo número de quadros da entrada
                grava(cen)
        dec.wait()
        enc.stdin.close()
        if enc.wait() != 0:
            raise SystemExit("[mascara] ffmpeg falhou ao gravar a máscara")
        return n, W, H
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def gerar(entrada, saida, largura=540, motor=None, suave=True, fps=None):
    motor = escolher_motor(motor)
    if motor == "vision":
        subprocess.run([bin_vision(), entrada, saida, str(largura)], check=True)
        print(f"ok (vision) -> {saida}")
        return motor
    if not FFMPEG or not FFPROBE:
        raise SystemExit("ffmpeg/ffprobe não encontrados (ver INSTALAR.md)")
    n, W, H = mascara_hyperframes(entrada, saida, largura, suave, fps)
    print(f"ok (hyperframes) {n} quadros {W}x{H} -> {saida}")
    return motor


if __name__ == "__main__":
    a = sys.argv[1:]
    motor, suave, fps = None, True, None
    if "--fps" in a:
        i = a.index("--fps")
        fps = float(a[i + 1])
        del a[i:i + 2]
    if "--motor" in a:
        i = a.index("--motor")
        motor = a[i + 1]
        del a[i:i + 2]
    if "--sem-suavizar" in a:
        a.remove("--sem-suavizar")
        suave = False
    if a and a[0] == "--conferir":
        try:
            m = escolher_motor(motor)
        except SystemExit as e:
            print(e)
            sys.exit(1)
        print(m, " ".join(cmd_hyperframes() or []) if m == "hyperframes" else bin_vision())
        sys.exit(0)
    if len(a) < 2:
        print(__doc__)
        sys.exit(1)
    gerar(a[0], a[1], int(a[2]) if len(a) > 2 else 540, motor, suave, fps)
