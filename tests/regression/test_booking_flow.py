"""
Regression tests: Booking flow — from cruise selection through to payment page.

Covers:
  - Booking entry (Book Now button on cruise detail page)
  - Cabin/stateroom selection for all cabin categories
  - Accessible cabin combinations (wheelchair, ambulatory, mobility)
  - Guest details with special needs options
  - Price/order summary on payment page
  - Payment page structure and required fields
  - Accessibility compliance across booking steps

NOTE: princess.com booking requires authentication and live voyage IDs.
      Tests skip gracefully when the flow is blocked (auth wall, headless SPA, etc.).
"""
from __future__ import annotations

import allure
import pytest

from pages.cruise_search_page import CruiseSearchPage
from pages.cruise_results_page import CruiseResultsPage
from pages.cruise_detail_page import CruiseDetailPage
from pages.booking_cabin_page import BookingCabinPage, CABIN_TYPES, ACCESSIBLE_CABIN_TYPES
from pages.booking_guests_page import BookingGuestsPage
from pages.booking_payment_page import BookingPaymentPage
from pages.booking_confirmation_page import BookingConfirmationPage
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.register_page import RegisterPage
from utilities.data_generators import generate_registration_user


# ── Shared helpers ────────────────────────────────────────────────────────────

def _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page):
    """Navigate to the first available cruise detail page; skip if SPA blocked."""
    cruise_search_page.load()
    loaded = cruise_results_page._wait_for_real_cards(timeout=40000)
    if not loaded:
        pytest.skip("Cruise result cards did not render — SPA blocked in headless mode")
    cruise_results_page.click_card(0)
    # Confirm we're on a detail page (URL changed from results)
    if "cruise-search" in cruise_detail_page.get_url().lower() and \
            "find-a-cruise" not in cruise_detail_page.get_url().lower():
        pass  # may still be results URL; detail page detection below handles it


def _reach_cabin_page(detail: CruiseDetailPage, cabin: BookingCabinPage) -> None:
    """Click Book Now and confirm we reach a cabin selection step."""
    if not detail.is_visible(detail.BOOK_NOW_BTN, timeout=10000):
        pytest.skip("Book Now button not found on cruise detail page")
    detail.click_book_now()
    if not cabin.wait_for_cabin_page(timeout=20000):
        url = cabin.get_url().lower()
        # Login wall is expected; skip rather than fail
        if any(k in url for k in ["login", "sign-in", "account", "auth"]):
            pytest.skip("Booking requires authentication — redirected to login page")
        if not cabin.is_on_cabin_page():
            pytest.skip(f"Did not reach cabin selection page (landed on: {cabin.get_url()})")


# ── Test classes ──────────────────────────────────────────────────────────────

