"""Custom wait strategies for dynamic / SPA content."""
from __future__ import annotations

import time
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


def wait_for_any_visible(page: Page, selectors: list[str], timeout: int = 15_000) -> str:
    """
    Wait until any selector in the list becomes visible.
    Returns the first selector that became visible.
    Raises TimeoutError if none become visible within the timeout.
    """
    deadline = time.time() + timeout / 1000
    while time.time() < deadline:
        for sel in selectors:
            try:
                if page.locator(sel).first.is_visible(timeout=500):
                    return sel
            except (PlaywrightTimeoutError, Exception):
                continue
        time.sleep(0.3)
    raise TimeoutError(f"None of {selectors} became visible within {timeout}ms")


def wait_for_network_idle(page: Page, timeout: int = 10_000) -> None:
    """Best-effort wait for network idle — safe on SPAs."""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except PlaywrightTimeoutError:
        pass


def wait_for_text_in_element(
    page: Page, selector: str, text: str, timeout: int = 10_000
) -> None:
    """Poll until `text` appears in the element's inner text."""
    deadline = time.time() + timeout / 1000
    while time.time() < deadline:
        try:
            content = page.locator(selector).first.inner_text(timeout=1_000)
            if text.lower() in content.lower():
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise TimeoutError(f"Text {text!r} not found in {selector!r} within {timeout}ms")
