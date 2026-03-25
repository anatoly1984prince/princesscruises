"""
Smoke tests — fast sanity checks that run on every deployment.
If any of these fail, the site is considered broken.
"""
from __future__ import annotations

import allure
import pytest

from pages.home_page import HomePage
from pages.cruise_search_page import CruiseSearchPage
from pages.deals_page import DealsPage
from pages.ships_page import ShipsPage
from pages.login_page import LoginPage
from pages.manage_booking_page import ManageBookingPage


@allure.epic("Princess Cruises - Smoke")
@allure.feature("Core Pages")
@pytest.mark.smoke
class TestSmoke:

    @allure.story("Homepage loads successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_homepage_loads(self, home_page: HomePage):
        home_page.load()
        home_page.assert_loaded()
        assert "Princess" in home_page.get_page_title()

    @allure.story("Homepage returns 200 - no navigation error")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_homepage_no_error_page(self, home_page: HomePage):
        home_page.load()
        assert not home_page.is_visible("h1:has-text('Error')", timeout=2000)
        assert not home_page.is_visible("h1:has-text('404')", timeout=2000)

    @allure.story("Find a Cruise page loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cruise_search_loads(self, cruise_search_page: CruiseSearchPage):
        cruise_search_page.load()
        cruise_search_page.assert_loaded()

    @allure.story("Deals page loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_deals_page_loads(self, deals_page: DealsPage):
        deals_page.load()
        deals_page.assert_loaded()

    @allure.story("Ships page loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ships_page_loads(self, ships_page: ShipsPage):
        ships_page.load()
        ships_page.assert_loaded()

    @allure.story("Login page loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_page_loads(self, login_page: LoginPage):
        login_page.load()
        login_page.assert_loaded()

    @allure.story("Manage Booking page loads")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_manage_booking_loads(self, manage_booking_page: ManageBookingPage):
        manage_booking_page.load()
        manage_booking_page.assert_loaded()

    @allure.story("Homepage header is present")
    def test_header_present(self, home_page: HomePage):
        home_page.load()
        assert home_page.is_visible(home_page.HEADER, timeout=10000)

    @allure.story("Homepage footer is present")
    def test_footer_present(self, home_page: HomePage):
        home_page.load()
        home_page.scroll_to_bottom()
        assert home_page.is_visible(home_page.FOOTER, timeout=10000)

    @allure.story("Site is served over HTTPS")
    def test_https(self, home_page: HomePage):
        home_page.load()
        assert home_page.get_url().startswith("https://")
