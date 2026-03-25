"""
Master conftest.py — Browser lifecycle, context isolation,
auto-screenshot on failure, and all page object fixtures.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Generator

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config.settings import settings
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.cruise_search_page import CruiseSearchPage
from pages.cruise_results_page import CruiseResultsPage
from pages.cruise_detail_page import CruiseDetailPage
from pages.deals_page import DealsPage
from pages.ships_page import ShipsPage
from pages.manage_booking_page import ManageBookingPage
from pages.newsletter_page import NewsletterPage
from pages.country_selector_page import CountrySelectorPage
from pages.booking_cabin_page import BookingCabinPage
from pages.booking_guests_page import BookingGuestsPage
from pages.booking_payment_page import BookingPaymentPage

REPORTS_DIR = Path(__file__).parent.parent / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
TRACES_DIR = REPORTS_DIR / "traces"
VIDEOS_DIR = REPORTS_DIR / "videos"

for d in (SCREENSHOTS_DIR, TRACES_DIR, VIDEOS_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ── Playwright / Browser — session-scoped (expensive to launch) ─────────────

@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    browser_type = getattr(playwright_instance, settings.BROWSER)
    br = browser_type.launch(
        headless=settings.HEADLESS,
        slow_mo=settings.SLOW_MO,
    )
    yield br
    br.close()


# ── Context + Page — function-scoped (fresh per test) ───────────────────────

@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    ctx = browser.new_context(
        viewport={"width": settings.VIEWPORT_WIDTH, "height": settings.VIEWPORT_HEIGHT},
        locale="en-US",
        record_video_dir=str(VIDEOS_DIR) if settings.VIDEO_MODE != "off" else None,
    )
    ctx.set_default_timeout(settings.DEFAULT_TIMEOUT)
    ctx.set_default_navigation_timeout(settings.NAVIGATION_TIMEOUT)

    if settings.TRACE_MODE != "off":
        ctx.tracing.start(screenshots=True, snapshots=True, sources=False)

    yield ctx

    # Save trace on failure
    if settings.TRACE_MODE == "retain-on-failure":
        # handled in the page fixture hook below
        pass
    elif settings.TRACE_MODE == "on":
        ctx.tracing.stop(path=str(TRACES_DIR / "trace.zip"))

    ctx.close()


@pytest.fixture
def page(context: BrowserContext, request: pytest.FixtureRequest) -> Generator[Page, None, None]:
    # Collect browser console errors during the test
    console_errors: list[str] = []
    pg = context.new_page()
    pg.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)

    yield pg

    # ── Auto-screenshot + failure details on failure ─────────────────────────
    rep_call = getattr(request.node, "rep_call", None)
    if rep_call and rep_call.failed:
        test_name = re.sub(r'[<>:"/\\|?*\[\]]', '_', request.node.nodeid).replace("::", "_")

        # 1. Full-page screenshot — saved before page.close()
        screenshot_path = SCREENSHOTS_DIR / f"{test_name}.png"
        try:
            pg.screenshot(path=str(screenshot_path), full_page=True)
            # Store path on node so the HTML hook can find it after teardown
            request.node._failure_screenshot = str(screenshot_path)
            allure.attach.file(
                str(screenshot_path),
                name="[SCREENSHOT] Browser state at failure",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            request.node._failure_screenshot = None

        # 2. Failure reason — exact exception message + traceback
        failure_reason = str(rep_call.longrepr) if rep_call.longrepr else "No traceback available"
        request.node._failure_reason = failure_reason
        allure.attach(
            failure_reason.encode("utf-8"),
            name="[FAILURE REASON] Exception & traceback",
            attachment_type=allure.attachment_type.TEXT,
        )

        # 3. URL + page title at moment of failure
        try:
            url_at_failure = f"URL at failure: {pg.url}\nPage title: {pg.title()}"
        except Exception:
            url_at_failure = "Could not capture URL (page already closed)"
        request.node._failure_url = url_at_failure
        allure.attach(
            url_at_failure.encode("utf-8"),
            name="[FAILURE CONTEXT] URL & page title",
            attachment_type=allure.attachment_type.TEXT,
        )

        # 4. Browser console errors collected during the test
        if console_errors:
            allure.attach(
                "\n".join(console_errors).encode("utf-8"),
                name="[BROWSER CONSOLE] Errors & warnings",
                attachment_type=allure.attachment_type.TEXT,
            )

        # 5. Playwright trace (if configured)
        if settings.TRACE_MODE == "retain-on-failure":
            trace_path = str(TRACES_DIR / f"{test_name}.zip")
            try:
                context.tracing.stop(path=trace_path)
                allure.attach.file(
                    trace_path,
                    name="[TRACE] Playwright trace (open with trace.playwright.dev)",
                    attachment_type=allure.attachment_type.ZIP,
                )
            except Exception:
                pass

    pg.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Store test outcome and attach failure details to the HTML report."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)

    # Attach to HTML report during teardown phase — by then the page fixture
    # has already saved the screenshot and stored paths on the item node.
    if call.when == "teardown":
        extras = getattr(rep, "extras", [])
        try:
            from pytest_html import extras as html_extras  # type: ignore

            # Screenshot (saved by the page fixture during teardown)
            screenshot_path = getattr(item, "_failure_screenshot", None)
            if screenshot_path and os.path.exists(screenshot_path):
                extras.append(html_extras.image(screenshot_path, name="Screenshot at failure"))

            # Failure reason (exact assertion / exception message)
            failure_reason = getattr(item, "_failure_reason", None)
            if failure_reason:
                lines = failure_reason.splitlines()
                short = "\n".join(lines[-40:]) if len(lines) > 40 else failure_reason
                extras.append(html_extras.text(short, name="Failure Reason"))

            # URL + page title at failure
            failure_url = getattr(item, "_failure_url", None)
            if failure_url:
                extras.append(html_extras.text(failure_url, name="URL at Failure"))

        except Exception:
            pass
        rep.extras = extras


# ── Data fixtures ────────────────────────────────────────────────────────────

@pytest.fixture
def test_user_data() -> dict:
    from utilities.data_generators import generate_user
    user = generate_user()
    return {
        "email": user.email,
        "password": user.password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
    }


@pytest.fixture
def auth_credentials() -> dict:
    return {
        "email": settings.TEST_USER_EMAIL,
        "password": settings.TEST_USER_PASSWORD,
    }


@pytest.fixture
def booking_credentials() -> dict:
    return {
        "booking_number": settings.TEST_BOOKING_NUMBER,
        "last_name": settings.TEST_BOOKING_LAST_NAME,
    }


# ── Page Object fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    return LoginPage(page)


@pytest.fixture
def register_page(page: Page) -> RegisterPage:
    return RegisterPage(page)


@pytest.fixture
def cruise_search_page(page: Page) -> CruiseSearchPage:
    return CruiseSearchPage(page)


@pytest.fixture
def cruise_results_page(page: Page) -> CruiseResultsPage:
    return CruiseResultsPage(page)


@pytest.fixture
def cruise_detail_page(page: Page) -> CruiseDetailPage:
    return CruiseDetailPage(page)


@pytest.fixture
def deals_page(page: Page) -> DealsPage:
    return DealsPage(page)


@pytest.fixture
def ships_page(page: Page) -> ShipsPage:
    return ShipsPage(page)


@pytest.fixture
def manage_booking_page(page: Page) -> ManageBookingPage:
    return ManageBookingPage(page)


@pytest.fixture
def newsletter_page(page: Page) -> NewsletterPage:
    return NewsletterPage(page)


@pytest.fixture
def country_selector_page(page: Page) -> CountrySelectorPage:
    return CountrySelectorPage(page)


@pytest.fixture
def booking_cabin_page(page: Page) -> BookingCabinPage:
    return BookingCabinPage(page)


@pytest.fixture
def booking_guests_page(page: Page) -> BookingGuestsPage:
    return BookingGuestsPage(page)


@pytest.fixture
def booking_payment_page(page: Page) -> BookingPaymentPage:
    return BookingPaymentPage(page)
