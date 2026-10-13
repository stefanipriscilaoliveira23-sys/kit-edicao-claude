# -*- coding: utf-8 -*-
"""Render de timeline com muitos segmentos: audio e video tem que terminar juntos."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.output_qc import expected_clip_duration
from scripts.render import render_clip
from scripts.utils import which

FPS = 30


def _stream_durations(path: Path) -> dict[str, float]:
    """
    Duracoes decodificadas (amostras de audio / frames de video). A "duration"
    do ffprobe no audio inclui priming + padding do ultimo frame AAC (ate ~43ms,
    fixo, nao cresce com o numero de segmentos) e nao mede sincronia.
    """
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    video = next(s for s in json.loads(out)["streams"] if s["codec_type"] == "video")
    frames = subprocess.run(
        ["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    pcm = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0", "-ac", "1", "-ar", "48000", "-f", "s16le", "-"],
        check=True, capture_output=True,
    ).stdout
    num, den = video["avg_frame_rate"].split("/")
    return {
        "video": int(frames) * int(den) / int(num),
        "audio": len(pcm) / 2 / 48000,
        "pix_fmt": video.get("pix_fmt"),
        "color_range": video.get("color_range"),
    }


@unittest.skipUnless(which("ffmpeg") and which("ffprobe"), "precisa de ffmpeg/ffprobe")
class TestRenderSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="vch-sync-")
        cls.source = Path(cls.tmp.name) / "source.mov"
        # yuvj420p/faixa cheia imita o bruto do iPhone.
        subprocess.run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "lavfi", "-i", f"testsrc2=size=640x360:rate={FPS}",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
            "-t", "20", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30",
            "-pix_fmt", "yuvj420p", "-color_range", "pc",
            "-c:a", "aac", "-ar", "48000", "-shortest", str(cls.source),
        ], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_audio_e_video_com_diferenca_menor_que_um_frame(self):
        # 14 segmentos curtos com respiros removidos entre eles (duracoes que nao
        # caem em frame inteiro), zoom/anchor variando e um trecho em split.
        timeline, t = [], 0.37
        for i in range(14):
            dur = 0.9 + (i % 5) * 0.137
            seg = {
                "order": i, "source_start": round(t, 3), "source_end": round(t + dur, 3),
                "crop_anchor_x": (i % 3) / 2, "zoom": 1.0 + (i % 4) * 0.15,
            }
            if i == 6:
                seg["layout"] = "split"
            timeline.append(seg)
            t += dur + 0.21
        plan = {"clip_id": "c1", "timeline": timeline}
        render_cfg = {
            "width": 360, "height": 640, "preset": "ultrafast", "crf": 30,
            "pixel_format": "yuv420p", "audio_sample_rate": 48000,
            "make_captioned_version": False, "make_preview_image": False,
        }
        out = Path(self.tmp.name) / "out"
        render_clip(self.source, {"id": "c1"}, plan, out, render_cfg)

        info = _stream_durations(out / "clip-clean.mp4")
        self.assertLess(abs(info["audio"] - info["video"]), 1.0 / FPS, info)
        self.assertAlmostEqual(info["video"], expected_clip_duration(plan), delta=1.5 / FPS)
        self.assertEqual(info["pix_fmt"], "yuv420p")
        # x264 so grava a flag de faixa quando ha outras tags de cor (o bruto do
        # iPhone tem; o testsrc nao) -- sem flag = faixa TV. So nao pode ser pc.
        self.assertIn(info["color_range"], {"tv", None})


class TestExpectedDuration(unittest.TestCase):
    def test_usa_soma_da_timeline_e_nao_o_candidato(self):
        plan = {"timeline": [
            {"source_start": 10.0, "source_end": 30.0},
            {"source_start": 32.5, "source_end": 62.37},
        ]}
        self.assertAlmostEqual(expected_clip_duration(plan, 56.87), 49.87, places=6)

    def test_sem_timeline_cai_no_fallback(self):
        self.assertEqual(expected_clip_duration({}, 56.87), 56.87)
        self.assertEqual(expected_clip_duration(None, 0), 0.0)


if __name__ == "__main__":
    unittest.main()
