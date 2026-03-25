"""Regression tests: Homepage."""
from __future__ import annotations

import allure
import pytest

from pages.home_page import HomePage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Homepage")
@pytest.mark.regression
class TestHomepage:

    @allure.story("Homepage has correct page title")
    def test_page_title(self, home_page: HomePage):
        home_page.load()
        title = home_page.get_page_title()
        assert "Princess" in title, f"Expected 'Princess' in title, got: {title!r}"

    @allure.story("Header / global nav component is present")
    def test_header_present(self, home_page: HomePage):
        home_page.load()
        # The header is a web component (pcl-global-header) or standard header tag
        assert home_page.is_visible(home_page.HEADER, timeout=10000), (
            "No header element found on homepage"
        )

    @allure.story("Navigation links exist in DOM (href check)")
    @pytest.mark.parametrize("href_fragment,label", [
        ("cruise-destinations", "Destinations"),
        ("cruise-deals-promotions", "Deals"),
    ])
    def test_nav_links_in_dom(self, home_page: HomePage, href_fragment: str, label: str):
        home_page.load()
        count = home_page.page.locator(f"a[href*='{href_fragment}']").count()
        assert count >= 1, f"No links containing '{href_fragment}' found for nav '{label}'"

    @allure.story("Login / account link exists in DOM")
    def test_login_link_in_dom(self, home_page: HomePage):
        home_page.load()
        count = home_page.page.locator(home_page.LOGIN_BTN).count()
        assert count >= 1, "No login / account link found in DOM"

    @allure.story("Find a Cruise link exists in DOM")
    def test_find_cruise_link_in_dom(self, home_page: HomePage):
        home_page.load()
        count = home_page.page.locator(home_page.FIND_CRUISE_BTN).count()
        assert count >= 1, "No Find a Cruise / Search Cruises link found in DOM"

    @allure.story("Hero / promo banner is visible")
    def test_hero_section_visible(self, home_page: HomePage):
        home_page.load()
        # Check each candidate independently — compound selector + .first can
        # hit a hidden element that appears first in DOM order
        visible = (
            home_page.is_visible("[class*='promo-banner']", timeout=10000) or
            home_page.is_visible("[class*='ve-hero-banner']", timeout=3000) or
            home_page.is_visible("[class*='cmp-ve-hero-banner']", timeout=3000)
        )
        assert visible, "No hero / promo banner found visible on homepage"

    @allure.story("Footer is present")
    def test_footer_present(self, home_page: HomePage):
        home_page.load()
        home_page.scroll_to_bottom()
        assert home_page.is_visible(home_page.FOOTER, timeout=10000)

    @allure.story("Homepage has a meta description")
    def test_meta_description(self, home_page: HomePage):
        home_page.load()
        desc = home_page.get_meta_description()
        assert desc and len(desc) > 20, f"Meta description missing or too short: {desc!r}"

    @allure.story("Homepage has at least one H1")
    def test_h1_present(self, home_page: HomePage):
        home_page.load()
        assert home_page.count_headings(1) >= 1

    @allure.story("Navigating to homepage URL loads successfully")
    def test_homepage_navigates(self, home_page: HomePage):
        home_page.load()
        assert "princess.com" in home_page.get_url()

    @allure.story("Clicking Deals nav navigates to deals page")
    def test_deals_nav_navigates(self, home_page: HomePage):
        home_page.load()
        home_page.click_deals_nav()
        assert "deal" in home_page.get_url().lower() or "promo" in home_page.get_url().lower()

    @allure.story("Clicking Ships nav navigates to ships page")
    def test_ships_nav_navigates(self, home_page: HomePage):
        home_page.load()
        home_page.click_ships_nav()
        assert "ship" in home_page.get_url().lower()
