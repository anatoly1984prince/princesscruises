"""E2E tests: User account journey — Login, Registration, Manage Booking."""
from __future__ import annotations

import allure
import pytest

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.manage_booking_page import ManageBookingPage


@allure.epic("Princess Cruises - E2E")
@allure.feature("User Account Journey")
@pytest.mark.e2e
@pytest.mark.auth
@pytest.mark.slow
class TestUserAccountJourney:

    @allure.story("User navigates from homepage to login page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_to_login(self, home_page: HomePage, login_page: LoginPage):
        with allure.step("1. Load homepage"):
            home_page.load()
            home_page.assert_loaded()

        with allure.step("2. Click login button"):
            home_page.click_login()

        with allure.step("3. Login page is displayed"):
            login_page.assert_loaded()
            login_page.take_screenshot("login_page")

    @allure.story("User navigates from login to registration")
    def test_login_to_registration(self, login_page: LoginPage, register_page: RegisterPage):
        with allure.step("1. Load login page"):
            login_page.load()
            login_page.assert_loaded()

        with allure.step("2. Click Create Account"):
            login_page.click_create_account()
            login_page.wait_for_load_state("domcontentloaded")

        with allure.step("3. Registration page is displayed"):
            register_page.assert_loaded()
            register_page.take_screenshot("register_page")

    @allure.story("User fills and submits registration form")
    def test_registration_form_flow(
        self, register_page: RegisterPage, test_user_data: dict
    ):
        with allure.step("1. Load registration page"):
            register_page.load()
            register_page.assert_loaded()

        with allure.step("2. Fill form with generated data"):
            register_page.fill_registration_form(
                first_name=test_user_data["first_name"],
                last_name=test_user_data["last_name"],
                email=test_user_data["email"],
                password=test_user_data["password"],
            )

        with allure.step("3. Submit and capture result"):
            register_page.submit()
            register_page.take_screenshot("post_registration")
            assert "princess.com" in register_page.get_url()

    @allure.story("User accesses Manage Booking portal")
    def test_manage_booking_access(
        self, home_page: HomePage, manage_booking_page: ManageBookingPage
    ):
        with allure.step("1. Load homepage"):
            home_page.load()

        with allure.step("2. Navigate to Manage Booking"):
            manage_booking_page.load()

        with allure.step("3. Form is accessible"):
            manage_booking_page.assert_loaded()
            manage_booking_page.take_screenshot("manage_booking")

    @allure.story("Invalid booking lookup returns user-friendly error")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_manage_booking_error_feedback(self, manage_booking_page: ManageBookingPage):
        with allure.step("1. Load Manage Booking page"):
            manage_booking_page.load()
            manage_booking_page.assert_loaded()

        with allure.step("2. Enter invalid booking data"):
            manage_booking_page.lookup_booking("99999999", "NotARealGuest")

        with allure.step("3. Error message is displayed"):
            manage_booking_page.assert_error_visible()

    @allure.story("Full authentication flow with valid credentials")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_login_flow(
        self,
        home_page: HomePage,
        login_page: LoginPage,
        auth_credentials: dict,
    ):
        if not auth_credentials["email"]:
            pytest.skip("TEST_USER_EMAIL not configured")

        with allure.step("1. Start from homepage"):
            home_page.load()
            home_page.assert_loaded()

        with allure.step("2. Navigate to login"):
            home_page.click_login()
            login_page.assert_loaded()

        with allure.step("3. Log in with valid credentials"):
            login_page.login(auth_credentials["email"], auth_credentials["password"])

        with allure.step("4. Verify post-login state"):
            assert "princess.com" in login_page.get_url()
            login_page.take_screenshot("post_login")
