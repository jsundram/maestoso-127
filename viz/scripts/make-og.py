#!/usr/bin/env python3
"""Build the 1200x630 Open Graph share card for viz/.

The card is data-driven: the semicircle rows are drawn from times.json with the
same geometry the page uses (alternating up/down half-circles, unscaled so a
slower recording is a wider row). times.json + this script are the source of
truth; assets/og.svg and assets/og.png are both generated.

    python3 viz/scripts/make-og.py

Requires headless Chrome (rsvg-convert cannot read the woff2 @font-face the
card embeds) and pngquant. Hard-fails if the PNG lands over 250 KB, which is
the margin under WhatsApp's ~300 KB scrape cutoff.
"""

import base64
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

VIZ = pathlib.Path(__file__).resolve().parent.parent
ASSETS = VIZ / "assets"

W, H = 1200, 630
BG = "rgb(209, 199, 180)"
INK = "#111"
MUTED = "#4a4335"
UP = "rgb(38, 40, 44)"
DOWN = "rgb(173, 36, 40)"

TITLE = "Opus 127: Maestoso"
SUBTITLE = "How twenty string quartets shape Beethoven's opening bars"

# Three recordings spanning the tempo range, slowest last so the eye reads
# the widening. Names must match times.json exactly.
FEATURED = ["Quatour Mosaiques", "Emerson String Quartet", "Takacs Quartet"]

LABEL_W = 250          # right-aligned meta column, mirrors the page's .meta
GUTTER = 24
LEFT = 70
CHART_X = LEFT + LABEL_W + GUTTER
CHART_W = W - CHART_X - LEFT
CHART_TOP = 244
CHART_BOTTOM = 536
ROW_GAP = 26

MAX_PNG_BYTES = 250 * 1024


def font_face(family, weight, filename):
    data = base64.b64encode((VIZ / "fonts" / filename).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;"
        f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
    )


def rows(entries):
    """Lay out the featured rows; returns (svg_fragment, total_height)."""
    by_artist = {e["artist"].strip(): e for e in entries}
    picked = [by_artist[name] for name in FEATURED]
    picked.sort(key=lambda e: max(e["timestamps"]))

    span = max(max(e["timestamps"]) for e in picked)
    scale = CHART_W / span

    laid = []
    for entry in picked:
        ts = entry["timestamps"]
        gaps = [(ts[i], ts[i + 1]) for i in range(len(ts) - 1)]
        up = max((b - a) for i, (a, b) in enumerate(gaps) if i % 2 == 0) / 2 * scale
        down = max((b - a) for i, (a, b) in enumerate(gaps) if i % 2 == 1) / 2 * scale
        laid.append((entry, gaps, up, down))

    height = sum(u + d for _, _, u, d in laid) + ROW_GAP * (len(laid) - 1)
    y = CHART_TOP + (CHART_BOTTOM - CHART_TOP - height) / 2

    out = []
    for entry, gaps, up, down in laid:
        baseline = y + up
        for i, (t1, t2) in enumerate(gaps):
            x1, x2 = t1 * scale, t2 * scale
            r = (x2 - x1) / 2
            sweep = 1 if i % 2 == 0 else 0        # even arcs bulge up, odd down
            fill = UP if i % 2 == 0 else DOWN
            out.append(
                f'<path d="M {CHART_X + x1:.1f} {baseline:.1f} '
                f'A {r:.1f} {r:.1f} 0 0 {sweep} {CHART_X + x2:.1f} {baseline:.1f} Z" '
                f'fill="{fill}"/>'
            )
        label_x = LEFT + LABEL_W
        out.append(
            f'<text x="{label_x}" y="{baseline - 6:.1f}" text-anchor="end" '
            f'class="artist">{entry["artist"].strip()}</text>'
        )
        out.append(
            f'<text x="{label_x}" y="{baseline + 22:.1f}" text-anchor="end" '
            f'class="dur">{max(entry["timestamps"]):.1f}s</text>'
        )
        y += up + down + ROW_GAP
    return "\n  ".join(out)


def build_svg():
    entries = json.loads((VIZ / "times.json").read_text())
    recordings = [e for e in entries if not e["artist"].strip().startswith("tempo@")]
    faces = "".join([
        font_face("Playfair Display", 700, "PlayfairDisplay-Bold.woff2"),
        font_face("Source Serif 4", 400, "SourceSerif4-Regular.woff2"),
    ])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    {faces}
    .title {{ font-family:'Playfair Display',serif; font-weight:700; font-size:76px; fill:{INK}; letter-spacing:0.02em; }}
    .subtitle {{ font-family:'Source Serif 4',serif; font-size:30px; fill:{MUTED}; }}
    .artist {{ font-family:'Source Serif 4',serif; font-weight:400; font-size:24px; fill:{INK}; }}
    .dur {{ font-family:'Source Serif 4',serif; font-size:19px; fill:{MUTED}; }}
    .footer {{ font-family:'Source Serif 4',serif; font-size:21px; fill:{MUTED}; }}
  </style>
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <text x="{W/2:.0f}" y="132" text-anchor="middle" class="title">{TITLE}</text>
  <text x="{W/2:.0f}" y="186" text-anchor="middle" class="subtitle">{SUBTITLE}</text>
  {rows(entries)}
  <text x="{W/2:.0f}" y="606" text-anchor="middle" class="footer">{len(recordings)} recordings, tapped and drawn to scale</text>
</svg>
"""


def chrome():
    for path in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("chromium") or "",
        shutil.which("google-chrome") or "",
    ):
        if path and pathlib.Path(path).exists():
            return path
    sys.exit("no Chrome/Chromium found; needed to rasterize the embedded woff2 fonts")


def main():
    ASSETS.mkdir(exist_ok=True)
    svg = ASSETS / "og.svg"
    png = ASSETS / "og.png"
    svg.write_text(build_svg())

    with tempfile.TemporaryDirectory() as tmp:
        raw = pathlib.Path(tmp) / "og.png"
        proc = subprocess.Popen([
            chrome(), "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--virtual-time-budget=5000",
            f"--screenshot={raw}", f"--window-size={W},{H}",
            f"--user-data-dir={tmp}/profile", svg.as_uri(),
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Chrome writes the screenshot but does not reliably exit afterwards
        # (its updater/crash-handler children keep the process alive), so wait
        # for the file to appear and settle, then shut it down ourselves.
        deadline = time.monotonic() + 120
        stable = 0
        while time.monotonic() < deadline:
            if proc.poll() is not None and raw.exists():
                break
            if raw.exists() and raw.stat().st_size > 0:
                stable += 1
                if stable >= 3:
                    break
            time.sleep(0.5)
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

        if not raw.exists() or raw.stat().st_size == 0:
            sys.exit("Chrome produced no screenshot")

        if shutil.which("pngquant"):
            subprocess.run([
                "pngquant", "--quality=70-95", "--speed=1", "--force",
                "--output", str(png), str(raw),
            ], check=True)
        else:
            shutil.copy(raw, png)

    size = png.stat().st_size
    print(f"{png.relative_to(VIZ.parent)}: {W}x{H}, {size/1024:.0f} KB")
    if size > MAX_PNG_BYTES:
        sys.exit(f"og.png is {size/1024:.0f} KB, over the {MAX_PNG_BYTES/1024:.0f} KB budget")


if __name__ == "__main__":
    main()
