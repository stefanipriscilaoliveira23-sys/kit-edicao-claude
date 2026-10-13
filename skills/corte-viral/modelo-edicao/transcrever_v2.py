# Transcreve <pasta>/source.mp4 com tempo por palavra (Whisper local large-v3-turbo) -> <pasta>/transcript.json
# Uso: python transcrever_v2.py <pasta> [<pasta> ...]
# As grafias certas e o vocabulario vem do Manual da Marca (marca.json):
#   "transcricao": {"vocabulario": "frase com o seu nome, a sua marca e os termos que voce fala",
#                   "trocas": {"palavra que o Whisper erra (minuscula, sem pontuacao)": "Grafia Certa"}}
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import marca
from faster_whisper import WhisperModel
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
TROCA = {k.lower(): v for k, v in marca.trocas().items()}
VOCAB = marca.vocabulario() or None
for n in sys.argv[1:]:
    segs, _ = m.transcribe(f"{n}/source.mp4", language="pt", word_timestamps=True, beam_size=5, initial_prompt=VOCAB)
    ws = []
    for s in segs:
        for x in s.words:
            t = x.word.strip(); base = re.sub(r"[^\wÀ-ÿ]", "", t).lower()
            if TROCA.get(base): t = re.sub(r"[\wÀ-ÿ]+", TROCA[base], t, count=1)
            ws.append({"text": t, "start": round(x.start, 3), "end": round(x.end, 3)})
    json.dump(ws, open(f"{n}/transcript.json", "w"), ensure_ascii=False, indent=1)
    print("##", n, " ".join(w["text"] for w in ws), flush=True)
