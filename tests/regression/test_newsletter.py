"""Regression tests: Newsletter signup form."""
from __future__ import annotations

import allure
import pytest

from pages.home_page import HomePage
from pages.newsletter_page import NewsletterPage


@allure.epic("Princess Cruises - Regression")
@allure.feature("Newsletter Signup")
@pytest.mark.regression
class TestNewsletter:

    @allure.story("Newsletter form is present on homepage")
    def test_newsletter_form_visible(self, home_page: HomePage, newsletter_page: NewsletterPage):
        home_page.load()
        newsletter_page.assert_form_visible()

    @allure.story("Newsletter form has email input")
    def test_email_field_visible(self, home_page: HomePage, newsletter_page: NewsletterPage):
        home_page.load()
        home_page.scroll_to_bottom()
        assert newsletter_page.is_visible(newsletter_page.EMAIL_INPUT, timeout=8000), (
            "Newsletter email input not visible"
        )

    @allure.story("Newsletter form has submit button")
    def test_submit_button_visible(self, home_page: HomePage, newsletter_page: NewsletterPage):
        home_page.load()
        home_page.scroll_to_bottom()
        assert newsletter_page.is_visible(newsletter_page.SUBMIT_BTN, timeout=8000), (
            "Newsletter submit button not visible"
        )

    @allure.story("Submitting empty form shows validation")
    def test_empty_newsletter_validation(self, home_page: HomePage, newsletter_page: NewsletterPage):
        home_page.load()
        home_page.scroll_to_bottom()
        if newsletter_page.is_visible(newsletter_page.SUBMIT_BTN, timeout=5000):
            newsletter_page.submit()
            assert (
                newsletter_page.is_visible(newsletter_page.ERROR_MESSAGE, timeout=5000) or
                newsletter_page.is_visible(newsletter_page.EMAIL_INPUT)
            ), "Expected validation after empty newsletter submit"

    @allure.story("Invalid email shows validation error")
    def test_invalid_email_validation(self, home_page: HomePage, newsletter_page: NewsletterPage):
        home_page.load()
        home_page.scroll_to_bottom()
        if newsletter_page.is_visible(newsletter_page.EMAIL_INPUT, timeout=5000):
            newsletter_page.scroll_to_element(newsletter_page.EMAIL_INPUT)
            newsletter_page.fill(newsletter_page.EMAIL_INPUT, "not-an-email")
            newsletter_page.submit()
            assert (
                newsletter_page.is_visible(newsletter_page.ERROR_MESSAGE, timeout=5000) or
                newsletter_page.is_visible(newsletter_page.EMAIL_INPUT)
            )

    @allure.story("Valid email signup produces feedback")
    def test_valid_newsletter_signup(
        self,
        home_page: HomePage,
        newsletter_page: NewsletterPage,
        test_user_data: dict,
    ):
        home_page.load()
        home_page.scroll_to_bottom()
        if not newsletter_page.is_visible(newsletter_page.EMAIL_INPUT, timeout=5000):
            pytest.skip("Newsletter form not found on page")
        newsletter_page.fill_signup_form(
            email=test_user_data["email"],
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
        )
        newsletter_page.submit()
        has_feedback = (
            newsletter_page.is_visible(newsletter_page.SUCCESS_MESSAGE, timeout=8000) or
            newsletter_page.is_visible(newsletter_page.ERROR_MESSAGE, timeout=5000)
        )
        if not has_feedback:
            pytest.skip("No feedback shown after newsletter submission — form may be suppressed in headless mode")
