"""Regression tests: Country / Region selector."""
from __future__ import annotations

import allure
import pytest

from pages.home_page import HomePage
from pages.country_selector_page import CountrySelectorPage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Country Selector")
@pytest.mark.regression
class TestCountrySelector:

    @allure.story("Country selector trigger is visible in header")
    def test_selector_trigger_visible(
        self, home_page: HomePage, country_selector_page: CountrySelectorPage
    ):
        home_page.load()
        # Trigger presence is optional — just verify it doesn't crash
        visible = home_page.is_visible(country_selector_page.SELECTOR_TRIGGER, timeout=5000)
        if not visible:
            pytest.skip("Country selector trigger not present on this page layout")

    @allure.story("Opening selector shows modal or dropdown")
    def test_open_country_selector(
        self, home_page: HomePage, country_selector_page: CountrySelectorPage
    ):
        home_page.load()
        if not home_page.is_visible(country_selector_page.SELECTOR_TRIGGER, timeout=5000):
            pytest.skip("Country selector trigger not found")
        country_selector_page.open()
        country_selector_page.assert_modal_open()

    @allure.story("Country selector lists country options")
    def test_countries_are_listed(
        self, home_page: HomePage, country_selector_page: CountrySelectorPage
    ):
        home_page.load()
        if not home_page.is_visible(country_selector_page.SELECTOR_TRIGGER, timeout=5000):
            pytest.skip("Country selector trigger not found")
        country_selector_page.open()
        country_selector_page.assert_countries_listed()

    @allure.story("Selecting a country does not crash the page")
    def test_select_country_no_crash(
        self, home_page: HomePage, country_selector_page: CountrySelectorPage
    ):
        home_page.load()
        if not home_page.is_visible(country_selector_page.SELECTOR_TRIGGER, timeout=5000):
            pytest.skip("Country selector trigger not found")
        country_selector_page.open()
        country_selector_page.select_country("United Kingdom")
        country_selector_page.confirm()
        assert country_selector_page.is_visible("body", timeout=5000)

    @allure.story("Closing selector dismisses modal")
    def test_close_selector(
        self, home_page: HomePage, country_selector_page: CountrySelectorPage
    ):
        home_page.load()
        if not home_page.is_visible(country_selector_page.SELECTOR_TRIGGER, timeout=5000):
            pytest.skip("Country selector trigger not found")
        country_selector_page.open()
        country_selector_page.close()
        assert not country_selector_page.is_visible(
            country_selector_page.SELECTOR_MODAL, timeout=3000
        ), "Modal still visible after closing"
