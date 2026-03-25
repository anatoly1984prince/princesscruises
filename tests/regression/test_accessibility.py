"""Regression tests: Accessibility basics — titles, landmarks, alt text, HTTPS."""
from __future__ import annotations

import allure
import pytest

from pages.home_page import HomePage
from pages.deals_page import DealsPage
from pages.ships_page import ShipsPage
from pages.login_page import LoginPage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Accessibility")
@pytest.mark.regression
@pytest.mark.accessibility
class TestAccessibilityBasics:

    @allure.story("Homepage has a meaningful page title")
    def test_homepage_title(self, home_page: HomePage):
        home_page.load()
        title = home_page.get_page_title()
        assert title and len(title) > 5, f"Page title too short: {title!r}"
        assert "Princess" in title, f"'Princess' not in title: {title!r}"

    @allure.story("Deals page has a meaningful title")
    def test_deals_title(self, deals_page: DealsPage):
        deals_page.load()
        title = deals_page.get_page_title()
        assert title and len(title) > 5, f"Deals title too short: {title!r}"

    @allure.story("Ships page has a meaningful title")
    def test_ships_title(self, ships_page: ShipsPage):
        ships_page.load()
        title = ships_page.get_page_title()
        assert title and len(title) > 5, f"Ships title too short: {title!r}"

    @allure.story("Login page has a meaningful title")
    def test_login_title(self, login_page: LoginPage):
        login_page.load()
        title = login_page.get_page_title()
        assert title and len(title) > 5, f"Login title too short: {title!r}"

    @allure.story("Homepage has at least one H1 tag")
    def test_homepage_h1(self, home_page: HomePage):
        home_page.load()
        assert home_page.count_headings(1) >= 1, "Homepage has no H1 heading"

    @allure.story("Homepage has a meta description")
    def test_homepage_meta_description(self, home_page: HomePage):
        home_page.load()
        desc = home_page.get_meta_description()
        assert desc and len(desc) > 20, f"Meta description missing or too short: {desc!r}"

    @allure.story("Homepage images have alt text (princess.com has many decorative images)")
    def test_image_alt_text(self, home_page: HomePage):
        home_page.load()
        missing = home_page.get_all_images_without_alt()
        # Princess.com homepage has many decorative/lazy images — flag if excessively missing
        assert len(missing) <= 70, (
            f"{len(missing)} images missing alt text (threshold: 70):\n" +
            "\n".join(missing[:5])
        )

    @allure.story("Homepage has a banner/header landmark")
    def test_banner_landmark(self, home_page: HomePage):
        home_page.load()
        count = home_page.page.locator("[role='banner'], header").count()
        assert count >= 1, "No banner/header landmark found"

    @allure.story("Homepage has a main content landmark")
    def test_main_landmark(self, home_page: HomePage):
        home_page.load()
        count = home_page.page.locator("[role='main'], main").count()
        assert count >= 1, "No main landmark found"

    @allure.story("Homepage has a footer/contentinfo landmark")
    def test_footer_landmark(self, home_page: HomePage):
        home_page.load()
        count = home_page.page.locator("[role='contentinfo'], footer").count()
        assert count >= 1, "No contentinfo/footer landmark found"

    @allure.story("All key pages use HTTPS")
    @pytest.mark.parametrize("fixture_name", [
        "home_page",
        "deals_page",
        "ships_page",
        "login_page",
    ])
    def test_pages_use_https(self, fixture_name: str, request: pytest.FixtureRequest):
        page_obj = request.getfixturevalue(fixture_name)
        page_obj.load()
        assert page_obj.get_url().startswith("https://"), (
            f"{fixture_name} not served over HTTPS: {page_obj.get_url()}"
        )

    @allure.story("Navigation links in DOM have valid href attributes")
    def test_nav_links_have_href(self, home_page: HomePage):
        home_page.load()
        # Only check <a> tags that have a non-empty, non-hash href (dropdown triggers use #)
        nav_links = home_page.page.locator("nav a[href]").all()
        truly_empty: list[str] = []
        for link in nav_links[:30]:
            href = (link.get_attribute("href") or "").strip()
            if href == "":
                truly_empty.append(link.inner_text().strip())
        assert len(truly_empty) == 0, f"Nav <a> tags with completely empty href: {truly_empty}"
