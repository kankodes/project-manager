#!/usr/bin/env python3
"""Builds the site's photographs and hero videos from Garnet's own event media.

Run from the repo root:  python3 tools/media.py  [--only name,name]
Then rebuild the pages:  python3 tools/build.py

Sources are read from the local media drive (SRC) and never modified. Every
output is re-encoded from decoded pixels, so no EXIF/GPS/camera metadata
survives. Writes:
  assets/img/<name>-<w>.avif / .webp   one pair per width in WIDTHS
  assets/img/<page>-hero-1920.webp    poster for the 16:9 hero video
  assets/img/<page>-hero-sm.webp      portrait poster for phones
  assets/videos/<page>-hero.mp4       1920x1080 H.264, muted, for >= 900px
  assets/videos/<page>-hero-sm.mp4    720x1280 portrait crop for phones
  assets/videos/<clip>.mp4            in-page clips (pre-wedding), 1280x720
  assets/img/og-image.jpg             1200x630 social card (photo + logo)
  tools/media.json                    sizes read by build.py

Needs: Pillow, ffmpeg, cwebp, avifenc.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parent.parent
SRC = Path("/Volumes/Kanhiya/Garnet")
IMG = ROOT / "assets/img"
VID = ROOT / "assets/videos"
WIDTHS = [640, 1080, 1600]  # capped at the master crop's own width
# Full-bleed slots (wide home tiles, the enquiry banner) also get a 2400w file for
# large retina screens; nothing else renders wider than ~800 CSS px.
FULL_BLEED = {"wedding-stage", "palace-stage", "led-stage"}

NS = "nikhil soni event"
BR = "BRNADING WORKS"
RV = "RAJ VILLAS EVENT"

# name: (source, crop aspect or None, focus x, focus y)
#   source is a path under SRC, or ("frame", video path, seconds) for a still
#   pulled from 4K/1080p footage. Crops to the largest box of that aspect
#   centred on the focus point; reel frames are cropped to clear on-screen text.
PHOTOS = {
    "wedding-stage": (f"{NS}/FullSizeRender.jpeg", None, .5, .5),
    "wedding-stage-tall": (f"{NS}/FullSizeRender (2).jpeg", "4:5", .5, .55),
    "peacock-entry": (f"{NS}/IMG_6072.jpeg", "4:5", .5, .5),
    "krishna-leela": (f"{NS}/IMG_6079.jpeg", "4:5", .5, .45),
    "stage-haze": (("frame", f"{NS}/IMG_6030.MOV", 80), None, .5, .5),
    "led-stage": (("frame", "New/VID_20231127_201022.mp4", 35), None, .5, .5),
    "palace-stage": (("frame", "reels/VID_20251125_215713787.mp4", 70), None, .5, .5),
    "brand-gate": (f"{BR}/WhatsApp Image 2024-08-31 at 7.41.38 PM (3).jpeg", None, .5, .5),
    "vip-bar": (f"{BR}/WhatsApp Image 2024-08-31 at 7.41.39 PM.jpeg", None, .5, .5),
    "box-office": (f"{BR}/WhatsApp Image 2024-08-31 at 7.41.37 PM (2).jpeg", None, .5, .5),
    "blue-florals": (("frame", "New/VID_20231230_211059.mp4", 12.8), "4:5", .5, .45),
    # top of the frame only: the twins' names are spelled out in lights lower down
    "birthday-florals": (("frame", "Garnet /Garnet 2026 Reels/IMG_7853.MP4", 19.3), "4:5", .5, 0),
    # 3:2 from the top drops the phone's date stamp
    "poolside-haldi": ("Ev/IMG-20250523-WA0026.jpg", "3:2", .5, 0),
    "haldi-canopy": ("Ev/IMG-20250523-WA0030.jpg", "3:2", .5, 0),
    "tile-backdrop": ("Ev/IMG-20250523-WA0027.jpg", "4:5", .5, .5),
}
# Not used: reels cut by outside creators (Stories of Shaadi, BTS Wedding Reels,
# Blink - incl. the Rajasthan villa event), photographer-watermarked sets
# (Wedding Swag by Rohit Thakur) and Vedas n Mantras branded decor films/photos.
# They need the owner's permission before they go on the site.

# page: (video, cut, focus x for the portrait phone crop)
#   cut is a start second (an 8 s clip from there) or a list of (start, seconds[, slow])
#   segments joined in order; slow > 1 stretches a segment into slow motion.
#   Contact has no hero video.
HEROES = {
    # three entries from the Mariam & Aftab teaser: sangeet, reception stage, nikah
    "home": ("Garnet /Mariam Teaser Photalk.mp4", [(10.75, 1.25, 1.6), (64.0, 1.45, 1.5), (76.25, 3.0)], .5),
    "about": ("Almond Amit/VID_20230510_213830.mp4", 5, .5),
    "services": (f"{NS}/IMG_6030.MOV", 92, .5),
    "gallery": ("New/VID_20231127_201022.mp4", 27, .5),
}
CLIP_SECONDS = 8

# In-page clips (not heroes): name: ([(path, start, seconds)], filter before scaling)
# The pre-wedding reels were supplied separately; they are landscape film stored sideways.
DOWNLOADS = Path.home() / "Downloads"
CLIPS = {
    "prewedding": ([
        (DOWNLOADS / "SnapReels.Net_AQNlD7eFK5zLxuoH_WGFXJqZ7I0DUVXoo7DCfZUXQYzelfCiyjIW1jq_28fd8TQykLqSGMmzGlr2kSo2HtkQuSlG6ye8RP3Pspsb65U.mp4", 4.0, 6.0),
        (DOWNLOADS / "SnapReels.Net_AQN8bpFAz35JBzIJsm_cxEEDQ_0OVdv1A1fR_nGcseMVPqNmp0VfDcruVD6_Vu-w0NPDyb8133TGE2sSUaMHHwB-KwIDDwZIawCkgtk.mp4", 3.0, 6.0),
    ], "transpose=2"),
}


def run(*cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def grab_frame(video, t, out):
    run("ffmpeg", "-nostdin", "-v", "error", "-ss", str(t), "-i", str(SRC / video),
        "-frames:v", "1", "-y", str(out))


def crop(im, aspect, fx, fy):
    if not aspect:
        return im
    a, b = (int(v) for v in aspect.split(":"))
    w, h = im.size
    cw, ch = (w, round(w * b / a)) if w * b / a <= h else (round(h * a / b), h)
    x = min(max(round(fx * w - cw / 2), 0), w - cw)
    y = min(max(round(fy * h - ch / 2), 0), h - ch)
    return im.crop((x, y, x + cw, y + ch))


def encode(im, stem, avif=True):
    """Writes stem.webp (+ stem.avif) from a PIL image; no metadata is carried over."""
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "in.png"
        im.save(png)
        run("cwebp", "-quiet", "-q", "78", "-m", "6", "-metadata", "none", str(png), "-o", f"{stem}.webp")
        if avif:
            run("avifenc", "-q", "56", "-s", "5", "--ignore-exif", "--ignore-xmp", str(png), f"{stem}.avif")


def master(source, tmp):
    if isinstance(source, tuple):
        _, video, t = source
        out = Path(tmp) / "frame.png"
        grab_frame(video, t, out)
        return Image.open(out).convert("RGB")
    return ImageOps.exif_transpose(Image.open(SRC / source)).convert("RGB")


def build_photo(name, spec):
    source, aspect, fx, fy = spec
    with tempfile.TemporaryDirectory() as tmp:
        im = crop(master(source, tmp), aspect, fx, fy)
    w, h = im.size
    sizes = WIDTHS + [2400] if name in FULL_BLEED else WIDTHS
    widths = [x for x in sizes if x < w] + [min(w, sizes[-1])]
    widths = sorted(set(widths))
    for x in widths:
        encode(im.resize((x, round(h * x / w)), Image.LANCZOS), IMG / f"{name}-{x}")
    top = widths[-1]
    return {"w": top, "h": round(h * top / w), "widths": widths}


def cut(segments, vf, out, crf, maxrate):
    """Joins (path, start, seconds[, slow]) segments, applies vf and writes a muted H.264 MP4."""
    inputs, parts, labels = [], [], ""
    for i, (path, start, dur, *slow) in enumerate(segments):
        inputs += ["-ss", str(start), "-t", str(dur), "-i", str(path)]
        parts.append(f"[{i}:v]setpts={slow[0] if slow else 1}*(PTS-STARTPTS),setsar=1[s{i}]")
        labels += f"[s{i}]"
    graph = ";".join(parts) + f";{labels}concat=n={len(segments)}:v=1:a=0,fps=25,{vf}[out]"
    run("ffmpeg", "-nostdin", "-v", "error", *inputs, "-filter_complex", graph, "-map", "[out]", "-an",
        "-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-crf", str(crf), "-maxrate", maxrate, "-bufsize", str(int(maxrate[:-1]) * 2) + "k",
        "-movflags", "+faststart", "-map_metadata", "-1", "-y", str(out))


def first_frame(out_png, mp4):
    run("ffmpeg", "-nostdin", "-v", "error", "-i", str(mp4), "-frames:v", "1", "-y", str(out_png))
    return Image.open(out_png).convert("RGB")


def build_hero(page, spec):
    video, when, fx = spec
    segments = [(SRC / video, *seg) for seg in (when if isinstance(when, list) else [(when, CLIP_SECONDS)])]
    lg, sm = VID / f"{page}-hero.mp4", VID / f"{page}-hero-sm.mp4"
    cut(segments, "scale=-2:1080:flags=lanczos,crop=1920:1080", lg, 29, "1600k")
    cut(segments, f"crop=ih*9/16:ih:(iw-ih*9/16)*{fx}:0,scale=720:1280:flags=lanczos", sm, 30, "640k")
    # posters (the clip's first frame) for the video element, which takes a single URL
    with tempfile.TemporaryDirectory() as tmp:
        encode(first_frame(Path(tmp) / "lg.png", lg), IMG / f"{page}-hero-1920", avif=False)
        encode(first_frame(Path(tmp) / "sm.png", sm), IMG / f"{page}-hero-sm", avif=False)


def build_clip(name, spec):
    segments, pre = spec
    out = VID / f"{name}.mp4"
    cut(segments, f"{pre},scale=1280:720:flags=lanczos", out, 27, "1400k")
    with tempfile.TemporaryDirectory() as tmp:
        encode(first_frame(Path(tmp) / "p.png", out), IMG / f"{name}-poster", avif=False)


def build_og():
    """Social share card: the wedding stage, darkened at the edge, with the gold logo."""
    with tempfile.TemporaryDirectory() as tmp:
        im = crop(master(PHOTOS["wedding-stage"][0], tmp), "40:21", .5, .5).resize((1200, 630), Image.LANCZOS)
    # dark garnet wash, strongest bottom-left where the logo sits
    shade = Image.new("L", im.size)
    shade.putdata([int(240 * max(0, 1 - x / 820) ** .8 * min(1, .45 + y / 630)) for y in range(630) for x in range(1200)])
    im = Image.composite(Image.new("RGB", im.size, (28, 6, 12)), im, shade)
    logo = Image.open(IMG / "logo-full-light.png").convert("RGBA")
    im.paste(logo, (56, 630 - logo.height - 40), logo)
    im.save(IMG / "og-image.jpg", quality=82, optimize=True, progressive=True)


def main():
    only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[1] == "--only" else None
    manifest_path = ROOT / "tools/media.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    IMG.mkdir(parents=True, exist_ok=True)
    VID.mkdir(parents=True, exist_ok=True)
    for name, spec in PHOTOS.items():
        if only is None or name in only:
            manifest[name] = build_photo(name, spec)
            print("photo", name, manifest[name])
    for page, spec in HEROES.items():
        if only is None or f"{page}-hero" in only:
            build_hero(page, spec)
            print("hero", page)
    for name, spec in CLIPS.items():
        if only is None or name in only:
            build_clip(name, spec)
            print("clip", name)
    if only is None or "og" in only:
        build_og()
    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), indent=1) + "\n")


if __name__ == "__main__":
    main()
