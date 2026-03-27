"""US market conftest — sets BASE_URL to https://www.princess.com (default US site)."""
from __future__ import annotations
import pytest
from config import settings as _settings_module


@pytest.fixture(scope="session", autouse=True)
def market_base_url():
    """Override BASE_URL for the US market."""
    _settings_module.settings.BASE_URL = "https://www.princess.com"
    yield _settings_module.settings.BASE_URL
