"""ActionableError dataclass with factory classmethods."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import UTC, datetime
from typing import Any

from actionable_errors.guidance import AIGuidance, Troubleshooting
from actionable_errors.types import ErrorType


@dataclass
class ActionableError(Exception):
    """Three-audience error — code routing, human suggestion, AI guidance.

    Always carries ``success = False`` and a UTC ``timestamp``.
    Construct via factory classmethods for consistency.
    """

    error: str
    error_type: ErrorType | str
    service: str
    suggestion: str | None = None
    ai_guidance: AIGuidance | None = None
    troubleshooting: Troubleshooting | None = None
    context: dict[str, Any] | None = None
    success: bool = field(default=False, init=False)
    timestamp: str = field(default="", init=False)

    def __post_init__(self) -> None:
        super().__init__(self.error)
        self.success = False
        self.timestamp = datetime.now(tz=UTC).isoformat()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict, excluding None-valued optional fields."""
        result: dict[str, Any] = {}
        for f in fields(self):
            value = getattr(self, f.name)
            if value is None:
                continue
            if f.name == "error_type":
                result["error_type"] = str(value)
            elif isinstance(value, (AIGuidance, Troubleshooting)):
                result[f.name] = value.to_dict()
            else:
                result[f.name] = value
        return result

    # ------------------------------------------------------------------
    # Factory classmethods
    # ------------------------------------------------------------------

    @classmethod
    def authentication(
        cls,
        service: str,
        raw_error: str,
        *,
        suggestion: str | None = None,
        ai_guidance: AIGuidance | None = None,
        troubleshooting: Troubleshooting | None = None,
    ) -> ActionableError:
        """Create an AUTHENTICATION error."""
        return cls(
            error=f"{service} authentication failed: {raw_error}",
            error_type=ErrorType.AUTHENTICATION,
            service=service,
            suggestion=suggestion or "Check your credentials and try again.",
            ai_guidance=ai_guidance
            or AIGuidance(
                action_required="Re-authenticate",
                command="az login",
            ),
            troubleshooting=troubleshooting,
        )

    @classmethod
    def configuration(
        cls,
        field_name: str,
        reason: str,
        *,
        suggestion: str | None = None,
        ai_guidance: AIGuidance | None = None,
        troubleshooting: Troubleshooting | None = None,
    ) -> ActionableError:
        """Create a CONFIGURATION error."""
        return cls(
            error=f"Configuration error — {field_name}: {reason}",
            error_type=ErrorType.CONFIGURATION,
            service="configuration",
            suggestion=suggestion or f"Check the '{field_name}' setting.",
            ai_guidance=ai_guidance,
            troubleshooting=troubleshooting,
        )

    @classmethod
    def connection(
        cls,
        service: str,
        url: str,
        raw_error: str,
        *,
        suggestion: str | None = None,
        ai_guidance: AIGuidance | None = None,
        troubleshooting: Troubleshooting | None = None,
    ) -> ActionableError:
        """Create a CONNECTION error."""
        return cls(
            error=f"{service} connection to {url} failed: {raw_error}",
            error_type=ErrorType.CONNECTION,
            service=service,
            suggestion=suggestion or f"Verify {service} is running at {url}.",
            ai_guidance=ai_guidance,
            troubleshooting=troubleshooting,
        )

    @classmethod
    def timeout(
        cls,
        service: str,
        operation: str,
        timeout_seconds: int | float,
        *,
        suggestion: str | None = None,
        ai_guidance: AIGuidance | None = None,
        troubleshooting: Troubleshooting | None = None,
    ) -> ActionableError:
        """Create a TIMEOUT error."""
        return cls(
            error=f"{service} {operation} timed out after {timeout_seconds}s",
            error_type=ErrorType.TIMEOUT,
            service=service,
            suggestion=suggestion or f"Increase the timeout or optimize the {operation}.",
            ai_guidance=ai_guidance,
            troubleshooting=troubleshooting,
        )

    @classmethod
    def permission(
        cls,
        service: str,
        resource: str,
        raw_error: str,
        *,
        suggestion: str | None = None,
        ai_guidance: AIGuidance | None = None,
        troubleshooting: Troubleshooting | None = None,
    ) -> ActionableError:
        """Create a PERMISSION error."""
        return cls(
            error=f"{service} permission denied on {resource}: {raw_error}",
            error_type=ErrorType.PERMISSION,
            service=service,
            suggestion=suggestion or f"Request access to {resource}.",
            ai_guidance=ai_guidance,
            troubleshooting=troubleshooting,
        )

    @classmethod
    def validation(
        cls,
        service: str,
        field_name: str,
        reason: str,
        *,
        suggestion: str | None = None,
        ai_guidance: AIGuidance | None = None,
        troubleshooting: Troubleshooting | None = None,
    ) -> ActionableError:
        """Create a VALIDATION error."""
        return cls(
            error=f"{service} validation failed — {field_name}: {reason}",
            error_type=ErrorType.VALIDATION,
            service=service,
            suggestion=suggestion or f"Fix the '{field_name}' value: {reason}.",
            ai_guidance=ai_guidance,
            troubleshooting=troubleshooting,
        )

    @classmethod
    def not_found(
        cls,
        service: str,
        resource_type: str,
        resource_id: str,
        raw_error: str,
        *,
        suggestion: str | None = None,
        ai_guidance: AIGuidance | None = None,
        troubleshooting: Troubleshooting | None = None,
    ) -> ActionableError:
        """Create a NOT_FOUND error."""
        return cls(
            error=f"{service} {resource_type} '{resource_id}' not found: {raw_error}",
            error_type=ErrorType.NOT_FOUND,
            service=service,
            suggestion=suggestion or f"Verify the {resource_type} identifier.",
            ai_guidance=ai_guidance,
            troubleshooting=troubleshooting,
        )

    @classmethod
    def internal(
        cls,
        service: str,
        operation: str,
        raw_error: str,
        *,
        suggestion: str | None = None,
        ai_guidance: AIGuidance | None = None,
        troubleshooting: Troubleshooting | None = None,
    ) -> ActionableError:
        """Create an INTERNAL error."""
        return cls(
            error=f"{service} unexpected error in {operation}: {raw_error}",
            error_type=ErrorType.INTERNAL,
            service=service,
            suggestion=suggestion or "Check logs for details.",
            ai_guidance=ai_guidance,
            troubleshooting=troubleshooting,
        )
