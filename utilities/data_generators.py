"""Faker-based test data generators."""
from __future__ import annotations

from dataclasses import dataclass
from faker import Faker

_fake = Faker("en_US")


@dataclass
class UserProfile:
    first_name: str
    last_name: str
    email: str
    password: str
    phone: str
    country: str = "US"


def generate_user(password: str = "Cruise@Test2025!") -> UserProfile:
    return UserProfile(
        first_name=_fake.first_name(),
        last_name=_fake.last_name(),
        email=_fake.email(),
        password=password,
        phone=_fake.phone_number(),
    )


def generate_newsletter_subscriber() -> dict:
    return {
        "email": _fake.email(),
        "first_name": _fake.first_name(),
        "last_name": _fake.last_name(),
    }


def generate_search_params() -> dict:
    from config.test_data import DESTINATIONS, DEPARTURE_PORTS
    return {
        "destination": _fake.random_element(DESTINATIONS),
        "port": _fake.random_element(DEPARTURE_PORTS),
    }
