"""Page Object: Princess.com Homepage."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class HomePage(BasePage):
    # ── Selectors ───────────────────────────────────────────────────────────
    HEADER = "header, [role='banner'], pcl-global-header, [class*='global-header']"
    FOOTER = "footer, [role='contentinfo']"
    # Logo — web component, check for the component itself or any logo img
    NAV_LOGO = "a[aria-label*='Princess'], [class*='cmp-global-header__logo'], [class*='global-header-mobile__logo']"
    # Nav — links exist in light DOM (mobile nav) and also via direct href
    NAV_DESTINATIONS = "a[href*='cruise-destinations']"
    NAV_SHIPS = "a[href*='ships-and-experience/ships']"
    NAV_DEALS = "a[href*='cruise-deals-promotions']"
    NAV_MANAGE_BOOKING = "a[href*='manage-booking']"
    # Login — use the my-princess URL presence check
    LOGIN_BTN = "a[href*='account-login'], a[href*='sign-in'], a[href*='my-princess/login']"
    # Find a cruise — direct link on the page
    FIND_CRUISE_BTN = "a[href*='cruise-search/results'], a[class*='search-cruise'], a:has-text('Find a Cruise')"
    SEARCH_ICON = "button[aria-label*='search' i], [class*='search'] button, button[class*='search']"
    # Hero — visible promo banner
    # Use specific visible classes — generic [class*='hero'] matches hidden elements first
    HERO_SECTION = "[class*='promo-banner'], [class*='ve-hero-banner'], [class*='country-banner']"
    BOOK_NOW_BTN = "a:has-text('Book Now'), button:has-text('Book Now')"

    def load(self) -> None:
        self.navigate("/")

    @allure.step("Assert homepage loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.HEADER)

    @allure.step("Click Find a Cruise")
    def click_find_a_cruise(self) -> None:
        # Navigate directly — nav links are in shadow DOM / mobile-only
        self.navigate("/cruise-search/results/?resType=C")

    @allure.step("Click Login")
    def click_login(self) -> None:
        self.navigate("/my-princess/account-login/")

    @allure.step("Click Deals nav link")
    def click_deals_nav(self) -> None:
        self.navigate("/cruise-deals-promotions/")

    @allure.step("Click Ships nav link")
    def click_ships_nav(self) -> None:
        self.navigate("/ships-and-experience/ships/")

    @allure.step("Click search icon")
    def click_search_icon(self) -> None:
        self._click_if_visible(self.SEARCH_ICON, timeout=5000)
