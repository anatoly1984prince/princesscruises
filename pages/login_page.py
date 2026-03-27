"""Page Object: Login / Sign-In page."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/my-princess/account-login/"

    EMAIL_INPUT = "input#loginId, input[name='loginId'], input[type='email'], input[name*='email' i]"
    PASSWORD_INPUT = "input#password, input[type='password'], input[name='password']"
    SUBMIT_BTN = (
        "button[type='submit'], "
        "button:has-text('Sign In'), "
        "button:has-text('Log In')"
    )
    GUEST_CHECKOUT_BTN = (
        "button:has-text('Continue as Guest'), button:has-text('Guest Checkout'), "
        "button:has-text('Book as Guest'), a:has-text('Continue as Guest'), "
        "a:has-text('Guest'), button:has-text('Skip'), "
        "[class*='guest'] button, [class*='guest-checkout']"
    )
    CREATE_ACCOUNT_LINK = (
        "a:has-text('Create Account'), "
        "a:has-text('Register'), "
        "a:has-text('Sign Up'), "
        "button:has-text('Create Account')"
    )
    FORGOT_PASSWORD_LINK = "a:has-text('Forgot'), a[href*='forgot'], a[href*='reset']"
    ERROR_MSG = (
        "[class*='error'], [role='alert'], "
        "[class*='alert'], [aria-live='polite']"
    )
    PAGE_HEADING = "h1, h2, [class*='heading']"

    def load(self) -> None:
        self.navigate(self.PATH)

    @allure.step("Assert login page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.EMAIL_INPUT)

    @allure.step("Log in with email={email}")
    def login(self, email: str, password: str) -> None:
        self.fill(self.EMAIL_INPUT, email)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.SUBMIT_BTN)
        self.wait_for_load_state("domcontentloaded")

    def has_guest_checkout(self) -> bool:
        return self.is_visible(self.GUEST_CHECKOUT_BTN, timeout=5000)

    @allure.step("Continue as guest (skip login)")
    def continue_as_guest(self) -> bool:
        if self.is_visible(self.GUEST_CHECKOUT_BTN, timeout=5000):
            self.click(self.GUEST_CHECKOUT_BTN)
            self.wait_for_load_state("domcontentloaded")
            return True
        return False

    @allure.step("Click Create Account")
    def click_create_account(self) -> None:
        self.click(self.CREATE_ACCOUNT_LINK)
        self.wait_for_load_state("domcontentloaded")

    @allure.step("Click Forgot Password")
    def click_forgot_password(self) -> None:
        self.click(self.FORGOT_PASSWORD_LINK)
        self.wait_for_load_state("domcontentloaded")

    @allure.step("Assert error message visible")
    def assert_error_visible(self) -> None:
        self.assert_visible(self.ERROR_MSG)
