"""Page Object: Cruise Detail page."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class CruiseDetailPage(BasePage):
    PAGE_TITLE = "h1, [class*='cruise-title'], [class*='voyage-title']"
    ITINERARY = "[class*='itinerary'], section:has-text('Itinerary')"
    PRICE = "[class*='price'], [aria-label*='price' i]"
    BOOK_NOW_BTN = (
        "a:has-text('Book Now'), button:has-text('Book Now'), "
        "a:has-text('Book This Cruise'), a[href*='book']"
    )
    SHIP_NAME = "[class*='ship-name'], [aria-label*='ship' i], a[href*='ship']"
    DEPARTURE_DATE = "[class*='departure'], [class*='sail-date'], [class*='date']"
    DURATION = "[class*='duration'], [class*='nights']"
    INCLUSIONS = "[class*='inclusions'], [class*='amenities'], section:has-text('Includes')"
    CABIN_CATEGORIES = "[class*='cabin'], [class*='stateroom'], section:has-text('Cabin')"
    SHARE_BTN = "button[aria-label*='share' i], a[aria-label*='share' i]"
    BACK_BTN = "a:has-text('Back'), button:has-text('Back'), [aria-label*='back' i]"

    @allure.step("Assert cruise detail page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.PAGE_TITLE, timeout=15000)

    def get_cruise_title(self) -> str:
        return self.get_text(self.PAGE_TITLE)

    def get_price_text(self) -> str:
        if self.is_visible(self.PRICE):
            return self.get_text(self.PRICE)
        return ""

    def get_ship_name(self) -> str:
        if self.is_visible(self.SHIP_NAME):
            return self.get_text(self.SHIP_NAME)
        return ""

    @allure.step("Click Book Now")
    def click_book_now(self) -> None:
        self.click(self.BOOK_NOW_BTN)
        self.wait_for_load_state("domcontentloaded")
