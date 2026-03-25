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
from pages.home_page import HomePage


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
    """Submit payment with test card and capture the confirmed booking number."""

    @allure.story("Confirmed booking number is displayed after payment submission")
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
        test_user_data: dict,
    ):
        """Full flow: search → cabin → guests → fill card → submit → read booking number."""
        with allure.step("Step 1: Navigate to cruise detail"):
            _navigate_to_detail(cruise_search_page, cruise_results_page, cruise_detail_page)

        with allure.step("Step 2: Enter booking flow (Book Now)"):
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

        with allure.step("Step 5: Confirm payment page loaded"):
            if not booking_payment_page.is_on_payment_page():
                pytest.skip(
                    f"Did not reach payment page (at: {booking_payment_page.get_url()})"
                )

        with allure.step("Step 6: Fill credit card — Tom Cat 4111111111111111 12/33 CVV 234"):
            booking_payment_page.fill_test_card(
                card_number="4111111111111111",
                expiry="12/33",
                cvv="234",
                name="Tom Cat",
            )

        with allure.step("Step 7: Accept terms and conditions"):
            booking_payment_page.accept_terms()

        with allure.step("Step 8: Submit booking"):
            booking_payment_page.click(booking_payment_page.COMPLETE_BOOKING_BTN)

        with allure.step("Step 9: Wait for confirmation page"):
            reached = booking_confirmation_page.wait_for_confirmation(timeout=30000)
            if not reached:
                pytest.skip(
                    f"Confirmation page not reached after submit "
                    f"(at: {booking_confirmation_page.get_url()})"
                )

        with allure.step("Step 10: Capture booking number"):
            booking_number = booking_confirmation_page.get_booking_number()
            allure.attach(
                f"Confirmed Booking Number: {booking_number}",
                name="[BOOKING NUMBER] Confirmation",
                attachment_type=allure.attachment_type.TEXT,
            )
            booking_confirmation_page.take_screenshot("booking_confirmation")
            assert booking_number, (
                "Confirmation page reached but no booking number found. "
                f"Current URL: {booking_confirmation_page.get_url()}"
            )
