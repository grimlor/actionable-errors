# actionable-errors

[![CI](https://github.com/grimlor/actionable-errors/actions/workflows/ci.yml/badge.svg)](https://github.com/grimlor/actionable-errors/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/grimlor/1fcd9ddb46319b8bf6ed2d6500ae5725/raw/actionable-errors-coverage.json)](https://github.com/grimlor/actionable-errors)
[![PyPI](https://img.shields.io/pypi/v/actionable-errors)](https://pypi.org/project/actionable-errors/)

Three-audience error framework for Python.

Every `ActionableError` speaks to three audiences simultaneously:

| Audience | Uses | Provided by |
|----------|------|-------------|
| **Calling code** | Typed `ErrorType` for routing (retry? escalate? ignore?) | `ErrorType(StrEnum)` — 8 base categories |
| **Human operator** | `suggestion` + `Troubleshooting` steps | Frozen dataclasses with actionable text |
| **AI agent** | `AIGuidance` with concrete next tool calls | Frozen dataclass with tool suggestions |

## Install

```bash
pip install actionable-errors
```

**Zero runtime dependencies** — stdlib only. Sits at the bottom of every dependency tree.

## Quick Start

```python
from actionable_errors import (
    ActionableError,
    AIGuidance,
    ToolResult,
    from_exception,
    sanitize,
)

# Domain-specific factory with built-in defaults
error = ActionableError.authentication(
    service="Azure DevOps",
    raw_error="401 Unauthorized",
)
print(error.suggestion)    # "Check your credentials and try again."
print(error.ai_guidance)   # AIGuidance(action_required="Re-authenticate", command="az login")

# Auto-classify any exception
try:
    raise ConnectionError("Connection refused")
except Exception as exc:
    ae = from_exception(exc, service="Kusto", operation="query")
    print(ae.error_type)   # "connection"

# Typed result envelope for MCP tool responses
result = ToolResult.ok(data={"items": 42})
result = ToolResult.fail(error=error)     # extracts error_type + suggestion

# Credential sanitization
clean = sanitize('password="hunter2" token=abc123')
# → 'password="***" token=***'
```

## Extending ErrorType

Python `StrEnum` can't be subclassed once it has members, so extend via composition:

```python
from enum import StrEnum
from actionable_errors import ActionableError

class RAGErrorType(StrEnum):
    EMBEDDING = "embedding"
    INDEX = "index"

error = ActionableError(
    error="Vector store unavailable",
    error_type=RAGErrorType.INDEX,
    service="pinecone",
    suggestion="Check Pinecone cluster status.",
)
```

## Factories

Eight domain-specific factories with sensible defaults:

| Factory | Key Parameters |
|---------|---------------|
| `.authentication(service, raw_error)` | Default suggestion + AI guidance |
| `.configuration(field_name, reason)` | — |
| `.connection(service, url, raw_error)` | — |
| `.timeout(service, operation, timeout_seconds)` | — |
| `.permission(service, resource, raw_error)` | — |
| `.validation(service, field_name, reason)` | — |
| `.not_found(service, resource_type, resource_id, raw_error)` | — |
| `.internal(service, operation, raw_error)` | — |

All factories accept optional `suggestion`, `ai_guidance`, and `troubleshooting` kwargs.

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run all checks
task check  # lint → type → test (90 tests, 100% coverage)
```

## License

MIT