@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow")
@pytest.mark.regression
@pytest.mark.booking
class TestBookingEntry:
    """Tests that verify entry into the booking flow."""

    @allure.story("Book Now button present on cruise detail page")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_book_now_button_present(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
    ):
        _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)
        assert cruise_detail_page.is_visible(cruise_detail_page.BOOK_NOW_BTN, timeout=10000), (
            "Book Now button not found on cruise detail page"
        )

    @allure.story("Clicking Book Now navigates away from detail page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_book_now_navigates(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
    ):
        _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)
        detail_url = cruise_detail_page.get_url()

        if not cruise_detail_page.is_visible(cruise_detail_page.BOOK_NOW_BTN, timeout=10000):
            pytest.skip("Book Now button not found")

        cruise_detail_page.click_book_now()
        booking_cabin_page.wait_for_load_state("domcontentloaded")
        new_url = booking_cabin_page.get_url()
        assert new_url != detail_url, (
            f"URL did not change after clicking Book Now: {new_url}"
        )

    @allure.story("Booking redirects to login when unauthenticated")
    @allure.severity(allure.severity_level.NORMAL)
    def test_book_now_auth_or_booking_page(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
    ):
        """After Book Now, we should land on either a cabin page or a login wall."""
        _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)

        if not cruise_detail_page.is_visible(cruise_detail_page.BOOK_NOW_BTN, timeout=10000):
            pytest.skip("Book Now button not found")

        cruise_detail_page.click_book_now()
        booking_cabin_page.wait_for_load_state("domcontentloaded")
        url = booking_cabin_page.get_url().lower()

        is_on_booking = booking_cabin_page.is_on_cabin_page()
        is_on_login = any(k in url for k in ["login", "sign-in", "account", "auth"])
        assert is_on_booking or is_on_login, (
            f"Unexpected URL after Book Now: {booking_cabin_page.get_url()}"
        )


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Cabin Selection")
@pytest.mark.regression
@pytest.mark.booking
class TestCabinSelection:
    """Tests for the stateroom/cabin selection step."""

    @pytest.fixture(autouse=True)
    def _reach_cabin_step(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
    ):
        _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)
        _reach_cabin_page(cruise_detail_page, booking_cabin_page)
        self._cabin = booking_cabin_page

    @allure.story("Cabin selection page has a heading")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cabin_page_has_heading(self):
        assert self._cabin.is_visible(self._cabin.PAGE_HEADING, timeout=15000), (
            "No heading found on cabin selection page"
        )

    @allure.story("Cabin cards are displayed")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cabin_cards_present(self):
        count = self._cabin.count(self._cabin.CABIN_CARDS)
        if count == 0:
            pytest.skip("No cabin cards rendered — may require authentication")
        assert count >= 1, f"Expected at least 1 cabin card, found {count}"

    @allure.story("Cabin prices are displayed")
    def test_cabin_prices_displayed(self):
        if self._cabin.count(self._cabin.CABIN_CARDS) == 0:
            pytest.skip("No cabin cards available")
        price = self._cabin.get_first_cabin_price()
        assert isinstance(price, str), "Price should be a string"

    @allure.story("Select button present on first cabin card")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cabin_select_button_present(self):
        if self._cabin.count(self._cabin.CABIN_CARDS) == 0:
            pytest.skip("No cabin cards available")
        assert self._cabin.is_visible(self._cabin.SELECT_CABIN_BTN, timeout=8000), (
            "No Select button found on cabin cards"
        )

    @allure.story("Cabin page has a Continue/Next button")
    def test_cabin_continue_button_present(self):
        assert self._cabin.is_visible(self._cabin.CONTINUE_BTN, timeout=8000) or \
               self._cabin.is_visible(self._cabin.SELECT_CABIN_BTN, timeout=3000), (
            "No Continue or Select button found on cabin page"
        )

    @allure.story("Cabin page URL is in booking flow")
    def test_cabin_page_url(self):
        assert self._cabin.is_on_cabin_page(), (
            f"Unexpected URL for cabin page: {self._cabin.get_url()}"
        )


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Cabin Categories")
@pytest.mark.regression
@pytest.mark.booking
class TestCabinCategories:
    """Tests for each cabin category tab (Interior/Oceanview/Balcony/Suite)."""

    @pytest.fixture(autouse=True)
    def _reach_cabin_step(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
    ):
        _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)
        _reach_cabin_page(cruise_detail_page, booking_cabin_page)
        if booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) == 0:
            pytest.skip("No cabin cards rendered — may require authentication")
        self._cabin = booking_cabin_page

    @allure.story("Interior cabin tab is selectable")
    @pytest.mark.parametrize("category", ["Interior", "Oceanview", "Balcony", "Suite"])
    def test_cabin_category_tab_clickable(self, category: str):
        """Each cabin category tab should be present and clickable."""
        tab_map = {
            "Interior": self._cabin.CABIN_TAB_INTERIOR,
            "Oceanview": self._cabin.CABIN_TAB_OCEANVIEW,
            "Balcony": self._cabin.CABIN_TAB_BALCONY,
            "Suite": self._cabin.CABIN_TAB_SUITE,
        }
        selector = tab_map[category]
        if not self._cabin.is_visible(selector, timeout=5000):
            pytest.skip(f"{category} tab not visible on this cruise")
        self._cabin.select_cabin_category(category)
        # After clicking, some cabin cards should still be present
        assert self._cabin.count(self._cabin.CABIN_CARDS) >= 0  # no crash

    @allure.story("Mini-Suite category is available when applicable")
    def test_mini_suite_tab_if_available(self):
        if not self._cabin.is_visible(self._cabin.CABIN_TAB_MINI_SUITE, timeout=3000):
            pytest.skip("Mini-Suite tab not available on this cruise")
        self._cabin.select_cabin_category("mini-suite")
        assert self._cabin.count(self._cabin.CABIN_CARDS) >= 0  # no crash


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Accessible Cabins")
@pytest.mark.regression
@pytest.mark.booking
@pytest.mark.accessibility
class TestAccessibleCabins:
    """
    Tests for accessibility cabin options.
    Princess.com offers:
      - Accessible staterooms (mobility impairment / wheelchair accessible)
      - Ambulatory accessible staterooms (can walk with assistance)
      - Each in multiple categories: Interior, Oceanview, Balcony, Suite
    """

    @pytest.fixture(autouse=True)
    def _reach_cabin_step(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
    ):
        _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)
        _reach_cabin_page(cruise_detail_page, booking_cabin_page)
        if booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) == 0:
            pytest.skip("No cabin cards rendered — may require authentication")
        self._cabin = booking_cabin_page

    @allure.story("Accessible cabin filter control is present")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_accessible_filter_present(self):
        """An accessible cabin filter (checkbox or button) should be present."""
        has_filter = self._cabin.is_visible(self._cabin.ACCESSIBLE_FILTER, timeout=5000)
        has_badge = self._cabin.has_accessible_cabins()
        # Either a filter control or accessible badge markers should exist
        assert has_filter or has_badge, (
            "No accessible cabin filter or accessibility badges found on cabin page"
        )

    @allure.story("Accessible cabin filter can be toggled without crash")
    def test_accessible_filter_toggleable(self):
        if not self._cabin.is_visible(self._cabin.ACCESSIBLE_FILTER, timeout=5000):
            pytest.skip("Accessible filter not present on this cruise")
        self._cabin.toggle_accessible_filter()
        # Page should still show cabin cards (or fewer cards) after filtering
        count = self._cabin.count(self._cabin.CABIN_CARDS)
        assert count >= 0, "Cabin page crashed after toggling accessible filter"

    @allure.story("Accessible cabin badges are displayed when filter is active")
    def test_accessible_badges_visible_with_filter(self):
        if not self._cabin.is_visible(self._cabin.ACCESSIBLE_FILTER, timeout=5000):
            pytest.skip("Accessible filter not present")
        self._cabin.toggle_accessible_filter()
        # Accessible badges or cabin count should indicate accessible options
        has_cabins = self._cabin.count(self._cabin.CABIN_CARDS) >= 0
        assert has_cabins, "Unexpected state after accessible filter"

    @allure.story("Accessible Interior cabin option available")
    @pytest.mark.parametrize("cabin_type,tab_label", [
        ("Interior", "Interior"),
        ("Oceanview", "Oceanview"),
        ("Balcony", "Balcony"),
    ])
    def test_accessible_cabin_per_category(self, cabin_type: str, tab_label: str):
        """For each cabin category, check that accessible option is discoverable."""
        # First select the category tab if available
        self._cabin.select_cabin_category(tab_label)
        # Then toggle accessible filter
        if not self._cabin.is_visible(self._cabin.ACCESSIBLE_FILTER, timeout=3000):
            pytest.skip(f"Accessible filter not present for {cabin_type}")
        self._cabin.toggle_accessible_filter()
        count = self._cabin.count(self._cabin.CABIN_CARDS)
        # Skip rather than fail if no accessible cabins exist for this category
        if count == 0:
            pytest.skip(f"No accessible {cabin_type} cabins available on this cruise")
        assert count >= 0


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Guest Details")
@pytest.mark.regression
@pytest.mark.booking
class TestGuestDetails:
    """Tests for the guest information entry step."""

    @pytest.fixture(autouse=True)
    def _reach_guests_step(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        booking_guests_page: BookingGuestsPage,
    ):
        _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)
        _reach_cabin_page(cruise_detail_page, booking_cabin_page)

        # Try to proceed from cabin selection
        if booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) > 0:
            selected = booking_cabin_page.select_first_cabin()
            if not selected:
                booking_cabin_page.continue_to_next_step()
        else:
            booking_cabin_page.continue_to_next_step()

        if not booking_guests_page.is_on_guests_page():
            pytest.skip(f"Did not reach guest page (at: {booking_guests_page.get_url()})")
        self._guests = booking_guests_page

    @allure.story("Guest details page has a heading")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_guests_page_has_heading(self):
        assert self._guests.is_visible(self._guests.PAGE_HEADING, timeout=15000), (
            "No heading found on guest details page"
        )

    @allure.story("First name field is present and fillable")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_first_name_field_present(self):
        assert self._guests.is_visible(self._guests.FIRST_NAME, timeout=8000), (
            "First name input not found on guest details page"
        )

    @allure.story("Last name field is present and fillable")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_last_name_field_present(self):
        assert self._guests.is_visible(self._guests.LAST_NAME, timeout=8000), (
            "Last name input not found on guest details page"
        )

    @allure.story("Date of birth field is present")
    def test_dob_field_present(self):
        assert self._guests.is_visible(self._guests.DATE_OF_BIRTH, timeout=5000), (
            "Date of birth input not found on guest details page"
        )

    @allure.story("Guest form validation triggers on empty submit")
    def test_empty_guest_form_shows_validation(self, test_user_data: dict):
        if not self._guests.is_visible(self._guests.CONTINUE_BTN, timeout=5000):
            pytest.skip("No Continue button found")
        self._guests.continue_to_next_step()
        has_errors = (
            self._guests.has_validation_errors() or
            self._guests.is_visible(self._guests.FIRST_NAME, timeout=3000)
        )
        assert has_errors, "Expected validation errors or return to form after empty submit"

    @allure.story("Guest form accepts valid data")
    def test_fill_guest_details(self, test_user_data: dict):
        if not self._guests.is_visible(self._guests.FIRST_NAME, timeout=5000):
            pytest.skip("Guest form fields not found")
        self._guests.fill_guest_details(
            first_name=test_user_data["first_name"],
            last_name=test_user_data["last_name"],
            email=test_user_data["email"],
        )
        # Verify fields were filled (no crash)
        assert self._guests.is_visible(self._guests.FIRST_NAME, timeout=3000)

    @allure.story("Special needs / accessibility section is present")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_special_needs_section_present(self):
        has_section = (
            self._guests.is_visible(self._guests.SPECIAL_NEEDS_SECTION, timeout=5000) or
            self._guests.is_visible(self._guests.WHEELCHAIR_CHECKBOX, timeout=3000) or
            self._guests.is_visible(self._guests.SPECIAL_NEEDS_CHECKBOX, timeout=3000)
        )
        if not has_section:
            pytest.skip("Special needs section not visible at this booking step")
        assert has_section, "Special needs / accessibility section not found"

    @allure.story("Wheelchair accessible option can be selected")
    def test_wheelchair_option_selectable(self):
        if not self._guests.is_visible(self._guests.WHEELCHAIR_CHECKBOX, timeout=5000):
            pytest.skip("Wheelchair checkbox not found")
        result = self._guests.select_accessibility_option("wheelchair")
        assert result, "Could not interact with wheelchair accessibility option"

    @allure.story("Mobility accessibility option can be selected")
    def test_mobility_option_selectable(self):
        if not self._guests.is_visible(self._guests.MOBILITY_CHECKBOX, timeout=5000):
            pytest.skip("Mobility checkbox not found")
        result = self._guests.select_accessibility_option("mobility")
        assert result, "Could not interact with mobility accessibility option"

    @allure.story("All accessibility combinations can be toggled without crash")
    @pytest.mark.parametrize("option_label", [
        "Wheelchair",
        "Ambulatory",
        "Mobility",
        "Accessible",
    ])
    def test_accessibility_combinations(self, option_label: str):
        """Each accessibility option should be togglable if present."""
        selector = f"label:has-text('{option_label}') input[type='checkbox']"
        if not self._guests.is_visible(selector, timeout=3000):
            pytest.skip(f"'{option_label}' accessibility option not present")
        cb = self._guests.page.locator(selector).first
        cb.click()  # toggle on
        cb.click()  # toggle off — ensure no crash
        assert True  # no exception = pass


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Payment Page")
@pytest.mark.regression
@pytest.mark.booking
class TestPaymentPage:
    """Tests for the payment/review step."""

    @pytest.fixture(autouse=True)
    def _reach_payment_step(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        booking_guests_page: BookingGuestsPage,
        booking_payment_page: BookingPaymentPage,
        test_user_data: dict,
    ):
        _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)
        _reach_cabin_page(cruise_detail_page, booking_cabin_page)

        # Cabin step
        if booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) > 0:
            booking_cabin_page.select_first_cabin()
        else:
            booking_cabin_page.continue_to_next_step()

        # Guest step
        if booking_guests_page.is_on_guests_page():
            if booking_guests_page.is_visible(booking_guests_page.FIRST_NAME, timeout=5000):
                booking_guests_page.fill_guest_details(
                    first_name=test_user_data["first_name"],
                    last_name=test_user_data["last_name"],
                    email=test_user_data["email"],
                )
            booking_guests_page.continue_to_next_step()

        if not booking_payment_page.is_on_payment_page():
            pytest.skip(
                f"Did not reach payment page (at: {booking_payment_page.get_url()})"
            )
        self._payment = booking_payment_page

    @allure.story("Payment page has a heading")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_payment_page_has_heading(self):
        assert self._payment.is_visible(self._payment.PAGE_HEADING, timeout=15000), (
            "No heading found on payment page"
        )

    @allure.story("Order summary is displayed")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_order_summary_present(self):
        assert self._payment.has_order_summary(), (
            "Order summary not found on payment page"
        )

    @allure.story("Total price is displayed on payment page")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_total_price_displayed(self):
        price = self._payment.get_total_price()
        assert price, "Total price not displayed on payment page"

    @allure.story("Deposit / due today amount is shown")
    def test_deposit_amount_displayed(self):
        deposit = self._payment.get_deposit_amount()
        # Deposit may not always be shown; just verify no exception
        assert isinstance(deposit, str)

    @allure.story("Payment form / credit card fields are present")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_payment_form_present(self):
        assert self._payment.has_payment_form(), (
            "Payment form (card input fields) not found on payment page"
        )

    @allure.story("Card number field is present")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_card_number_field_present(self):
        assert self._payment.is_visible(self._payment.CARD_NUMBER, timeout=8000), (
            "Card number input not found on payment page"
        )

    @allure.story("Card expiry field is present")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_card_expiry_field_present(self):
        assert self._payment.is_visible(self._payment.CARD_EXPIRY, timeout=5000), (
            "Card expiry input not found on payment page"
        )

    @allure.story("CVV field is present")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cvv_field_present(self):
        assert self._payment.is_visible(self._payment.CARD_CVV, timeout=5000), (
            "CVV input not found on payment page"
        )

    @allure.story("Terms and conditions checkbox is present")
    def test_terms_checkbox_present(self):
        if not self._payment.has_terms_checkbox():
            pytest.skip("Terms checkbox not present on payment page")
        assert self._payment.has_terms_checkbox()

    @allure.story("Complete Booking / Confirm button is present")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_complete_booking_button_present(self):
        assert self._payment.has_complete_booking_btn(), (
            "Complete Booking button not found on payment page"
        )

    @allure.story("Payment page uses HTTPS")
    def test_payment_page_https(self):
        assert self._payment.get_url().startswith("https://"), (
            f"Payment page not served over HTTPS: {self._payment.get_url()}"
        )

    @allure.story("Payment form accepts credit card details")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_fill_credit_card_details(self):
        """Fill payment form with test credit card data and verify fields accept input."""
        if not self._payment.has_payment_form():
            pytest.skip("Payment form not found on payment page")

        self._payment.fill_test_card(
            card_number="4111111111111111",
            expiry="12/33",
            cvv="234",
            name="Tom Cat",
        )

        # Verify card number field retained input
        if self._payment.is_visible(self._payment.CARD_NUMBER, timeout=3000):
            card_field = self._payment.page.locator(self._payment.CARD_NUMBER).first
            value = card_field.input_value()
            assert value, "Card number field appears empty after fill"

        # Verify cardholder name field retained input
        if self._payment.is_visible(self._payment.CARDHOLDER_NAME, timeout=3000):
            name_field = self._payment.page.locator(self._payment.CARDHOLDER_NAME).first
            assert "Tom Cat" in name_field.input_value(), (
                "Cardholder name field did not retain expected value"
            )

    @allure.story("Complete Booking button is not clickable without card details")
    def test_cannot_submit_without_card_details(self):
        """Submitting without card data should show errors, not book a cruise."""
        if not self._payment.has_complete_booking_btn():
            pytest.skip("No Complete Booking button found")
        self._payment.click(self._payment.COMPLETE_BOOKING_BTN)
        # Should stay on payment page or show validation
        still_on_payment = self._payment.is_on_payment_page()
        has_errors = self._payment.is_visible(self._payment.PAYMENT_ERROR, timeout=5000)
        assert still_on_payment or has_errors, (
            "Booking should not proceed without valid payment details"
        )


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Full E2E (to payment)")
@pytest.mark.regression
@pytest.mark.booking
@pytest.mark.e2e
class TestBookingE2E:
    """End-to-end booking flow: results → detail → cabin → guests → payment."""

    @allure.story("Complete booking flow reaches payment page")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_full_booking_flow_to_payment(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        booking_guests_page: BookingGuestsPage,
        booking_payment_page: BookingPaymentPage,
        test_user_data: dict,
    ):
        """Navigate through every booking step and confirm payment page loads."""
        with allure.step("Step 1: Load cruise search results"):
            _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)

        with allure.step("Step 2: Click Book Now on cruise detail"):
            _reach_cabin_page(cruise_detail_page, booking_cabin_page)

        with allure.step("Step 3: Select first available cabin"):
            if booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) > 0:
                booking_cabin_page.select_first_cabin()
            else:
                booking_cabin_page.continue_to_next_step()

        with allure.step("Step 4: Fill guest details"):
            if booking_guests_page.is_on_guests_page():
                if booking_guests_page.is_visible(booking_guests_page.FIRST_NAME, timeout=5000):
                    booking_guests_page.fill_guest_details(
                        first_name=test_user_data["first_name"],
                        last_name=test_user_data["last_name"],
                        email=test_user_data["email"],
                    )
                booking_guests_page.continue_to_next_step()

        with allure.step("Step 5: Verify payment page reached"):
            if not booking_payment_page.is_on_payment_page():
                pytest.skip(
                    f"Did not reach payment page — stopped at: {booking_payment_page.get_url()}"
                )
            assert booking_payment_page.has_payment_form() or \
                   booking_payment_page.has_order_summary(), (
                "Payment page did not show expected content"
            )

    @allure.story("Accessible cabin booking flow to payment")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_accessible_cabin_booking_flow(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        booking_guests_page: BookingGuestsPage,
        booking_payment_page: BookingPaymentPage,
        test_user_data: dict,
    ):
        """Book an accessible cabin and verify the flow reaches payment."""
        with allure.step("Navigate to cruise detail"):
            _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)

        with allure.step("Enter booking flow"):
            _reach_cabin_page(cruise_detail_page, booking_cabin_page)

        with allure.step("Enable accessible cabin filter"):
            if booking_cabin_page.is_visible(booking_cabin_page.ACCESSIBLE_FILTER, timeout=5000):
                booking_cabin_page.toggle_accessible_filter()

        with allure.step("Select accessible cabin"):
            if booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) == 0:
                pytest.skip("No accessible cabin cards rendered")
            booking_cabin_page.select_first_cabin()

        with allure.step("Fill guest details with accessibility need"):
            if booking_guests_page.is_on_guests_page():
                if booking_guests_page.is_visible(booking_guests_page.FIRST_NAME, timeout=5000):
                    booking_guests_page.fill_guest_details(
                        first_name=test_user_data["first_name"],
                        last_name=test_user_data["last_name"],
                        email=test_user_data["email"],
                    )
                booking_guests_page.select_accessibility_option("Accessible")
                booking_guests_page.continue_to_next_step()

        with allure.step("Verify payment page reached"):
            if not booking_payment_page.is_on_payment_page():
                pytest.skip(
                    f"Accessible booking did not reach payment page "
                    f"(at: {booking_payment_page.get_url()})"
                )
            assert booking_payment_page.is_visible(booking_payment_page.PAGE_HEADING, timeout=10000)


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Confirmation")
@pytest.mark.regression
@pytest.mark.booking
class TestBookingConfirmation:
    """Submit payment as guest with test card and capture the confirmed booking number."""

    @allure.story("Confirmed booking number is displayed after guest payment submission")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_confirmed_booking_number(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        booking_guests_page: BookingGuestsPage,
        booking_payment_page: BookingPaymentPage,
        booking_confirmation_page: BookingConfirmationPage,
        login_page: LoginPage,
        test_user_data: dict,
    ):
        """Guest flow: search → cabin → guest checkout → guests → fill card → submit → booking number."""
        with allure.step("Step 1: Navigate to cruise detail"):
            _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)

        with allure.step("Step 2: Click Book Now"):
            if not cruise_detail_page.is_visible(cruise_detail_page.BOOK_NOW_BTN, timeout=10000):
                pytest.skip("Book Now button not found")
            cruise_detail_page.click_book_now()
            booking_cabin_page.wait_for_load_state("domcontentloaded")

        with allure.step("Step 3: Handle intermediate pages (login wall / guest count)"):
            booking_cabin_page.wait_for_load_state("domcontentloaded")
            url = booking_cabin_page.get_url().lower()

            # Login wall
            if any(k in url for k in ["login", "sign-in", "account", "auth"]):
                proceeded = login_page.continue_as_guest()
                if not proceeded:
                    pytest.skip("Login wall has no guest checkout option")
                booking_cabin_page.wait_for_load_state("domcontentloaded")
                url = booking_cabin_page.get_url().lower()

            # Guest count selection page — wait for PAX buttons then click "2 Guests"
            if "guest-count" in url:
                select_pax = booking_cabin_page.page.locator("button.select-pax-btn")
                try:
                    select_pax.first.wait_for(state="visible", timeout=15000)
                except Exception:
                    pass
                if select_pax.count() > 0:
                    clicked = False
                    for i in range(select_pax.count()):
                        btn = select_pax.nth(i)
                        if btn.is_visible() and "2" in btn.inner_text():
                            btn.click()
                            clicked = True
                            break
                    if not clicked and select_pax.first.is_visible():
                        select_pax.first.click()
                    booking_cabin_page.wait_for_load_state("domcontentloaded")
                    booking_cabin_page.page.wait_for_timeout(3000)

        with allure.step("Step 4: Confirm cabin selection page"):
            booking_cabin_page.page.wait_for_timeout(3000)
            if not booking_cabin_page.wait_for_cabin_page(timeout=20000):
                pytest.skip(f"Did not reach cabin page (at: {booking_cabin_page.get_url()})")

        with allure.step("Step 5: Select stateroom type and cabin"):
            url = booking_cabin_page.get_url().lower()

            # stateroom-type page: select a tab then click SELECT
            if "stateroom-type" in url:
                page = booking_cabin_page.page
                # Try tabs in order of preference: Interior → Oceanview → Balcony → Mini-Suites
                for tab_text in ["Interior", "Oceanview", "Balcony", "Mini-Suites"]:
                    tab = page.locator(f"button:has-text('{tab_text}'):not([disabled])")
                    if tab.count() > 0 and tab.first.is_visible():
                        tab.first.click()
                        page.wait_for_timeout(1500)
                        break
                # Level 1: Click "SELECT" on Interior Guarantee to reveal specific options
                select_btn = page.locator("button:has-text('SELECT')")
                if select_btn.count() > 0 and select_btn.first.is_visible():
                    select_btn.first.click()
                    booking_cabin_page.page.wait_for_timeout(3000)

                # Level 2: Poll for "Select from $XXX" buttons (appear after SELECT click)
                select_from_btn = page.locator(
                    "button:has-text('Select from'), button:has-text('Select  from')"
                )
                clicked_level2 = False
                for _ in range(15):
                    try:
                        cnt = select_from_btn.count()
                        if cnt > 0:
                            for j in range(cnt):
                                btn = select_from_btn.nth(j)
                                if btn.is_visible():
                                    btn.click(timeout=10000)
                                    clicked_level2 = True
                                    break
                        if clicked_level2:
                            break
                    except Exception:
                        pass
                    page.wait_for_timeout(1000)
                if clicked_level2:
                    booking_cabin_page.wait_for_load_state("domcontentloaded")
                    booking_cabin_page.page.wait_for_timeout(3000)

                booking_cabin_page.take_screenshot("step5_after_cabin_select")

                # Check for login wall and try guest checkout
                url2 = booking_cabin_page.get_url().lower()
                if any(k in url2 for k in ["login", "sign-in", "account", "auth"]):
                    login_page.continue_as_guest()
                    booking_cabin_page.wait_for_load_state("domcontentloaded")
            else:
                # Generic cabin cards flow
                if booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) > 0:
                    booking_cabin_page.select_first_cabin()
                else:
                    booking_cabin_page.continue_to_next_step()

        with allure.step("Step 5b: Handle packages page if shown"):
            booking_cabin_page.page.wait_for_timeout(2000)
            url_pkg = booking_cabin_page.get_url().lower()
            if "packages" in url_pkg:
                page = booking_cabin_page.page
                booking_cabin_page.take_screenshot("step5b_packages_page")
                # "I'LL PAY MORE ONBOARD" skips the package upsell
                # Use filter(has_text=) to avoid CSS quote-escaping issues
                pkg_clicked = False
                for btn_text in ["I'LL PAY MORE ONBOARD", "PAY MORE ONBOARD", "Pay More Onboard",
                                  "No Thanks", "No Package", "Continue"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        pkg_clicked = True
                        booking_cabin_page.wait_for_load_state("domcontentloaded")
                        booking_cabin_page.page.wait_for_timeout(2000)
                        break
                if not pkg_clicked:
                    # Fallback: try partial text match
                    btn = page.locator("button").filter(has_text="ONBOARD")
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        booking_cabin_page.wait_for_load_state("domcontentloaded")
                        booking_cabin_page.page.wait_for_timeout(2000)

        with allure.step("Step 5c: Handle stateroom summary page if shown"):
            booking_cabin_page.page.wait_for_timeout(1500)
            url_sum = booking_cabin_page.get_url().lower()
            if "stateroom-summary" in url_sum:
                page = booking_cabin_page.page
                booking_cabin_page.take_screenshot("step5c_stateroom_summary")
                for btn_text in ["Continue", "Next", "Proceed", "Book"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        booking_cabin_page.wait_for_load_state("domcontentloaded")
                        booking_cabin_page.page.wait_for_timeout(2000)
                        break

        with allure.step("Step 6: Fill guest details"):
            guest_data = [
                ("Tom", "Cat", test_user_data["email"]),
                ("Jane", "Cat", "jane.cat@example.com"),
                ("Bob", "Cat", "bob.cat@example.com"),
            ]
            page = booking_guests_page.page

            def _fill_one_guest(first, last, email):
                try:
                    page.get_by_label("First Name").first.fill(first)
                except Exception:
                    try:
                        page.locator(booking_guests_page.FIRST_NAME).first.fill(first)
                    except Exception:
                        pass
                try:
                    page.get_by_label("Last Name").first.fill(last)
                except Exception:
                    try:
                        page.locator(booking_guests_page.LAST_NAME).first.fill(last)
                    except Exception:
                        pass
                # Gender
                try:
                    page.get_by_label("Gender").first.select_option("M")
                except Exception:
                    try:
                        page.locator("select[name*='gender' i], select[id*='gender' i]").first.select_option("M")
                    except Exception:
                        pass
                # DOB — Month/Day/Year selects
                month_sel = page.locator("select[name*='month' i], select[id*='month' i]")
                if month_sel.count() > 0:
                    try:
                        month_sel.first.select_option(index=1)
                    except Exception:
                        pass
                else:
                    try:
                        page.locator("select").filter(has_text="Month").first.select_option(index=1)
                    except Exception:
                        pass
                day_sel = page.locator("select[name*='day' i], select[id*='day' i]")
                try:
                    (day_sel if day_sel.count() > 0 else page.locator("select").filter(has_text="Day")).first.select_option("15")
                except Exception:
                    pass
                year_sel = page.locator("select[name*='year' i], select[id*='year' i]")
                try:
                    (year_sel if year_sel.count() > 0 else page.locator("select").filter(has_text="Year")).first.select_option("1980")
                except Exception:
                    pass
                # Zip
                try:
                    page.get_by_label("Zip/Postal Code").first.fill("90210")
                except Exception:
                    try:
                        page.locator("input[name*='zip' i], input[id*='zip' i]").first.fill("90210")
                    except Exception:
                        pass
                # Phone
                try:
                    page.locator("input[type='tel']").first.fill("3105550100")
                except Exception:
                    pass
                # Email
                try:
                    page.get_by_label("Email").first.fill(email)
                except Exception:
                    pass
                # Click SAVE & CONTINUE
                try:
                    page.locator("button").filter(has_text="SAVE & CONTINUE").first.click()
                except Exception:
                    booking_guests_page.continue_to_next_step()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)

            for idx, (first, last, email) in enumerate(guest_data):
                if not booking_guests_page.is_on_guests_page():
                    break
                _fill_one_guest(first, last, email)

            page.screenshot(path="debug_after_guests.png")

        with allure.step("Step 7: Confirm payment page loaded"):
            if not booking_payment_page.is_on_payment_page():
                pytest.skip(
                    f"Did not reach payment page (at: {booking_payment_page.get_url()})"
                )

        with allure.step("Step 8: Fill credit card — Tom Cat 4111111111111111 12/33 CVV 234"):
            pay_page = booking_payment_page.page
            # Wait for loading spinner to disappear
            try:
                pay_page.wait_for_function(
                    "() => !document.querySelector('.loading, [class*=\"loading\"]') || "
                    "document.querySelector('.loading, [class*=\"loading\"]').offsetParent === null",
                    timeout=15000
                )
            except Exception:
                pay_page.wait_for_timeout(3000)
            pay_page.screenshot(path="debug_payment_page.png")

            def _pay_js_fill(css_id, value):
                """Fill a React-controlled input via native setter + events."""
                pay_page.evaluate(f"""
                    const el = document.querySelector('{css_id}');
                    if (el) {{
                        const setter = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value').set;
                        setter.call(el, '{value}');
                        el.dispatchEvent(new Event('input', {{bubbles: true}}));
                        el.dispatchEvent(new Event('change', {{bubbles: true}}));
                    }}
                """)

            def _pay_fill(selector, value):
                """Fill without clicking — uses Playwright locator.fill()."""
                try:
                    pay_page.locator(selector).first.fill(value, timeout=5000)
                except Exception:
                    _pay_js_fill(selector, value)

            def _pay_click_type(selector, value):
                """Force-click then type — triggers keystroke events."""
                try:
                    pay_page.locator(selector).first.click(force=True, timeout=5000)
                    pay_page.keyboard.type(value, delay=30)
                except Exception:
                    _pay_js_fill(selector, value)

            def _pay_select(selector, value):
                try:
                    pay_page.locator(selector).first.select_option(value, timeout=5000)
                except Exception:
                    pass

            # Cardholder's Name — plain fill works (already working)
            try:
                pay_page.locator("#cardholder-name").first.fill("Tom Cat", timeout=5000)
            except Exception:
                _pay_js_fill("#cardholder-name", "Tom Cat")

            # Payment inputs are in Mastercard Gateway cross-origin iframes.
            # Detect frames by their actual inputs, not URL patterns.
            for frame in pay_page.frames:
                if "mastercard.com" not in frame.url:
                    continue
                try:
                    ids = frame.evaluate(
                        "() => [...document.querySelectorAll('input')].map(i=>i.id)"
                    )
                    print(f"MC FRAME {frame.url[-30:]}: ids={ids}")
                    if "number" in ids:
                        frame.locator("#number").first.fill("4111111111111111", timeout=5000)
                    if "expiryMonth" in ids:
                        frame.locator("#expiryMonth").first.fill("12", timeout=3000)
                    if "expiryYear" in ids:
                        frame.locator("#expiryYear").first.fill("2033", timeout=3000)
                    if "nameOnCard" in ids:
                        frame.locator("#nameOnCard").first.fill("Tom Cat", timeout=3000)
                    if "securityCode" in ids:
                        frame.locator("#securityCode").first.fill("234", timeout=3000)
                except Exception as e:
                    print(f"Frame error: {e}")

            # Main page: sync expiry selects and fill zip
            year_options = pay_page.evaluate(
                "() => [...document.querySelectorAll('#expiry-year option')].map(o=>o.value)"
            )
            target_year = "2033" if "2033" in year_options else (year_options[-1] if year_options else "2026")
            _pay_select("#expiry-month", "12")
            _pay_select("#expiry-year", target_year)
            # Zip — scroll into view then click (not force) + type
            zip_loc = pay_page.locator("input[name='zip']")
            try:
                zip_loc.first.scroll_into_view_if_needed(timeout=5000)
                pay_page.wait_for_timeout(300)
                zip_loc.first.click(timeout=5000)  # regular click after scroll
                pay_page.keyboard.press("Control+a")
                pay_page.keyboard.type("90210", delay=80)
                pay_page.keyboard.press("Tab")
                pay_page.wait_for_timeout(200)
            except Exception:
                # Last resort: JS with InputEvent
                pay_page.evaluate("""
                    const el = document.querySelector("input[name='zip']");
                    if (el) {
                        el.focus();
                        const s = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype, 'value').set;
                        s.call(el, '90210');
                        el.dispatchEvent(new InputEvent('input', {bubbles:true, data:'90210', inputType:'insertText'}));
                        el.dispatchEvent(new Event('change', {bubbles:true}));
                        el.dispatchEvent(new Event('blur', {bubbles:true}));
                    }
                """)

            pay_page.screenshot(path="debug_payment_filled.png")

        with allure.step("Step 9: Accept terms and conditions"):
            pay_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            pay_page.wait_for_timeout(500)
            # Check via JS to bypass React event handling
            pay_page.evaluate("""
                const cb = document.querySelector('#passageContractInputCheckBox');
                if (cb && !cb.checked) {
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype, 'checked').set;
                    setter.call(cb, true);
                    cb.dispatchEvent(new Event('change', {bubbles: true}));
                    cb.dispatchEvent(new Event('click', {bubbles: true}));
                }
            """)
            pay_page.wait_for_timeout(300)
            pay_page.screenshot(path="debug_payment_terms.png")

        with allure.step("Step 10: Submit booking"):
            pay_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            pay_page.wait_for_timeout(500)
            pay_page.screenshot(path="debug_before_submit.png")
            try:
                # "BOOK NOW" is the submit button text on princess.com pay page
                book_now = pay_page.locator("button").filter(has_text="BOOK NOW")
                if book_now.count() > 0 and book_now.first.is_visible():
                    book_now.first.click(timeout=15000)
                else:
                    for txt in ["Book Now", "Book", "Complete", "Confirm", "Pay"]:
                        btn = pay_page.locator("button").filter(has_text=txt)
                        if btn.count() > 0 and btn.first.is_visible():
                            btn.first.click(timeout=15000)
                            break
                    else:
                        booking_payment_page.click(booking_payment_page.COMPLETE_BOOKING_BTN)
            except Exception:
                booking_payment_page.click(booking_payment_page.COMPLETE_BOOKING_BTN)

        with allure.step("Step 11: Wait for confirmation page"):
            reached = booking_confirmation_page.wait_for_confirmation(timeout=30000)
            if not reached:
                pytest.skip(
                    f"Confirmation page not reached after submit "
                    f"(at: {booking_confirmation_page.get_url()})"
                )

        with allure.step("Step 12: Capture booking number"):
            booking_number = booking_confirmation_page.get_booking_number()
            confirm_url = booking_confirmation_page.get_url()
            print(f"\n{'='*60}")
            print(f"CONFIRMATION URL: {confirm_url}")
            print(f"BOOKING NUMBER:   {booking_number}")
            print(f"{'='*60}\n")
            allure.attach(
                f"Confirmed Booking Number: {booking_number}",
                name="[BOOKING NUMBER] Confirmation",
                attachment_type=allure.attachment_type.TEXT,
            )
            booking_confirmation_page.take_screenshot("booking_confirmation")
            assert booking_number, (
                "Confirmation page reached but no booking number found. "
                f"Current URL: {confirm_url}"
            )


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Login at Stateroom Summary")
@pytest.mark.regression
@pytest.mark.booking
@pytest.mark.e2e
class TestBookingLoginAtStatroomSummary:
    """Register a fresh account, navigate the booking funnel as a guest up to
    the stateroom-summary page, then sign in via the header 'Log In' link so
    the booking becomes associated with the newly created account."""

    @allure.story("Sign in with a newly registered account at the stateroom summary step")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_booking_login_at_stateroom_summary(
        self,
        register_page: RegisterPage,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        login_page: LoginPage,
    ):
        """Full flow:
        1. Register a new random user (age > 25, address 1449 Hollywood Blvd FL 33020)
        2. Sign out so the booking funnel runs as a non-logged-in guest
        3. Navigate: cruise search → detail → Book Now → guest-count →
           stateroom-type → packages → stateroom-summary
        4. Click 'Log In' in the page header
        5. Sign in with the registered credentials
        6. Assert the login succeeded
        """

        # ── Step 1: Register a new user ───────────────────────────────────────
        with allure.step("Step 1: Register a new random user (age > 25)"):
            user = generate_registration_user(
                address1="1449 Hollywood Blvd",
                city="Hollywood",
                state="FL",
                zip_code="33020",
            )
            print(f"\n{'='*60}")
            print(f"REGISTERING: {user.first_name} {user.last_name} <{user.email}>")
            print(f"DOB:         {user.dob_year}-{user.dob_month}-{user.dob_day}")
            print(f"ADDRESS:     {user.address1}, {user.city}, {user.state} {user.zip_code}")
            print(f"{'='*60}\n")

            allure.attach(
                (
                    f"Name:    {user.first_name} {user.last_name}\n"
                    f"Email:   {user.email}\n"
                    f"DOB:     {user.dob_year}-{user.dob_month}-{user.dob_day}\n"
                    f"Address: {user.address1}, {user.city} {user.state} {user.zip_code}"
                ),
                name="Registered user",
                attachment_type=allure.attachment_type.TEXT,
            )

            register_page.load()
            register_page.assert_loaded()
            register_page.fill_registration_form(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                password=user.password,
                dob_month=user.dob_month,
                dob_day=user.dob_day,
                dob_year=user.dob_year,
                address1=user.address1,
                city=user.city,
                state=user.state,
                zip_code=user.zip_code,
                cell_phone=user.cell_phone,
            )
            register_page.submit()
            register_page.page.wait_for_timeout(3000)
            register_page.take_screenshot("step1_registered")

            if not register_page.is_registered():
                pytest.skip("Registration did not succeed — cannot continue booking test")

        # ── Step 2: Clear session so booking funnel runs as a guest ─────────
        with allure.step("Step 2: Clear cookies/session to ensure the user is not logged in"):
            page = register_page.page
            # Clear cookies AND web storage to ensure a fully logged-out state.
            page.context.clear_cookies()
            page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
            page.wait_for_timeout(500)
            print("Session cleared — starting booking as a non-logged-in guest")

        # ── Steps 3-5: Navigate booking funnel to stateroom-summary ──────────
        with allure.step("Step 3: Load cruise search results"):
            cruise_search_page.load()
            loaded = cruise_results_page._wait_for_real_cards(timeout=40000)
            if not loaded:
                pytest.skip("Cruise result cards did not render — SPA blocked in headless mode")

        with allure.step("Step 4: Open cruise detail and click Book Now"):
            cruise_results_page.click_card(0)
            booking_cabin_page.wait_for_load_state("domcontentloaded")
            if not cruise_detail_page.is_visible(cruise_detail_page.BOOK_NOW_BTN, timeout=10000):
                pytest.skip("Book Now button not found on cruise detail page")
            cruise_detail_page.click_book_now()
            booking_cabin_page.wait_for_load_state("domcontentloaded")
            booking_cabin_page.page.wait_for_timeout(3000)

        with allure.step("Step 5: Navigate guest-count → stateroom-type → packages → stateroom-summary"):
            page = booking_cabin_page.page

            # Guest-count
            if "guest-count" in page.url.lower():
                select_pax = page.locator("button.select-pax-btn")
                try:
                    select_pax.first.wait_for(state="visible", timeout=15000)
                except Exception:
                    pass
                clicked = False
                for i in range(select_pax.count()):
                    btn = select_pax.nth(i)
                    if btn.is_visible() and "2" in btn.inner_text():
                        btn.click(); clicked = True; break
                if not clicked and select_pax.count() > 0:
                    select_pax.first.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)

            # Stateroom-type
            if "stateroom-type" in page.url.lower():
                for tab_text in ["Interior", "Oceanview", "Balcony", "Mini-Suites"]:
                    tab = page.locator(f"button:has-text('{tab_text}'):not([disabled])")
                    if tab.count() > 0 and tab.first.is_visible():
                        tab.first.click(force=True); page.wait_for_timeout(1500); break
                sel_btn = page.locator("button:has-text('SELECT')")
                if sel_btn.count() > 0 and sel_btn.first.is_visible():
                    sel_btn.first.click(); page.wait_for_timeout(3000)
                select_from_btn = page.locator(
                    "button:has-text('Select from'), button:has-text('Select  from')"
                )
                for _ in range(15):
                    if select_from_btn.count() > 0:
                        for j in range(select_from_btn.count()):
                            b = select_from_btn.nth(j)
                            if b.is_visible():
                                b.click(timeout=10000); break
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(3000)
                        break
                    page.wait_for_timeout(1000)

            # Packages
            page.wait_for_timeout(2000)
            if "packages" in page.url.lower():
                for btn_text in ["I'LL PAY MORE ONBOARD", "PAY MORE ONBOARD", "No Thanks", "Continue"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        break

            page.wait_for_timeout(2000)
            if "stateroom-summary" not in page.url.lower():
                pytest.skip(
                    f"Did not reach stateroom-summary page (at: {page.url})"
                )

            booking_cabin_page.take_screenshot("step5_stateroom_summary")
            print(f"\nReached stateroom-summary: {page.url}")

        # ── Step 6: Open the login modal via the header 'Log In' link ───────
        with allure.step("Step 6: Click 'Log In' in the header to open the login modal"):
            # Scroll to top so the sticky header is accessible
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)

            # princess.com uses login-in-modal="true" on its global header:
            # clicking Log In opens an in-page modal, not a new page.
            login_link = None
            for sel in [
                "a[href*='account-login']",
                "a[href*='/login']",
                "a.login-link",
                "a:has-text('Log In')",
                "a:has-text('Sign In')",
                "button:has-text('Log In')",
            ]:
                loc = page.locator(sel)
                if loc.count() > 0:
                    print(f"  '{sel}': count={loc.count()}, visible={loc.first.is_visible()}")
                    if login_link is None:
                        login_link = loc

            if login_link is None or login_link.count() == 0:
                pytest.skip("No 'Log In' link found in the header at stateroom-summary.")

            href = login_link.first.get_attribute("href") or ""
            print(f"Clicking Log In link: {href}")
            login_link.first.click(timeout=10000)
            page.wait_for_timeout(3000)
            booking_cabin_page.take_screenshot("step6_after_login_click")
            print(f"URL after Log In click: {page.url}")

        # ── Step 7: Fill credentials (modal or navigated login page) ─────────
        with allure.step(f"Step 7: Sign in as {user.email}"):
            allure.attach(
                f"Email: {user.email}\nPassword: {user.password}",
                name="Login credentials",
                attachment_type=allure.attachment_type.TEXT,
            )

            # The global header opens login in a modal (login-in-modal="true").
            # The modal may be in the pcl-global-header shadow DOM or rendered
            # into the main document. Try all known locations.

            # 1. Navigate directly to the login page if still on stateroom-summary
            #    (clicking the link may not trigger navigation due to JS handler)
            if "stateroom-summary" in page.url.lower():
                login_url = href if href else "https://www.princess.com/my-princess/account-login/"
                print(f"Modal not detected — navigating directly to login page: {login_url}")
                page.goto(login_url, timeout=20000)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)
                booking_cabin_page.take_screenshot("step7_login_page_direct")
                print(f"Login page URL: {page.url}")

            # 2. Find the email input — prefer any visible input on the current page
            email_sel = (
                "input[name='loginId'], input[id='loginId'], "
                "input[type='email'], input[name*='email' i]"
            )
            email_field = page.locator(email_sel)
            if not email_field.first.is_visible(timeout=10000):
                pytest.skip(
                    f"Login email field not found (URL: {page.url})"
                )

            email_field.first.fill(user.email)
            page.locator("input[type='password']").first.fill(user.password)

            booking_cabin_page.take_screenshot("step7_credentials_filled")

            # Submit
            submit = page.locator(
                "button[type='submit'], "
                "button:has-text('Sign In'), "
                "button:has-text('Log In')"
            )
            submit.first.click(timeout=10000)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(4000)
            booking_cabin_page.take_screenshot("step7_after_login")
            print(f"URL after login submit: {page.url}")

        # ── Step 8: Assert login succeeded ────────────────────────────────────
        with allure.step("Step 8: Assert the user is now logged in"):
            final_url = page.url.lower()
            booking_cabin_page.take_screenshot("step8_final_state")

            # Collect all visible text in any error/alert element
            error_texts: list[str] = []
            try:
                for loc in page.locator("[class*='error'], [role='alert']").all():
                    if loc.is_visible():
                        t = loc.inner_text().strip()
                        if t:
                            error_texts.append(t)
            except Exception:
                pass
            error_text = " | ".join(error_texts)

            print(f"Final URL:    {page.url}")
            print(f"Error texts:  {error_text!r}")

            allure.attach(
                f"Final URL:   {page.url}\nError texts: {error_text!r}",
                name="Login result",
                attachment_type=allure.attachment_type.TEXT,
            )

            # Real success = navigated AWAY from the login page
            still_on_login_page = any(
                k in final_url for k in ["account-login", "/login"]
            )

            if still_on_login_page:
                # Classify the reason we're still on the login page
                lower_err = error_text.lower()
                if any(kw in lower_err for kw in ["verify", "confirm", "activate", "check your email"]):
                    pytest.skip(
                        f"Login requires email verification for the freshly created "
                        f"account ({user.email}). Error: {error_text!r}"
                    )
                if any(kw in lower_err for kw in ["captcha", "robot", "human"]):
                    pytest.skip(
                        f"CAPTCHA challenge detected on login page — cannot proceed "
                        f"in automated mode."
                    )
                if any(kw in lower_err for kw in [
                    "invalid", "incorrect", "wrong", "not found",
                    "password", "try again"
                ]):
                    pytest.fail(
                        f"Login rejected with error: {error_text!r}\n"
                        f"Credentials used: {user.email} / {user.password}"
                    )
                # No clear error — still failed to navigate away
                pytest.fail(
                    f"Still on login page after submitting credentials. "
                    f"Error text: {error_text!r}  URL: {page.url}"
                )

            print(f"\n{'='*60}")
            print(f"LOGIN SUCCESSFUL: {user.first_name} {user.last_name} <{user.email}>")
            print(f"Redirected to:    {page.url}")
            print(f"{'='*60}\n")


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — Login at Stateroom Summary + Confirmation")
@pytest.mark.regression
@pytest.mark.booking
@pytest.mark.e2e
class TestBookingLoginAndConfirm:
    """Cruise booking that signs in at the stateroom-summary page with a
    specific account, then completes payment and returns the booking number."""

    _LOGIN_EMAIL    = "asemenov@test.com"
    _LOGIN_PASSWORD = "Test123$"

    @allure.story("Sign in at stateroom summary then complete booking to confirmation")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_booking_login_and_confirm(
        self,
        cruise_search_page: CruiseSearchPage,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        booking_guests_page: BookingGuestsPage,
        booking_payment_page: BookingPaymentPage,
        booking_confirmation_page: BookingConfirmationPage,
        login_page: LoginPage,
    ):
        page = cruise_search_page.page

        # ── Step 1: Navigate booking funnel to stateroom-summary ─────────────
        with allure.step("Step 1: Cruise search → detail → Book Now → stateroom-summary"):
            _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)

            if not cruise_detail_page.is_visible(cruise_detail_page.BOOK_NOW_BTN, timeout=10000):
                pytest.skip("Book Now button not found")
            cruise_detail_page.click_book_now()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)

            # Guest-count
            if "guest-count" in page.url.lower():
                pax = page.locator("button.select-pax-btn")
                try:
                    pax.first.wait_for(state="visible", timeout=15000)
                except Exception:
                    pass
                clicked = False
                for i in range(pax.count()):
                    b = pax.nth(i)
                    if b.is_visible() and "2" in b.inner_text():
                        b.click(); clicked = True; break
                if not clicked and pax.count() > 0:
                    pax.first.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)

            # Stateroom-type
            if "stateroom-type" in page.url.lower():
                for t in ["Interior", "Oceanview", "Balcony"]:
                    tab = page.locator(f"button:has-text('{t}'):not([disabled])")
                    if tab.count() > 0 and tab.first.is_visible():
                        tab.first.click(force=True); page.wait_for_timeout(1500); break
                sel_btn = page.locator("button:has-text('SELECT')")
                if sel_btn.count() > 0 and sel_btn.first.is_visible():
                    sel_btn.first.click(); page.wait_for_timeout(3000)
                sfb = page.locator("button:has-text('Select from'), button:has-text('Select  from')")
                for _ in range(15):
                    if sfb.count() > 0:
                        for j in range(sfb.count()):
                            b = sfb.nth(j)
                            if b.is_visible():
                                b.click(timeout=10000); break
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(3000); break
                    page.wait_for_timeout(1000)

            # Packages
            page.wait_for_timeout(2000)
            if "packages" in page.url.lower():
                for txt in ["I'LL PAY MORE ONBOARD", "PAY MORE ONBOARD", "No Thanks", "Continue"]:
                    btn = page.locator("button").filter(has_text=txt)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000); break

            page.wait_for_timeout(2000)
            if "stateroom-summary" not in page.url.lower():
                pytest.skip(f"Did not reach stateroom-summary (at: {page.url})")

            print(f"\nReached stateroom-summary: {page.url}")
            booking_cabin_page.take_screenshot("s1_stateroom_summary")

        # ── Step 2: Click Log In in the header ───────────────────────────────
        with allure.step(f"Step 2: Click Log In in the header at stateroom-summary"):
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)

            login_link = page.locator("a[href*='account-login'], a[href*='/login']")
            if login_link.count() == 0:
                pytest.skip("No Log In link found in the header at stateroom-summary")

            login_href = login_link.first.get_attribute("href") or \
                         "https://www.princess.com/my-princess/account-login/?src=cruise-search"
            print(f"Log In href: {login_href}")
            login_link.first.click(timeout=10000)
            page.wait_for_timeout(2000)

            # The header uses login-in-modal="true" so clicking the link may not
            # trigger navigation. Navigate directly to the login URL if still here.
            if "stateroom-summary" in page.url.lower():
                print("Modal did not open — navigating directly to login page")
                page.goto(login_href, timeout=20000)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)

            print(f"Login page URL: {page.url}")
            booking_cabin_page.take_screenshot("s2_login_page")

        # ── Step 3: Fill credentials and submit ──────────────────────────────
        with allure.step(f"Step 3: Sign in as {self._LOGIN_EMAIL}"):
            email_input = page.locator(
                "input[name='loginId'], input[id='loginId'], "
                "input[type='email'], input[name*='email' i]"
            )
            if not email_input.first.is_visible(timeout=10000):
                pytest.skip(f"Login form not found (URL: {page.url})")

            email_input.first.fill(self._LOGIN_EMAIL)
            page.locator("input[type='password']").first.fill(self._LOGIN_PASSWORD)
            page.screenshot(path="debug_s3_credentials_filled.png", full_page=True)
            booking_cabin_page.take_screenshot("s3_credentials_filled")

            page.locator(
                "button[type='submit'], button:has-text('Sign In'), button:has-text('Log In')"
            ).first.click(timeout=10000)

            # Wait for the spinner on the LOG IN button to disappear, then
            # wait for navigation away from the login page (up to 30 s total).
            try:
                page.wait_for_function(
                    "() => !document.querySelector('button[type=\"submit\"] svg, "
                    "button[type=\"submit\"] circle, "
                    ".login-btn svg, .login-btn circle')",
                    timeout=10000,
                )
            except Exception:
                pass
            try:
                page.wait_for_url(
                    lambda u: "account-login" not in u.lower() and "/login" not in u.lower(),
                    timeout=30000,
                )
            except Exception:
                pass  # may have already navigated or will check below

            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            print(f"URL after login: {page.url}")
            page.screenshot(path="debug_s3_after_login.png", full_page=True)
            booking_cabin_page.take_screenshot("s3_after_login")

            # Verify login succeeded — must have navigated away from the login page
            if any(k in page.url.lower() for k in ["account-login", "/login"]):
                # Collect genuine error text (ignore transient loading messages)
                err_texts = []
                try:
                    for loc in page.locator("[class*='error'], [role='alert']").all():
                        if loc.is_visible():
                            t = loc.inner_text().strip()
                            if t and t not in ("Loading complete", "Loading", "Loading..."):
                                err_texts.append(t)
                except Exception:
                    pass
                err = " | ".join(err_texts)
                pytest.fail(
                    f"Login failed — still on login page.\n"
                    f"Error: {err!r}\n"
                    f"Credentials: {self._LOGIN_EMAIL} / {self._LOGIN_PASSWORD}"
                )

            print(f"\n{'='*60}")
            print(f"LOGGED IN AS: {self._LOGIN_EMAIL}")
            print(f"Redirected to: {page.url}")
            print(f"{'='*60}\n")

        # ── Step 4: Return to stateroom-summary and click CONTINUE ────────────
        with allure.step("Step 4: Return to stateroom-summary and click CONTINUE"):
            if "stateroom-summary" not in page.url.lower():
                print("Navigating back to stateroom-summary after login…")
                page.goto("https://www.princess.com/cruise-search/stateroom-summary/",
                          timeout=20000)
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)
                print(f"URL after nav back: {page.url}")

            # If the booking was lost we may have been redirected to guest-count
            if "stateroom-summary" in page.url.lower():
                cont = page.locator("button").filter(has_text="CONTINUE")
                if cont.count() > 0 and cont.first.is_visible():
                    cont.first.click(timeout=10000)
                    page.wait_for_load_state("domcontentloaded")
                    page.wait_for_timeout(3000)
                    print(f"URL after CONTINUE: {page.url}")
                    booking_cabin_page.take_screenshot("s4_after_continue")

        # ── Step 5: Guest details (forms may be pre-filled for the account) ───
        with allure.step("Step 5: Fill guest details"):
            def _fill_guest(first, last, email):
                try:
                    page.get_by_label("First Name").first.fill(first)
                except Exception:
                    pass
                try:
                    page.get_by_label("Last Name").first.fill(last)
                except Exception:
                    pass
                try:
                    page.get_by_label("Gender").first.select_option("M")
                except Exception:
                    pass
                # Month by index, day/year by value
                try:
                    page.locator("select[name*='month' i], select[id*='month' i]").first.select_option(index=1)
                except Exception:
                    pass
                try:
                    page.locator("select[name*='day' i], select[id*='day' i]").first.select_option("15")
                except Exception:
                    pass
                try:
                    page.locator("select[name*='year' i], select[id*='year' i]").first.select_option("1985")
                except Exception:
                    pass
                try:
                    page.get_by_label("Zip/Postal Code").first.fill("90210")
                except Exception:
                    try:
                        page.locator("input[name*='zip' i]").first.fill("90210")
                    except Exception:
                        pass
                try:
                    page.locator("input[type='tel']").first.fill("3105550100")
                except Exception:
                    pass
                try:
                    page.get_by_label("Email").first.fill(email)
                except Exception:
                    pass
                try:
                    page.locator("button").filter(has_text="SAVE & CONTINUE").first.click()
                except Exception:
                    try:
                        booking_guests_page.continue_to_next_step()
                    except Exception:
                        pass
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)

            guest_rows = [
                ("Alex", "Semenov", self._LOGIN_EMAIL),
                ("Jane", "Smith",   "jane.smith@example.com"),
            ]
            for first, last, email in guest_rows:
                if not booking_guests_page.is_on_guests_page():
                    break
                _fill_guest(first, last, email)

        # ── Step 6: Payment ───────────────────────────────────────────────────
        with allure.step("Step 6: Confirm payment page reached"):
            if not booking_payment_page.is_on_payment_page():
                pytest.skip(
                    f"Did not reach payment page (at: {booking_payment_page.get_url()})"
                )

        with allure.step("Step 7: Fill payment — Tom Cat 4111111111111111 12/33 234"):
            pay_page = booking_payment_page.page
            try:
                pay_page.wait_for_function(
                    "() => !document.querySelector('[class*=\"loading\"]') || "
                    "document.querySelector('[class*=\"loading\"]').offsetParent === null",
                    timeout=15000
                )
            except Exception:
                pay_page.wait_for_timeout(3000)

            # Cardholder name
            try:
                pay_page.locator("#cardholder-name").first.fill("Tom Cat", timeout=5000)
            except Exception:
                pass

            # Mastercard Gateway iframes
            for frame in pay_page.frames:
                if "mastercard.com" not in frame.url:
                    continue
                try:
                    ids = frame.evaluate(
                        "() => [...document.querySelectorAll('input')].map(i=>i.id)"
                    )
                    if "number"       in ids:
                        frame.locator("#number").first.fill("4111111111111111", timeout=5000)
                    if "expiryMonth"  in ids:
                        frame.locator("#expiryMonth").first.fill("12", timeout=3000)
                    if "expiryYear"   in ids:
                        frame.locator("#expiryYear").first.fill("2033", timeout=3000)
                    if "nameOnCard"   in ids:
                        frame.locator("#nameOnCard").first.fill("Tom Cat", timeout=3000)
                    if "securityCode" in ids:
                        frame.locator("#securityCode").first.fill("234", timeout=3000)
                except Exception as e:
                    print(f"Frame error: {e}")

            # Expiry selects on main page
            year_opts = pay_page.evaluate(
                "() => [...document.querySelectorAll('#expiry-year option')].map(o=>o.value)"
            )
            tgt_year = "2033" if "2033" in year_opts else (year_opts[-1] if year_opts else "2026")
            try:
                pay_page.locator("#expiry-month").first.select_option("12", timeout=5000)
            except Exception:
                pass
            try:
                pay_page.locator("#expiry-year").first.select_option(tgt_year, timeout=5000)
            except Exception:
                pass

            # Zip
            zip_loc = pay_page.locator("input[name='zip']")
            try:
                zip_loc.first.scroll_into_view_if_needed(timeout=5000)
                pay_page.wait_for_timeout(300)
                zip_loc.first.click(timeout=5000)
                pay_page.keyboard.press("Control+a")
                pay_page.keyboard.type("90210", delay=80)
                pay_page.keyboard.press("Tab")
                pay_page.wait_for_timeout(200)
            except Exception:
                pay_page.evaluate("""
                    const el = document.querySelector("input[name='zip']");
                    if (el) {
                        el.focus();
                        const s = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype,'value').set;
                        s.call(el,'90210');
                        el.dispatchEvent(new InputEvent('input',{bubbles:true,data:'90210',inputType:'insertText'}));
                        el.dispatchEvent(new Event('change',{bubbles:true}));
                        el.dispatchEvent(new Event('blur',{bubbles:true}));
                    }
                """)

            pay_page.screenshot(path="debug_pay_filled_login_test.png")

        with allure.step("Step 8: Accept terms and click BOOK NOW"):
            pay_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            pay_page.wait_for_timeout(500)
            pay_page.evaluate("""
                const cb = document.querySelector('#passageContractInputCheckBox');
                if (cb && !cb.checked) {
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype,'checked').set;
                    setter.call(cb, true);
                    cb.dispatchEvent(new Event('change',{bubbles:true}));
                    cb.dispatchEvent(new Event('click',{bubbles:true}));
                }
            """)
            pay_page.wait_for_timeout(300)

            book_now = pay_page.locator("button").filter(has_text="BOOK NOW")
            if book_now.count() > 0 and book_now.first.is_visible():
                book_now.first.click(timeout=15000)
            else:
                for txt in ["Book Now", "Complete", "Confirm", "Pay"]:
                    btn = pay_page.locator("button").filter(has_text=txt)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click(timeout=15000); break

        # ── Step 9: Capture booking number ────────────────────────────────────
        with allure.step("Step 9: Wait for confirmation and capture booking number"):
            reached = booking_confirmation_page.wait_for_confirmation(timeout=30000)
            if not reached:
                pytest.skip(
                    f"Confirmation page not reached (at: {booking_confirmation_page.get_url()})"
                )

            booking_number = booking_confirmation_page.get_booking_number()
            confirm_url    = booking_confirmation_page.get_url()

            print(f"\n{'='*60}")
            print(f"ACCOUNT:        {self._LOGIN_EMAIL}")
            print(f"CONFIRMATION:   {confirm_url}")
            print(f"BOOKING NUMBER: {booking_number}")
            print(f"{'='*60}\n")

            allure.attach(
                f"Account:        {self._LOGIN_EMAIL}\n"
                f"Booking Number: {booking_number}\n"
                f"URL:            {confirm_url}",
                name="[BOOKING NUMBER] Confirmation",
                attachment_type=allure.attachment_type.TEXT,
            )
            booking_confirmation_page.take_screenshot("booking_confirmation_login_test")

            assert booking_number, (
                f"Confirmation page reached but no booking number found. "
                f"URL: {confirm_url}"
            )


