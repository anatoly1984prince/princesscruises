"""Page Object: Booking — Guest Details step."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class BookingGuestsPage(BasePage):
    """Guest information entry step of the booking wizard."""

    PAGE_HEADING = (
        "h1, h2, [class*='guest-header'], [class*='passenger-header'], "
        "[class*='step-title']:has-text('Guest'), "
        "[class*='step-title']:has-text('Passenger')"
    )

    # ── Primary guest fields ─────────────────────────────────────────────────
    FIRST_NAME = (
        "input[name*='firstName' i], input[name*='first-name' i], "
        "input[id*='firstName' i], input[placeholder*='First' i], "
        "input[aria-label*='First name' i]"
    )
    LAST_NAME = (
        "input[name*='lastName' i], input[name*='last-name' i], "
        "input[id*='lastName' i], input[placeholder*='Last' i], "
        "input[aria-label*='Last name' i]"
    )
    DATE_OF_BIRTH = (
        "input[name*='dob' i], input[name*='birthDate' i], "
        "input[id*='dob' i], input[placeholder*='MM/DD/YYYY'], "
        "input[aria-label*='date of birth' i], input[type='date']"
    )
    GENDER = (
        "select[name*='gender' i], select[id*='gender' i], "
        "input[name*='gender' i][type='radio']"
    )
    NATIONALITY = (
        "select[name*='nationality' i], select[name*='country' i], "
        "select[id*='nationality' i], select[aria-label*='nationality' i]"
    )

    # ── Contact info ─────────────────────────────────────────────────────────
    EMAIL_INPUT = (
        "input[type='email'], input[name*='email' i], "
        "input[id*='email' i], input[placeholder*='Email' i]"
    )
    PHONE_INPUT = (
        "input[type='tel'], input[name*='phone' i], "
        "input[id*='phone' i], input[placeholder*='Phone' i]"
    )

    # ── Special needs / accessibility ────────────────────────────────────────
    SPECIAL_NEEDS_SECTION = (
        "[class*='special-needs'], [class*='accessibility'], "
        "section:has-text('Special'), section:has-text('Accessibility'), "
        "[id*='special-needs'], [id*='accessibility']"
    )
    WHEELCHAIR_CHECKBOX = (
        "input[type='checkbox'][aria-label*='wheelchair' i], "
        "input[type='checkbox'][id*='wheelchair' i], "
        "label:has-text('wheelchair') input"
    )
    MOBILITY_CHECKBOX = (
        "input[type='checkbox'][aria-label*='mobility' i], "
        "input[type='checkbox'][id*='mobility' i], "
        "label:has-text('mobility') input, label:has-text('Mobility') input"
    )
    SPECIAL_NEEDS_CHECKBOX = (
        "input[type='checkbox'][aria-label*='special' i], "
        "input[type='checkbox'][id*='special' i], "
        "label:has-text('Special needs') input, "
        "label:has-text('Accessible') input"
    )
    SPECIAL_NEEDS_TEXT = (
        "textarea[name*='special' i], textarea[id*='special' i], "
        "textarea[placeholder*='special' i], textarea[aria-label*='special' i]"
    )

    # ── Navigation ──────────────────────────────────────────────────────────
    CONTINUE_BTN = (
        "button:has-text('Continue'), button:has-text('Next'), "
        "a:has-text('Continue'), button[class*='continue']"
    )
    SAVE_GUEST_BTN = (
        "button:has-text('Save'), button:has-text('Add Guest'), "
        "button[class*='save-guest']"
    )

    # ── Validation ───────────────────────────────────────────────────────────
    VALIDATION_ERROR = (
        "[class*='error'], [role='alert'], [aria-live='polite'], "
        "[class*='invalid-feedback'], [class*='field-error']"
    )
    REQUIRED_FIELD_ERROR = (
        "input:invalid, [class*='required-error'], "
        "[class*='field--error'], [aria-describedby*='error']"
    )

    def is_on_guests_page(self) -> bool:
        url = self.get_url().lower()
        return any(k in url for k in ["guest", "passenger", "traveler"])

    @allure.step("Assert guests page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.PAGE_HEADING, timeout=20000)

    @allure.step("Fill primary guest details")
    def fill_guest_details(
        self,
        first_name: str,
        last_name: str,
        dob: str = "",
        email: str = "",
        phone: str = "",
    ) -> None:
        if self.is_visible(self.FIRST_NAME, timeout=5000):
            self.fill(self.FIRST_NAME, first_name)
        if self.is_visible(self.LAST_NAME, timeout=3000):
            self.fill(self.LAST_NAME, last_name)
        if dob and self.is_visible(self.DATE_OF_BIRTH, timeout=3000):
            self.fill(self.DATE_OF_BIRTH, dob)
        if email and self.is_visible(self.EMAIL_INPUT, timeout=3000):
            self.fill(self.EMAIL_INPUT, email)
        if phone and self.is_visible(self.PHONE_INPUT, timeout=3000):
            self.fill(self.PHONE_INPUT, phone)

    @allure.step("Check accessibility/special needs option: {option_label}")
    def select_accessibility_option(self, option_label: str) -> bool:
        """Check a special needs / accessibility checkbox by label text."""
        selector = f"label:has-text('{option_label}') input[type='checkbox']"
        if not self.is_visible(selector, timeout=3000):
            # Fallback: look for any accessible checkbox
            selector = self.SPECIAL_NEEDS_CHECKBOX
        if self.is_visible(selector, timeout=3000):
            cb = self.page.locator(selector).first
            if not cb.is_checked():
                cb.click()
            return True
        return False

    @allure.step("Submit guest form")
    def continue_to_next_step(self) -> bool:
        if self.is_visible(self.CONTINUE_BTN, timeout=5000):
            self.click(self.CONTINUE_BTN)
            self.wait_for_load_state("domcontentloaded")
            return True
        return False

    def has_validation_errors(self) -> bool:
        return self.count(self.VALIDATION_ERROR) > 0
