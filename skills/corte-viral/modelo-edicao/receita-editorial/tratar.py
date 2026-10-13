# Tratamento final da voz (depois do DeepFilterNet + depof): estalos (adeclick), S estourado (adynamicequalizer 7 kHz
# + compressor forte só no agudo acima de 4,5 kHz), compressor leve e loudnorm -14. Mede antes/depois os estouros.
# Uso: python tratar.py <pasta-ruido> [ini-fim,ini-fim,...]
#   <pasta-ruido>/df-depof.wav -> <pasta-ruido>/voz-final.wav ; os trechos opcionais (em segundos) são onde medir os estouros
import subprocess, numpy as np, wave, sys, os
from numpy.fft import rfft, rfftfreq
R = sys.argv[1] if len(sys.argv) > 1 else "ruido"
FC = ("[0:a]adeclick=w=20:o=50:a=2:t=2:b=2,"
      "adynamicequalizer=dfrequency=7000:dqfactor=1.2:tfrequency=7000:tqfactor=1.2:threshold=0.008:ratio=12:attack=0.5:release=40:makeup=0:range=30:mode=cutbelow:tftype=bell,"
      "acrossover=split=4500:order=8th[lo][hi];[hi]acompressor=threshold=0.01:ratio=16:attack=0.2:release=40[hic];"
      "[lo][hic]amix=inputs=2:normalize=0,acompressor=threshold=0.1:ratio=2.5:attack=5:release=80:makeup=1.5,loudnorm=I=-14:TP=-1.5:LRA=9[o]")
subprocess.run(["ffmpeg","-v","error","-y","-i",f"{R}/df-depof.wav","-filter_complex",FC,"-map","[o]","-ar","48000",f"{R}/voz-final.wav"],check=True)
def load(p):
    w=wave.open(p); return w.getframerate(), np.frombuffer(w.readframes(10**9),dtype=np.int16).astype(np.float32)/32768
def estouros(p, trechos):
    sr,x=load(p); N=1024; f=rfftfreq(N,1/sr); out=[]
    for t0,t1 in trechos:
        lf=[];hf=[];mid=[]
        for t in np.arange(t0,t1,0.02):
            i=int(t*sr); S=np.abs(rfft(x[i:i+N]*np.hanning(N)))**2
            lf.append(10*np.log10(S[(f>20)&(f<100)].sum()+1e-12)); hf.append(10*np.log10(S[(f>12000)].sum()+1e-12)); mid.append(10*np.log10(S[(f>300)&(f<2500)].sum()+1e-12))
        m=max(mid); out.append(f"grave {max(lf)-m:+.0f} / agudo {max(hf)-m:+.0f} dB vs voz")
    return out
T = [tuple(float(v) for v in x.split("-")) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else []
if T:
    for p in [f"{R}/voz.wav", f"{R}/df/voz.wav", f"{R}/voz-final.wav"]:
        if os.path.exists(p): print(p, estouros(p, T))
