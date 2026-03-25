"""Page Object: Ships & Experience / Fleet page."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class ShipsPage(BasePage):
    PATH = "/ships-and-experience/ships/"

    PAGE_HEADING = "h1, [class*='page-title'], [class*='ships-hero'] h1"
    # Real class on princess.com destination grid
    SHIP_CARDS = (
        "[class*='cmp-destination-grid__card-cta-link'], "
        "[class*='destination-grid__card'], "
        "[class*='ship-card'], [class*='fleet-card']"
    )
    SHIP_NAME = (
        "[class*='cmp-destination-grid__card-cta-link__card'] [class*='title'], "
        "[class*='destination-grid__card'] h2, "
        "[class*='destination-grid__card'] h3"
    )

    def load(self) -> None:
        self.navigate(self.PATH)

    @allure.step("Assert ships page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.PAGE_HEADING, timeout=15000)

    @allure.step("Assert ship cards visible")
    def assert_ships_visible(self, min_count: int = 1) -> None:
        self.wait_for_visible(self.SHIP_CARDS, timeout=20000)
        count = self.count(self.SHIP_CARDS)
        assert count >= min_count, f"Expected >= {min_count} ship cards, found {count}"

    def get_ship_count(self) -> int:
        return self.count(self.SHIP_CARDS)

    def get_ship_names(self) -> list[str]:
        return [
            el.inner_text().strip()
            for el in self.page.locator(self.SHIP_NAME).all()
        ]

    @allure.step("Click ship card at index {index}")
    def click_ship(self, index: int = 0) -> None:
        card = self.page.locator(self.SHIP_CARDS).nth(index)
        # The card element itself may be an <a> tag
        tag = card.evaluate("el => el.tagName.toLowerCase()")
        if tag == "a":
            card.click()
        else:
            card.locator("a").first.click()
        self.wait_for_load_state("domcontentloaded")
