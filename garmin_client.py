"""Small Garmin heart-rate client.

The Garmin Health API is available to approved Garmin partners. Keep the
endpoint and credentials outside the repository so this client can also be
used with a local proxy or test fixture.
"""

import json
import os
import secrets
import webbrowser
from dataclasses import dataclass
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from http.server import BaseHTTPRequestHandler, HTTPServer


class GarminError(RuntimeError):
    """Raised when Garmin data cannot be fetched or parsed."""


@dataclass(frozen=True)
class HeartRateReading:
    bpm: int
    timestamp: Optional[str] = None


def _oauth_config(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise GarminError(f"Set {name} before starting Garmin login")
    return value


def _save_access_token(access_token: str) -> None:
    """Persist the token locally without printing it to the terminal."""
    env_path = os.getenv("GARMIN_ENV_FILE", ".env")
    lines = []
    try:
        with open(env_path, "r", encoding="utf-8") as env_file:
            lines = env_file.read().splitlines()
    except FileNotFoundError:
        pass

    replacement = f"GARMIN_ACCESS_TOKEN={access_token}"
    for index, line in enumerate(lines):
        if line.startswith("GARMIN_ACCESS_TOKEN="):
            lines[index] = replacement
            break
    else:
        lines.append(replacement)
    with open(env_path, "w", encoding="utf-8") as env_file:
        env_file.write("\n".join(lines) + "\n")


def login_with_garmin() -> None:
    """Open Garmin authorization in a browser and handle its local callback."""
    authorization_url = _oauth_config("GARMIN_AUTHORIZATION_URL")
    token_url = _oauth_config("GARMIN_TOKEN_URL")
    client_id = _oauth_config("GARMIN_CLIENT_ID")
    redirect_uri = os.getenv("GARMIN_REDIRECT_URI", "http://localhost:8765/garmin/callback")
    parsed_redirect = urlparse(redirect_uri)
    if parsed_redirect.hostname not in ("localhost", "127.0.0.1"):
        raise GarminError("GARMIN_REDIRECT_URI must point to localhost for local login")

    state = secrets.token_urlsafe(32)
    query = urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    })
    result = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - required by BaseHTTPRequestHandler
            request = urlparse(self.path)
            values = parse_qs(request.query)
            if values.get("state", [None])[0] != state:
                result["error"] = "OAuth state validation failed"
            elif values.get("error"):
                result["error"] = values["error"][0]
            else:
                code = values.get("code", [None])[0]
                if not code:
                    result["error"] = "Garmin did not return an authorization code"
                else:
                    token_request = Request(
                        token_url,
                        data=urlencode({
                            "grant_type": "authorization_code",
                            "code": code,
                            "client_id": client_id,
                            "redirect_uri": redirect_uri,
                        }).encode(),
                        headers={"Content-Type": "application/x-www-form-urlencoded"},
                    )
                    try:
                        with urlopen(token_request, timeout=15) as response:
                            token_payload = json.load(response)
                        token = token_payload.get("access_token")
                        if not token:
                            result["error"] = "Garmin token response had no access token"
                        else:
                            _save_access_token(token)
                            result["success"] = True
                    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
                        result["error"] = f"Unable to exchange Garmin login code: {error}"

            self.send_response(200 if result.get("success") else 400)
            self.end_headers()
            self.wfile.write(
                b"Garmin connected. You can close this window."
                if result.get("success")
                else f"Garmin login failed: {result['error']}".encode()
            )

        def log_message(self, format, *args):
            return

    server = HTTPServer((parsed_redirect.hostname, parsed_redirect.port or 80), CallbackHandler)
    browser_url = f"{authorization_url}?{query}"
    print("Opening Garmin login in your browser...")
    webbrowser.open(browser_url)
    server.handle_request()
    server.server_close()
    if result.get("error"):
        raise GarminError(result["error"])
    print("Garmin connected. Access token saved to .env.")


def _number(value: object) -> Optional[int]:
    if isinstance(value, bool):
        return None
    try:
        bpm = int(float(value))
    except (TypeError, ValueError):
        return None
    return bpm if 20 <= bpm <= 240 else None


def parse_heart_rate(payload: object) -> HeartRateReading:
    """Extract the latest valid heart-rate value from common Garmin payloads."""
    if isinstance(payload, dict):
        for key in ("heartRate", "currentHeartRate", "heart_rate", "bpm"):
            bpm = _number(payload.get(key))
            if bpm is not None:
                return HeartRateReading(bpm, payload.get("timestamp"))

        for key in ("samples", "heartRateSamples", "heart_rate_samples"):
            samples = payload.get(key)
            if isinstance(samples, list):
                for sample in reversed(samples):
                    reading = parse_heart_rate(sample)
                    if reading.bpm:
                        return reading

    raise GarminError("Garmin response did not contain a valid heart-rate reading")


def fetch_heart_rate(
    url: Optional[str] = None,
    access_token: Optional[str] = None,
    timeout: int = 15,
) -> HeartRateReading:
    """Fetch the latest heart rate from a configured Garmin endpoint."""
    if os.getenv("GARMIN_PROVIDER", "garminconnect").lower() == "garminconnect":
        from garmin_service import fetch_wrapper_heart_rate

        return fetch_wrapper_heart_rate()

    url = url or os.getenv("GARMIN_HEART_RATE_URL")
    access_token = access_token or os.getenv("GARMIN_ACCESS_TOKEN")
    if not url:
        raise GarminError("Set GARMIN_HEART_RATE_URL before starting Garmin tracking")
    if "your-garmin-proxy.example" in url:
        raise GarminError(
            "Replace GARMIN_HEART_RATE_URL with your real Garmin Health API or proxy endpoint"
        )
    if not access_token:
        raise GarminError("Set GARMIN_ACCESS_TOKEN before starting Garmin tracking")

    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise GarminError(f"Unable to fetch Garmin heart rate: {error}") from error
    return parse_heart_rate(payload)