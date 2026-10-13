# -*- coding: utf-8 -*-
"""
Versão em Python do `olhar` (para Windows, Linux ou Mac Intel sem o binário).
Mede onde está o rosto e para onde ele está virado em cada quadro, com o detector YuNet (OpenCV)
que já vem na skill em models/face_detection_yunet_2023mar.onnx.

Saída CSV igual à do binário do Mac:  tempo,yaw,pitch,tem_rosto,cx,cy,larg
  yaw/pitch em graus (estimados pelos pontos do rosto; pitch SOBE quando a pessoa olha pra baixo)
  cx/cy = centro do rosto em fração do quadro (y a partir do topo); larg = largura do rosto em fração

Uso: python olhar.py <video> <saida.csv> [pular=2]   (analisa 1 a cada N quadros)
É menos preciso que o Vision do Mac no yaw/pitch, mas serve pra achar rosto, enquadrar e marcar desvio grande.
"""
import math
import os
import sys

import cv2

if len(sys.argv) < 3:
    print("uso: olhar.py video saida.csv [pular]")
    sys.exit(1)
video, saida = sys.argv[1], sys.argv[2]
pular = int(sys.argv[3]) if len(sys.argv) > 3 else 2
_cands = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "models", "face_detection_yunet_2023mar.onnx"),
          os.path.expanduser("~/.claude/skills/corte-viral/models/face_detection_yunet_2023mar.onnx")]
MODELO = next((c for c in _cands if os.path.exists(c)), _cands[-1])

cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
det = None
linhas = ["tempo,yaw,pitch,tem_rosto,cx,cy,larg"]
i = 0
while True:
    ok, quadro = cap.read()
    if not ok:
        break
    i += 1
    if i % pular:
        continue
    t = (i - 1) / fps
    h, w = quadro.shape[:2]
    escala = 640 / max(w, h)
    peq = cv2.resize(quadro, (int(w * escala), int(h * escala)))
    if det is None:
        det = cv2.FaceDetectorYN.create(MODELO, "", (peq.shape[1], peq.shape[0]), 0.7, 0.3, 5000)
    _, rostos = det.detect(peq)
    if rostos is None or len(rostos) == 0:
        linhas.append(f"{t:.3f},0,0,0,0,0,0")
        continue
    f = max(rostos, key=lambda r: r[2])          # maior rosto do quadro
    x, y, bw, bh = f[:4]
    olho_d, olho_e, nariz, boca_d, boca_e = [(f[4 + 2 * k], f[5 + 2 * k]) for k in range(5)]
    dist_olhos = max(1e-3, math.hypot(olho_e[0] - olho_d[0], olho_e[1] - olho_d[1]))
    meio_x = (olho_d[0] + olho_e[0]) / 2
    yaw = math.degrees(math.atan((nariz[0] - meio_x) / (0.55 * dist_olhos)))
    olho_y = (olho_d[1] + olho_e[1]) / 2
    boca_y = (boca_d[1] + boca_e[1]) / 2
    r = (nariz[1] - olho_y) / max(1e-3, boca_y - olho_y)
    pitch = (r - 0.52) * 150
    ph, pw = peq.shape[:2]
    linhas.append(f"{t:.3f},{yaw:.1f},{pitch:.1f},1,{(x + bw / 2) / pw:.3f},{(y + bh / 2) / ph:.3f},{bw / pw:.3f}")
open(saida, "w").write("\n".join(linhas))
print(f"ok {len(linhas) - 1} quadros analisados")
