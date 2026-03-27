"""Market test: US site — guest booking flow.

Imports the existing US-market booking tests from tests/regression/test_booking_flow.py.
The conftest.py for this directory sets BASE_URL to https://www.princess.com.
"""
from __future__ import annotations

# Re-export the US guest booking confirmation test so it runs under the US market directory.
# This avoids duplicating code while still giving market-scoped test execution.
from tests.regression.test_booking_flow import (  # noqa: F401
    TestBookingConfirmation,
    TestBookingLoginAndConfirm,
)

# These imports bring the US booking classes into scope for pytest discovery.
__all__ = [
    "TestBookingConfirmation",
    "TestBookingLoginAndConfirm",
]
