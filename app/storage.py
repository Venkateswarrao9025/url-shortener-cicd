"""A tiny in-memory store for short URLs.

Kept deliberately simple (a dict) so the focus stays on the CI/CD pipeline,
not on database setup. Swap this out for SQLite/Postgres later if you want.
"""

from __future__ import annotations

import string
from threading import Lock

# Characters used to build short codes (base62).
_ALPHABET = string.ascii_letters + string.digits


class URLStore:
    """Maps short codes <-> long URLs, with a thread-safe counter."""

    def __init__(self) -> None:
        self._code_to_url: dict[str, str] = {}
        self._counter = 0
        self._lock = Lock()

    @staticmethod
    def _encode(number: int) -> str:
        """Turn an integer into a short base62 code."""
        if number == 0:
            return _ALPHABET[0]
        chars: list[str] = []
        base = len(_ALPHABET)
        while number > 0:
            number, remainder = divmod(number, base)
            chars.append(_ALPHABET[remainder])
        return "".join(reversed(chars))

    def add(self, url: str) -> str:
        """Store a long URL and return its newly generated short code."""
        with self._lock:
            code = self._encode(self._counter)
            self._counter += 1
            self._code_to_url[code] = url
            return code

    def get(self, code: str) -> str | None:
        """Look up the long URL for a code, or None if it doesn't exist."""
        return self._code_to_url.get(code)

    def all(self) -> dict[str, str]:
        """Return a copy of every stored mapping."""
        return dict(self._code_to_url)
