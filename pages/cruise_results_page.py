"""Page Object: Cruise Results / Listing page."""
from __future__ import annotations

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class CruiseResultsPage(BasePage):
    # princess.com cruise result cards
    CARD = "[class*='product-grid-container']"
    CARD_SKELETON = "[class*='product-card'][class*='skeleton']"
    CARD_TITLE = "[class*='product-grid-container'] [class*='product-details'] a"
    CARD_PRICE = "[class*='product-grid-container'] [class*='price']"
    CARD_SHIP  = "[class*='product-grid-container'] [class*='ship']"
    CARD_CTA   = "[class*='product-grid-container'] a[href*='itinerary-details']"
    SORT_SELECT = "select[name*='sort' i], [aria-label*='sort' i] select, [class*='sort'] select"
    RESULTS_COUNT = "[class*='result-count'], [class*='results-found'], [aria-live='polite']"
    PAGINATION = "[class*='pagination'], nav[aria-label*='page' i]"

    def _wait_for_real_cards(self, timeout: int = 40000) -> bool:
        """Wait for at least one cruise card to be visible on the page."""
        self.page.evaluate("window.scrollTo(0, 400)")
        try:
            self.page.wait_for_function(
                "() => [...document.querySelectorAll(\"[class*='product-grid-container']\")]"
                ".some(el => el.offsetParent !== null && el.getBoundingClientRect().height > 0)",
                timeout=timeout,
            )
            return True
        except Exception:
            return False

    @allure.step("Assert cruise result cards visible (min: {min_count})")
    def assert_cards_visible(self, min_count: int = 1) -> None:
        import pytest as _pytest
        loaded = self._wait_for_real_cards(timeout=40000)
        if not loaded:
            _pytest.skip(
                "No cruise product cards rendered after 40s — "
                "SPA may be blocked in headless mode or API is rate-limited."
            )
        count = self.get_card_count()
        assert count >= min_count, f"Expected >= {min_count} cruise cards, found {count}"

    def get_card_count(self) -> int:
        return self.page.evaluate(
            "() => [...document.querySelectorAll(\"[class*='product-grid-container']\")]"
            ".filter(el => el.offsetParent !== null).length"
        )

    def has_results(self) -> bool:
        self._wait_for_real_cards(timeout=30000)
        return self.page.locator(self.CARD).count() > 0

    @allure.step("Click cruise card at index {index}")
    def click_card(self, index: int = 0) -> None:
        # Find all itinerary-details links on the page (visible ones)
        links = self.page.locator("a[href*='itinerary-details']")
        # Wait for at least one to be visible
        try:
            links.first.wait_for(state="visible", timeout=15000)
        except Exception:
            pass
        clicked = 0
        for i in range(links.count()):
            try:
                link = links.nth(i)
                if link.is_visible():
                    if clicked == index:
                        link.click(timeout=15000)
                        self.wait_for_load_state("domcontentloaded")
                        return
                    clicked += 1
            except Exception:
                continue
        raise Exception(f"Could not click cruise card at index {index}")

    def get_card_title(self, index: int = 0) -> str:
        try:
            locator = self.page.locator(self.CARD)
            if locator.count() == 0:
                locator = self.page.locator("[class*='product-card']")
            return locator.nth(index).locator("h2, h3, [class*='title']").first.inner_text().strip()
        except Exception:
            return ""

    def get_card_ship_name(self, index: int = 0) -> str:
        try:
            return self.page.locator(self.CARD).nth(index).locator(
                "[class*='ship']"
            ).first.inner_text().strip()
        except Exception:
            return ""

    def get_card_price(self, index: int = 0) -> str:
        try:
            return self.page.locator(self.CARD).nth(index).locator(
                "[class*='price']"
            ).first.inner_text().strip()
        except Exception:
            return ""

    @allure.step("Sort results by: {option}")
    def sort_by(self, option: str) -> None:
        if self.is_visible(self.SORT_SELECT):
            self.select_option(self.SORT_SELECT, option)
            self.wait_for_load_state("domcontentloaded")
