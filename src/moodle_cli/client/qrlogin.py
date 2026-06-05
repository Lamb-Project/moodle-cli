"""QR-login: turn a Moodle "QR login" passport into a web-service token.

Why this exists
---------------
Newer Moodle (4.x) sites show a **QR code** on the mobile-app / security-keys
page instead of a plain web-service token string. That QR is NOT a token — it
encodes a one-time *autologin passport*, e.g.::

    moodlemobile://https://moodle.example.com?qrlogin=<key>&userid=<id>

Moodle exposes ``tool_mobile_get_tokens_for_qr_login``, which exchanges a fresh
passport for the real mobile token. It is callable BEFORE authentication via
``/lib/ajax/service-nologin.php``, so this is the **SSO/CAS-friendly** path:
no password and no admin needed — exactly the case where ``auth login`` with a
username/password fails.

Two hard constraints on the passport key:

* it is **single-use**, and
* it has a **short TTL** (~3 minutes by default).

So: refresh the QR page, then exchange immediately. A stale key returns the
Moodle error ``invalidkey``.

One server-side gotcha: the exchange function is gated behind an *app-request*
check (error ``apprequired``) unless the request carries a ``MoodleMobile``
``User-Agent``. We send one; see :data:`MOODLE_APP_USER_AGENT`.
"""

from __future__ import annotations

import urllib.parse
from typing import Any

import httpx

from moodle_cli.client.exceptions import AuthenticationError, ConnectionError

# The official Moodle app self-identifies with a MoodleMobile User-Agent. Without
# it, tool_mobile_get_tokens_for_qr_login is rejected with the `apprequired` error.
MOODLE_APP_USER_AGENT = "MoodleMobile 4.5.0 (44500)"


def parse_moodlemobile_uri(uri: str) -> tuple[str, str, str]:
    """Parse a ``moodlemobile://<site>?qrlogin=<key>&userid=<id>`` URI.

    Returns ``(site_url, qrlogin_key, userid)``. Note the URI nests a second
    scheme (the site is ``https://...``), so we cannot use ``urlsplit`` on the
    whole thing — we strip the ``moodlemobile://`` prefix first.
    """
    rest = uri.split("://", 1)[1] if "://" in uri else uri
    if "?" not in rest:
        raise AuthenticationError(
            "QR payload has no query string with qrlogin/userid. "
            "Is this a 'QR with automatic login' code?"
        )
    base, query = rest.split("?", 1)
    site_url = base.rstrip("/")
    if not site_url.startswith("http"):
        site_url = "https://" + site_url
    parsed = urllib.parse.parse_qs(query)
    key = parsed.get("qrlogin", [""])[0]
    userid = parsed.get("userid", [""])[0]
    if not key or not userid:
        raise AuthenticationError(
            f"Could not find qrlogin/userid in QR payload: {query}"
        )
    return site_url, key, userid


def decode_qr_image(path: str) -> str:
    """Decode the text payload of a QR-code image file.

    Requires the optional ``qr`` extra (``pyzbar`` + ``pillow``). Tries a few
    upscales / binarisations because the QR shown on a Moodle page is often small
    and dense.
    """
    try:
        from PIL import Image  # type: ignore[import-not-found]
        from pyzbar.pyzbar import decode  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise AuthenticationError(
            "QR image decoding needs the optional 'qr' extra:\n"
            "    pip install 'moodle-cli[qr]'\n"
            "(macOS note: the system Python may fail to load Homebrew's libzbar "
            "due to SIP — use a venv/uv Python, with "
            "DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib.)\n"
            "Alternatively, decode the QR yourself and pass the moodlemobile:// URI."
        ) from exc

    gray = Image.open(path).convert("L")
    for scale in (1, 2, 3, 4, 6):
        big = gray.resize((gray.width * scale, gray.height * scale), Image.LANCZOS)
        variants = (big, big.point(lambda x: 0 if x < 128 else 255, "1").convert("L"))
        for variant in variants:
            result = decode(variant)
            if result:
                return str(result[0].data.decode("utf-8", "replace"))
    raise AuthenticationError(f"Could not decode any QR code from image: {path}")


def exchange_qr_login(
    site_url: str, qrlogin_key: str, userid: str | int, timeout: float = 30.0
) -> dict[str, Any]:
    """Exchange a fresh qrlogin passport for a token.

    Calls ``tool_mobile_get_tokens_for_qr_login`` via the no-login AJAX endpoint.
    Returns the ``data`` dict, which contains ``token`` (and ``privatetoken``).

    Raises :class:`AuthenticationError` on a Moodle-level error (e.g. an expired
    or already-used key -> ``invalidkey``; a missing app User-Agent ->
    ``apprequired``), and :class:`ConnectionError` on transport failure.
    """
    base = site_url.rstrip("/")
    endpoint = f"{base}/lib/ajax/service-nologin.php?info=tool_mobile_get_tokens_for_qr_login"
    payload = [
        {
            "index": 0,
            "methodname": "tool_mobile_get_tokens_for_qr_login",
            "args": {"qrloginkey": qrlogin_key, "userid": int(userid)},
        }
    ]
    try:
        resp = httpx.post(
            endpoint,
            json=payload,
            headers={"User-Agent": MOODLE_APP_USER_AGENT},
            timeout=timeout,
        )
        resp.raise_for_status()
    except httpx.ConnectError as exc:
        raise ConnectionError(f"Could not connect to {base}: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        raise ConnectionError(f"HTTP {exc.response.status_code} from {base}") from exc

    data = resp.json()
    if not isinstance(data, list) or not data:
        raise AuthenticationError(f"Unexpected QR-login response shape: {data!r}")

    item = data[0]
    if item.get("error"):
        exc_info = item.get("exception", {}) or {}
        code = exc_info.get("errorcode")
        message = exc_info.get("message", "QR login exchange failed")
        if code == "invalidkey":
            message += (
                " — the QR key is expired or already used (keys are single-use "
                "with a ~3-minute TTL). Refresh the QR page and retry immediately."
            )
        elif code == "apprequired":
            message += (
                " — the site requires an app request; this is a bug if you are "
                "using moodle-cli (we send a MoodleMobile User-Agent)."
            )
        raise AuthenticationError(message, error_code=code)

    result = item.get("data") or {}
    if "token" not in result:
        raise AuthenticationError(f"No token in QR-login response: {result!r}")
    return result
