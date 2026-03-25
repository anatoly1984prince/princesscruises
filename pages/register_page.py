"""Page Object: Registration / Create Account page."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class RegisterPage(BasePage):
    PATH = "/my-princess/register/"

    FIRST_NAME = "input[name*='first' i], input[placeholder*='First' i]"
    LAST_NAME = "input[name*='last' i], input[placeholder*='Last' i]"
    EMAIL = "input[type='email'], input[name*='email' i]"
    PASSWORD = "input[type='password'][name*='password' i]:not([name*='confirm' i])"
    CONFIRM_PASSWORD = (
        "input[name*='confirm' i], "
        "input[placeholder*='confirm' i], "
        "input[type='password']:nth-of-type(2)"
    )
    SUBMIT_BTN = "button[type='submit'], button:has-text('Create'), button:has-text('Register')"
    ERROR_MSG = "[class*='error'], [role='alert'], [class*='alert']"
    SUCCESS_MSG = "[class*='success'], [class*='confirm'], h1:has-text('Thank')"

    def load(self) -> None:
        self.navigate(self.PATH)

    @allure.step("Assert registration page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible("form")

    @allure.step("Fill registration form")
    def fill_registration_form(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
    ) -> None:
        if self.is_visible(self.FIRST_NAME):
            self.fill(self.FIRST_NAME, first_name)
        if self.is_visible(self.LAST_NAME):
            self.fill(self.LAST_NAME, last_name)
        if self.is_visible(self.EMAIL):
            self.fill(self.EMAIL, email)
        if self.is_visible(self.PASSWORD):
            self.fill(self.PASSWORD, password)
        if self.is_visible(self.CONFIRM_PASSWORD):
            self.fill(self.CONFIRM_PASSWORD, password)

    @allure.step("Submit registration form")
    def submit(self) -> None:
        self.click(self.SUBMIT_BTN)
        self.wait_for_load_state("domcontentloaded")
