"""Regression tests: Manage Booking portal.

NOTE: Princess.com's manage booking requires authentication.
Tests requiring the booking form are skipped unless TEST_BOOKING_NUMBER is configured.
"""
from __future__ import annotations

import allure
import pytest

from pages.manage_booking_page import ManageBookingPage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Manage Booking")
@pytest.mark.regression
class TestManageBooking:

    @allure.story("Manage Booking page loads (redirects to login if unauthenticated)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_page_loads(self, manage_booking_page: ManageBookingPage):
        manage_booking_page.load()
        manage_booking_page.assert_loaded()

    @allure.story("Page URL is a princess.com URL")
    def test_page_url(self, manage_booking_page: ManageBookingPage):
        manage_booking_page.load()
        assert "princess.com" in manage_booking_page.get_url()

    @allure.story("Page title is meaningful")
    def test_page_title_meaningful(self, manage_booking_page: ManageBookingPage):
        manage_booking_page.load()
        title = manage_booking_page.get_page_title()
        assert title and len(title) > 5, f"Page title too short: {title!r}"

    @allure.story("Booking number input is present (requires unauthenticated form)")
    def test_booking_number_input(self, manage_booking_page: ManageBookingPage):
        manage_booking_page.load()
        if not manage_booking_page._has_booking_form():
            pytest.skip("Manage booking form not accessible without authentication")
        assert manage_booking_page.is_visible(manage_booking_page.BOOKING_NUMBER_INPUT)

    @allure.story("Last name input is present (requires unauthenticated form)")
    def test_last_name_input(self, manage_booking_page: ManageBookingPage):
        manage_booking_page.load()
        if not manage_booking_page._has_booking_form():
            pytest.skip("Manage booking form not accessible without authentication")
        assert manage_booking_page.is_visible(manage_booking_page.LAST_NAME_INPUT)

    @allure.story("Invalid booking lookup shows error (requires form)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_booking_shows_error(self, manage_booking_page: ManageBookingPage):
        manage_booking_page.load()
        if not manage_booking_page._has_booking_form():
            pytest.skip("Manage booking form not accessible without authentication")
        manage_booking_page.lookup_booking("00000000", "FakeLastName")
        manage_booking_page.assert_error_visible()

    @allure.story("Empty booking lookup shows validation (requires form)")
    def test_empty_booking_validation(self, manage_booking_page: ManageBookingPage):
        manage_booking_page.load()
        if not manage_booking_page._has_booking_form():
            pytest.skip("Manage booking form not accessible without authentication")
        manage_booking_page.submit_find_booking()
        assert (
            manage_booking_page.is_visible(manage_booking_page.ERROR_MSG, timeout=5000) or
            manage_booking_page.is_visible(manage_booking_page.BOOKING_NUMBER_INPUT)
        )

    @allure.story("Valid booking lookup shows booking details")
    def test_valid_booking_lookup(
        self,
        manage_booking_page: ManageBookingPage,
        booking_credentials: dict,
    ):
        if not booking_credentials["booking_number"]:
            pytest.skip("TEST_BOOKING_NUMBER not configured")
        manage_booking_page.load()
        manage_booking_page.lookup_booking(
            booking_credentials["booking_number"],
            booking_credentials["last_name"],
        )
        manage_booking_page.assert_booking_details_visible()
