"""Page Object: Manage Booking portal.

NOTE: Princess.com's manage booking requires authentication.
The public-facing /manage-booking/ redirects to a 404.
Authenticated booking management lives at book.princess.com.
Tests that require the form inputs are skipped unless credentials are provided.
"""
from __future__ import annotations

import allure
import pytest
from pages.base_page import BasePage


class ManageBookingPage(BasePage):
    # Unauthenticated entry point — will redirect to login
    PATH = "/my-princess/account-login/"

    PAGE_HEADING = "h1, [class*='page-title'], [class*='manage-heading'], [class*='account-login']"
    BOOKING_NUMBER_INPUT = (
        "input[name*='booking' i], input[placeholder*='booking' i], "
        "input[id*='booking' i], input[aria-label*='booking number' i], "
        "input[name='reservationNumber']"
    )
    LAST_NAME_INPUT = (
        "input[name*='lastName' i], input[name*='last' i], "
        "input[placeholder*='Last Name' i], input[id*='last' i]"
    )
    FIND_BOOKING_BTN = (
        "button[type='submit']:not([class*='site-search']), "
        "button:has-text('Find My Booking'), button:has-text('Look Up'), "
        "button:has-text('Find Booking')"
    )
    ERROR_MSG = "[class*='error'], [role='alert'], [class*='alert'], [aria-live='polite']"
    BOOKING_DETAILS = "[class*='booking-detail'], [class*='reservation'], h2:has-text('Booking')"

    def load(self) -> None:
        self.navigate(self.PATH)

    @allure.step("Assert manage booking page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible("body")
        assert "princess.com" in self.get_url()

    def _has_booking_form(self) -> bool:
        return self.is_visible(self.BOOKING_NUMBER_INPUT, timeout=5000)

    @allure.step("Look up booking number={booking_number}")
    def lookup_booking(self, booking_number: str, last_name: str) -> None:
        if not self._has_booking_form():
            pytest.skip("Manage booking form not accessible without authentication")
        self.fill(self.BOOKING_NUMBER_INPUT, booking_number)
        if self.is_visible(self.LAST_NAME_INPUT):
            self.fill(self.LAST_NAME_INPUT, last_name)
        self.submit_find_booking()

    @allure.step("Submit find booking form")
    def submit_find_booking(self) -> None:
        if self.is_visible(self.FIND_BOOKING_BTN, timeout=3000):
            self.click(self.FIND_BOOKING_BTN)
            self.wait_for_load_state("domcontentloaded")

    @allure.step("Assert error message visible")
    def assert_error_visible(self) -> None:
        assert self.is_visible(self.ERROR_MSG, timeout=8000), (
            "Expected error message after invalid booking lookup"
        )

    @allure.step("Assert booking details visible")
    def assert_booking_details_visible(self) -> None:
        self.assert_visible(self.BOOKING_DETAILS, timeout=10000)
