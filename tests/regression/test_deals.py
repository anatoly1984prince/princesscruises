"""Regression tests: Deals & Promotions page."""
from __future__ import annotations

import allure
import pytest

from pages.deals_page import DealsPage
from pages.home_page import HomePage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Deals & Promotions")
@pytest.mark.regression
class TestDealsPage:

    @allure.story("Deals page loads with heading")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_deals_page_loads(self, deals_page: DealsPage):
        deals_page.load()
        deals_page.assert_loaded()

    @allure.story("Deals page shows deal/teaser cards")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_deals_cards_visible(self, deals_page: DealsPage):
        deals_page.load()
        deals_page.assert_deals_visible(min_count=1)

    @allure.story("Deals page URL is correct")
    def test_deals_url(self, deals_page: DealsPage):
        deals_page.load()
        url = deals_page.get_url()
        assert "deal" in url.lower() or "promo" in url.lower(), (
            f"Expected 'deal' or 'promo' in URL, got {url}"
        )

    @allure.story("Deals page has a meta description")
    def test_deals_meta_description(self, deals_page: DealsPage):
        deals_page.load()
        desc = deals_page.get_meta_description()
        assert desc is not None, "Deals page missing meta description tag"

    @allure.story("Deals page title is meaningful")
    def test_deals_page_title(self, deals_page: DealsPage):
        deals_page.load()
        title = deals_page.get_page_title()
        assert title and len(title) > 5, f"Deals page title too short: {title!r}"

    @allure.story("Deals page has links to cruise search")
    def test_cruise_search_links_present(self, deals_page: DealsPage):
        deals_page.load()
        count = deals_page.page.locator("a[href*='cruise-search']").count()
        assert count >= 1, "No cruise-search links found on deals page"

    @allure.story("Deals page accessible via direct navigation")
    def test_deals_accessible_from_nav(self, home_page: HomePage):
        home_page.load()
        home_page.click_deals_nav()
        url = home_page.get_url()
        assert "deal" in url.lower() or "promo" in url.lower(), (
            f"Expected deals URL after nav click, got {url}"
        )

    @allure.story("Multiple deals/teasers are shown")
    def test_multiple_deals_shown(self, deals_page: DealsPage):
        deals_page.load()
        if deals_page.is_visible(deals_page.DEAL_CARDS, timeout=10000):
            count = deals_page.get_deal_count()
            assert count > 1, f"Expected multiple deals, found {count}"
