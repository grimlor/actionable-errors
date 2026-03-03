"""AIGuidance and Troubleshooting frozen dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any


@dataclass(frozen=True)
class AIGuidance:
    """Structured guidance for AI agents consuming error responses.

    Only ``action_required`` is mandatory.  Optional fields let producers
    provide richer context without burdening simple callers.
    """

    action_required: str
    command: str | None = None
    discovery_tool: str | None = None
    checks: list[str] | None = None
    steps: list[str] | None = None
    optimization_tips: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict, excluding None-valued optional fields."""
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if getattr(self, f.name) is not None
        }


@dataclass(frozen=True)
class Troubleshooting:
    """Ordered human-readable troubleshooting steps.

    ``steps`` must contain at least one entry.
    """

    steps: list[str]

    def __post_init__(self) -> None:
        if not self.steps:
            msg = "Troubleshooting requires at least one step."
            raise ValueError(msg)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {"steps": list(self.steps)}
