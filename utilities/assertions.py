"""Custom assertion helpers with rich failure messages."""
from __future__ import annotations

import re
from typing import Any


def assert_contains(haystack: str, needle: str, msg: str = "") -> None:
    assert needle.lower() in haystack.lower(), (
        msg or f"Expected {needle!r} to be found in {haystack!r}"
    )


def assert_price_format(price_text: str) -> None:
    pattern = r"\$[\d,]+(\.\d{2})?"
    assert re.search(pattern, price_text), (
        f"Price text does not match '$X,XXX' format: {price_text!r}"
    )


def assert_url_contains_any(url: str, fragments: list[str]) -> None:
    assert any(f.lower() in url.lower() for f in fragments), (
        f"URL {url!r} does not contain any of {fragments}"
    )


def assert_list_not_empty(items: list[Any], label: str = "list") -> None:
    assert len(items) > 0, f"Expected non-empty {label}, got empty list"


def assert_count_gte(actual: int, minimum: int, label: str = "items") -> None:
    assert actual >= minimum, f"Expected >= {minimum} {label}, got {actual}"
