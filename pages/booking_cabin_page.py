"""Page Object: Booking — Cabin/Stateroom Selection step."""
from __future__ import annotations

import allure
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


# Cabin categories offered on princess.com
CABIN_TYPES = ["Interior", "Oceanview", "Balcony", "Mini-Suite", "Suite"]
ACCESSIBLE_CABIN_TYPES = [
    "Accessible Interior",
    "Accessible Oceanview",
    "Accessible Balcony",
    "Accessible Suite",
]


class BookingCabinPage(BasePage):
    """Stateroom/cabin selection step of the booking wizard."""

    # ── Step indicator ──────────────────────────────────────────────────────
    STEP_INDICATOR = (
        "[class*='booking-step'], [class*='step-indicator'], "
        "[class*='wizard-step'], [aria-label*='step' i]"
    )
    PAGE_HEADING = (
        "h1, h2, [class*='booking-header'], [class*='stateroom-header'], "
        "[class*='cabin-select'] h1, [class*='step-title']"
    )

    # ── Cabin category tabs / filter buttons ────────────────────────────────
    CABIN_TAB_INTERIOR = (
        "button:has-text('Interior'), [data-category='interior'], "
        "[aria-label*='Interior'], [class*='cabin-tab']:has-text('Interior')"
    )
    CABIN_TAB_OCEANVIEW = (
        "button:has-text('Ocean View'), button:has-text('Oceanview'), "
        "[data-category='oceanview'], [class*='cabin-tab']:has-text('Ocean')"
    )
    CABIN_TAB_BALCONY = (
        "button:has-text('Balcony'), [data-category='balcony'], "
        "[class*='cabin-tab']:has-text('Balcony')"
    )
    CABIN_TAB_MINI_SUITE = (
        "button:has-text('Mini-Suite'), button:has-text('Mini Suite'), "
        "[data-category='mini-suite'], [class*='cabin-tab']:has-text('Mini')"
    )
    CABIN_TAB_SUITE = (
        "button:has-text('Suite'), [data-category='suite'], "
        "[class*='cabin-tab']:has-text('Suite')"
    )

    # ── Accessible cabin controls ────────────────────────────────────────────
    ACCESSIBLE_FILTER = (
        "input[type='checkbox'][aria-label*='ccessib' i], "
        "input[type='checkbox'][id*='accessible' i], "
        "button:has-text('Accessible'), [class*='accessible-filter'], "
        "label:has-text('Accessible') input[type='checkbox']"
    )
    ACCESSIBLE_BADGE = (
        "[class*='accessible'], [aria-label*='accessible' i], "
        "[class*='wheelchair'], [aria-label*='wheelchair' i], "
        "[class*='mobility'], img[alt*='ccessib' i]"
    )

    # ── Cabin cards / results ───────────────────────────────────────────────
    CABIN_CARDS = (
        "[class*='stateroom-card'], [class*='cabin-card'], "
        "[class*='category-card'], [class*='room-card'], "
        "[class*='stateroom-result'], [class*='booking-card']"
    )
    CABIN_PRICE = (
        "[class*='stateroom-card'] [class*='price'], "
        "[class*='cabin-card'] [class*='price'], "
        "[class*='category-card'] [class*='price'], "
        "[class*='per-person'], [class*='from-price']"
    )
    SELECT_CABIN_BTN = (
        "[class*='stateroom-card'] button:has-text('Select'), "
        "[class*='cabin-card'] button:has-text('Select'), "
        "[class*='category-card'] button:has-text('Select'), "
        "[class*='stateroom-card'] a:has-text('Select'), "
        "button[class*='select-cabin'], button[class*='choose']"
    )

    # ── Guest count ─────────────────────────────────────────────────────────
    GUESTS_SELECTOR = (
        "select[name*='guest' i], select[aria-label*='guest' i], "
        "input[name*='guest' i], [class*='guest-count'] select, "
        "[class*='occupancy'] select"
    )
    GUESTS_MINUS = "button[aria-label*='decrease' i], button[aria-label*='remove guest' i]"
    GUESTS_PLUS = "button[aria-label*='increase' i], button[aria-label*='add guest' i]"

    # ── Navigation ──────────────────────────────────────────────────────────
    CONTINUE_BTN = (
        "button:has-text('Continue'), button:has-text('Next'), "
        "a:has-text('Continue'), button[class*='continue'], "
        "button[class*='next-step']"
    )
    BACK_BTN = "button:has-text('Back'), a:has-text('Back'), [aria-label*='back' i]"

    # ── Pricing summary ─────────────────────────────────────────────────────
    PRICE_SUMMARY = (
        "[class*='price-summary'], [class*='booking-summary'], "
        "[class*='total-price'], [aria-label*='total' i]"
    )

    # ── Page-load detection ─────────────────────────────────────────────────

    def is_on_cabin_page(self) -> bool:
        url = self.get_url().lower()
        # Exclude guest-count page which contains 'stateroom' as a query param
        if "guest-count" in url:
            return False
        return any(k in url for k in ["/stateroom", "/cabin", "book/", "booking/", "select-room"])

    def wait_for_cabin_page(self, timeout: int = 20000) -> bool:
        try:
            self.page.wait_for_url("**/book/**", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            pass
        try:
            self.page.wait_for_url("**/stateroom/**", timeout=3000)
            return True
        except PlaywrightTimeoutError:
            pass
        return self.is_on_cabin_page()

    # ── Assertions ──────────────────────────────────────────────────────────

    @allure.step("Assert cabin selection page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.PAGE_HEADING, timeout=20000)

    @allure.step("Assert cabin cards visible (min: {min_count})")
    def assert_cabin_cards_visible(self, min_count: int = 1) -> None:
        self.page.locator(self.CABIN_CARDS).first.wait_for(state="visible", timeout=20000)
        count = self.count(self.CABIN_CARDS)
        assert count >= min_count, f"Expected >= {min_count} cabin cards, found {count}"

    # ── Actions ─────────────────────────────────────────────────────────────

    @allure.step("Select cabin category tab: {category}")
    def select_cabin_category(self, category: str) -> None:
        """Click the tab for a cabin category (Interior/Oceanview/Balcony/etc.)."""
        tab_map = {
            "interior": self.CABIN_TAB_INTERIOR,
            "ocean view": self.CABIN_TAB_OCEANVIEW,
            "oceanview": self.CABIN_TAB_OCEANVIEW,
            "balcony": self.CABIN_TAB_BALCONY,
            "mini-suite": self.CABIN_TAB_MINI_SUITE,
            "mini suite": self.CABIN_TAB_MINI_SUITE,
            "suite": self.CABIN_TAB_SUITE,
        }
        selector = tab_map.get(category.lower())
        if selector and self.is_visible(selector, timeout=5000):
            self.click(selector)

    @allure.step("Toggle accessible cabin filter")
    def toggle_accessible_filter(self) -> None:
        if self.is_visible(self.ACCESSIBLE_FILTER, timeout=5000):
            self.click(self.ACCESSIBLE_FILTER)

    @allure.step("Select first available cabin")
    def select_first_cabin(self) -> bool:
        if self.is_visible(self.SELECT_CABIN_BTN, timeout=10000):
            self.click(self.SELECT_CABIN_BTN)
            self.wait_for_load_state("domcontentloaded")
            return True
        return False

    def get_cabin_count(self) -> int:
        return self.count(self.CABIN_CARDS)

    def get_first_cabin_price(self) -> str:
        if self.is_visible(self.CABIN_PRICE, timeout=5000):
            return self.get_text(self.CABIN_PRICE)
        return ""

    def has_accessible_cabins(self) -> bool:
        return self.count(self.ACCESSIBLE_BADGE) > 0

    @allure.step("Click Continue to next booking step")
    def continue_to_next_step(self) -> bool:
        if self.is_visible(self.CONTINUE_BTN, timeout=5000):
            self.click(self.CONTINUE_BTN)
            self.wait_for_load_state("domcontentloaded")
            return True
        return False
