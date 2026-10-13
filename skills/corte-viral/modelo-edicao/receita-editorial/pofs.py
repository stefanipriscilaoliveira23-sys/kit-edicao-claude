# Conta os "pofs" de ar (grave < 160 Hz chegando perto da voz no mesmo instante) em um ou mais wav.
# Uso: python pofs.py antes.wav depois.wav ...   -> quantos pofs e os primeiros instantes (s) de cada arquivo
import numpy as np, wave, sys
from scipy.signal import butter, sosfilt
def load(p):
    w=wave.open(p); return w.getframerate(), np.frombuffer(w.readframes(10**9),dtype=np.int16).astype(np.float32)/32768
def pofs(p):
    sr,x=load(p); x=x/(np.sqrt(np.mean(x**2))+1e-9)*0.1
    lf=sosfilt(butter(4,[25,160],'bp',fs=sr,output='sos'),x); vo=sosfilt(butter(4,[300,3000],'bp',fs=sr,output='sos'),x)
    hop=int(0.01*sr); L=np.array([np.sqrt(np.mean(lf[i:i+hop]**2)) for i in range(0,len(x)-hop,hop)]); V=np.array([np.sqrt(np.mean(vo[i:i+hop]**2)) for i in range(0,len(x)-hop,hop)])
    r=20*np.log10((L+1e-6)/(V+1e-4))   # grave em relação à voz no mesmo instante
    ev=[]
    for k in np.where(r>-2)[0]:
        if not ev or k-ev[-1]>8: ev.append(k)
    return [round(k*0.01,2) for k in ev], r
for p in sys.argv[1:]:
    ev,r=pofs(p); print(f"{p}: {len(ev)} pofs | primeiros: {ev[:20]}")
