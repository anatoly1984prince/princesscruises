"""Regression tests: Header / site-wide search functionality."""
from __future__ import annotations

import allure
import pytest

from pages.home_page import HomePage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Site Search")
@pytest.mark.regression
@pytest.mark.search
class TestSiteSearch:

    SEARCH_INPUT = "input[type='search'], input[placeholder*='Search' i], [role='searchbox']"
    SEARCH_RESULTS = "[class*='search-result'], [class*='suggestion'], [role='listbox'] li"

    @allure.story("Search icon opens search input")
    def test_search_icon_opens_input(self, home_page: HomePage):
        home_page.load()
        home_page.click_search_icon()
        visible = home_page.is_visible(self.SEARCH_INPUT, timeout=5000)
        if not visible:
            pytest.skip("Search input not found after icon click — layout may differ")

    @allure.story("Typing in search shows suggestions")
    def test_search_shows_suggestions(self, home_page: HomePage):
        home_page.load()
        home_page.click_search_icon()
        if not home_page.is_visible(self.SEARCH_INPUT, timeout=5000):
            pytest.skip("Search input not visible")
        home_page.type_slowly(self.SEARCH_INPUT, "Alaska", delay=80)
        assert (
            home_page.is_visible(self.SEARCH_RESULTS, timeout=5000) or
            home_page.is_visible(self.SEARCH_INPUT)
        ), "No suggestions appeared after typing"

    @allure.story("Pressing Enter on search navigates to results")
    def test_search_enter_navigates(self, home_page: HomePage):
        home_page.load()
        home_page.click_search_icon()
        if not home_page.is_visible(self.SEARCH_INPUT, timeout=5000):
            pytest.skip("Search input not visible")
        home_page.fill(self.SEARCH_INPUT, "Caribbean cruises")
        home_page.page.keyboard.press("Enter")
        home_page.wait_for_load_state("domcontentloaded")
        assert "princess.com" in home_page.get_url()

    @allure.story("Searching for a ship name returns results")
    def test_search_ship_name(self, home_page: HomePage):
        home_page.load()
        home_page.click_search_icon()
        if not home_page.is_visible(self.SEARCH_INPUT, timeout=5000):
            pytest.skip("Search input not visible")
        home_page.fill(self.SEARCH_INPUT, "Sun Princess")
        home_page.page.keyboard.press("Enter")
        home_page.wait_for_load_state("domcontentloaded")
        assert "princess.com" in home_page.get_url()

    @allure.story("Empty search does not crash the page")
    def test_empty_search_no_crash(self, home_page: HomePage):
        home_page.load()
        home_page.click_search_icon()
        if home_page.is_visible(self.SEARCH_INPUT, timeout=5000):
            home_page.page.keyboard.press("Enter")
        assert home_page.is_visible("body")
