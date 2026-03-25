"""ErrorType base categories — extensible by consumers via standard Python enum extension."""

from __future__ import annotations

from enum import StrEnum


class ErrorType(StrEnum):
    """
    Broad error categories for routing decisions.

    Consumers extend this via standard Python enum inheritance::

        class MyErrorType(ErrorType):
            EMBEDDING = "embedding"
            RATE_LIMIT = "rate_limit"
    """

    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    CONNECTION = "connection"
    TIMEOUT = "timeout"
    PERMISSION = "permission"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    INTERNAL = "internal"
