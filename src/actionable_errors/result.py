"""ToolResult typed envelope — success/failure with data/error fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from actionable_errors.error import ActionableError


@dataclass
class ToolResult:
    """
    Structured envelope for MCP tool responses.

    Use the ``.ok()`` and ``.fail()`` factory classmethods instead of
    constructing directly.
    """

    success: bool
    data: Any | None = None
    error: str | None = None
    error_type: str | None = None
    suggestion: str | None = None
    ai_guidance: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def ok(
        cls,
        data: Any | None = None,
        *,
        suggestion: str | None = None,
        ai_guidance: dict[str, Any] | None = None,
    ) -> ToolResult:
        """Create a success result."""
        return cls(
            success=True,
            data=data,
            suggestion=suggestion,
            ai_guidance=ai_guidance,
        )

    @classmethod
    def fail(
        cls,
        error: str | ActionableError,
        *,
        suggestion: str | None = None,
        ai_guidance: dict[str, Any] | None = None,
    ) -> ToolResult:
        """
        Create a failure result from a string or :class:`ActionableError`.

        When *error* is an ``ActionableError``, ``error_type`` and
        ``suggestion`` are extracted automatically.  An explicit
        *suggestion* kwarg overrides the one carried by the error.
        """
        if isinstance(error, ActionableError):
            return cls(
                success=False,
                error=error.error,
                error_type=str(error.error_type),
                suggestion=suggestion if suggestion is not None else error.suggestion,
                ai_guidance=ai_guidance,
            )
        return cls(
            success=False,
            error=error,
            suggestion=suggestion,
            ai_guidance=ai_guidance,
        )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict, excluding None-valued optional fields."""
        d: dict[str, Any] = {"success": self.success}
        if self.data is not None:
            d["data"] = self.data
        if self.error is not None:
            d["error"] = self.error
        if self.error_type is not None:
            d["error_type"] = self.error_type
        if self.suggestion is not None:
            d["suggestion"] = self.suggestion
        if self.ai_guidance is not None:
            d["ai_guidance"] = self.ai_guidance
        return d