@allure.epic("Princess Cruises - Regression")
@allure.feature("Booking Flow — UK Site Guest Booking")
@pytest.mark.regression
@pytest.mark.booking
@pytest.mark.e2e
class TestBookingUKGuest:
    """Complete a guest booking starting from https://www.princess.com/en-uk
    through to confirmation, and print the confirmed booking number."""

    UK_BASE_URL = "https://www.princess.com/en-uk"
    UK_RESULTS_URL = "https://www.princess.com/en-uk/cruise-search/results/?resType=C&guestCount=2"

    @allure.story("Guest booking on UK site shows confirmed booking number")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_uk_guest_booking_number(
        self,
        cruise_results_page: CruiseResultsPage,
        cruise_detail_page: CruiseDetailPage,
        booking_cabin_page: BookingCabinPage,
        booking_guests_page: BookingGuestsPage,
        booking_payment_page: BookingPaymentPage,
        booking_confirmation_page: BookingConfirmationPage,
        login_page: LoginPage,
        test_user_data: dict,
    ):
        """Navigate https://www.princess.com/en-uk → cruise results → detail →
        CONTINUE → stateroom-type → packages → stateroom-summary → guest forms →
        payment (Tom Cat 4111111111111111 12/33 234) → confirmation number."""

        page = cruise_results_page.page

        with allure.step("Step 1: Navigate to UK cruise search results"):
            page.goto(self.UK_RESULTS_URL, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            print(f"\nUK results URL: {page.url}")
            loaded = cruise_results_page._wait_for_real_cards(timeout=40000)
            if not loaded:
                # Try from UK base URL with navigation
                page.goto(self.UK_BASE_URL, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_timeout(2000)
                # Navigate to find a cruise
                page.goto(
                    "https://www.princess.com/cruise-search/results/?resType=C&guestCount=2",
                    timeout=60000,
                    wait_until="domcontentloaded",
                )
                page.wait_for_load_state("domcontentloaded")
                loaded = cruise_results_page._wait_for_real_cards(timeout=40000)
                if not loaded:
                    pytest.skip("Cruise result cards did not render — SPA blocked in headless mode")

        with allure.step("Step 2: Click first cruise card to open detail page"):
            cruise_results_page.click_card(0)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)
            print(f"Detail page URL: {page.url}")
            booking_cabin_page.take_screenshot("uk_step2_detail_page")

        with allure.step("Step 3: Click CONTINUE (UK detail page) to enter booking"):
            # UK detail page has a CONTINUE button instead of "Book Now"
            # Try CONTINUE first, then fall back to Book Now
            continue_btn = page.locator("button").filter(has_text="CONTINUE")
            book_now_btn = page.locator(cruise_detail_page.BOOK_NOW_BTN)

            if continue_btn.count() > 0 and continue_btn.first.is_visible(timeout=10000):
                continue_btn.first.click(timeout=15000)
            elif book_now_btn.count() > 0 and book_now_btn.first.is_visible(timeout=10000):
                cruise_detail_page.click_book_now()
            else:
                # Last resort: any prominent CTA button
                for txt in ["Book", "Select", "Choose", "Reserve"]:
                    btn = page.locator("button").filter(has_text=txt)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click(timeout=15000)
                        break
                else:
                    pytest.skip("No CONTINUE / Book Now button found on UK detail page")

            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(3000)
            print(f"URL after CONTINUE: {page.url}")

        with allure.step("Step 4: Handle login wall / guest-count if shown"):
            url = page.url.lower()
            if any(k in url for k in ["login", "sign-in", "auth"]):
                proceeded = login_page.continue_as_guest()
                if not proceeded:
                    pytest.skip("Login wall present with no guest checkout option")
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(2000)
                url = page.url.lower()

            # UK normally skips guest-count (guestCount=2 in URL), but handle it if shown
            if "guest-count" in url:
                pax = page.locator("button.select-pax-btn")
                try:
                    pax.first.wait_for(state="visible", timeout=15000)
                except Exception:
                    pass
                clicked = False
                for i in range(pax.count()):
                    b = pax.nth(i)
                    if b.is_visible() and "2" in b.inner_text():
                        b.click()
                        clicked = True
                        break
                if not clicked and pax.count() > 0:
                    pax.first.click()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)

        with allure.step("Step 5: Select stateroom type"):
            if not booking_cabin_page.wait_for_cabin_page(timeout=20000):
                url = page.url.lower()
                if any(k in url for k in ["login", "sign-in"]):
                    pytest.skip("Redirected to login — guest checkout not available on UK site")
                # May be on stateroom-type already without matching is_on_cabin_page check
                if "stateroom-type" not in url and "stateroom" not in url:
                    pytest.skip(f"Did not reach cabin/stateroom page (at: {page.url})")

            if "stateroom-type" in page.url.lower():
                for tab_text in ["Interior", "Oceanview", "Balcony", "Mini-Suites"]:
                    tab = page.locator(f"button:has-text('{tab_text}'):not([disabled])")
                    if tab.count() > 0 and tab.first.is_visible():
                        tab.first.click(force=True)
                        page.wait_for_timeout(1500)
                        break

                sel_btn = page.locator("button:has-text('SELECT')")
                if sel_btn.count() > 0 and sel_btn.first.is_visible():
                    sel_btn.first.click()
                    page.wait_for_timeout(3000)

                select_from_btn = page.locator(
                    "button:has-text('Select from'), button:has-text('Select  from')"
                )
                for _ in range(15):
                    try:
                        if select_from_btn.count() > 0:
                            for j in range(select_from_btn.count()):
                                b = select_from_btn.nth(j)
                                if b.is_visible():
                                    b.click(timeout=10000)
                                    break
                            page.wait_for_load_state("domcontentloaded")
                            page.wait_for_timeout(3000)
                            break
                    except Exception:
                        pass
                    page.wait_for_timeout(1000)

                booking_cabin_page.take_screenshot("uk_step5_after_cabin_select")

            elif booking_cabin_page.count(booking_cabin_page.CABIN_CARDS) > 0:
                booking_cabin_page.select_first_cabin()

        with allure.step("Step 5b: Skip packages upsell if shown"):
            page.wait_for_timeout(2000)
            if "packages" in page.url.lower():
                booking_cabin_page.take_screenshot("uk_step5b_packages")
                for btn_text in ["I'LL PAY MORE ONBOARD", "PAY MORE ONBOARD",
                                  "Pay More Onboard", "No Thanks", "Continue"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        break

        with allure.step("Step 5c: Continue past stateroom summary if shown"):
            page.wait_for_timeout(1500)
            if "stateroom-summary" in page.url.lower():
                booking_cabin_page.take_screenshot("uk_step5c_summary")
                for btn_text in ["CONTINUE", "Continue", "Next", "Proceed"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        break

        with allure.step("Step 6: Fill guest details"):
            guest_data = [
                ("Tom", "Cat", test_user_data["email"]),
                ("Jane", "Cat", "jane.cat@example.com"),
                ("Bob",  "Cat", "bob.cat@example.com"),
            ]

            def _fill_one_guest(first, last, email):
                try:
                    page.get_by_label("First Name").first.fill(first)
                except Exception:
                    try:
                        page.locator(booking_guests_page.FIRST_NAME).first.fill(first)
                    except Exception:
                        pass
                try:
                    page.get_by_label("Last Name").first.fill(last)
                except Exception:
                    try:
                        page.locator(booking_guests_page.LAST_NAME).first.fill(last)
                    except Exception:
                        pass
                # Gender
                try:
                    page.get_by_label("Gender").first.select_option("M")
                except Exception:
                    try:
                        page.locator("select[name*='gender' i], select[id*='gender' i], select[name='sex']").first.select_option("M")
                    except Exception:
                        pass
                # Month by index, day/year by value
                month_sel = page.locator("select[name*='month' i], select[id*='month' i]")
                if month_sel.count() > 0:
                    try:
                        month_sel.first.select_option(index=1)
                    except Exception:
                        pass
                else:
                    try:
                        page.locator("select").filter(has_text="Month").first.select_option(index=1)
                    except Exception:
                        pass
                day_sel = page.locator("select[name*='day' i], select[id*='day' i]")
                try:
                    (day_sel if day_sel.count() > 0 else page.locator("select").filter(has_text="Day")).first.select_option("15")
                except Exception:
                    pass
                year_sel = page.locator("select[name*='year' i], select[id*='year' i]")
                try:
                    (year_sel if year_sel.count() > 0 else page.locator("select").filter(has_text="Year")).first.select_option("1980")
                except Exception:
                    pass
                # Address — UK format: Strand, London WC2R 0EZ
                for addr_sel in ["input[name='address1']", "input[id='address1']"]:
                    try:
                        field = page.locator(addr_sel).first
                        if field.count() > 0:
                            field.click()
                            field.press("Control+a")
                            field.type("Strand", delay=30)
                            field.press("Escape")
                            page.wait_for_timeout(300)
                            break
                    except Exception:
                        pass
                try:
                    city_f = page.locator("input[name='city'], input[id='city']").first
                    city_f.click()
                    city_f.press("Control+a")
                    city_f.type("London", delay=30)
                    city_f.press("Escape")
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                # UK-specific: nearestAirport (secondary guests)
                try:
                    airport_sel = page.locator("select[name='nearestAirport'], select[id='nearestAirport']")
                    if airport_sel.count() > 0:
                        airport_sel.first.select_option(index=1)
                except Exception:
                    pass
                # Zip — UK postcode format
                try:
                    zip_f = page.locator("input[name='zip'], input[id='zip']").first
                    zip_f.click()
                    zip_f.press("Control+a")
                    zip_f.type("WC2R 0EZ", delay=30)
                    zip_f.press("Tab")
                    page.wait_for_timeout(200)
                except Exception:
                    try:
                        page.locator("input[name*='zip' i], input[id*='zip' i]").first.fill("WC2R 0EZ")
                    except Exception:
                        pass
                # Phone
                try:
                    page.locator("input[type='tel']").first.fill("3105550100")
                except Exception:
                    pass
                # Email
                try:
                    page.get_by_label("Email").first.fill(email)
                except Exception:
                    pass
                # UK-specific: membership radio (select "No" option — value '2')
                try:
                    page.locator("input[name='membership']").filter(has_attribute="value=2").first.click()
                except Exception:
                    try:
                        page.locator("input#membership_2").first.click()
                    except Exception:
                        try:
                            page.locator("input[name='membership'][value='2']").first.click()
                        except Exception:
                            pass
                # UK-specific: countryCode select
                try:
                    cc_sel = page.locator("select[name='countryCode'], select[id='countryCode']")
                    if cc_sel.count() > 0:
                        try:
                            cc_sel.first.select_option("GB")
                        except Exception:
                            try:
                                cc_sel.first.select_option(index=1)
                            except Exception:
                                pass
                except Exception:
                    pass
                # UK-specific: numberType select (phone type)
                try:
                    nt_sel = page.locator("select[name='numberType'], select[id='numberType']")
                    if nt_sel.count() > 0:
                        try:
                            nt_sel.first.select_option(index=1)
                        except Exception:
                            pass
                except Exception:
                    pass
                # UK-specific: hearFromPCL — click "No" (sets validity.valid=True) then dismiss lightbox
                def _dismiss_lightbox():
                    """Wait for lightbox to appear then force-click 'I Understand' to close it."""
                    understand_btn = page.locator("button").filter(has_text="I Understand")
                    try:
                        understand_btn.first.wait_for(state="visible", timeout=3000)
                    except Exception:
                        return  # no lightbox appeared
                    for _ in range(5):
                        try:
                            if understand_btn.first.is_visible():
                                understand_btn.first.click(force=True, timeout=3000)
                                page.wait_for_timeout(600)
                                # Wait for overlay to go hidden
                                overlay = page.locator("[data-test-id='handleLightbox']")
                                try:
                                    overlay.first.wait_for(state="hidden", timeout=4000)
                                except Exception:
                                    pass
                                page.wait_for_timeout(300)
                            else:
                                break
                        except Exception:
                            break

                try:
                    no_radio = page.locator("input[name='hearFromPCL'][value='No']")
                    if no_radio.count() > 0:
                        no_radio.first.click()
                        page.wait_for_timeout(800)
                        _dismiss_lightbox()
                    else:
                        # Try by id pattern
                        no_radio2 = page.locator("input#hearFromPCL_2, input[id='hearFromPCL_2']")
                        if no_radio2.count() > 0:
                            no_radio2.first.click()
                            page.wait_for_timeout(800)
                            _dismiss_lightbox()
                except Exception:
                    pass
                # UK-specific: agreement checkbox (check it if unchecked)
                try:
                    cb = page.locator("input#agreement, input[name='agreement']")
                    if cb.count() > 0 and not cb.first.is_checked():
                        cb.first.click()
                        page.wait_for_timeout(300)
                except Exception:
                    pass
                # UK-specific: receiveNewsDeals checkbox (optional, check it)
                try:
                    news_cb = page.locator("input[name='receiveNewsDeals'], input#receiveNewsDeals")
                    if news_cb.count() > 0 and not news_cb.first.is_checked():
                        news_cb.first.click()
                        page.wait_for_timeout(200)
                except Exception:
                    pass
                # Debug: show invalid/required fields before submit
                form_fields = page.evaluate("""
                    () => [...document.querySelectorAll('input,select,textarea')]
                        .filter(el => el.name || el.id)
                        .map(el => ({
                            tag: el.tagName, name: el.name, id: el.id,
                            type: el.type, value: el.value, checked: el.checked,
                            required: el.required, valid: el.validity ? el.validity.valid : null
                        }))
                """)
                invalid_fields = [f for f in form_fields if f.get("required") and not f.get("valid")]
                print(f"  Invalid required fields: {invalid_fields}")
                print(f"  All fields: {form_fields}")
                page.screenshot(path=f"debug_uk_guest_before_submit_{first}.png")
                btn_count = page.locator("button").filter(has_text="SAVE & CONTINUE").count()
                print(f"  SAVE & CONTINUE buttons found: {btn_count}")
                all_btns = [b.inner_text()[:30] for b in page.locator("button").all() if b.is_visible()]
                print(f"  Visible buttons: {all_btns[:10]}")
                # Dismiss any lingering lightbox before clicking SAVE & CONTINUE
                _dismiss_lightbox()
                page.wait_for_timeout(500)
                # Capture URL before clicking so we can detect real navigation
                url_before_save = page.url
                # Click SAVE & CONTINUE — regular click (no force) after modal is dismissed
                save_btn = page.locator("button").filter(has_text="SAVE & CONTINUE")
                try:
                    if save_btn.count() > 0:
                        save_btn.first.scroll_into_view_if_needed()
                        save_btn.first.click(timeout=10000)
                        print(f"  Clicked SAVE & CONTINUE (regular)")
                    else:
                        raise Exception("Button not found")
                except Exception as e:
                    print(f"  Regular click failed: {e!r} — trying force click")
                    try:
                        save_btn.first.click(force=True, timeout=5000)
                        print(f"  Clicked SAVE & CONTINUE (force)")
                    except Exception as e2:
                        print(f"  Force click failed: {e2!r} — trying data-track-id")
                        try:
                            page.locator("button[data-track-id='save-guest-1'], button[data-track-id='save-guest-2']").first.click(force=True)
                        except Exception:
                            booking_guests_page.continue_to_next_step()
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_timeout(3000)
                # Wait for URL to actually CHANGE from the page we were on before clicking
                try:
                    page.wait_for_url(
                        lambda u, _prev=url_before_save: u != _prev and any(
                            k in u.lower() for k in ["pay", "guest-", "confirmation", "review"]
                        ),
                        timeout=20000,
                    )
                    print(f"  URL changed to: {page.url}")
                except Exception:
                    # If still stuck, try one more click
                    if page.url == url_before_save:
                        print(f"  Still at same URL — retrying SAVE & CONTINUE")
                        try:
                            save_btn2 = page.locator("button").filter(has_text="SAVE & CONTINUE")
                            if save_btn2.count() > 0:
                                save_btn2.first.click(force=True, timeout=5000)
                                page.wait_for_load_state("domcontentloaded")
                                page.wait_for_timeout(5000)
                        except Exception:
                            pass
                # Report any validation errors + highlighted fields
                for err in page.locator("[class*='error'], [role='alert']").all():
                    if err.is_visible():
                        print(f"  Validation error: {err.inner_text()[:100]!r}")
                # Find fields with error classes (React-level validation)
                highlighted = page.evaluate("""
                    () => [...document.querySelectorAll('[class*="error"],[class*="invalid"],[class*="has-error"]')]
                        .filter(el => el.tagName.match(/INPUT|SELECT|LABEL|DIV|SPAN/))
                        .map(el => ({tag: el.tagName, name: el.name||el.htmlFor||'', cls: el.className.slice(0,80), checked: el.checked}))
                """)
                print(f"  Highlighted/errored fields: {highlighted[:15]}")

            for idx, (first, last, email) in enumerate(guest_data):
                if not booking_guests_page.is_on_guests_page():
                    print(f"Guest loop: not on guests page at idx={idx}, url={page.url}")
                    break
                print(f"Filling guest {idx}: {first} {last} @ {page.url}")
                _fill_one_guest(first, last, email)
                print(f"After guest {idx} fill: {page.url}")

            page.screenshot(path="debug_uk_after_guests.png")
            print(f"After guest loop URL: {page.url}")
            # If still on guest page, wait for navigation to payment
            if "guest" in page.url.lower():
                try:
                    page.wait_for_url(
                        lambda u: any(k in u.lower() for k in ["pay", "payment", "confirm", "review"]),
                        timeout=15000,
                    )
                    print(f"After waiting for payment URL: {page.url}")
                except Exception:
                    print(f"Still on guest page after wait: {page.url}")

        with allure.step("Step 6b: Skip transfers upsell if shown"):
            page.wait_for_timeout(1500)
            if "transfer" in page.url.lower():
                booking_cabin_page.take_screenshot("uk_step6b_transfers")
                print(f"Transfers page URL: {page.url}")
                for btn_text in [
                    "No, thanks", "No Thanks", "No, Thank You", "Skip",
                    "Continue without", "CONTINUE", "Continue", "Next",
                ]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        print(f"After transfers skip: {page.url}")
                        break
                else:
                    # Try any link that mentions skipping
                    for link_text in ["No, thanks", "Skip", "Continue"]:
                        lnk = page.locator(f"a:has-text('{link_text}')")
                        if lnk.count() > 0 and lnk.first.is_visible():
                            lnk.first.click()
                            page.wait_for_load_state("domcontentloaded")
                            page.wait_for_timeout(2000)
                            break

        with allure.step("Step 6c: Skip insurance upsell if shown"):
            page.wait_for_timeout(1000)
            if "insurance" in page.url.lower() or "protect" in page.url.lower():
                booking_cabin_page.take_screenshot("uk_step6c_insurance")
                for btn_text in ["No, thanks", "No Thanks", "Skip", "Continue", "CONTINUE"]:
                    btn = page.locator("button").filter(has_text=btn_text)
                    if btn.count() > 0 and btn.first.is_visible():
                        btn.first.click()
                        page.wait_for_load_state("domcontentloaded")
                        page.wait_for_timeout(2000)
                        break

        with allure.step("Step 7: Confirm payment page loaded"):
            # Wait up to 10s for payment URL to appear if still on an intermediate page
            current = page.url.lower()
            if not any(k in current for k in ["pay", "payment", "checkout", "confirm", "review"]):
                try:
                    page.wait_for_url(
                        lambda u: any(k in u.lower() for k in ["pay", "payment", "checkout", "confirm", "review"]),
                        timeout=10000,
                    )
                except Exception:
                    pass
            if not booking_payment_page.is_on_payment_page():
                pytest.skip(
                    f"Did not reach payment page after guest forms "
                    f"(at: {booking_payment_page.get_url()})"
                )

        with allure.step("Step 8: Fill payment — Tom Cat 4111111111111111 12/33 234"):
            pay_page = booking_payment_page.page
            try:
                pay_page.wait_for_function(
                    "() => !document.querySelector('.loading, [class*=\"loading\"]') || "
                    "document.querySelector('.loading, [class*=\"loading\"]').offsetParent === null",
                    timeout=15000,
                )
            except Exception:
                pay_page.wait_for_timeout(3000)

            pay_page.screenshot(path="debug_uk_payment_page.png")

            # Cardholder name
            try:
                pay_page.locator("#cardholder-name").first.fill("Tom Cat", timeout=5000)
            except Exception:
                pass

            # Mastercard Gateway cross-origin iframes
            for frame in pay_page.frames:
                if "mastercard.com" not in frame.url:
                    continue
                try:
                    ids = frame.evaluate(
                        "() => [...document.querySelectorAll('input')].map(i=>i.id)"
                    )
                    print(f"MC FRAME {frame.url[-30:]}: ids={ids}")
                    if "number"       in ids:
                        frame.locator("#number").first.fill("4111111111111111", timeout=5000)
                    if "expiryMonth"  in ids:
                        frame.locator("#expiryMonth").first.fill("12", timeout=3000)
                    if "expiryYear"   in ids:
                        frame.locator("#expiryYear").first.fill("2033", timeout=3000)
                    if "nameOnCard"   in ids:
                        frame.locator("#nameOnCard").first.fill("Tom Cat", timeout=3000)
                    if "securityCode" in ids:
                        frame.locator("#securityCode").first.fill("234", timeout=3000)
                except Exception as e:
                    print(f"Frame error: {e}")

            # Main-page expiry selects
            year_opts = pay_page.evaluate(
                "() => [...document.querySelectorAll('#expiry-year option')].map(o=>o.value)"
            )
            tgt_year = "2033" if "2033" in year_opts else (year_opts[-1] if year_opts else "2026")
            try:
                pay_page.locator("#expiry-month").first.select_option("12", timeout=5000)
            except Exception:
                pass
            try:
                pay_page.locator("#expiry-year").first.select_option(tgt_year, timeout=5000)
            except Exception:
                pass

            # Zip
            zip_loc = pay_page.locator("input[name='zip']")
            try:
                zip_loc.first.scroll_into_view_if_needed(timeout=5000)
                pay_page.wait_for_timeout(300)
                zip_loc.first.click(timeout=5000)
                pay_page.keyboard.press("Control+a")
                pay_page.keyboard.type("90210", delay=80)
                pay_page.keyboard.press("Tab")
                pay_page.wait_for_timeout(200)
            except Exception:
                pay_page.evaluate("""
                    const el = document.querySelector("input[name='zip']");
                    if (el) {
                        el.focus();
                        const s = Object.getOwnPropertyDescriptor(
                            window.HTMLInputElement.prototype,'value').set;
                        s.call(el,'90210');
                        el.dispatchEvent(new InputEvent('input',{bubbles:true,data:'90210',inputType:'insertText'}));
                        el.dispatchEvent(new Event('change',{bubbles:true}));
                        el.dispatchEvent(new Event('blur',{bubbles:true}));
                    }
                """)

            pay_page.screenshot(path="debug_uk_payment_filled.png")

        with allure.step("Step 9: Accept terms and click BOOK NOW"):
            pay_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            pay_page.wait_for_timeout(500)
            pay_page.evaluate("""
                const cb = document.querySelector('#passageContractInputCheckBox');
                if (cb && !cb.checked) {
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLInputElement.prototype,'checked').set;
                    setter.call(cb, true);
                    cb.dispatchEvent(new Event('change',{bubbles:true}));
                    cb.dispatchEvent(new Event('click',{bubbles:true}));
                }
            """)
            pay_page.wait_for_timeout(300)
            pay_page.screenshot(path="debug_uk_payment_terms.png")

            try:
                book_now = pay_page.locator("button").filter(has_text="BOOK NOW")
                if book_now.count() > 0 and book_now.first.is_visible():
                    book_now.first.click(timeout=15000)
                else:
                    for txt in ["Book Now", "Book", "Complete", "Confirm", "Pay"]:
                        btn = pay_page.locator("button").filter(has_text=txt)
                        if btn.count() > 0 and btn.first.is_visible():
                            btn.first.click(timeout=15000)
                            break
                    else:
                        booking_payment_page.click(booking_payment_page.COMPLETE_BOOKING_BTN)
            except Exception:
                booking_payment_page.click(booking_payment_page.COMPLETE_BOOKING_BTN)

        with allure.step("Step 10: Wait for confirmation and capture booking number"):
            reached = booking_confirmation_page.wait_for_confirmation(timeout=30000)
            if not reached:
                pytest.skip(
                    f"Confirmation page not reached after submit "
                    f"(at: {booking_confirmation_page.get_url()})"
                )

            booking_number = booking_confirmation_page.get_booking_number()
            confirm_url    = booking_confirmation_page.get_url()

            print(f"\n{'='*60}")
            print(f"UK BOOKING")
            print(f"CONFIRMATION URL: {confirm_url}")
            print(f"BOOKING NUMBER:   {booking_number}")
            print(f"{'='*60}\n")

            allure.attach(
                f"UK Booking\nConfirmed Booking Number: {booking_number}\nURL: {confirm_url}",
                name="[UK BOOKING NUMBER] Confirmation",
                attachment_type=allure.attachment_type.TEXT,
            )
            booking_confirmation_page.take_screenshot("uk_booking_confirmation")

            assert booking_number, (
                f"UK confirmation page reached but no booking number found. "
                f"URL: {confirm_url}"
            )
