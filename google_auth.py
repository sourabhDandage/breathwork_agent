import base64
import hashlib
import hmac
import json
import os
import secrets
from http.cookies import SimpleCookie
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class GoogleAuthError(RuntimeError):
    pass


SESSION_COOKIE = "prana_session"


def _required(name):
    value = os.getenv(name)
    if not value:
        raise GoogleAuthError(f"Set {name} before using Google login")
    return value


def google_login_url():
    client_id = _required("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    state = secrets.token_urlsafe(24)
    params = urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    })
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}", state


def exchange_code(code, state, expected_state):
    if not hmac.compare_digest(state or "", expected_state or ""):
        raise GoogleAuthError("Google login state validation failed")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    request = Request(
        "https://oauth2.googleapis.com/token",
        data=urlencode({
            "code": code,
            "client_id": _required("GOOGLE_CLIENT_ID"),
            "client_secret": _required("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urlopen(request, timeout=15) as response:
            token_payload = json.load(response)
        access_token = token_payload["access_token"]
        user_request = Request(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        with urlopen(user_request, timeout=15) as response:
            return json.load(response)
    except (KeyError, HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise GoogleAuthError(f"Google login failed: {error}") from error


def make_session(user):
    payload = base64.urlsafe_b64encode(json.dumps({
        "email": user.get("email", ""),
        "name": user.get("name", "Google user"),
    }).encode()).decode().rstrip("=")
    secret = _required("SESSION_SECRET").encode()
    signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def read_session(cookie_header):
    if not cookie_header:
        return None
    cookies = SimpleCookie()
    cookies.load(cookie_header)
    value = cookies.get(SESSION_COOKIE)
    if not value:
        return None
    try:
        payload, signature = value.value.split(".", 1)
        expected = hmac.new(_required("SESSION_SECRET").encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        padded = payload + "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))
    except (ValueError, TypeError, json.JSONDecodeError, GoogleAuthError):
        return None
