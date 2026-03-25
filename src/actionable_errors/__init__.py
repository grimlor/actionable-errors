"""
actionable-errors: Three-audience error framework.

Every ActionableError speaks to three audiences simultaneously:
- Calling code: typed ErrorType for routing (retry? escalate? ignore?)
- Human operator: suggestion + Troubleshooting steps
- AI agent: AIGuidance with concrete next tool calls
"""

from __future__ import annotations

from actionable_errors.classifier import from_exception
from actionable_errors.error import ActionableError
from actionable_errors.guidance import AIGuidance, Troubleshooting
from actionable_errors.result import ToolResult
from actionable_errors.sanitizer import CredentialSanitizer, register_pattern, sanitize
from actionable_errors.types import ErrorType

__all__ = [
    "AIGuidance",
    "ActionableError",
    "CredentialSanitizer",
    "ErrorType",
    "ToolResult",
    "Troubleshooting",
    "from_exception",
    "register_pattern",
    "sanitize",
]
