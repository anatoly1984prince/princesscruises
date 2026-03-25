"""General-purpose utility functions."""
from __future__ import annotations

import re
import time
import random
import string
from datetime import datetime, timedelta
from typing import Callable, Any


def retry(
    func: Callable,
    retries: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,),
) -> Any:
    """Retry a callable up to `retries` times on specified exceptions."""
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except exceptions as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(delay)
    raise last_exc  # type: ignore[misc]


def random_string(length: int = 8, prefix: str = "") -> str:
    chars = string.ascii_lowercase + string.digits
    return prefix + "".join(random.choices(chars, k=length))


def random_email(domain: str = "qa-automation.example.com") -> str:
    return f"qa.{random_string(6)}@{domain}"


def extract_price_value(price_text: str) -> float | None:
    """Extract a numeric price from a string like '$1,299' or 'From $899'."""
    cleaned = price_text.replace(",", "")
    match = re.search(r"\$?([\d]+\.?\d*)", cleaned)
    return float(match.group(1)) if match else None


def future_date(days_from_now: int = 90, fmt: str = "%m/%d/%Y") -> str:
    """Return a formatted date N days from today."""
    return (datetime.now() + timedelta(days=days_from_now)).strftime(fmt)


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    return re.sub(r"[^a-z0-9-]", "-", text.lower()).strip("-")


def truncate(text: str, max_length: int = 50) -> str:
    return text if len(text) <= max_length else text[:max_length] + "..."
