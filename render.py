"""Export the Octo Manager animation to MP4 (or a few preview PNGs).

    pip install playwright && playwright install chromium
    python render.py video  assets/demo.mp4
    python render.py preview

Frames are rendered deterministically: the page exposes render(t), we call it
for every frame at 2x scale and pipe the frames into ffmpeg.
"""
import base64
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
FPS, DUR = 30, 18


def grab(page, fmt="png"):
    mime = "image/png" if fmt == "png" else "image/jpeg"
    data = page.evaluate(f"document.getElementById('c').toDataURL('{mime}', 0.95)")
    return base64.b64decode(data.split(",", 1)[1])


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "assets" / "demo.mp4"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.goto((ROOT / "index.html").as_uri() + "?render=1")
        page.wait_for_function("window.ready === true")
        if mode == "preview":
            for t in (0.0, 4.0, 9.0, 13.0):
                page.evaluate(f"render({t})")
                (ROOT / f"preview_{t:.0f}.png").write_bytes(grab(page))
        else:
            ff = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                 "-c:v", "mjpeg", "-i", "-", "-vf", "scale=1080:1350:flags=lanczos",
                 "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                 "-movflags", "+faststart", str(out)],
                stdin=subprocess.PIPE,
            )
            for f in range(FPS * DUR):
                page.evaluate(f"render({f / FPS})")
                ff.stdin.write(grab(page, "jpeg"))
            ff.stdin.close()
            ff.wait()
            print(f"saved {out}")
        browser.close()


if __name__ == "__main__":
    main()
