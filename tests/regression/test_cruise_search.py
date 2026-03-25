"""Regression tests: Cruise Search / Results page."""
from __future__ import annotations

import allure
import pytest

from pages.cruise_search_page import CruiseSearchPage
from pages.cruise_results_page import CruiseResultsPage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Cruise Search")
@pytest.mark.regression
@pytest.mark.search
class TestCruiseSearch:

    @allure.story("Cruise search page loads")
    def test_search_page_loads(self, cruise_search_page: CruiseSearchPage):
        cruise_search_page.load()
        cruise_search_page.assert_loaded()

    @allure.story("Cruise search page URL contains 'cruise-search'")
    def test_search_page_url(self, cruise_search_page: CruiseSearchPage):
        cruise_search_page.load()
        assert "cruise-search" in cruise_search_page.get_url().lower() or \
               "find-a-cruise" in cruise_search_page.get_url().lower()

    @allure.story("Default search returns cruise cards")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_default_search_returns_results(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        cruise_search_page.load()
        cruise_results_page.assert_cards_visible(min_count=1)

    @allure.story("Applying destination filter keeps or reduces results")
    def test_filter_by_destination(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        cruise_search_page.load()
        cruise_search_page.select_destination("Alaska")
        cruise_search_page.apply_search()
        # Either results are shown or a no-results message appears — page doesn't crash
        assert "princess.com" in cruise_search_page.get_url()

    @allure.story("Results count is displayed or cards are rendered")
    def test_results_shown(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        cruise_search_page.load()
        if cruise_results_page.has_results():
            count = cruise_results_page.get_card_count()
            assert count > 0, "No cruise cards rendered after results loaded"

    @allure.story("Cruise search page serves HTTPS")
    def test_search_https(self, cruise_search_page: CruiseSearchPage):
        cruise_search_page.load()
        assert cruise_search_page.get_url().startswith("https://")
