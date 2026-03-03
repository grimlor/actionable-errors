# actionable-errors

Three-audience error framework for Python.

Every `ActionableError` speaks to three audiences simultaneously:

| Audience | Uses | Provided by |
|----------|------|-------------|
| **Calling code** | Typed `ErrorType` for routing (retry? escalate? ignore?) | `ErrorType(StrEnum)` base categories |
| **Human operator** | `suggestion` + `Troubleshooting` steps | Frozen dataclasses with actionable text |
| **AI agent** | `AIGuidance` with concrete next tool calls | Frozen dataclass with tool suggestions |

## Install

```bash
pip install actionable-errors
```

## Zero Dependencies

This package uses only the Python standard library. It sits at the bottom of every dependency tree.

## Quick Start

```python
from actionable_errors import ActionableError, ErrorType, ToolResult

# Typed error with actionable guidance
error = ActionableError.authentication(
    message="Token expired",
    suggestion="Run `az login` to refresh credentials",
)

# Typed result envelope
result = ToolResult.ok(data={"items": 42})
result = ToolResult.fail(error=error)
```

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run all checks
task check  # lint → type → test
```

## License

MIT
