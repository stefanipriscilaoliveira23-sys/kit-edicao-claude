# corta do final.mp4 os silêncios > 0,5 s da voz (medidos no source.mp4), deixando 0,08 s de cada lado
import re, subprocess, sys, json
D = sys.argv[1]
out = subprocess.run(["ffmpeg","-i",f"{D}/source.mp4","-af","silencedetect=noise=-35dB:d=0.45","-f","null","-"],capture_output=True,text=True).stderr
ss = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]; ee = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
sil = [[a, b] for a, b in zip(ss, ee)]
# junta silêncios separados por respiro curto (< 0,08 s)
j = []
for a, b in sil:
    if j and a - j[-1][1] < 0.08: j[-1][1] = b
    else: j.append([a, b])
DUR = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{D}/final.mp4"],capture_output=True,text=True).stdout)
cortes = [[a + 0.08, b - 0.08] for a, b in j if b - a > 0.5 and a > 0.5 and b < DUR - 0.5]
print("cortando", [[round(a,2), round(b,2)] for a, b in cortes])
keep = []; t = 0.0
for a, b in cortes: keep.append([t, a]); t = b
keep.append([t, DUR])
fr = lambda x: round(round(x * 30000 / 1001) * 1001 / 30000, 4)
fc = [f"[0:v]trim={fr(a)}:{fr(b)},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={fr(a)}:{fr(b)},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(0, fr(b)-fr(a)-0.03):.3f}:d=0.03[a{k}]" for k, (a, b) in enumerate(keep)]
fc.append("".join(f"[v{k}][a{k}]" for k in range(len(keep))) + f"concat=n={len(keep)}:v=1:a=1[v][a]")
subprocess.run(["ffmpeg","-nostdin","-v","error","-y","-i",f"{D}/final.mp4","-filter_complex",";".join(fc),"-map","[v]","-map","[a]","-c:v","libx264","-crf","17","-preset","medium","-pix_fmt","yuv420p","-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{D}/final-limpo.mp4"], check=True)
print("ok", round(DUR - sum(b - a for a, b in cortes), 2), "s")
