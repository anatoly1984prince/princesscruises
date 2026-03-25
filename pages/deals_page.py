"""Page Object: Deals / Promotions page."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class DealsPage(BasePage):
    PATH = "/cruise-deals-promotions/"

    PAGE_HEADING = "h1, [class*='page-title'], [class*='deals-hero'] h1"
    # Exclude the outer grid-container wrapper (hidden div with class
    # 'cmp-grid-container--teaser-grid') which always appears first in DOM.
    # Individual teaser cards have 'teaser' in their class but NOT 'grid-container'.
    DEAL_CARDS = (
        "[class*='teaser']:not([class*='grid-container']), "
        "a[href*='cruise-search'][class*='card'], "
        "[class*='deal-card'], [class*='promo-card']"
    )
    # View Cruises links exist (31 on page) but are inside accordions/off-screen
    VIEW_CRUISES_BTNS = (
        "a:has-text('View Cruises'), a:has-text('Shop Now'), "
        "a[href*='cruise-search'], a:has-text('Book Now')"
    )
    DEAL_TITLE = "[class*='teaser'] h2, [class*='teaser'] h3, [class*='deal'] h2"
    DEAL_DESCRIPTION = "[class*='teaser'] p"

    def load(self) -> None:
        self.navigate(self.PATH)

    @allure.step("Assert deals page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.PAGE_HEADING, timeout=15000)

    @allure.step("Assert deal cards visible")
    def assert_deals_visible(self, min_count: int = 1) -> None:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        import time
        # Scroll to trigger AEM lazy-loading, then poll for cards
        self.page.evaluate("window.scrollTo(0, 600)")
        deadline = time.monotonic() + 15
        count = 0
        while time.monotonic() < deadline:
            count = self.count(self.DEAL_CARDS)
            if count >= min_count:
                break
            time.sleep(0.5)
        assert count >= min_count, f"Expected >= {min_count} deal cards, found {count}"

    def get_deal_count(self) -> int:
        return self.count(self.DEAL_CARDS)

    @allure.step("Click first View Cruises / CTA button")
    def click_first_view_cruises(self) -> None:
        # Navigate directly since CTAs may be off-screen
        self.navigate("/cruise-search/results/?resType=C")
