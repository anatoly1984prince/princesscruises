"""
Central settings loader — reads from environment variables / .env file.
All framework-wide configuration lives here.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (one level above config/)
load_dotenv(Path(__file__).parent.parent / ".env")


class Settings:
    # ── URLs ────────────────────────────────────────────────────────────────
    BASE_URL: str = "https://www.princess.com"

    # ── Browser ─────────────────────────────────────────────────────────────
    BROWSER: str = os.getenv("BROWSER", "chromium").lower()
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))

    # ── Timeouts (ms) ───────────────────────────────────────────────────────
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "60000"))

    # ── Recording ───────────────────────────────────────────────────────────
    TRACE_MODE: str = os.getenv("TRACE_MODE", "retain-on-failure")

    # ── Test credentials ────────────────────────────────────────────────────
    TEST_USER_EMAIL: str = os.getenv("TEST_USER_EMAIL", "")
    TEST_USER_PASSWORD: str = os.getenv("TEST_USER_PASSWORD", "")
    TEST_BOOKING_NUMBER: str = os.getenv("TEST_BOOKING_NUMBER", "")
    TEST_BOOKING_LAST_NAME: str = os.getenv("TEST_BOOKING_LAST_NAME", "")

    # ── Viewport ────────────────────────────────────────────────────────────
    VIEWPORT_WIDTH: int = 1440
    VIEWPORT_HEIGHT: int = 900


settings = Settings()
