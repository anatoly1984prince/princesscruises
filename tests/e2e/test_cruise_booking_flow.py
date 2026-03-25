"""E2E tests: Cruise discovery flow — Homepage → Search → Results → Detail."""
from __future__ import annotations

import allure
import pytest

from pages.home_page import HomePage
from pages.cruise_search_page import CruiseSearchPage
from pages.cruise_results_page import CruiseResultsPage
from pages.cruise_detail_page import CruiseDetailPage
from pages.deals_page import DealsPage


@allure.epic("Princess Cruises - E2E")
@allure.feature("Cruise Discovery Flow")
@pytest.mark.e2e
@pytest.mark.slow
class TestCruiseDiscoveryFlow:

    @allure.story("User discovers a cruise from homepage to detail page")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_homepage_to_cruise_detail(
        self,
        home_page: HomePage,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
    ):
        with allure.step("1. Load homepage"):
            home_page.load()
            home_page.assert_loaded()

        with allure.step("2. Click Find a Cruise"):
            home_page.click_find_a_cruise()
            cruise_search_page.wait_for_load_state("domcontentloaded")

        with allure.step("3. Results are shown"):
            cruise_results_page.assert_cards_visible(min_count=1)
            count = cruise_results_page.get_card_count()
            allure.attach(
                f"Cruise results shown: {count}",
                name="results_count",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("4. Click first cruise card"):
            cruise_results_page.click_card(0)

        with allure.step("5. Detail page is loaded"):
            cruise_detail_page.assert_visible(cruise_detail_page.PAGE_TITLE, timeout=15000)
            title = cruise_detail_page.get_cruise_title()
            assert title, "Cruise detail title is empty"
            cruise_detail_page.take_screenshot("cruise_detail")

        with allure.step("6. Book Now button is present"):
            assert cruise_detail_page.is_visible(cruise_detail_page.BOOK_NOW_BTN, timeout=8000)

    @allure.story("User filters cruises by destination")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_destination_filter_flow(
        self,
        home_page: HomePage,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        with allure.step("1. Navigate to Find a Cruise"):
            home_page.load()
            home_page.click_find_a_cruise()

        with allure.step("2. Apply Alaska filter"):
            cruise_search_page.select_destination("Alaska")
            cruise_search_page.apply_search()

        with allure.step("3. Results or no-results message shown"):
            assert (
                cruise_results_page.has_results() or
                cruise_search_page.is_visible(cruise_search_page.NO_RESULTS_MSG, timeout=5000)
            ), "Neither results nor no-results message found"

        with allure.step("4. Clear filters and verify all results return"):
            cruise_search_page.clear_filters()
            cruise_results_page.assert_cards_visible(min_count=1)

    @allure.story("User browses deals then views cruises")
    def test_deals_to_cruises_flow(
        self,
        home_page: HomePage,
        deals_page: DealsPage,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
    ):
        with allure.step("1. Load homepage"):
            home_page.load()

        with allure.step("2. Navigate to Deals"):
            home_page.click_deals_nav()
            deals_page.assert_loaded()
            deals_page.take_screenshot("deals_page")

        with allure.step("3. Click View Cruises CTA"):
            if not deals_page.is_visible(deals_page.VIEW_CRUISES_BTNS, timeout=5000):
                pytest.skip("No View Cruises button found on deals page")
            deals_page.click_first_view_cruises()

        with allure.step("4. Results page shows cruises"):
            cruise_results_page.assert_cards_visible(min_count=1)
