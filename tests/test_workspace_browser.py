"""FOLIO W03-01 browser regression: synthetic/local-only, no service calls.

Run from the repository root:
    python -m pip install playwright==1.57.0
    python -m playwright install chromium webkit
    FOLIO_BROWSER=chromium python -m unittest discover -s tests -p "test_*.py" -v
    FOLIO_BROWSER=webkit python -m unittest discover -s tests -p "test_*.py" -v

This tests the checked-out index.html itself; it never uploads user PDFs.
"""
import os
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(__file__).resolve().parents[1] / "index.html"
ENGINE = os.environ.get("FOLIO_BROWSER", "chromium")


def synthetic_pdf():
    """Generate a one-page, text-free, non-personal PDF in memory."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    positions = [0]
    for i, obj in enumerate(objects, start=1):
        positions.append(len(pdf))
        pdf.extend(str(i).encode() + b" 0 obj\n" + obj + b"\nendobj\n")
    start = len(pdf)
    pdf.extend(b"xref\n0 4\n0000000000 65535 f \n")
    for pos in positions[1:]:
        pdf.extend(f"{pos:010d} 00000 n \n".encode())
    pdf.extend(b"trailer\n<< /Root 1 0 R /Size 4 >>\nstartxref\n")
    pdf.extend(str(start).encode() + b"\n%%EOF\n")
    return bytes(pdf)


class WorkspaceBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if ENGINE not in ("chromium", "webkit"):
            raise ValueError("FOLIO_BROWSER must be chromium or webkit")
        if not HTML.is_file():
            raise FileNotFoundError(f"Checked-out HTML not found: {HTML}")
        cls.playwright = sync_playwright().start()
        cls.browser = getattr(cls.playwright, ENGINE).launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "browser"):
            cls.browser.close()
        if hasattr(cls, "playwright"):
            cls.playwright.stop()

    def open_workspace(self, width=390, height=844):
        context = self.browser.new_context(
            viewport={"width": width, "height": height},
            reduced_motion="reduce",
        )
        self.addCleanup(context.close)
        page = context.new_page()
        external = []
        errors = []
        page.on("request", lambda req: external.append(req.url) if req.url.startswith(("http:", "https:")) else None)
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(HTML.as_uri(), wait_until="load")
        page.wait_for_function("document.documentElement.classList.contains('js-ready')")
        self.assertEqual([], errors, f"JS errors: {errors}")
        self.assertEqual([], external, f"Unexpected network requests: {external}")
        return page, external, errors

    def assert_clean(self, external, errors):
        self.assertEqual([], errors)
        self.assertEqual([], external)

    def test_mobile_quiz_navigation_both_directions(self):
        for width, height in ((320, 720), (390, 844), (670, 900)):
            with self.subTest(width=width):
                page, ext, errors = self.open_workspace(width, height)
                page.locator('#pane-left select[data-pane="left"]').select_option("notes")
                page.locator('#pane-left [data-action="open-quiz"]').click()
                self.assertTrue(page.locator("#pane-right").is_visible())
                self.assertFalse(page.locator("#pane-left").is_visible())
                self.assertTrue(page.locator('.phone-side[data-side="right"]').evaluate("(el) => el.classList.contains('active')"))
                self.assertTrue(page.locator('#pane-right .quiz-item').first.is_visible())
                # Reverse: right-side notes should open left quiz and make it visible.
                page.locator('#pane-right select[data-pane="right"]').select_option("notes")
                page.locator('#pane-right [data-action="open-quiz"]').click()
                self.assertTrue(page.locator("#pane-left").is_visible())
                self.assertTrue(page.locator('#pane-left .quiz-item').first.is_visible())
                self.assertTrue(page.locator('.phone-side[data-side="left"]').evaluate("(el) => el.classList.contains('active')"))
                self.assert_clean(ext, errors)

    def test_mobile_source_pdf_navigation_both_directions(self):
        for width, height in ((320, 720), (390, 844), (670, 900)):
            with self.subTest(width=width):
                page, ext, errors = self.open_workspace(width, height)
                page.locator('#pane-left select[data-pane="left"]').select_option("notes")
                page.locator('#pane-left [data-action="source-page"]').click()
                self.assertTrue(page.locator("#pane-right").is_visible())
                self.assertTrue(page.locator('#pane-right .pdf-shell').is_visible())
                self.assertEqual("12", page.locator('#pane-right [data-page-now]').inner_text())
                page.locator('#pane-right select[data-pane="right"]').select_option("notes")
                page.locator('#pane-right [data-action="source-page"]').click()
                self.assertTrue(page.locator("#pane-left").is_visible())
                self.assertTrue(page.locator('#pane-left .pdf-shell').is_visible())
                self.assertEqual("12", page.locator('#pane-left [data-page-now]').inner_text())
                self.assert_clean(ext, errors)

    def test_tablet_layout_and_independent_panes(self):
        for width, height, expected_orientation in (
            (768, 1024, "horizontal"), (1024, 768, "vertical"), (1366, 1024, "vertical"),
        ):
            with self.subTest(width=width):
                page, ext, errors = self.open_workspace(width, height)
                self.assertTrue(page.locator("#pane-left").is_visible())
                self.assertTrue(page.locator("#pane-right").is_visible())
                self.assertEqual(expected_orientation, page.locator("#splitter").get_attribute("aria-orientation"))
                page.locator('#pane-right [data-action="open-quiz"]').click()
                self.assertTrue(page.locator('#pane-left .quiz-item').first.is_visible())
                self.assertTrue(page.locator('#pane-right .notes-shell').is_visible())
                self.assertTrue(page.locator("#pane-right").is_visible())
                self.assert_clean(ext, errors)

    def test_splitter_keyboard_and_orientation(self):
        page, ext, errors = self.open_workspace(1024, 768)
        splitter = page.locator("#splitter")
        self.assertEqual("57", splitter.get_attribute("aria-valuenow"))
        splitter.focus()
        splitter.press("ArrowRight")
        self.assertEqual("60", splitter.get_attribute("aria-valuenow"))
        page.set_viewport_size({"width": 768, "height": 1024})
        # Resize/media-query event dispatch is asynchronous in real browsers.
        page.wait_for_function(
            "document.querySelector('#splitter').getAttribute('aria-orientation') === 'horizontal'"
        )
        self.assertEqual("horizontal", splitter.get_attribute("aria-orientation"))
        splitter.focus()
        splitter.press("ArrowDown")
        self.assertEqual("56", splitter.get_attribute("aria-valuenow"))
        self.assert_clean(ext, errors)

    def test_quiz_feedback_and_pdf_controls(self):
        page, ext, errors = self.open_workspace(1024, 768)
        page.locator('#pane-left select[data-pane="left"]').select_option("quiz")
        item = page.locator('#pane-left .quiz-item').first
        item.locator('button[data-choice="1"]').click()
        item.locator('button[data-action="submit-answer"]').click()
        self.assertIn("정답입니다", item.locator(".answer-feedback").inner_text())
        self.assertIn("1 / 4", page.locator('#pane-left [data-quiz-progress]').inner_text())
        page.locator('#pane-left select[data-pane="left"]').select_option("pdf")
        page.locator('#pane-left [data-action="next-page"]').click()
        self.assertEqual("13", page.locator('#pane-left [data-page-now]').inner_text())
        page.locator('#pane-left [data-action="zoom-in"]').click()
        self.assertEqual("110%", page.locator('#pane-left [data-zoom-count]').inner_text())
        self.assert_clean(ext, errors)

    def test_local_pdf_without_external_upload(self):
        page, ext, errors = self.open_workspace(1024, 768)
        page.locator('#pane-left input[data-pdf-input]').set_input_files({
            "name": "synthetic.pdf",
            "mimeType": "application/pdf",
            "buffer": synthetic_pdf(),
        })
        self.assertEqual("synthetic.pdf", page.locator('#pane-left [data-pdf-name]').inner_text())
        self.assertTrue(page.locator('#pane-left [data-pdf-iframe]').get_attribute("src").startswith("blob:"))
        page.locator('#pane-right select[data-pane="right"]').select_option("notes")
        self.assertIn("분석되지 않은", page.locator('#pane-right .main-title').inner_text())
        self.assert_clean(ext, errors)


if __name__ == "__main__":
    unittest.main()
