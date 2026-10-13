#!/usr/bin/env python3
"""
Mede, quadro a quadro, o zoom (escala), o giro (graus) e o deslocamento de um video
(serve pra estudar uma referencia nova antes de mudar os valores do zoom_transicao.py).

  python3 -I movimento.py referencia.mp4 > movimento-por-quadro.tsv

Colunas: tempo, escala entre um quadro e o seguinte (1.02 = +2% de zoom), giro, dx, dy,
pontos em comum, diferenca media, nitidez e brilho. Precisa de numpy e opencv.
"""
import cv2, numpy as np, sys, math
cap=cv2.VideoCapture(sys.argv[1]); fps=cap.get(cv2.CAP_PROP_FPS)
orb=cv2.ORB_create(1500); bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True)
prev=None; i=0; out=[]
while True:
    ok,f=cap.read()
    if not ok: break
    g=cv2.cvtColor(cv2.resize(f,(360,640)),cv2.COLOR_BGR2GRAY)
    sharp=cv2.Laplacian(g,cv2.CV_64F).var(); bright=g.mean()
    s=r=dx=dy=float('nan'); inl=0; diff=0
    if prev is not None:
        diff=np.abs(g.astype(int)-prev.astype(int)).mean()
        k1,d1=orb.detectAndCompute(prev,None); k2,d2=orb.detectAndCompute(g,None)
        if d1 is not None and d2 is not None and len(k1)>10 and len(k2)>10:
            m=bf.match(d1,d2)
            if len(m)>12:
                p1=np.float32([k1[x.queryIdx].pt for x in m]); p2=np.float32([k2[x.trainIdx].pt for x in m])
                M,mask=cv2.estimateAffinePartial2D(p1,p2,ransacReprojThreshold=3)
                if M is not None:
                    inl=int(mask.sum()); s=math.hypot(M[0,0],M[1,0]); r=math.degrees(math.atan2(M[1,0],M[0,0])); dx,dy=M[0,2],M[1,2]
    out.append((i/fps,s,r,dx,dy,inl,diff,sharp,bright)); prev=g; i+=1
print("t\tescala\tgiro\tdx\tdy\tinl\tdif\tnitidez\tbrilho")
for o in out: print("%.3f\t%.4f\t%.2f\t%.1f\t%.1f\t%d\t%.1f\t%.0f\t%.0f"%o)
