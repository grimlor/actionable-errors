"""Credential redaction — regex-based, 8+ patterns, configurable."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class _Pattern:
    """Internal representation of a registered redaction pattern."""

    name: str
    regex: re.Pattern[str]
    replacement: str


# ------------------------------------------------------------------ #
# Built-in patterns                                                   #
# ------------------------------------------------------------------ #

_BUILTIN_PATTERNS: list[_Pattern] = [
    # password="...", password=..., Password=...
    _Pattern(
        name="password_assignment",
        regex=re.compile(
            r'((?:password|passwd|pwd)\s*[=:]\s*)"?([^";,\s]+)"?',
            re.IGNORECASE,
        ),
        replacement=r"\1***",
    ),
    # api_key="...", apikey=...
    _Pattern(
        name="api_key_assignment",
        regex=re.compile(
            r'((?:api[_-]?key)\s*[=:]\s*)"?([^";,\s]+)"?',
            re.IGNORECASE,
        ),
        replacement=r"\1***",
    ),
    # token="...", access_token=...
    _Pattern(
        name="token_assignment",
        regex=re.compile(
            r'((?:token|access_token)\s*[=:]\s*)"?([^";,\s]+)"?',
            re.IGNORECASE,
        ),
        replacement=r"\1***",
    ),
    # client_secret="...", secret=...
    _Pattern(
        name="secret_assignment",
        regex=re.compile(
            r'((?:(?:client_)?secret)\s*[=:]\s*)"?([^";,\s]+)"?',
            re.IGNORECASE,
        ),
        replacement=r"\1***",
    ),
    # Authorization: Bearer <token>
    _Pattern(
        name="bearer_token",
        regex=re.compile(
            r"(Bearer\s+)\S+",
            re.IGNORECASE,
        ),
        replacement=r"\1***",
    ),
    # SAS token sig= parameter
    _Pattern(
        name="sas_signature",
        regex=re.compile(
            r"(sig=)[^&\s]+",
            re.IGNORECASE,
        ),
        replacement=r"\1***",
    ),
    # Connection string Password=...;
    _Pattern(
        name="connection_string_password",
        regex=re.compile(
            r"(Password\s*=\s*)([^;]+)",
            re.IGNORECASE,
        ),
        replacement=r"\1***",
    ),
    # AccountKey=...;
    _Pattern(
        name="account_key",
        regex=re.compile(
            r"(AccountKey\s*=\s*)([^;]+)",
            re.IGNORECASE,
        ),
        replacement=r"\1***",
    ),
]


@dataclass
class CredentialSanitizer:
    """Regex-based credential sanitizer with built-in + custom patterns."""

    _patterns: list[_Pattern] = field(default_factory=lambda: list(_BUILTIN_PATTERNS))

    def register_pattern(
        self,
        name: str,
        pattern: str | re.Pattern[str],
        replacement: str = "***",
    ) -> None:
        """
        Register an additional redaction pattern.

        Parameters
        ----------
        name:
            Human-readable label for logging/debugging.
        pattern:
            Raw string or compiled ``re.Pattern``.
        replacement:
            Replacement text (may use back-references).

        """
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
        self._patterns.append(_Pattern(name=name, regex=compiled, replacement=replacement))

    def sanitize(self, text: str) -> str:
        """Apply all registered patterns to *text* and return the redacted result."""
        for p in self._patterns:
            text = p.regex.sub(p.replacement, text)
        return text


# ------------------------------------------------------------------ #
# Module-level convenience API (uses a shared default instance)       #
# ------------------------------------------------------------------ #

_default = CredentialSanitizer()


def sanitize(text: str) -> str:
    """Redact credentials from *text* using built-in patterns."""
    return _default.sanitize(text)


def register_pattern(
    name: str,
    pattern: str | re.Pattern[str],
    replacement: str = "***",
) -> None:
    """Register an additional redaction pattern on the default sanitizer."""
    _default.register_pattern(name=name, pattern=pattern, replacement=replacement)
