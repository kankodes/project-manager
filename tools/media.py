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
FULL_BLEED = {"palace-stage", "led-stage"}
OG_SOURCE = "nikhil soni event/FullSizeRender.jpeg"  # wedding stage, used only for the share card

NS = "nikhil soni event"
BR = "BRNADING WORKS"
RV = "RAJ VILLAS EVENT"

# name: (source, crop aspect or None, focus x, focus y)
#   source is a path under SRC, or ("frame", video path, seconds) for a still
#   pulled from 4K/1080p footage. Crops to the largest box of that aspect
#   centred on the focus point; reel frames are cropped to clear on-screen text.
PHOTOS = {
    "wedding-stage-tall": (f"{NS}/FullSizeRender (2).jpeg", "4:5", .5, .55),
    "peacock-entry": (f"{NS}/IMG_6072.jpeg", "4:5", .5, .5),
    "stage-haze": (("frame", f"{NS}/IMG_6030.MOV", 80), None, .5, .5),
    "led-stage": (("frame", "New/VID_20231127_201022.mp4", 35), None, .5, .5),
    "palace-stage": (("frame", "reels/VID_20251125_215713787.mp4", 70), None, .5, .5),
    "brand-gate": (f"{BR}/WhatsApp Image 2024-08-31 at 7.41.38 PM (3).jpeg", None, .5, .5),
    "blue-florals": (("frame", "New/VID_20231230_211059.mp4", 12.8), "4:5", .5, .45),
    # 3:2 from the top drops the phone's date stamp
    "poolside-haldi": ("Ev/IMG-20250523-WA0026.jpg", "3:2", .5, 0),
    "haldi-canopy": ("Ev/IMG-20250523-WA0030.jpg", "3:2", .5, 0),
}
# Not used: reels cut by outside creators (Stories of Shaadi, BTS Wedding Reels,
# Blink - incl. the Rajasthan villa event), photographer-watermarked sets
# (Wedding Swag by Rohit Thakur) and Vedas n Mantras branded decor films/photos.
# They need the owner's permission before they go on the site.

# page: (video, cut, focus x for the portrait phone crop)
#   cut is a start second (an 8 s clip from there) or a list of (start, seconds[, slow])
#   segments joined in order; slow > 1 stretches a segment into slow motion.
#   Contact is built separately from the 2026 reels (CONTACT below).
HEROES = {
    # entries from the Mariam & Aftab teaser: sangeet couple, sangeet bride with dancers,
    # the stage light show, then the reception stage (no nikah footage, at the client's request)
    "home": ("Garnet /Mariam Teaser Photalk.mp4", [(10.75, 1.25, 1.6), (32.25, 1.75, 1.3), (35.25, 1.0), (64.0, 1.45, 1.6)], .5),
    "about": ("Almond Amit/VID_20230510_213830.mp4", 5, .5),
    "services": (f"{NS}/IMG_6030.MOV", 92, .5),
    "gallery": ("New/VID_20231127_201022.mp4", 27, .5),
}
CLIP_SECONDS = 8

# In-page clips (not heroes): name: (segments, filter applied to each segment, crf)
#   segments are (path, start, seconds[, slow]); the filter must end at one fixed size.
DOWNLOADS = Path.home() / "Downloads"
R26 = SRC / "Garnet /Garnet 2026 Reels"
# Garnet's own 2026 reels carry captions in the top fifth of the frame: every crop
# below starts under that band. Left out: IMG_9377 (third-party "Varmala Decor" caption)
# and IMG_3943 (couple's names on the baraat car). CARD = 4:5 (service cards), PANEL = 4:5 large.
CARD = "crop=iw:iw*5/4:0:(ih-iw*5/4)*0.75,scale=480:600:flags=lanczos"
CARD_HIGH = "crop=iw:iw*5/4:0:(ih-iw*5/4)*0.2,scale=480:600:flags=lanczos"
PANEL = "crop=iw:iw*5/4:0:(ih-iw*5/4)*0.75,scale=864:1080:flags=lanczos"
CLIPS = {
    # supplied separately: landscape film stored sideways
    "prewedding": ([
        (DOWNLOADS / "SnapReels.Net_AQNlD7eFK5zLxuoH_WGFXJqZ7I0DUVXoo7DCfZUXQYzelfCiyjIW1jq_28fd8TQykLqSGMmzGlr2kSo2HtkQuSlG6ye8RP3Pspsb65U.mp4", 4.0, 6.0),
        (DOWNLOADS / "SnapReels.Net_AQN8bpFAz35JBzIJsm_cxEEDQ_0OVdv1A1fR_nGcseMVPqNmp0VfDcruVD6_Vu-w0NPDyb8133TGE2sSUaMHHwB-KwIDDwZIawCkgtk.mp4", 3.0, 6.0),
    ], "transpose=2,scale=1280:720:flags=lanczos", 27),
    "svc-planning": ([(R26 / "IMG_3829.MP4", 2.8, 3.5)], CARD, 30),      # mehendi entrance decor
    "svc-design": ([(R26 / "IMG_4195.MP4", 0.8, 3.5)], CARD, 30),        # haldi dreamcatcher decor
    "svc-venue": ([(R26 / "IMG_4540.MP4", 23.4, 3.2)], CARD, 30),        # banquet hall, yellow stage
    # crew dressing an outdoor venue (first 10 s, before the reel's caption appears)
    "svc-vendors": ([(SRC / "reels/Decor WIP reel.MOV", 2.5, 4.0)], CARD, 30),
    "svc-decor": ([(R26 / "IMG_7853.MP4", 18.3, 2.7)], CARD_HIGH, 30),   # rose ceiling (crop stays above the name lights)
    "svc-light": ([(R26 / "IMG_4539.MP4", 10.4, 1.4, 2.2)], CARD, 30),        # stage lighting
    "svc-entertainment": ([(R26 / "IMG_4048.MP4", 1.6, 1.6, 2.0)], CARD, 30), # shadow-dance act
    "svc-onsite": ([(R26 / "IMG_3881.MP4", 0.6, 4.0)], CARD, 30),        # last-minute stage set-up
    "svc-logistics": ([(R26 / "IMG_4322.MP4", 0.3, 4.0)], CARD, 30),     # baraat on the move, sparklers
    "svc-weddings": ([(R26 / "IMG_4326.MP4", 7.6, 5.0)], PANEL, 28),     # golden-wheel bridal entry
}

