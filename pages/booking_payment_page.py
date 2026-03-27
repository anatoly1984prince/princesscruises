"""Page Object: Booking — Review & Payment step."""
from __future__ import annotations

import allure
from pages.base_page import BasePage


class BookingPaymentPage(BasePage):
    """Payment and review step — the final step before booking confirmation."""

    PAGE_HEADING = (
        "h1, h2, [class*='payment-header'], [class*='review-header'], "
        "[class*='step-title']:has-text('Payment'), "
        "[class*='step-title']:has-text('Review')"
    )

    # ── Order / price summary ────────────────────────────────────────────────
    ORDER_SUMMARY = (
        "[class*='order-summary'], [class*='booking-summary'], "
        "[class*='price-summary'], [class*='cart-summary'], "
        "section:has-text('Summary'), [aria-label*='summary' i]"
    )
    TOTAL_PRICE = (
        "[class*='total-price'], [class*='grand-total'], "
        "[aria-label*='total' i], [class*='amount-due'], "
        "[class*='booking-total']"
    )
    DEPOSIT_AMOUNT = (
        "[class*='deposit'], [aria-label*='deposit' i], "
        "[class*='due-today'], [class*='amount-due-today']"
    )
    CRUISE_NAME_SUMMARY = (
        "[class*='order-summary'] h2, [class*='order-summary'] h3, "
        "[class*='booking-summary'] [class*='title'], "
        "[class*='cruise-name'], [class*='voyage-name']"
    )
    CABIN_TYPE_SUMMARY = (
        "[class*='stateroom-type'], [class*='cabin-type'], "
        "[class*='order-summary'] [class*='category']"
    )
    GUEST_COUNT_SUMMARY = (
        "[class*='guest-count'], [class*='passenger-count'], "
        "[class*='order-summary'] [class*='guest']"
    )

    # ── Payment form ─────────────────────────────────────────────────────────
    PAYMENT_SECTION = (
        "[class*='payment-form'], [class*='payment-section'], "
        "form[id*='payment' i], section:has-text('Payment')"
    )
    CARD_NUMBER = (
        "input[name*='cardNumber' i], input[name*='card-number' i], "
        "input[autocomplete='cc-number'], input[id*='cardNumber' i], "
        "input[placeholder*='card number' i]"
    )
    CARD_EXPIRY = (
        "input[name*='expiry' i], input[name*='exp' i], "
        "input[autocomplete='cc-exp'], input[placeholder*='MM/YY' i], "
        "input[id*='expiry' i]"
    )
    CARD_CVV = (
        "input[name*='cvv' i], input[name*='cvc' i], input[name*='cvv2' i], "
        "input[autocomplete='cc-csc'], input[id*='cvv' i]"
    )
    CARDHOLDER_NAME = (
        "input[name*='cardholderName' i], input[name*='card-name' i], "
        "input[autocomplete='cc-name'], input[id*='cardName' i]"
    )
    BILLING_ADDRESS = (
        "input[name*='address' i], input[id*='address' i], "
        "input[autocomplete='street-address']"
    )
    BILLING_ZIP = (
        "input[name*='zip' i], input[name*='postal' i], "
        "input[autocomplete='postal-code']"
    )

    # ── Terms / agreement ────────────────────────────────────────────────────
    TERMS_CHECKBOX = (
        "input[type='checkbox'][id*='terms' i], "
        "input[type='checkbox'][name*='terms' i], "
        "label:has-text('terms') input[type='checkbox'], "
        "label:has-text('agree') input[type='checkbox']"
    )
    TERMS_LINK = "a:has-text('Terms'), a:has-text('Conditions'), a[href*='terms']"

    # ── Final booking button ─────────────────────────────────────────────────
    COMPLETE_BOOKING_BTN = (
        "button:has-text('Complete Booking'), button:has-text('Confirm Booking'), "
        "button:has-text('Book Now'), button:has-text('Purchase'), "
        "button[class*='complete-booking'], button[class*='confirm-booking']"
    )
    BACK_BTN = "button:has-text('Back'), a:has-text('Back')"

    # ── Error / validation messages ──────────────────────────────────────────
    PAYMENT_ERROR = (
        "[class*='payment-error'], [class*='error-message'], "
        "[role='alert'], [aria-live='assertive']"
    )

    def is_on_payment_page(self) -> bool:
        url = self.get_url().lower()
        return any(k in url for k in ["payment", "review", "checkout", "confirm", "/pay/", "/pay?", "/pay", "pay/"])

    @allure.step("Assert payment/review page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.PAGE_HEADING, timeout=20000)

    def get_total_price(self) -> str:
        if self.is_visible(self.TOTAL_PRICE, timeout=5000):
            return self.get_text(self.TOTAL_PRICE)
        return ""

    def get_deposit_amount(self) -> str:
        if self.is_visible(self.DEPOSIT_AMOUNT, timeout=5000):
            return self.get_text(self.DEPOSIT_AMOUNT)
        return ""

    def has_order_summary(self) -> bool:
        return self.is_visible(self.ORDER_SUMMARY, timeout=5000)

    def has_payment_form(self) -> bool:
        return (
            self.is_visible(self.PAYMENT_SECTION, timeout=5000) or
            self.is_visible(self.CARD_NUMBER, timeout=3000)
        )

    def has_terms_checkbox(self) -> bool:
        return self.is_visible(self.TERMS_CHECKBOX, timeout=3000)

    def has_complete_booking_btn(self) -> bool:
        return self.is_visible(self.COMPLETE_BOOKING_BTN, timeout=5000)

    @allure.step("Accept terms and conditions")
    def accept_terms(self) -> bool:
        if self.is_visible(self.TERMS_CHECKBOX, timeout=3000):
            cb = self.page.locator(self.TERMS_CHECKBOX).first
            if not cb.is_checked():
                cb.click()
            return True
        return False

    @allure.step("Fill payment card details (test data)")
    def fill_test_card(
        self,
        card_number: str = "4111 1111 1111 1111",
        expiry: str = "12/28",
        cvv: str = "123",
        name: str = "Test User",
    ) -> None:
        if self.is_visible(self.CARD_NUMBER, timeout=5000):
            self.fill(self.CARD_NUMBER, card_number)
        if self.is_visible(self.CARD_EXPIRY, timeout=3000):
            self.fill(self.CARD_EXPIRY, expiry)
        if self.is_visible(self.CARD_CVV, timeout=3000):
            self.fill(self.CARD_CVV, cvv)
        if self.is_visible(self.CARDHOLDER_NAME, timeout=3000):
            self.fill(self.CARDHOLDER_NAME, name)
