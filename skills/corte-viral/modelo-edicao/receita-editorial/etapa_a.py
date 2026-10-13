# Corte do bruto + tirar respiros (>0,3 s pelas palavras do Whisper) + transcrição final.
# Uso: python etapa_a.py <nome> <bruto.mov>   (os trechos do bruto ficam em segs-resolvidos.json: {"<nome>": [[ini, fim], ...]})
# Alternativa mais precisa (corte pelo SOM e corte em L): corte.py
import json, os, subprocess, sys
nome = sys.argv[1]; SRC = os.path.expanduser(sys.argv[2]); D = nome; os.makedirs(D, exist_ok=True)
segs = json.load(open("segs-resolvidos.json"))[nome]
PY = sys.executable; TR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "transcrever_v2.py")
run = lambda a: subprocess.run(a, check=True)
if not os.path.exists(f"{D}/bruto.mp4"):
    args, fc = [], []
    for k, (a, b) in enumerate(segs):
        args += ["-ss", str(a), "-to", str(b), "-i", SRC]
        fc.append(f"[{k}:v]setpts=PTS-STARTPTS,fps=30000/1001[v{k}]")
        run(["ffmpeg","-nostdin","-v","error","-y","-ss",str(a),"-to",str(b),"-i",SRC,"-map","0:a:0","-vn","-ac","2","-ar","48000","-af","afade=t=in:d=0.02,areverse,afade=t=in:d=0.03,areverse",f"{D}/a{k}.wav"])
    fc.append("".join(f"[v{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=1:a=0[v]")
    run(["ffmpeg","-nostdin","-v","error","-y",*args,"-filter_complex",";".join(fc),"-map","[v]","-c:v","libx264","-crf","16","-preset","fast","-pix_fmt","yuv420p",f"{D}/v.mp4"])
    open(f"{D}/lista.txt","w").write("".join(f"file 'a{k}.wav'\n" for k in range(len(segs))))
    run(["ffmpeg","-nostdin","-v","error","-y","-f","concat","-safe","0","-i",f"{D}/lista.txt","-c","copy",f"{D}/a.wav"])
    run(["ffmpeg","-nostdin","-v","error","-y","-i",f"{D}/v.mp4","-i",f"{D}/a.wav","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",f"{D}/bruto.mp4"])
# transcrição do bruto cortado -> respiros
os.makedirs(f"{D}/t1", exist_ok=True)
if not os.path.exists(f"{D}/t1/source.mp4"): os.link(f"{D}/bruto.mp4", f"{D}/t1/source.mp4")
if not os.path.exists(f"{D}/t1/transcript.json"): subprocess.run([PY, TR, f"{D}/t1"], capture_output=True)
ws = json.load(open(f"{D}/t1/transcript.json"))
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{D}/bruto.mp4"],capture_output=True,text=True).stdout)
corte = [max(0, ws[0]["start"] - 0.08)]; plano = []
for p, q in zip(ws, ws[1:]):
    if q["start"] - p["end"] > 0.30: plano.append([corte[0], p["end"] + 0.10]); corte = [q["start"] - 0.08]
plano.append([corte[0], min(dur, ws[-1]["end"] + 0.45)])
fr = lambda t: round(round(t * 30) / 30, 4)
plano = [[fr(a), fr(b)] for a, b in plano if b - a > 0.12]
fc = [f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={max(0,b-a-0.025):.3f}:d=0.025[a{k}]" for k, (a, b) in enumerate(plano)]
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(plano))) + f"concat=n={len(plano)}:v=1:a=1[v][a]")
open(f"{D}/fc.txt","w").write(";".join(fc)); json.dump(plano, open(f"{D}/plano-pausas.json","w"))
run(["ffmpeg","-nostdin","-v","error","-y","-i",f"{D}/bruto.mp4","-filter_complex_script",f"{D}/fc.txt","-map","[v]","-map","[a]","-c:v","libx264","-crf","16","-preset","fast","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",f"{D}/cortado.mp4"])
os.makedirs(f"{D}/t2", exist_ok=True)
if os.path.exists(f"{D}/t2/source.mp4"): os.remove(f"{D}/t2/source.mp4")
os.link(f"{D}/cortado.mp4", f"{D}/t2/source.mp4")
subprocess.run([PY, TR, f"{D}/t2"], capture_output=True)
w2 = json.load(open(f"{D}/t2/transcript.json"))
print(f"pronto {nome}: {dur:.1f}s -> {sum(b-a for a,b in plano):.1f}s")
print("  ", " ".join(x["text"] for x in w2))
