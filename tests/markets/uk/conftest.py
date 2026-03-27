"""UK market conftest — sets BASE_URL to https://www.princess.com/en-uk."""
from __future__ import annotations
import pytest
from config import settings as _settings_module


@pytest.fixture(scope="session", autouse=True)
def market_base_url():
    """Override BASE_URL for the UK market."""
    _settings_module.settings.BASE_URL = "https://www.princess.com/en-uk"
    yield _settings_module.settings.BASE_URL
