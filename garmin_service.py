"""Application-facing adapter for python-garminconnect.

The wrapper keeps Garmin authentication and token refresh in its own token
store. The webapp only receives a normalized heart-rate reading.
"""

import os
from datetime import date
from getpass import getpass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from garmin_client import GarminError, HeartRateReading

load_dotenv(Path(__file__).with_name(".env"))

_ACTIVE_CLIENT = None


def _latest_from_response(payload: Any) -> HeartRateReading:
    values = payload.get("heartRateValues", []) if isinstance(payload, dict) else []
    for item in reversed(values):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            try:
                bpm = int(float(item[1]))
            except (TypeError, ValueError):
                continue
            if 20 <= bpm <= 240:
                return HeartRateReading(bpm, str(item[0]))
    raise GarminError("Garmin Connect returned no valid heart-rate samples for today")


def _client(email=None, password=None):
    global _ACTIVE_CLIENT
    if _ACTIVE_CLIENT is not None:
        return _ACTIVE_CLIENT
    try:
        from garminconnect import Garmin
    except ImportError as error:
        raise GarminError(
            "Install garminconnect with Python 3.12+ before using Garmin Connect"
        ) from error

    email = email or os.getenv("GARMIN_EMAIL")
    password = password or os.getenv("GARMIN_PASSWORD")
    client = Garmin(email, password, prompt_mfa=lambda: getpass("Garmin MFA code: "))
    tokenstore = os.getenv("GARMIN_TOKENSTORE", os.path.expanduser("~/.garminconnect"))
    try:
        client.login(tokenstore)
    except Exception as error:
        if not email or not password:
            raise GarminError(
                "Garmin token cache is unavailable or expired. Enter your Garmin "
                "credentials in the Connect Garmin form."
            ) from error
        raise GarminError(f"Garmin Connect login failed: {error}") from error
    _ACTIVE_CLIENT = client
    return _ACTIVE_CLIENT


def login_and_fetch_heart_rate(email=None, password=None) -> HeartRateReading:
    """Log in or resume the cached session, then fetch today's heart rate."""
    return _latest_from_response(_client(email, password).get_heart_rates(date.today().isoformat()))


def fetch_wrapper_heart_rate() -> HeartRateReading:
    """Fetch from the cached Garmin Connect session without prompting in the UI."""
    return login_and_fetch_heart_rate()