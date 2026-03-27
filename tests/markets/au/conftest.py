"""AU market conftest — sets BASE_URL to https://www.princess.com/en-au."""
from __future__ import annotations
import pytest
from config import settings as _settings_module


@pytest.fixture(scope="session", autouse=True)
def market_base_url():
    """Override BASE_URL for the AU market."""
    _settings_module.settings.BASE_URL = "https://www.princess.com/en-au"
    yield _settings_module.settings.BASE_URL
