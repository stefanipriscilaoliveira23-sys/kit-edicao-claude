# Compara 2 tratamentos de S estourado (sibilância) num wav: mede a diferença agudo (4,5-16 kHz) x voz (300-3000 Hz).
# O deesser do ffmpeg NÃO resolve quando a pessoa fala colada no microfone de mão; o B foi o aprovado.
# Uso: python desser.py <voz.wav> [pasta-saida]   -> grava limpoA.wav e limpoB.wav e imprime (mediana, p95, max) em dB
import subprocess, numpy as np, wave, sys, os
from numpy.fft import rfft, rfftfreq
SRC = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(SRC))
V = {
 "A": "[0:a]acrossover=split=4500:order=8th[lo][hi];[hi]acompressor=threshold=0.015:ratio=12:attack=0.3:release=40[hic];[lo][hic]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[o]",
 "B": "[0:a]adynamicequalizer=dfrequency=7000:dqfactor=1.2:tfrequency=7000:tqfactor=1.2:threshold=0.008:ratio=12:attack=0.5:release=40:makeup=0:range=30:mode=cutbelow:tftype=bell,acrossover=split=4500:order=8th[lo][hi];[hi]acompressor=threshold=0.01:ratio=16:attack=0.2:release=40[hic];[lo][hic]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[o]",
}
def med(p):
    w=wave.open(p); sr=w.getframerate(); x=np.frombuffer(w.readframes(10**9),dtype=np.int16).astype(np.float32)/32768
    N=2048; f=rfftfreq(N,1/sr); R=[]
    for i in range(0,len(x)-N,N//2):
        S=np.abs(rfft(x[i:i+N]*np.hanning(N)))**2; R.append((10*np.log10(S[(f>4500)&(f<16000)].sum()+1e-12),10*np.log10(S[(f>300)&(f<3000)].sum()+1e-12)))
    R=np.array(R); sp=R[:,1]>np.percentile(R[:,1],40); d=R[sp,0]-R[sp,1]
    return np.median(d).round(1), np.percentile(d,95).round(1), d.max().round(1)
print("original", med(SRC))
for k, fc in V.items():
    dst = os.path.join(OUT, f"limpo{k}.wav")
    r = subprocess.run(["ffmpeg","-v","error","-y","-i",SRC,"-filter_complex",fc,"-map","[o]","-ar","48000",dst],capture_output=True,text=True)
    print(k, r.stderr[-300:] if r.returncode else med(dst))
