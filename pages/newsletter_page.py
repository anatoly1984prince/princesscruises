"""Page Object: Newsletter / Email sign-up section (in homepage footer area)."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class NewsletterPage(BasePage):
    """
    Load the homepage first, then use this page object.
    The sign-up form uses class 'cmp-ve-sign-up-form' on princess.com.
    """
    FORM = "[class*='cmp-ve-sign-up-form'], [class*='sign-up'] form"
    EMAIL_INPUT = "input[class*='cmp-ve-sign-up-form__field-input'][type='email'], [class*='cmp-ve-sign-up-form'] input[type='email']"
    FIRST_NAME_INPUT = "input[class*='cmp-ve-sign-up-form__field-input'][name='firstName'], [class*='cmp-ve-sign-up-form'] input[name='firstName']"
    LAST_NAME_INPUT = "input[class*='cmp-ve-sign-up-form__field-input'][name='lastName'], [class*='cmp-ve-sign-up-form'] input[name='lastName']"
    SUBMIT_BTN = "button[class*='cmp-ve-sign-up-form__submit-btn']"
    ERROR_MESSAGE = "[class*='cmp-ve-sign-up-form'] [class*='error'], [class*='cmp-ve-sign-up-form'] [role='alert']"
    SUCCESS_MESSAGE = "[class*='cmp-ve-sign-up-form'] [class*='success'], [class*='cmp-ve-sign-up-form'] [class*='thank']"
    PROMO_CHECKBOX = "[class*='cmp-ve-sign-up-form'] input[type='checkbox']"

    @allure.step("Assert newsletter form visible")
    def assert_form_visible(self) -> None:
        self.scroll_to_bottom()
        self.assert_visible(self.FORM, timeout=10000)

    @allure.step("Fill newsletter signup form")
    def fill_signup_form(
        self,
        email: str,
        first_name: str = "",
        last_name: str = "",
        accept_promo: bool = False,
    ) -> None:
        self.scroll_to_element(self.EMAIL_INPUT)
        self.fill(self.EMAIL_INPUT, email)
        if first_name and self.is_visible(self.FIRST_NAME_INPUT):
            self.fill(self.FIRST_NAME_INPUT, first_name)
        if last_name and self.is_visible(self.LAST_NAME_INPUT):
            self.fill(self.LAST_NAME_INPUT, last_name)
        if accept_promo and self.is_visible(self.PROMO_CHECKBOX):
            cb = self.page.locator(self.PROMO_CHECKBOX).first
            if not cb.is_checked():
                cb.click()

    @allure.step("Submit newsletter form")
    def submit(self) -> None:
        if self.is_visible(self.SUBMIT_BTN, timeout=3000):
            self.click(self.SUBMIT_BTN)
