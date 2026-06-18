"""Browser integration tests using Playwright."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.browser

playwright = pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright


def _click_hotspot(page, src: str) -> None:
    page.evaluate(
        """(src) => {
            const img = document.getElementById('plot_image');
            const box = img.getBoundingClientRect();
            const marker = [...document.querySelectorAll('.hotspot-marker')].find((item) => item.dataset.src === src);
            if (!marker) {
                throw new Error('Hotspot not found: ' + src);
            }
            marker.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        }""",
        src,
    )


@pytest.fixture(scope="module")
def browser_context():
    with sync_playwright() as playwright_instance:
        browser = playwright_instance.chromium.launch(headless=True)
        yield browser
        browser.close()


def test_preview_panel_opens_and_switches(browser_context, preview_html):
    page = browser_context.new_page(viewport={"width": 1400, "height": 900})
    page.goto(preview_html.resolve().as_uri())
    page.wait_for_function("() => document.getElementById('plot_image').clientWidth > 0")

    _click_hotspot(page, "media/a.png")
    page.wait_for_timeout(300)
    assert page.locator("#preview_panel").is_visible()
    assert page.locator("#preview_image").is_visible()
    assert page.evaluate("() => document.getElementById('preview_image').src").endswith("media/a.png")

    _click_hotspot(page, "media/b.png")
    page.wait_for_timeout(300)
    assert page.evaluate("() => document.getElementById('preview_image').src").endswith("media/b.png")

    _click_hotspot(page, "media/clip.mp4")
    page.wait_for_timeout(300)
    assert page.locator("#preview_video").is_visible()
    assert page.evaluate("() => document.getElementById('preview_video').getAttribute('src')").endswith(
        "media/clip.mp4"
    )
    page.close()


def test_close_panel_restores_layout(browser_context, preview_html):
    page = browser_context.new_page(viewport={"width": 1400, "height": 900})
    page.goto(preview_html.resolve().as_uri())
    page.wait_for_function("() => document.getElementById('plot_image').clientWidth > 0")

    assert not page.evaluate("() => document.body.classList.contains('preview-active')")
    _click_hotspot(page, "media/a.png")
    page.wait_for_timeout(300)
    assert page.locator("#preview_panel").is_visible()
    assert page.evaluate("() => document.body.classList.contains('preview-active')")
    panel_width = page.evaluate("() => document.getElementById('preview_panel').clientWidth")
    assert panel_width > 0

    page.click("#preview_close")
    page.wait_for_timeout(300)
    assert not page.locator("#preview_panel").is_visible()
    assert not page.evaluate("() => document.body.classList.contains('preview-active')")
    page.close()


def test_splitter_visible_and_resizes_plot(browser_context, preview_html):
    page = browser_context.new_page(viewport={"width": 1400, "height": 900})
    page.goto(preview_html.resolve().as_uri())
    page.wait_for_function("() => document.getElementById('plot_image').clientWidth > 0")

    _click_hotspot(page, "media/a.png")
    page.wait_for_timeout(300)
    assert page.locator("#layout_splitter").is_visible()

    width_before_drag = page.evaluate("() => document.getElementById('plot_image').clientWidth")
    splitter_box = page.locator("#layout_splitter").bounding_box()
    assert splitter_box is not None

    page.mouse.move(splitter_box["x"] + splitter_box["width"] / 2, splitter_box["y"] + 50)
    page.mouse.down()
    page.mouse.move(splitter_box["x"] - 200, splitter_box["y"] + 50)
    page.mouse.up()
    page.wait_for_timeout(200)

    width_after_drag = page.evaluate("() => document.getElementById('plot_image').clientWidth")
    assert width_after_drag < width_before_drag
    page.close()
