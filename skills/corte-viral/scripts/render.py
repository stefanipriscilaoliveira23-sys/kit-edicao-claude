from __future__ import annotations

import json
import math
import os
import shutil
from pathlib import Path
from typing import Any

from scripts.media_probe import probe_media
from scripts.utils import HarnessError, load_json, run_command, sha256_file, slugify, which, write_json


def _filter_path(path: Path) -> str:
    value = str(path.resolve()).replace("\\", "/")
    value = value.replace(":", r"\:").replace("'", r"\'")
    return value


def _video_filter(
    width: int, height: int, anchor_x: float, zoom: float, fps: Any = "source", anchor_y: float = 0.5
) -> str:
    zoom = max(1.0, min(2.0, float(zoom)))
    target_w = int(math.ceil(width * zoom / 2) * 2)
    target_h = int(math.ceil(height * zoom / 2) * 2)
    anchor_x = max(0.0, min(1.0, float(anchor_x)))
    anchor_y = max(0.0, min(1.0, float(anchor_y)))
    filters = [
        f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase",
        f"crop={width}:{height}:x='max(0,min(iw-ow,(iw-ow)*{anchor_x:.6f}))':y='max(0,min(ih-oh,(ih-oh)*{anchor_y:.6f}))'",
        "setsar=1",
    ]
    if fps not in {None, "source", "inherit"}:
        filters.append(f"fps={float(fps):g}")
    return ",".join(filters)


def _even(value: float) -> int:
    """FFmpeg/yuv420p exige dimensoes pares."""
    return max(2, int(round(value / 2)) * 2)


def split_geometry(width: int, height: int, src_w: int, src_h: int, zoom: float = 1.0) -> dict[str, int]:
    """
    Layout 'split' (vertical-reframe): metade de cima = quadro inteiro sem crop
    (contexto: todo mundo na mesa), metade de baixo = crop fechado no locutor.

    A altura do topo e a natural do aspecto da fonte, nunca um valor arbitrario:
    e o que garante que a metade de cima nao distorce nem fica com faixa preta.
    Para 1920x1080 -> 1080x1920 isso da 608 em cima e 1312 embaixo.
    """
    if not src_w or not src_h:
        raise HarnessError("Layout split exige largura/altura da fonte")
    top_h = _even(width * src_h / src_w)
    bottom_h = height - top_h
    if top_h <= 0 or bottom_h < height * 0.35:
        # Fonte alta demais (ja quase vertical): o split nao sobra leitura embaixo.
        raise HarnessError(
            f"Layout split invalido para fonte {src_w}x{src_h}: topo {top_h}px deixaria "
            f"apenas {bottom_h}px de leitura. Use layout 'cover'."
        )
    crop_w = _even(src_h * width / bottom_h / max(1.0, float(zoom)))
    crop_w = min(crop_w, _even(src_w))
    return {"top_h": top_h, "bottom_h": bottom_h, "crop_w": crop_w, "crop_h": _even(src_h)}


def _split_filter(
    width: int, height: int, src_w: int, src_h: int, anchor_x: float, zoom: float, fps: Any = "source",
    in_label: str = "0:v", out_label: str = "vout", tag: str = "sp",
) -> str:
    geo = split_geometry(width, height, src_w, src_h, zoom)
    anchor_x = max(0.0, min(1.0, float(anchor_x)))
    crop_x = int(round((src_w - geo["crop_w"]) * anchor_x))
    crop_x = max(0, min(src_w - geo["crop_w"], crop_x))
    tail = f",fps={float(fps):g}" if fps not in {None, "source", "inherit"} else ""
    t = tag
    return (
        f"[{in_label}]split=2[{t}top][{t}bot];"
        f"[{t}top]scale={width}:{geo['top_h']},setsar=1[{t}topv];"
        f"[{t}bot]crop={geo['crop_w']}:{geo['crop_h']}:{crop_x}:0,"
        f"scale={width}:{geo['bottom_h']},setsar=1[{t}botv];"
        f"[{t}topv][{t}botv]vstack=inputs=2,setsar=1{tail}[{out_label}]"
    )


def _output_fps(src_fps: float | None) -> float:
    """
    FPS de saida quando o config pede "source". Bruto de celular e VFR e a media
    sai quebrada (iPhone: 29,885): taxa NTSC exata e mantida, o resto encosta no
    inteiro mais proximo se estiver a ate 2% dele (29,885 -> 30).
    """
    if not src_fps or src_fps <= 0:
        return 30.0
    for ntsc in (24000 / 1001, 30000 / 1001, 60000 / 1001):
        if abs(src_fps - ntsc) / ntsc < 0.001:
            return ntsc
    nearest = round(src_fps)
    if nearest > 0 and abs(src_fps - nearest) / nearest <= 0.02:
        return float(nearest)
    return float(src_fps)


