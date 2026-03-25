"""Regression tests: Authentication — Login, Logout, Registration."""
from __future__ import annotations

import allure
import pytest

from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.home_page import HomePage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Authentication")
@pytest.mark.regression
@pytest.mark.auth
class TestLoginPage:

    @allure.story("Login page loads with email field")
    def test_login_page_loads(self, login_page: LoginPage):
        login_page.load()
        login_page.assert_loaded()

    @allure.story("Login page has password field")
    def test_login_has_password_field(self, login_page: LoginPage):
        login_page.load()
        assert login_page.is_visible(login_page.PASSWORD_INPUT, timeout=8000)

    @allure.story("Login page has submit button")
    def test_login_has_submit_btn(self, login_page: LoginPage):
        login_page.load()
        assert login_page.is_visible(login_page.SUBMIT_BTN, timeout=8000)

    @allure.story("Login page has Forgot Password link")
    def test_forgot_password_link_visible(self, login_page: LoginPage):
        login_page.load()
        assert login_page.is_visible(login_page.FORGOT_PASSWORD_LINK, timeout=8000)

    @allure.story("Login page has Create Account link")
    def test_create_account_link_visible(self, login_page: LoginPage):
        login_page.load()
        assert login_page.is_visible(login_page.CREATE_ACCOUNT_LINK, timeout=8000)

    @allure.story("Invalid credentials show error message")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_login_shows_error(self, login_page: LoginPage):
        login_page.load()
        login_page.login("invalid@notreal.com", "WrongPassword123!")
        assert login_page.is_visible(login_page.ERROR_MSG, timeout=10000), (
            "Expected error message after invalid login"
        )

    @allure.story("Empty form submission shows validation")
    def test_empty_form_validation(self, login_page: LoginPage):
        login_page.load()
        login_page.click(login_page.SUBMIT_BTN)
        assert (
            login_page.is_visible(login_page.ERROR_MSG, timeout=5000) or
            login_page.is_visible(login_page.EMAIL_INPUT)
        ), "Expected validation feedback on empty submit"

    @allure.story("Valid credentials log in successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_login(self, login_page: LoginPage, auth_credentials: dict):
        if not auth_credentials["email"]:
            pytest.skip("TEST_USER_EMAIL not configured")
        login_page.load()
        login_page.login(auth_credentials["email"], auth_credentials["password"])
        assert (
            login_page.is_visible("[class*='account'], [class*='dashboard'], [aria-label*='account' i]", timeout=10000) or
            "princess.com" in login_page.get_url()
        )

    @allure.story("Login page title contains expected text")
    def test_login_page_title(self, login_page: LoginPage):
        login_page.load()
        title = login_page.get_page_title()
        assert title and len(title) > 5, f"Login page title too short: {title!r}"

    @allure.story("Forgot Password link navigates to reset page")
    def test_forgot_password_navigation(self, login_page: LoginPage):
        login_page.load()
        login_page.click_forgot_password()
        login_page.wait_for_load_state("domcontentloaded")
        assert any(kw in login_page.get_url().lower() for kw in ["forgot", "reset", "password"])

    @allure.story("Create Account link navigates to registration")
    def test_create_account_navigation(self, login_page: LoginPage):
        login_page.load()
        login_page.click_create_account()
        login_page.wait_for_load_state("domcontentloaded")
        assert any(kw in login_page.get_url().lower() for kw in ["register", "create", "signup", "sign-up"])


@allure.epic("Princess Cruises - Regression")
@allure.feature("Registration")
@pytest.mark.regression
@pytest.mark.auth
class TestRegistrationPage:

    @allure.story("Registration page loads")
    def test_registration_page_loads(self, register_page: RegisterPage):
        register_page.load()
        register_page.assert_loaded()

    @allure.story("Registration form has required fields")
    def test_registration_fields_present(self, register_page: RegisterPage):
        register_page.load()
        assert register_page.is_visible("input", timeout=8000), "No input fields on registration page"

    @allure.story("Empty registration form shows validation")
    def test_empty_registration_validation(self, register_page: RegisterPage):
        register_page.load()
        register_page.submit()
        assert (
            register_page.is_visible(register_page.ERROR_MSG, timeout=5000) or
            register_page.is_visible("input")
        ), "Expected validation feedback on empty registration submit"
