#!/usr/bin/env python3
"""Render caption cues as transparent PNGs and emit an ffmpeg overlay filtergraph.

For ffmpeg builds without libass/freetype (no `ass`, `subtitles`, or `drawtext`
filter). Pillow draws the text; ffmpeg only composites with `overlay`.

Usage:
    render_captions.py cues.json outdir [--width 1080] [--height 1920]
                       [--font "/System/Library/Fonts/Avenir Next.ttc"]
                       [--size 86] [--margin-v 420] [--max-width-frac 0.82]

cues.json: [{"start": 0.0, "end": 0.9, "text": "Most implant"}, ...]

Writes outdir/cue_000.png ... and outdir/filtergraph.txt, and prints the
ffmpeg command to stderr for reference.
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size, index=0)
    except Exception:
        for fb in (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/HelveticaNeue.ttc",
        ):
            try:
                return ImageFont.truetype(fb, size, index=0)
            except Exception:
                continue
    raise SystemExit("no usable font found")


def wrap(draw, text, font, max_px):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_px or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cues")
    ap.add_argument("outdir")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--font", default="/System/Library/Fonts/Avenir Next.ttc")
    ap.add_argument("--size", type=int, default=86)
    ap.add_argument("--margin-v", type=int, default=420,
                    help="baseline distance from frame bottom, keeps cues clear of platform UI")
    ap.add_argument("--max-width-frac", type=float, default=0.82)
    ap.add_argument("--fill", default="#FFFFFF")
    ap.add_argument("--stroke", default="#000000")
    ap.add_argument("--stroke-w", type=int, default=8)
    a = ap.parse_args()

    cues = json.load(open(a.cues))
    os.makedirs(a.outdir, exist_ok=True)
    font = load_font(a.font, a.size)
    max_px = int(a.width * a.max_width_frac)
    line_h = int(a.size * 1.22)

    parts = []
    for i, c in enumerate(cues):
        img = Image.new("RGBA", (a.width, a.height), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        lines = wrap(d, c["text"], font, max_px)
        block_h = line_h * len(lines)
        top = a.height - a.margin_v - block_h
        for j, ln in enumerate(lines):
            w = d.textlength(ln, font=font)
            d.text(
                ((a.width - w) / 2, top + j * line_h), ln, font=font,
                fill=a.fill, stroke_width=a.stroke_w, stroke_fill=a.stroke,
            )
        png = os.path.join(a.outdir, f"cue_{i:03d}.png")
        img.save(png)
        parts.append((png, float(c["start"]), float(c["end"])))

    # one overlay per cue, gated on its time window
    chain, label = [], "0:v"
    for i, (_, s, e) in enumerate(parts):
        nxt = f"v{i}"
        chain.append(
            f"[{label}][{i+1}:v]overlay=0:0:enable='between(t,{s:.3f},{e:.3f})'[{nxt}]"
        )
        label = nxt
    graph = ";".join(chain)
    open(os.path.join(a.outdir, "filtergraph.txt"), "w").write(graph)

    # -loop 1 is REQUIRED: a single-frame PNG input is exhausted immediately and
    # the time-gated overlay then never composites. Verified 2026-08-25.
    inputs = " ".join(f'-loop 1 -i "{p}"' for p, _, _ in parts)
    print(f'ffmpeg -y -i master.mp4 {inputs} -filter_complex "{graph}" '
          f'-map "[{label}]" -map 0:a -shortest -c:v libx264 -preset slow -crf 18 '
          f'-pix_fmt yuv420p -c:a copy final.mp4', file=sys.stderr)
    print(json.dumps({"count": len(parts), "final_label": label,
                      "filtergraph": os.path.join(a.outdir, "filtergraph.txt")}))


if __name__ == "__main__":
    main()
