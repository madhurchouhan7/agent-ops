"""Recursive redaction engine for scrubbing credentials and secrets."""

from __future__ import annotations

import re
from typing import Any

SENSITIVE_KEY_SUBSTRINGS: frozenset[str] = frozenset(
    {
        "api_key",
        "apikey",
        "secret",
        "token",
        "password",
        "passwd",
        "authorization",
        "auth",
        "cookie",
        "private_key",
        "client_secret",
        "access_token",
        "refresh_token",
    }
)

SENSITIVE_VALUE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)\bbearer\s+[a-zA-Z0-9_\-\.]+\b"),
    re.compile(r"\bsk-[a-zA-Z0-9]{20,}\b"),
    re.compile(r"\bghp_[a-zA-Z0-9]{36}\b"),
    re.compile(r"(?i)\bbasic\s+[a-zA-Z0-9+/=]{10,}\b"),
]

REDACTED_SUBSTITUTE = "[REDACTED]"


class RedactionEngine:
    """Recursively scrub sensitive keys and token shapes from data."""

    @classmethod
    def is_sensitive_key(cls, key: str) -> bool:
        """Check whether a dictionary key corresponds to sensitive data."""
        normalized = key.strip().lower()
        return any(term in normalized for term in SENSITIVE_KEY_SUBSTRINGS)

    @classmethod
    def redact_string(cls, value: str) -> str:
        """Scrub known secret formats (tokens, bearer auth) from a string."""
        sanitized = value
        for pattern in SENSITIVE_VALUE_PATTERNS:
            sanitized = pattern.sub(REDACTED_SUBSTITUTE, sanitized)
        return sanitized

    @classmethod
    def redact(cls, data: Any, max_depth: int = 25) -> Any:
        """Recursively scrub sensitive keys and patterns from objects."""
        if max_depth <= 0:
            return data

        if isinstance(data, dict):
            redacted_dict: dict[str, Any] = {}
            for key, val in data.items():
                if isinstance(key, str) and cls.is_sensitive_key(key):
                    redacted_dict[key] = REDACTED_SUBSTITUTE
                else:
                    redacted_dict[key] = cls.redact(val, max_depth - 1)
            return redacted_dict

        if isinstance(data, list):
            return [cls.redact(item, max_depth - 1) for item in data]

        if isinstance(data, tuple):
            return tuple(cls.redact(item, max_depth - 1) for item in data)

        if isinstance(data, set):
            return {cls.redact(item, max_depth - 1) for item in data}

        if isinstance(data, str):
            return cls.redact_string(data)

        return data