def _timeline_graph(
    timeline: list[dict[str, Any]],
    render_cfg: dict[str, Any],
    has_audio: bool,
    src_w: int | None,
    src_h: int | None,
    fade_before: list[bool],
    fade_after: list[bool],
    src_fps: float | None = None,
) -> tuple[list[str], str]:
    """
    Monta entradas + filter_complex que renderizam a timeline inteira numa
    passada: cada segmento e uma entrada com -ss/-t (seek na entrada), recebe
    crop/zoom/escala e o micro-fade, e o filtro concat costura video e audio
    juntos. Antes cada segmento virava um MP4 proprio e o concat demuxer (-c copy)
    somava o priming/padding do AAC de cada um e o arredondamento de frame de cada
    video: com 14 segmentos o audio ficava ~0,2s mais longo que o video e a boca
    descolava da voz no fim. Aqui existe um encode so, entao nao ha o que somar.

    Alem disso cada segmento e travado num numero inteiro de frames: o video sai
    em CFR com exatamente N frames (clonando o ultimo se o seek entregou um a
    menos) e o audio e completado/cortado para exatamente N/fps. Sem isso o
    concat alinha o inicio de cada segmento mas o video de cada um arredonda
    para frame inteiro e o audio nao, e o fim do clipe ainda descola 1-2 frames.
    """
    click_fade = 0.025
    width = int(render_cfg.get("width", 1080))
    height = int(render_cfg.get("height", 1920))
    fps = render_cfg.get("fps", "source")
    rate = int(render_cfg.get("audio_sample_rate", 48000))
    fps = _output_fps(src_fps) if fps in {None, "source", "inherit"} else float(fps)
    inputs: list[str] = []
    chains: list[str] = []
    pads = ""
    elapsed = 0.0
    for i, segment in enumerate(timeline):
        start = float(segment["source_start"])
        end = float(segment["source_end"])
        duration = end - start
        if duration <= 0:
            raise HarnessError(f"Segmento inválido: {start}–{end}")
        # Arredondamento acumulado: o total nunca se afasta mais de meio frame da
        # soma do plano (arredondar segmento a segmento perderia ate N/2 frames).
        frames = max(1, int(round((elapsed + duration) * fps)) - int(round(elapsed * fps)))
        elapsed += duration
        seg_dur = frames / fps
        video_lock = (
            f"fps={fps:.6f},tpad=stop_mode=clone:stop_duration={2 / fps:.6f},"
            f"trim=end_frame={frames},setpts=PTS-STARTPTS"
        )
        # Input seeking evita decodificar o bruto inteiro antes de cada segmento
        # distante; o seek preciso padrao do FFmpeg ainda decodifica a partir do
        # keyframe anterior e descarta ate o timestamp pedido.
        # Le um frame a mais que o necessario: trim/atrim cortam no ponto exato
        # e o padding (clone/silencio) so entra se o bruto acabar antes.
        inputs += ["-ss", f"{start:.6f}", "-t", f"{seg_dur + 1 / fps:.6f}", "-i", "{source}"]
        anchor = float(segment.get("crop_anchor_x", render_cfg.get("crop_anchor_x", 0.5)))
        anchor_y = float(segment.get("crop_anchor_y", render_cfg.get("crop_anchor_y", 0.5)))
        zoom = float(segment.get("zoom", 1.0))
        layout = str(segment.get("layout") or render_cfg.get("layout") or "cover").lower()
        if layout == "split":
            chains.append(_split_filter(
                width, height, int(src_w or 0), int(src_h or 0), anchor, zoom, fps,
                in_label=f"{i}:v:0", out_label=f"vs{i}", tag=f"sp{i}",
            ))
            chains.append(f"[vs{i}]setpts=PTS-STARTPTS,{video_lock}[v{i}]")
        else:
            vf = _video_filter(width, height, anchor, zoom, fps, anchor_y)
            chains.append(f"[{i}:v:0]setpts=PTS-STARTPTS,{vf},{video_lock}[v{i}]")
        pads += f"[v{i}]"
        if has_audio:
            # Micro-fade (25ms) so nas bordas de corte real -- mata o clique de
            # descontinuidade de onda na emenda sem soar como transicao. Nunca na
            # abertura/fechamento do proprio clipe (ver render_clip).
            afilters = [
                f"aresample={rate}", "asetpts=PTS-STARTPTS",
                f"apad=whole_len={int(round(seg_dur * rate))}",
                f"atrim=end_sample={int(round(seg_dur * rate))}", "asetpts=PTS-STARTPTS",
            ]
            if fade_before[i]:
                afilters.append(f"afade=t=in:st=0:d={click_fade}")
            if fade_after[i]:
                afilters.append(f"afade=t=out:st={max(seg_dur - click_fade, 0):.6f}:d={click_fade}")
            chains.append(f"[{i}:a:0]{','.join(afilters)}[a{i}]")
            pads += f"[a{i}]"
    n = len(timeline)
    pixel = str(render_cfg.get("pixel_format", "yuv420p"))
    # iPhone grava yuvj420p (faixa cheia). Converter explicitamente para faixa TV
    # garante que o arquivo sai yuv420p de verdade (verify-output confere).
    video_tail = f"scale=out_range=tv,format={pixel}[v]"
    if has_audio:
        target = float(render_cfg.get("loudness_lufs", -14))
        peak = float(render_cfg.get("true_peak_db", -1.0))
        lra = float(render_cfg.get("loudness_range", 11))
        chains.append(f"{pads}concat=n={n}:v=1:a=1[vc][ac]")
        chains.append(f"[vc]{video_tail}")
        chains.append(f"[ac]loudnorm=I={target}:TP={peak}:LRA={lra},aresample={rate}[a]")
    else:
        chains.append(f"{pads}concat=n={n}:v=1:a=0[vc]")
        chains.append(f"[vc]{video_tail}")
    return inputs, ";".join(chains)


