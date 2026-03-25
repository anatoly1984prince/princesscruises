"""Regression tests: Cruise Results listing page."""
from __future__ import annotations

import allure
import pytest

from pages.cruise_search_page import CruiseSearchPage
from pages.cruise_results_page import CruiseResultsPage
from pages.cruise_detail_page import CruiseDetailPage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Cruise Results")
@pytest.mark.regression
class TestCruiseResults:

    @allure.story("Results page shows cruise cards")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_results_cards_visible(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        cruise_search_page.load()
        cruise_results_page.assert_cards_visible(min_count=1)

    @allure.story("Each result card has a title")
    def test_cards_have_titles(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        cruise_search_page.load()
        if cruise_results_page.has_results():
            title = cruise_results_page.get_card_title(0)
            assert isinstance(title, str)

    @allure.story("Each result card has a price")
    def test_cards_have_prices(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        cruise_search_page.load()
        if cruise_results_page.has_results():
            price = cruise_results_page.get_card_price(0)
            assert isinstance(price, str)

    @allure.story("Clicking a result navigates to detail page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_click_result_navigates_to_detail(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        cruise_search_page.load()
        if cruise_results_page.has_results():
            original_url = cruise_results_page.get_url()
            cruise_results_page.click_card(0)
            assert cruise_results_page.get_url() != original_url, (
                "URL did not change after clicking a cruise card"
            )

    @allure.story("Multiple cruise cards are shown (>1)")
    def test_multiple_results_shown(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        cruise_search_page.load()
        if cruise_results_page.has_results():
            count = cruise_results_page.get_card_count()
            assert count > 1, f"Expected multiple results, got {count}"

    @allure.story("Results page serves HTTPS")
    def test_results_https(self, cruise_search_page: CruiseSearchPage):
        cruise_search_page.load()
        assert cruise_search_page.get_url().startswith("https://")
