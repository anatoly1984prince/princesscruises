"""Page Object: Registration / Create Account page."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class RegisterPage(BasePage):
    PATH = "/my-princess/register/"

    # ── Identity ─────────────────────────────────────────────────────────────
    TITLE_SELECT     = "select[aria-label='Title']"
    FIRST_NAME       = "input[name='firstName']"
    LAST_NAME        = "input[name='lastName']"
    EMAIL            = "input[name='contactEmail']"
    PASSWORD         = "input[name='password']"

    # ── Date of birth (three separate <select name='birthDate'>) ─────────────
    DOB_MONTH        = "select[aria-label='Birthday Month selection']"
    DOB_DAY          = "select[aria-label='Birthday Day selection']"
    DOB_YEAR         = "select[aria-label='Birthday Year selection']"

    # ── Address ───────────────────────────────────────────────────────────────
    ADDRESS1         = "input[name='address1']"
    CITY             = "input[name='city']"
    STATE_SELECT     = "select[aria-label='State/Province']"
    ZIP              = "input[name='zip']"

    # ── Phone ─────────────────────────────────────────────────────────────────
    CELL_PHONE       = "input[name='cellPhone']"
    HOME_PHONE       = "input[name='phone']"

    # ── Cruise history radio ──────────────────────────────────────────────────
    CRUISED_NO       = "input[aria-label='No']"

    # ── Form response ─────────────────────────────────────────────────────────
    SUBMIT_BTN       = "button[type='submit']"
    ERROR_MSG        = "[class*='error'], [role='alert'], [class*='alert']"
    SUCCESS_MSG      = "[class*='success'], [class*='confirm'], h1:has-text('Thank')"

    def load(self) -> None:
        self.navigate(self.PATH)

    @allure.step("Assert registration page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.EMAIL)

    @allure.step("Fill registration form for {first_name} {last_name}")
    def fill_registration_form(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        dob_month: str = "",
        dob_day: str = "",
        dob_year: str = "",
        address1: str = "",
        city: str = "",
        state: str = "",
        zip_code: str = "",
        cell_phone: str = "",
        title: str = "MR",
    ) -> None:
        # Email and password come first in the DOM
        self.fill(self.EMAIL, email)
        self.fill(self.PASSWORD, password)

        # Title / name
        if self.is_visible(self.TITLE_SELECT, timeout=3000):
            self.select_option(self.TITLE_SELECT, title)
        self.fill(self.FIRST_NAME, first_name)
        self.fill(self.LAST_NAME, last_name)

        # Date of birth
        if dob_month and self.is_visible(self.DOB_MONTH, timeout=3000):
            self.select_option(self.DOB_MONTH, dob_month)
        if dob_day and self.is_visible(self.DOB_DAY, timeout=3000):
            self.select_option(self.DOB_DAY, dob_day)
        if dob_year and self.is_visible(self.DOB_YEAR, timeout=3000):
            self.select_option(self.DOB_YEAR, dob_year)

        # Address
        if address1 and self.is_visible(self.ADDRESS1, timeout=3000):
            self.fill(self.ADDRESS1, address1)
        if city and self.is_visible(self.CITY, timeout=3000):
            self.fill(self.CITY, city)
        if state and self.is_visible(self.STATE_SELECT, timeout=3000):
            self.select_option(self.STATE_SELECT, state)
        if zip_code and self.is_visible(self.ZIP, timeout=3000):
            self.fill(self.ZIP, zip_code)

        # Phone
        if cell_phone and self.is_visible(self.CELL_PHONE, timeout=3000):
            self.fill(self.CELL_PHONE, cell_phone)

        # Cruise history — default "No" to avoid loyalty number prompt
        if self.is_visible(self.CRUISED_NO, timeout=3000):
            self.page.locator(self.CRUISED_NO).first.check()

    @allure.step("Submit registration form")
    def submit(self) -> None:
        self.click(self.SUBMIT_BTN)
        self.wait_for_load_state("domcontentloaded")

    def is_registered(self) -> bool:
        """Returns True if the page indicates successful registration."""
        url = self.get_url().lower()
        return (
            any(k in url for k in ["success", "confirm", "thank", "welcome", "dashboard", "account"]) or
            self.is_visible(self.SUCCESS_MSG, timeout=5000)
        )
