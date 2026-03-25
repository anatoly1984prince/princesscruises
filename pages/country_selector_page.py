"""Page Object: Country / Region selector modal."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class CountrySelectorPage(BasePage):
    SELECTOR_TRIGGER = (
        "[aria-label*='country' i], [aria-label*='region' i], "
        "button[class*='country'], button[class*='region'], "
        "[class*='locale'] button, [class*='country-select']"
    )
    SELECTOR_MODAL = (
        "[class*='country-modal'], [class*='region-modal'], "
        "[role='dialog'][class*='country'], "
        "[class*='locale-modal']"
    )
    COUNTRY_OPTION = (
        "[class*='country-option'], [class*='country-item'], "
        "[role='option'], [role='listitem']"
    )
    CONFIRM_BTN = (
        "button:has-text('Confirm'), button:has-text('Continue'), "
        "button:has-text('Save'), button[type='submit']"
    )
    CLOSE_BTN = (
        "[class*='modal'] button[aria-label*='close' i], "
        "[role='dialog'] button[aria-label*='close' i], "
        "button[aria-label='Close']"
    )

    @allure.step("Open country selector")
    def open(self) -> None:
        self.click(self.SELECTOR_TRIGGER)
        self.wait_for_visible(self.SELECTOR_MODAL, timeout=5000)

    @allure.step("Assert country selector modal open")
    def assert_modal_open(self) -> None:
        self.assert_visible(self.SELECTOR_MODAL)

    @allure.step("Assert countries are listed")
    def assert_countries_listed(self) -> None:
        count = self.count(self.COUNTRY_OPTION)
        assert count >= 1, f"Expected country options in selector, found {count}"

    @allure.step("Select country: {country_name}")
    def select_country(self, country_name: str) -> None:
        option_sel = (
            f"[class*='country-option']:has-text('{country_name}'), "
            f"[role='option']:has-text('{country_name}'), "
            f"li:has-text('{country_name}')"
        )
        if self.is_visible(option_sel, timeout=3000):
            self.click(option_sel)

    @allure.step("Confirm country selection")
    def confirm(self) -> None:
        if self.is_visible(self.CONFIRM_BTN, timeout=2000):
            self.click(self.CONFIRM_BTN)
            self.wait_for_load_state("domcontentloaded")

    @allure.step("Close country selector")
    def close(self) -> None:
        if self.is_visible(self.CLOSE_BTN, timeout=2000):
            self.click(self.CLOSE_BTN)
        else:
            self.page.keyboard.press("Escape")
