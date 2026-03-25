"""Regression tests: Ships & Fleet page."""
from __future__ import annotations

import allure
import pytest

from pages.ships_page import ShipsPage
from pages.home_page import HomePage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Ships & Fleet")
@pytest.mark.regression
class TestShipsPage:

    @allure.story("Ships page loads with heading")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ships_page_loads(self, ships_page: ShipsPage):
        ships_page.load()
        ships_page.assert_loaded()

    @allure.story("Ships page shows ship cards")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ship_cards_visible(self, ships_page: ShipsPage):
        ships_page.load()
        ships_page.assert_ships_visible(min_count=1)

    @allure.story("Multiple ships listed")
    def test_multiple_ships_listed(self, ships_page: ShipsPage):
        ships_page.load()
        if ships_page.is_visible(ships_page.SHIP_CARDS, timeout=10000):
            count = ships_page.get_ship_count()
            assert count >= 5, f"Expected at least 5 ships, found {count}"

    @allure.story("Ships page URL is correct")
    def test_ships_url(self, ships_page: ShipsPage):
        ships_page.load()
        assert "ship" in ships_page.get_url().lower(), (
            f"Expected 'ship' in URL, got {ships_page.get_url()}"
        )

    @allure.story("Ships page title is meaningful")
    def test_ships_page_title(self, ships_page: ShipsPage):
        ships_page.load()
        title = ships_page.get_page_title()
        assert title and len(title) > 5, f"Ships page title too short: {title!r}"

    @allure.story("Clicking a ship card navigates to ship detail")
    def test_click_ship_navigates(self, ships_page: ShipsPage):
        ships_page.load()
        if ships_page.is_visible(ships_page.SHIP_CARDS, timeout=10000):
            original_url = ships_page.get_url()
            ships_page.click_ship(0)
            assert ships_page.get_url() != original_url, (
                "URL did not change after clicking a ship card"
            )

    @allure.story("Ships page accessible via direct navigation")
    def test_ships_nav_accessible(self, home_page: HomePage):
        home_page.load()
        home_page.click_ships_nav()
        assert "ship" in home_page.get_url().lower()

    @allure.story("Ships page has meta description")
    def test_ships_meta_description(self, ships_page: ShipsPage):
        ships_page.load()
        desc = ships_page.get_meta_description()
        assert desc is not None, "Ships page missing meta description"