# Contact banner, compiled from the 2026 reels: three portrait columns side by side on
# wide screens (cuts staggered per column), one portrait sequence on phones.
COLUMN = ("crop=ih*0.474:ih*0.8:(iw-ih*0.474)/2:ih*0.2,scale=636:1080:flags=lanczos,"
          "pad=640:1080:2:0:color=0x1d1416")
PORTRAIT = "crop=ih*0.45:ih*0.8:(iw-ih*0.45)/2:ih*0.2,scale=720:1280:flags=lanczos"
CONTACT = {
    "columns": [
        [(R26 / "IMG_4326.MP4", 7.6, 4.0), (R26 / "IMG_4325.MP4", 5.6, 4.0)],
        [(R26 / "IMG_4540.MP4", 21.5, 3.0), (R26 / "IMG_4195.MP4", 9.0, 5.0)],
        [(R26 / "sangit hritick.mp4", 12.0, 3.0), (R26 / "varmala hritick.mp4", 19.0, 5.0)],
    ],
    "phone": [(R26 / "IMG_4326.MP4", 8.0, 1.7), (R26 / "varmala hritick.mp4", 9.0, 1.7),
              (R26 / "IMG_4325.MP4", 6.2, 1.7), (R26 / "IMG_4322.MP4", 0.6, 1.7),
              (R26 / "IMG_4195.MP4", 10.0, 1.7), (R26 / "sangit hritick.mp4", 12.5, 1.7)],
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
        parts.append(f"[{i}:v]setpts={slow[0] if slow else 1}*(PTS-STARTPTS),{vf},setsar=1[s{i}]")
        labels += f"[s{i}]"
    graph = ";".join(parts) + f";{labels}concat=n={len(segments)}:v=1:a=0,fps=25[out]"
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
    segments, vf, crf = spec
    out = VID / f"{name}.mp4"
    cut(segments, vf, out, crf, "1400k" if crf < 30 else "600k")
    with tempfile.TemporaryDirectory() as tmp:
        encode(first_frame(Path(tmp) / "p.png", out), IMG / f"{name}-poster", avif=False)


def build_contact():
    lg, sm = VID / "contact-hero.mp4", VID / "contact-hero-sm.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        cols = [Path(tmp) / f"c{i}.mp4" for i in range(3)]
        for col, segs in zip(cols, CONTACT["columns"]):
            cut(segs, COLUMN, col, 18, "8000k")
        run("ffmpeg", "-nostdin", "-v", "error", *[a for c in cols for a in ("-i", str(c))],
            "-filter_complex", "[0:v][1:v][2:v]hstack=3[out]", "-map", "[out]", "-an",
            "-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-crf", "29", "-maxrate", "1600k", "-bufsize", "3200k", "-movflags", "+faststart",
            "-map_metadata", "-1", "-y", str(lg))
        cut(CONTACT["phone"], PORTRAIT, sm, 30, "640k")
        encode(first_frame(Path(tmp) / "lg.png", lg), IMG / "contact-hero-1920", avif=False)
        encode(first_frame(Path(tmp) / "sm.png", sm), IMG / "contact-hero-sm", avif=False)


def build_og():
    """Social share card: the wedding stage, darkened at the edge, with the gold logo."""
    with tempfile.TemporaryDirectory() as tmp:
        im = crop(master(OG_SOURCE, tmp), "40:21", .5, .5).resize((1200, 630), Image.LANCZOS)
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
    if only is None or "contact-hero" in only:
        build_contact()
        print("hero contact (2026 reels)")
    if only is None or "og" in only:
        build_og()
    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), indent=1) + "\n")


if __name__ == "__main__":
    main()
