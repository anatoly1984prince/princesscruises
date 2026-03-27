"""Faker-based test data generators."""
from __future__ import annotations

import datetime
import random
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


@dataclass
class RegistrationProfile:
    first_name: str
    last_name: str
    email: str
    password: str
    cell_phone: str
    dob_month: str       # zero-padded: '01'..'12'
    dob_day: str         # zero-padded: '01'..'28'
    dob_year: str        # four-digit year string
    address1: str
    city: str
    state: str
    zip_code: str
    country: str = "US"
    title: str = "MR"


def generate_registration_user(
    address1: str = "1449 Hollywood Blvd",
    city: str = "Hollywood",
    state: str = "FL",
    zip_code: str = "33020",
    password: str = "Cruise@Test2025!",
) -> RegistrationProfile:
    """Generate a new user whose DOB satisfies:
      - not earlier than 2000-01-01
      - user is strictly older than 25 years (i.e. born before today − 25 years)

    The valid window is therefore  2000-01-01 → (today − 25 years − 1 day).
    A random date is chosen uniformly within that window.
    """
    today   = datetime.date.today()
    min_dob = datetime.date(2000, 1, 1)
    # Strictly older than 25 → must have had their 26th birthday already,
    # so DOB ≤ today minus 26 years is one safe reading, but the clearest
    # interpretation is DOB < (today − 25 years), i.e. ≤ (today − 25 years − 1 day).
    max_dob = today.replace(year=today.year - 25) - datetime.timedelta(days=1)

    delta = (max_dob - min_dob).days
    dob   = min_dob + datetime.timedelta(days=random.randint(0, delta))
    year, month, day = dob.year, dob.month, dob.day

    return RegistrationProfile(
        first_name=_fake.first_name(),
        last_name=_fake.last_name(),
        email=_fake.unique.email(),
        password=password,
        cell_phone=_fake.numerify("##########"),   # 10 digits
        dob_month=f"{month:02d}",
        dob_day=f"{day:02d}",
        dob_year=str(year),
        address1=address1,
        city=city,
        state=state,
        zip_code=zip_code,
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
