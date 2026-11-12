"""Capture private browser screenshots of the fully local, synthetic FOLIO demo.

Run only on the checked-out design branch. No user files, network, deployment,
or remote screenshots are involved. CI uploads images as a private artifact.
"""
from pathlib import Path
from playwright.sync_api import Error as PlaywrightError, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "studio-previews"


def capture(browser, width, height, name, side=None, zoom_steps=0, page_steps=0):
    context = browser.new_context(
        viewport={"width": width, "height": height},
        reduced_motion="reduce",
        device_scale_factor=1,
    )
    try:
        page = context.new_page()
        external = []
        page.on(
            "request",
            lambda req: external.append(req.url)
            if req.url.startswith(("http:", "https:")) else None,
        )
        page.goto((ROOT / "index.html").as_uri())
        page.wait_for_function("document.documentElement.classList.contains('js-ready')")
        if side:
            page.locator(f'.phone-side[data-side="{side}"]').click()
        for _ in range(zoom_steps):
            page.locator('#pane-left [data-action="zoom-in"]').click()
        for _ in range(page_steps):
            page.locator('#pane-left [data-action="next-page"]').click()
        if external:
            raise RuntimeError(f"External requests not permitted: {external}")
        try:
            page.screenshot(path=str(OUT / name), full_page=False, animations="disabled")
        except PlaywrightError as exc:
            # Rare headless Chromium protocol capture failure; never mask other errors.
            if "Unable to capture screenshot" not in str(exc):
                raise
            page.wait_for_timeout(250)
            page.screenshot(path=str(OUT / name), full_page=False, animations="disabled")
    finally:
        context.close()


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        try:
            capture(b, 1366, 900, "desktop-landscape.png")
            capture(b, 768, 1024, "tablet-portrait.png")
            capture(b, 390, 844, "phone-pdf.png")
            capture(b, 390, 844, "phone-explanation.png", side="right")
            capture(b, 768, 1024, "tablet-portrait-zoom130.png", zoom_steps=3)
            capture(b, 390, 844, "phone-pdf-zoom160.png", zoom_steps=6)
            capture(b, 390, 844, "phone-pdf-page13.png", page_steps=1)
        finally:
            b.close()
    print(f"Saved 7 synthetic demo previews in {OUT}")
