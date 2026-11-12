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


    def test_studio_v2_stylesheet_replaces_legacy_appearance(self):
        page, ext, errors = self.open_workspace(1024, 768)
        self.assertEqual(0, page.locator("head style").count())
        self.assertEqual("styles/studio-v2.css", page.locator('link[rel="stylesheet"]').get_attribute("href"))
        self.assertTrue(page.evaluate("""
            () => [...document.styleSheets].some(s => (s.href || '').endsWith('/styles/studio-v2.css'))
        """))
        self.assertEqual("rgb(23, 41, 50)", page.locator(".session-bar").evaluate(
            "(el) => getComputedStyle(el).backgroundColor"
        ))
        self.assertEqual("rgb(255, 255, 255)", page.locator(".study-shell").first.evaluate(
            "(el) => getComputedStyle(el).backgroundColor"
        ))
        self.assertEqual("FOLIO — Study Studio", page.title())
        self.assert_clean(ext, errors)

    def test_studio_responsive_workspace_without_document_overflow(self):
        for width, height in ((320, 720), (390, 844), (670, 900),
                              (768, 1024), (1024, 768), (1366, 1024)):
            with self.subTest(viewport=(width, height)):
                page, ext, errors = self.open_workspace(width, height)
                metrics = page.evaluate("""() => ({
                    documentWidth: document.documentElement.scrollWidth,
                    windowWidth: innerWidth,
                    appHeight: document.querySelector('.app').getBoundingClientRect().height,
                    windowHeight: innerHeight
                })""")
                self.assertLessEqual(metrics["documentWidth"], metrics["windowWidth"] + 1)
                self.assertLessEqual(abs(metrics["appHeight"] - metrics["windowHeight"]), 1)
                if width <= 670:
                    self.assertTrue(page.locator(".phone-switcher").is_visible())
                    self.assertTrue(page.locator("#pane-left").is_visible())
                    self.assertFalse(page.locator("#pane-right").is_visible())
                else:
                    self.assertFalse(page.locator(".phone-switcher").is_visible())
                    self.assertTrue(page.locator("#pane-left").is_visible())
                    self.assertTrue(page.locator("#pane-right").is_visible())
                self.assert_clean(ext, errors)

    def test_mobile_current_view_screenreader_metadata(self):
        page, ext, errors = self.open_workspace(390, 844)
        left = page.locator('.phone-side[data-side="left"]')
        right = page.locator('.phone-side[data-side="right"]')
        self.assertEqual("pane-left", left.get_attribute("aria-controls"))
        self.assertEqual("pane-right", right.get_attribute("aria-controls"))
        self.assertEqual("true", left.get_attribute("aria-current"))
        self.assertIsNone(right.get_attribute("aria-current"))
        right.click()
        self.assertIsNone(left.get_attribute("aria-current"))
        self.assertEqual("true", right.get_attribute("aria-current"))
        self.assertTrue(page.locator("#pane-right").is_visible())
        # Content-driven navigation must update the same ARIA state.
        page.locator('#pane-right [data-action="open-quiz"]').click()
        self.assertEqual("true", left.get_attribute("aria-current"))
        self.assertIsNone(right.get_attribute("aria-current"))
        self.assertTrue(page.locator("#pane-left .quiz-item").first.is_visible())
        self.assert_clean(ext, errors)

    def test_studio_mobile_controls_are_touch_sized(self):
        page, ext, errors = self.open_workspace(320, 720)
        selector = page.locator('#pane-left select[data-pane="left"]').bounding_box()
        nav = page.locator('.phone-side[data-side="left"]').bounding_box()
        upload = page.locator('#pane-left [data-action="upload-pdf"]').bounding_box()
        self.assertGreaterEqual(selector["height"], 42)
        self.assertGreaterEqual(nav["height"], 48)
        self.assertGreaterEqual(upload["height"], 38)
        self.assert_clean(ext, errors)

    def test_studio_pdf_uses_original_document_colors_by_default(self):
        page, ext, errors = self.open_workspace(1024, 768)
        page.locator('#pane-left input[data-pdf-input]').set_input_files({
            "name": "test-only.pdf",
            "mimeType": "application/pdf",
            "buffer": synthetic_pdf(),
        })
        frame = page.locator('#pane-left [data-pdf-iframe]')
        self.assertTrue(frame.evaluate("(el) => el.classList.contains('original-colors')"))
        self.assertEqual("none", frame.evaluate("(el) => getComputedStyle(el).filter"))
        page.locator('#pane-left [data-action="toggle-pdf-colors"]').click()
        self.assertFalse(frame.evaluate("(el) => el.classList.contains('original-colors')"))
        page.locator('#pane-left [data-action="toggle-pdf-colors"]').click()
        self.assertTrue(frame.evaluate("(el) => el.classList.contains('original-colors')"))
        self.assert_clean(ext, errors)


    def test_studio_portrait_compact_toolbar_preserves_pdf_reading_height(self):
        page, ext, errors = self.open_workspace(768, 1024)
        metrics = page.evaluate("""() => {
            const height = (selector) =>
                document.querySelector(selector).getBoundingClientRect().height;
            return {
                paneTopbar: height('#pane-left .pane-topbar'),
                pdfBar: height('#pane-left .pdf-bar'),
                pdfControls: height('#pane-left .pdf-controls'),
                pdfStage: height('#pane-left .pdf-stage'),
                notesTopline: height('#pane-right .study-topline'),
                notesPaneVisible: document.querySelector('#pane-right').getBoundingClientRect().height
            };
        }""")
        self.assertLessEqual(metrics["paneTopbar"], 49)
        self.assertLessEqual(metrics["pdfBar"], 43)
        self.assertLessEqual(metrics["pdfControls"], 50)
        self.assertGreater(metrics["pdfStage"], 360)
        self.assertLessEqual(metrics["notesTopline"], 39)
        self.assertGreater(metrics["notesPaneVisible"], 300)
        self.assertEqual("horizontal", page.locator("#splitter").get_attribute("aria-orientation"))
        self.assert_clean(ext, errors)

    def test_studio_mobile_korean_explanation_legibility(self):
        for width in (320, 390):
            with self.subTest(width=width):
                page, ext, errors = self.open_workspace(width, 844)
                page.locator('.phone-side[data-side="right"]').click()
                self.assertTrue(page.locator("#pane-right .notes-shell").is_visible())
                typography = page.locator("#pane-right .key-line p").first.evaluate("""el => {
                    const style = getComputedStyle(el);
                    return {
                        font: parseFloat(style.fontSize),
                        line: parseFloat(style.lineHeight),
                        width: el.getBoundingClientRect().width
                    };
                }""")
                self.assertGreaterEqual(typography["font"], 14)
                self.assertGreaterEqual(typography["line"], 25)
                self.assertGreater(typography["width"], 180)
                self.assertFalse(page.evaluate(
                    "document.documentElement.scrollWidth > window.innerWidth + 1"
                ))
                self.assert_clean(ext, errors)


    def test_tablet_pdf_zoom_preserves_scroll_and_document_node(self):
        page, ext, errors = self.open_workspace(768, 1024)
        stage = page.locator('#pane-left [data-pdf-stage]')
        stage.evaluate("""el => {
            el.dataset.sentinel = 'preserved';
            el.scrollTop = 160;
        }""")
        before = stage.evaluate("(el) => el.scrollTop")
        self.assertGreater(before, 90, "Synthetic PDF must be vertically scrollable")
        page.locator('#pane-left [data-action="zoom-in"]').click()
        self.assertEqual("110%", page.locator('#pane-left [data-zoom-count]').inner_text())
        self.assertEqual("preserved", stage.get_attribute("data-sentinel"))
        self.assertAlmostEqual(before * 1.1, stage.evaluate("(el) => el.scrollTop"), delta=3)
        page.locator('#pane-left [data-action="fit-pdf"]').click()
        self.assertEqual("100%", page.locator('#pane-left [data-zoom-count]').inner_text())
        self.assertEqual("preserved", stage.get_attribute("data-sentinel"))
        self.assertAlmostEqual(before, stage.evaluate("(el) => el.scrollTop"), delta=4)
        self.assert_clean(ext, errors)

    def test_mobile_zoomed_pdf_can_pan_to_both_horizontal_edges(self):
        for width in (320, 390):
            with self.subTest(width=width):
                page, ext, errors = self.open_workspace(width, 844)
                stage = page.locator('#pane-left [data-pdf-stage]')
                for _ in range(6):
                    page.locator('#pane-left [data-action="zoom-in"]').click()
                self.assertEqual("160%", page.locator('#pane-left [data-zoom-count]').inner_text())
                width_info = stage.evaluate("""el => ({
                    viewport: el.clientWidth,
                    content: el.scrollWidth
                })""")
                self.assertGreater(width_info["content"], width_info["viewport"] + 25,
                                   "Zoomed demo PDF must have a reachable horizontal pan range")
                stage.evaluate("(el) => el.scrollLeft = 0")
                self.assertEqual(0, stage.evaluate("(el) => el.scrollLeft"))
                stage.evaluate("(el) => el.scrollLeft = 9999")
                self.assertGreater(stage.evaluate("(el) => el.scrollLeft"), 25)
                page.locator('#pane-left [data-action="zoom-out"]').click()
                self.assertEqual("150%", page.locator('#pane-left [data-zoom-count]').inner_text())
                self.assert_clean(ext, errors)

    def test_local_pdf_zoom_updates_fragment_without_rebuilding_iframe(self):
        page, ext, errors = self.open_workspace(1024, 768)
        page.locator('#pane-left input[data-pdf-input]').set_input_files({
            "name": "local-only.pdf",
            "mimeType": "application/pdf",
            "buffer": synthetic_pdf(),
        })
        frame = page.locator('#pane-left [data-pdf-iframe]')
        frame.evaluate("(el) => el.dataset.sentinel = 'preserved'")
        source = frame.get_attribute("src")
        self.assertIn("#page=1&zoom=100", source)
        page.locator('#pane-left [data-action="zoom-in"]').click()
        self.assertEqual("preserved", frame.get_attribute("data-sentinel"))
        self.assertEqual(source.split("#")[0] + "#page=1&zoom=110", frame.get_attribute("src"))
        page.locator('#pane-left [data-action="fit-pdf"]').click()
        self.assertEqual("preserved", frame.get_attribute("data-sentinel"))
        self.assertEqual(source, frame.get_attribute("src"))
        self.assert_clean(ext, errors)


    def test_local_pdf_color_toggle_keyboard_focus_and_frame_identity(self):
        page, ext, errors = self.open_workspace(1024, 768)
        page.locator('#pane-left input[data-pdf-input]').set_input_files({
            "name": "local-color-test.pdf",
            "mimeType": "application/pdf",
            "buffer": synthetic_pdf(),
        })
        page.locator('#pane-right select[data-pane="right"]').select_option("pdf")
        before_sources = []
        for side in ("left", "right"):
            frame = page.locator(f'#pane-{side} [data-pdf-iframe]')
            frame.evaluate("(el) => el.dataset.identity = 'pdf-stays-mounted'")
            before_sources.append(frame.get_attribute("src"))
            self.assertTrue(frame.evaluate(
                "(el) => el.classList.contains('original-colors')"
            ))
        toggle = page.locator('#pane-left [data-action="toggle-pdf-colors"]')
        toggle.focus()
        self.assertTrue(toggle.evaluate("(el) => document.activeElement === el"))
        toggle.press("Enter")
        self.assertTrue(toggle.evaluate(
            "(el) => document.activeElement === el"
        ), "Keyboard focus must remain on the toggle after changing native PDF colors")
        self.assertEqual("false", toggle.get_attribute("aria-pressed"))
        for side, src in zip(("left", "right"), before_sources):
            frame = page.locator(f'#pane-{side} [data-pdf-iframe]')
            self.assertEqual("pdf-stays-mounted", frame.get_attribute("data-identity"))
            self.assertEqual(src, frame.get_attribute("src"))
            self.assertFalse(frame.evaluate(
                "(el) => el.classList.contains('original-colors')"
            ))
        toggle.press("Enter")
        self.assertEqual("true", toggle.get_attribute("aria-pressed"))
        self.assertTrue(toggle.evaluate("(el) => document.activeElement === el"))
        self.assert_clean(ext, errors)

    def test_pdf_zoom_limits_disable_only_the_unavailable_action(self):
        page, ext, errors = self.open_workspace(1024, 768)
        page.locator('#pane-right select[data-pane="right"]').select_option("pdf")
        plus = page.locator('#pane-left [data-action="zoom-in"]')
        minus = page.locator('#pane-left [data-action="zoom-out"]')
        self.assertTrue(plus.is_enabled())
        self.assertTrue(minus.is_enabled())
        for _ in range(3):
            minus.click()
        self.assertEqual("70%", page.locator('#pane-left [data-zoom-count]').inner_text())
        self.assertFalse(minus.is_enabled())
        self.assertFalse(page.locator('#pane-right [data-action="zoom-out"]').is_enabled())
        self.assertTrue(plus.is_enabled())
        plus.focus()
        plus.press("Enter")
        self.assertEqual("80%", page.locator('#pane-left [data-zoom-count]').inner_text())
        self.assertTrue(minus.is_enabled())
        for _ in range(8):
            plus.click()
        self.assertEqual("160%", page.locator('#pane-left [data-zoom-count]').inner_text())
        self.assertFalse(plus.is_enabled())
        self.assertFalse(page.locator('#pane-right [data-action="zoom-in"]').is_enabled())
        self.assertTrue(minus.is_enabled())
        page.locator('#pane-left [data-action="fit-pdf"]').click()
        self.assertEqual("100%", page.locator('#pane-left [data-zoom-count]').inner_text())
        self.assertTrue(plus.is_enabled())
        self.assertTrue(minus.is_enabled())
        self.assert_clean(ext, errors)


    def test_local_pdf_page_navigation_preserves_focus_and_iframe(self):
        page, ext, errors = self.open_workspace(1024, 768)
        page.locator('#pane-left input[data-pdf-input]').set_input_files({
            "name": "private-local-test.pdf",
            "mimeType": "application/pdf",
            "buffer": synthetic_pdf(),
        })
        page.locator('#pane-right select[data-pane="right"]').select_option("pdf")
        nodes = {}
        for side in ("left", "right"):
            frame = page.locator(f'#pane-{side} [data-pdf-iframe]')
            frame.evaluate("(el) => el.dataset.identity = 'same-native-frame'")
            nodes[side] = frame.get_attribute("src").split("#")[0]
        next_button = page.locator('#pane-left [data-action="next-page"]')
        next_button.focus()
        next_button.press("Enter")
        self.assertTrue(next_button.evaluate("(el) => document.activeElement === el"))
        for side in ("left", "right"):
            frame = page.locator(f'#pane-{side} [data-pdf-iframe]')
            self.assertEqual("same-native-frame", frame.get_attribute("data-identity"))
            self.assertEqual(nodes[side] + "#page=2&zoom=100", frame.get_attribute("src"))
            self.assertEqual("2", page.locator(f'#pane-{side} [data-page-now]').inner_text())
        prev_button = page.locator('#pane-left [data-action="prev-page"]')
        prev_button.focus()
        prev_button.press("Enter")
        self.assertTrue(prev_button.evaluate("(el) => document.activeElement === el"))
        self.assertEqual("1쪽", page.locator("#globalProgressLabel").inner_text())
        for side in ("left", "right"):
            frame = page.locator(f'#pane-{side} [data-pdf-iframe]')
            self.assertEqual("same-native-frame", frame.get_attribute("data-identity"))
            self.assertEqual(nodes[side] + "#page=1&zoom=100", frame.get_attribute("src"))
        # Reaching a boundary must not remount the native PDF iframe.
        prev_button.press("Enter")
        self.assertTrue(prev_button.evaluate("(el) => document.activeElement === el"))
        self.assertEqual("same-native-frame",
                         page.locator('#pane-left [data-pdf-iframe]').get_attribute("data-identity"))
        self.assert_clean(ext, errors)

    def test_demo_pdf_page_navigation_preserves_zoom_and_toolbar(self):
        page, ext, errors = self.open_workspace(390, 844)
        for _ in range(3):
            page.locator('#pane-left [data-action="zoom-in"]').click()
        stage = page.locator('#pane-left [data-pdf-stage]')
        stage.evaluate("(el) => { el.dataset.identity = 'same-demo-stage'; el.scrollTop = 180; }")
        self.assertGreater(stage.evaluate("(el) => el.scrollTop"), 50)
        next_button = page.locator('#pane-left [data-action="next-page"]')
        next_button.focus()
        next_button.press("Enter")
        self.assertEqual("13", page.locator('#pane-left [data-page-now]').inner_text())
        self.assertEqual("130%", page.locator('#pane-left [data-zoom-count]').inner_text())
        self.assertIn("복소 지수와 위상", page.locator('#pane-left .demo-title').inner_text())
        self.assertEqual("same-demo-stage", stage.get_attribute("data-identity"))
        self.assertTrue(next_button.evaluate("(el) => document.activeElement === el"))
        self.assertEqual(0, stage.evaluate("(el) => el.scrollTop"))
        self.assert_clean(ext, errors)


if __name__ == "__main__":
    unittest.main()
