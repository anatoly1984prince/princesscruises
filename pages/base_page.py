"""
BasePage — foundation for all Page Object Models.

All shared Playwright interactions, waits, screenshots, and common
overlay dismissals live here so individual page objects stay clean.
"""
from __future__ import annotations

import allure
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config.settings import settings


class BasePage:
    # Selectors for site-wide overlays present on many pages
    COOKIE_BANNER = (
        "[id*='cookie'] button, "
        "[class*='cookie'] button[class*='accept'], "
        "[class*='cookie'] button[class*='close'], "
        "#onetrust-accept-btn-handler, "
        "button[aria-label*='Accept'], "
        "button[aria-label*='cookie' i]"
    )
    CHAT_WIDGET = (
        "[class*='chat'] button[aria-label*='close' i], "
        "[id*='chat'] button[aria-label*='close' i], "
        "[class*='launcher'] button[aria-label*='close' i], "
        "button[aria-label='Close Chat'], "
        "#launcher"
    )
    POPUP_CLOSE = (
        "[class*='modal'] button[aria-label*='close' i], "
        "[class*='overlay'] button[aria-label*='close' i], "
        "[class*='dialog'] button[aria-label*='close' i], "
        "button[data-dismiss='modal']"
    )

    def __init__(self, page: Page) -> None:
        self.page = page
        self.base_url = settings.BASE_URL
        self.page.set_default_timeout(settings.DEFAULT_TIMEOUT)
        self.page.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)

    # ── Navigation ──────────────────────────────────────────────────────────

    def navigate(self, path: str = "/") -> None:
        url = self.base_url + path if path.startswith("/") else path
        self.page.goto(url, wait_until="domcontentloaded")
        self._dismiss_overlays()

    def load(self) -> None:
        """Override in subclasses to navigate to the page's canonical URL."""
        self.navigate("/")

    def get_url(self) -> str:
        return self.page.url

    def wait_for_load_state(self, state: str = "networkidle") -> None:
        try:
            self.page.wait_for_load_state(state, timeout=settings.NAVIGATION_TIMEOUT)
        except PlaywrightTimeoutError:
            pass  # networkidle is best-effort on SPAs

    # ── Overlay Dismissal ───────────────────────────────────────────────────

    def _dismiss_overlays(self) -> None:
        """Silently dismiss cookie banners, chat widgets, and modal popups."""
        for selector in (self.COOKIE_BANNER, self.POPUP_CLOSE):
            self._click_if_visible(selector, timeout=3000)

    def _click_if_visible(self, selector: str, timeout: int = 2000) -> bool:
        try:
            loc = self.page.locator(selector).first
            if loc.is_visible(timeout=timeout):
                loc.click(timeout=timeout)
                return True
        except (PlaywrightTimeoutError, Exception):
            pass
        return False

    # ── Element Interactions ────────────────────────────────────────────────

    def click(self, selector: str, timeout: int | None = None) -> None:
        self.page.locator(selector).first.click(
            timeout=timeout or settings.DEFAULT_TIMEOUT
        )

    def fill(self, selector: str, value: str) -> None:
        loc = self.page.locator(selector).first
        loc.click()
        loc.fill(value)

    def type_slowly(self, selector: str, text: str, delay: int = 100) -> None:
        self.page.locator(selector).first.type(text, delay=delay)

    def select_option(self, selector: str, value: str) -> None:
        self.page.locator(selector).first.select_option(value)

    def hover(self, selector: str) -> None:
        self.page.locator(selector).first.hover()

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).first.inner_text().strip()

    def get_attribute(self, selector: str, attribute: str) -> str | None:
        return self.page.locator(selector).first.get_attribute(attribute)

    def count(self, selector: str) -> int:
        return self.page.locator(selector).count()

    # ── Visibility / State ──────────────────────────────────────────────────

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        try:
            return self.page.locator(selector).first.is_visible(timeout=timeout)
        except (PlaywrightTimeoutError, Exception):
            return False

    def wait_for_visible(self, selector: str, timeout: int | None = None) -> None:
        self.page.locator(selector).first.wait_for(
            state="visible", timeout=timeout or settings.DEFAULT_TIMEOUT
        )

    def wait_for_hidden(self, selector: str, timeout: int | None = None) -> None:
        self.page.locator(selector).first.wait_for(
            state="hidden", timeout=timeout or settings.DEFAULT_TIMEOUT
        )

    # ── Assertions ──────────────────────────────────────────────────────────

    def assert_visible(self, selector: str, timeout: int | None = None) -> None:
        self.wait_for_visible(selector, timeout)
        assert self.page.locator(selector).first.is_visible(), (
            f"Expected element to be visible: {selector}"
        )

    def assert_text_contains(self, selector: str, text: str) -> None:
        actual = self.get_text(selector)
        assert text.lower() in actual.lower(), (
            f"Expected text {text!r} in element {selector!r}, got {actual!r}"
        )

    def assert_url_contains(self, fragment: str) -> None:
        assert fragment.lower() in self.get_url().lower(), (
            f"Expected URL to contain {fragment!r}, got {self.get_url()!r}"
        )

    def assert_loaded(self) -> None:
        """Basic check that the page is responsive."""
        self.assert_visible("body")

    # ── Page Metadata ────────────────────────────────────────────────────────

    def get_page_title(self) -> str:
        return self.page.title()

    def get_meta_description(self) -> str | None:
        return self.page.locator("meta[name='description']").get_attribute("content")

    def count_headings(self, level: int) -> int:
        return self.page.locator(f"h{level}").count()

    def get_all_images_without_alt(self) -> list[str]:
        images = self.page.locator("img").all()
        missing: list[str] = []
        for img in images:
            alt = img.get_attribute("alt")
            src = img.get_attribute("src") or "(no src)"
            if alt is None or alt.strip() == "":
                missing.append(src)
        return missing

    # ── Scrolling ────────────────────────────────────────────────────────────

    def scroll_to_bottom(self) -> None:
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    def scroll_to_element(self, selector: str) -> None:
        self.page.locator(selector).first.scroll_into_view_if_needed()

    # ── Screenshots ──────────────────────────────────────────────────────────

    @allure.step("Take screenshot: {name}")
    def take_screenshot(self, name: str) -> None:
        screenshot = self.page.screenshot(full_page=False)
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