def _render_timeline(
    ffmpeg: str,
    source: Path,
    output: Path,
    timeline: list[dict[str, Any]],
    render_cfg: dict[str, Any],
    has_audio: bool,
    src_w: int | None,
    src_h: int | None,
    fade_before: list[bool],
    fade_after: list[bool],
    src_fps: float | None = None,
) -> None:
    if not timeline:
        raise HarnessError("Nenhum segmento para renderizar")
    inputs, graph = _timeline_graph(
        timeline, render_cfg, has_audio, src_w, src_h, fade_before, fade_after, src_fps,
    )
    inputs = [str(source) if item == "{source}" else item for item in inputs]
    command = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *inputs,
        "-filter_complex", graph, "-map", "[v]",
        "-c:v", str(render_cfg.get("video_codec", "libx264")),
        "-preset", str(render_cfg.get("preset", "medium")),
        "-crf", str(render_cfg.get("crf", 18)),
        "-pix_fmt", str(render_cfg.get("pixel_format", "yuv420p")),
        "-color_range", "tv",
    ]
    if has_audio:
        command += [
            "-map", "[a]",
            "-c:a", str(render_cfg.get("audio_codec", "aac")), "-b:a", "192k",
            "-ar", str(render_cfg.get("audio_sample_rate", 48000)),
        ]
    else:
        command += ["-an"]
    command += ["-movflags", "+faststart", str(output)]
    run_command(command)


def _tem_filtro_ass(ffmpeg: str) -> bool:
    import re as _re
    resultado = run_command([ffmpeg, "-hide_banner", "-filters"], check=False)
    saida = (resultado.stdout or "") + (resultado.stderr or "")
    # Palavra inteira: "ass" como substring casa com lowpass/highpass/bass/allpass.
    return bool(_re.search(r"^\s*\S*\s+(subtitles|ass)\s", saida, _re.MULTILINE))


def _burn_subtitles(ffmpeg: str, clean: Path, ass: Path, output: Path, render_cfg: dict[str, Any]) -> None:
    if not ass.exists():
        raise HarnessError(f"Legenda ASS não encontrada: {ass}")
    if not _tem_filtro_ass(ffmpeg):
        # Sem esta checagem o ffmpeg morre com "No option name near ..." — erro
        # que não diz o problema real. Nesta skill a queima é opcional: o padrão
        # entrega o vertical limpo e a motion-vox queima por outro caminho.
        raise HarnessError(
            "Este ffmpeg não tem o filtro `ass` (compilado sem libass), então não "
            "há como queimar legenda por aqui. Desligue `render.make_captioned_version` "
            "no config — o vertical limpo é o entregável desta skill — ou instale um "
            "ffmpeg com libass. Ver INSTALAR.md."
        )
    run_command([
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(clean),
        "-vf", f"ass='{_filter_path(ass)}'",
        "-c:v", str(render_cfg.get("video_codec", "libx264")),
        "-preset", str(render_cfg.get("preset", "medium")),
        "-crf", str(render_cfg.get("crf", 18)),
        "-pix_fmt", str(render_cfg.get("pixel_format", "yuv420p")),
        "-c:a", "copy", "-movflags", "+faststart", str(output)
    ])


