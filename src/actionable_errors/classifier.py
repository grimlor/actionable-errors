"""from_exception() keyword-based auto-classifier."""

from __future__ import annotations

from actionable_errors.error import ActionableError
from actionable_errors.types import ErrorType

# Keyword → ErrorType mapping.  First match wins, so order matters.
# Each tuple is (keywords, target_type).
_KEYWORD_RULES: list[tuple[list[str], ErrorType]] = [
    (
        [
            "unauthorized",
            "unauthenticated",
            "credential",
            "login",
            "auth",
            "401",
            "no accounts",
            "token",
            "defaultazurecredential",
        ],
        ErrorType.AUTHENTICATION,
    ),
    (["forbidden", "permission", "denied", "access", "403"], ErrorType.PERMISSION),
    (["timeout", "timed out", "deadline"], ErrorType.TIMEOUT),
    (
        ["connection refused", "connection error", "unreachable", "dns", "connect"],
        ErrorType.CONNECTION,
    ),
    (["not found", "no such", "missing", "does not exist", "404"], ErrorType.NOT_FOUND),
    (["invalid", "validation", "malformed", "schema", "constraint"], ErrorType.VALIDATION),
    (["config", "configuration", "setting", "environment variable"], ErrorType.CONFIGURATION),
]


def from_exception(
    exc: Exception,
    service: str,
    operation: str,
    *,
    suggestion: str | None = None,
) -> ActionableError:
    """
    Classify an arbitrary exception into an ActionableError.

    Scans ``str(exc)`` against keyword rules (case-insensitive) and assigns
    the matching :class:`ErrorType`.  Falls back to ``INTERNAL`` when no
    rule matches.

    If *suggestion* is provided it is passed through to the resulting error.
    """
    text = str(exc).lower()

    for keywords, error_type in _KEYWORD_RULES:
        for kw in keywords:
            if kw in text:
                return ActionableError(
                    error=str(exc),
                    error_type=error_type,
                    service=service,
                    suggestion=suggestion,
                )

    # Fallback: unrecognised → INTERNAL
    return ActionableError(
        error=str(exc),
        error_type=ErrorType.INTERNAL,
        service=service,
        suggestion=suggestion,
    )
