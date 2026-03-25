"""Page Object: Cruise Search / Results page."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class CruiseSearchPage(BasePage):
    PATH = "/cruise-search/results/?resType=C"

    # Filter selectors — the SPA may render these inside a React component
    DESTINATION_SELECT = (
        "select[name*='destination' i], [aria-label*='destination' i] select, "
        "[class*='destination'] select, select[id*='destination' i]"
    )
    DESTINATION_BTN = (
        "button[aria-label*='destination' i], [class*='destination'] button, "
        "button:has-text('All Destinations'), button:has-text('Destination')"
    )
    DURATION_SELECT = (
        "select[name*='duration' i], [aria-label*='duration' i] select, "
        "select[id*='duration' i]"
    )
    PORT_SELECT = (
        "select[name*='port' i], select[name*='departure' i], "
        "[aria-label*='port' i] select, [aria-label*='departure' i] select"
    )
    SEARCH_BTN = (
        "button[type='submit']:not([class*='site-search']), "
        "button:has-text('Search Cruises'), button:has-text('Find Cruises'), "
        "button:has-text('Apply Filters')"
    )
    CLEAR_BTN = "button:has-text('Clear All'), button:has-text('Reset'), a:has-text('Clear All')"
    NO_RESULTS_MSG = (
        "[class*='no-result'], [class*='empty-state'], "
        "p:has-text('No cruises'), p:has-text('no results')"
    )
    # Page loaded indicator — results or filter container
    FILTER_PANEL = (
        "[class*='product-card'], [class*='filter-panel'], "
        "[class*='search-results'], [class*='refinement'], body"
    )

    def load(self) -> None:
        self.navigate(self.PATH)
        self.wait_for_load_state("networkidle")

    @allure.step("Assert cruise search page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible("body")
        assert "cruise-search" in self.get_url().lower() or "find-a-cruise" in self.get_url().lower(), (
            f"Expected cruise search URL, got {self.get_url()}"
        )

    @allure.step("Select destination: {destination}")
    def select_destination(self, destination: str) -> None:
        if self.is_visible(self.DESTINATION_SELECT, timeout=3000):
            self.select_option(self.DESTINATION_SELECT, destination)
        elif self.is_visible(self.DESTINATION_BTN, timeout=3000):
            self.click(self.DESTINATION_BTN)
            option_sel = f"[role='option']:has-text('{destination}'), li:has-text('{destination}')"
            if self.is_visible(option_sel, timeout=3000):
                self.click(option_sel)

    @allure.step("Select duration: {duration}")
    def select_duration(self, duration: str) -> None:
        if self.is_visible(self.DURATION_SELECT, timeout=3000):
            self.select_option(self.DURATION_SELECT, duration)

    @allure.step("Select departure port: {port}")
    def select_port(self, port: str) -> None:
        if self.is_visible(self.PORT_SELECT, timeout=3000):
            self.select_option(self.PORT_SELECT, port)

    @allure.step("Apply cruise search")
    def apply_search(self) -> None:
        if self.is_visible(self.SEARCH_BTN, timeout=3000):
            self.click(self.SEARCH_BTN)
            self.wait_for_load_state("domcontentloaded")

    @allure.step("Clear all search filters")
    def clear_filters(self) -> None:
        if self.is_visible(self.CLEAR_BTN, timeout=3000):
            self.click(self.CLEAR_BTN)
            self.wait_for_load_state("domcontentloaded")