def _preview(ffmpeg: str, video: Path, output: Path) -> None:
    run_command([
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-ss", "0.2", "-i", str(video),
        "-frames:v", "1", "-q:v", "2", str(output)
    ])


def render_clip(
    source_video: str | Path,
    clip: dict[str, Any],
    plan: dict[str, Any],
    output_dir: str | Path,
    render_cfg: dict[str, Any],
) -> dict[str, Any]:
    ffmpeg = which("ffmpeg")
    if not ffmpeg:
        raise HarnessError("FFmpeg não encontrado")
    source = Path(source_video).expanduser().resolve()
    if not source.exists():
        raise HarnessError(f"Vídeo fonte não encontrado: {source}")
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    media = probe_media(source)
    has_audio = bool(media.get("audio"))
    src_video = media.get("video") or {}
    src_w, src_h = int(src_video.get("width") or 0), int(src_video.get("height") or 0)
    timeline = plan.get("timeline") or clip.get("segments") or []
    if not timeline:
        raise HarnessError(f"Clip {clip.get('id')} sem timeline")
    timeline = sorted(timeline, key=lambda item: item.get("order", 0))

    # Um corte real e uma descontinuidade de tempo-fonte entre segmentos vizinhos
    # (gap ou overlap); segmentos que so seguem um ao outro no bruto (fronteira de
    # decupagem interna, sem pular nada) nao levam fade -- teriam fade dos dois
    # lados e soariam como um mergulho de volume no meio de fala continua.
    gap_eps = 0.05
    n = len(timeline)
    fade_before = [False] * n
    fade_after = [False] * n
    for i in range(n - 1):
        gap = abs(float(timeline[i + 1].get("source_start", 0)) - float(timeline[i].get("source_end", 0)))
        if gap > gap_eps:
            fade_after[i] = True
            fade_before[i + 1] = True

    clean = output / "clip-clean.mp4"
    _render_timeline(
        ffmpeg, source, clean, timeline, render_cfg, has_audio, src_w, src_h, fade_before, fade_after,
        src_video.get("fps"),
    )

    captioned = output / "clip-vertical.mp4"
    ass = output / "captions.ass"
    if render_cfg.get("make_captioned_version", True):
        _burn_subtitles(ffmpeg, clean, ass, captioned, render_cfg)
    else:
        shutil.copy2(clean, captioned)

    preview = output / "preview.jpg"
    if render_cfg.get("make_preview_image", True):
        _preview(ffmpeg, captioned, preview)

    write_json(output / "edit-plan.json", plan)
    transcript_text = clip.get("reconstructed_transcript", "")
    (output / "transcript.txt").write_text(transcript_text + ("\n" if transcript_text else ""), encoding="utf-8")
    (output / "editor-notes.md").write_text(
        f"# {clip.get('title', clip.get('id', 'Clip'))}\n\n{plan.get('editor_notes') or clip.get('editor_notes', '')}\n",
        encoding="utf-8",
    )
    final_probe = probe_media(captioned)
    metadata = {
        "schema_version": "1.0",
        "clip_id": clip.get("id"),
        "title": clip.get("title"),
        "primary_context": clip.get("primary_context"),
        "profile": clip.get("profile"),
        "tags": clip.get("tags", []),
        "status": clip.get("status"),
        "scores": clip.get("scores", {}),
        "events": clip.get("events", {}),
        "segments": clip.get("segments", []),
        "output": {
            "clip_vertical": str(captioned),
            "clip_clean": str(clean),
            "captions_srt": str(output / "captions.srt"),
            "captions_ass": str(ass),
            "preview": str(preview) if preview.exists() else None,
        },
        "rendered_media": final_probe,
        "sha256": sha256_file(captioned),
    }
    write_json(output / "metadata.json", metadata)
    return metadata


def render_all(
    run_dir: str | Path,
    source_video: str | Path,
    final_clips: dict[str, Any],
    edit_plans: dict[str, Any],
    render_cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    run = Path(run_dir)
    plans = {str(plan["clip_id"]): plan for plan in edit_plans.get("plans", [])}
    rendered = []
    for clip in final_clips.get("clips", []):
        if clip.get("status") not in {"APPROVED", "LONG_CLIP"}:
            continue
        clip_id = str(clip.get("id"))
        plan = plans.get(clip_id)
        if not plan:
            raise HarnessError(f"Edit plan ausente para {clip_id}")
        context = slugify(plan.get("primary_context") or clip.get("primary_context") or "outro")
        slug = slugify(plan.get("output_slug") or f"{clip_id}-{clip.get('title', '')}")
        output = run / "output" / "final-clips" / context / slug
        rendered.append(render_clip(source_video, clip, plan, output, render_cfg))
    return rendered
