"""Page Object: Booking Confirmation page."""
from __future__ import annotations

import re

import allure
from pages.base_page import BasePage


class BookingConfirmationPage(BasePage):
    """Confirmation page shown after a successful booking submission."""

    PAGE_HEADING = (
        "h1:has-text('Confirmation'), h1:has-text('Thank You'), h1:has-text('Confirmed'), "
        "h2:has-text('Confirmation'), h2:has-text('Thank You'), "
        "[class*='confirmation-header'], [class*='booking-confirmed']"
    )

    # ── Booking / reservation number ─────────────────────────────────────────
    BOOKING_NUMBER = (
        "[class*='booking-number'], [class*='reservation-number'], "
        "[class*='confirmation-number'], [class*='booking-ref'], "
        "[aria-label*='booking number' i], [aria-label*='reservation' i], "
        "[data-testid*='booking-number'], [data-testid*='confirmation']"
    )
    # Fallback: any element containing the label text near a number
    BOOKING_NUMBER_LABEL = (
        "dt:has-text('Booking'), dt:has-text('Reservation'), dt:has-text('Confirmation'), "
        "span:has-text('Booking #'), span:has-text('Reservation #'), "
        "p:has-text('Booking Number'), p:has-text('Confirmation Number')"
    )

    # ── Summary fields ────────────────────────────────────────────────────────
    CRUISE_NAME = (
        "[class*='confirmation'] [class*='cruise-name'], "
        "[class*='confirmation'] [class*='voyage-name'], "
        "[class*='booking-summary'] h2, [class*='booking-summary'] h3"
    )
    GUEST_NAME = (
        "[class*='confirmation'] [class*='guest-name'], "
        "[class*='confirmation'] [class*='passenger-name']"
    )
    TOTAL_CHARGED = (
        "[class*='confirmation'] [class*='total'], "
        "[class*='confirmation'] [class*='amount'], "
        "[class*='amount-paid'], [class*='total-charged']"
    )

    def is_on_confirmation_page(self) -> bool:
        url = self.get_url().lower()
        return any(k in url for k in ["confirmation", "confirmed", "thank-you", "thankyou", "success"])

    def wait_for_confirmation(self, timeout: int = 30000) -> bool:
        try:
            self.page.wait_for_url(
                re.compile(r"confirmation|confirmed|thank.you|success", re.I),
                timeout=timeout,
            )
            return True
        except Exception:
            pass
        # Fallback: wait for heading to appear
        return self.is_visible(self.PAGE_HEADING, timeout=timeout)

    @allure.step("Get booking confirmation number")
    def get_booking_number(self) -> str:
        """Return the booking/reservation number shown on the confirmation page."""
        # Try dedicated element first
        if self.is_visible(self.BOOKING_NUMBER, timeout=5000):
            return self.get_text(self.BOOKING_NUMBER)

        # Try label → sibling/next text pattern
        if self.is_visible(self.BOOKING_NUMBER_LABEL, timeout=3000):
            label = self.page.locator(self.BOOKING_NUMBER_LABEL).first
            # Try the adjacent <dd> (definition list)
            try:
                sibling = label.locator("xpath=following-sibling::dd[1]")
                if sibling.is_visible(timeout=2000):
                    return sibling.inner_text().strip()
            except Exception:
                pass
            # Try parent container text
            try:
                parent = label.locator("xpath=..")
                text = parent.inner_text().strip()
                if text:
                    return text
            except Exception:
                pass

        # Last resort: scan full page text for a booking number pattern
        try:
            body = self.page.locator("body").inner_text()
            match = re.search(
                r"(?:booking|reservation|confirmation)[^\d]*#?\s*(\d{5,12})",
                body,
                re.I,
            )
            if match:
                return match.group(1)
        except Exception:
            pass

        return ""

    @allure.step("Assert confirmation page loaded")
    def assert_loaded(self) -> None:
        self.assert_visible(self.PAGE_HEADING, timeout=30000)
