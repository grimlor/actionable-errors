# Architecture

> Error philosophy and module responsibilities for contributors.

---

## Design Principle: Three-Audience Errors

Every `ActionableError` speaks to three audiences simultaneously:

| Audience | Uses | Provided by |
|----------|------|-------------|
| **Calling code** | Typed `ErrorType` for routing (retry? escalate? ignore?) | `ErrorType(StrEnum)` base categories |
| **Human operator** | `suggestion` + `Troubleshooting` steps | Frozen dataclasses with actionable text |
| **AI agent** | `AIGuidance` with concrete next tool calls | Frozen dataclass with tool suggestions |

This is not a convenience pattern — it is the core invariant. An error that
only speaks to one audience forces consumers to parse, guess, or ignore.

---

## Module Map

```
actionable_errors/
├── types.py        ErrorType(StrEnum) — base categories, extensible by consumers
├── guidance.py     AIGuidance, Troubleshooting — frozen dataclasses
├── error.py        ActionableError — the central dataclass + factory classmethods
├── classifier.py   from_exception() — keyword-based auto-classifier
├── sanitizer.py    Credential redaction — regex, 8+ patterns, configurable
├── result.py       ToolResult — typed envelope (success/failure + data/error)
└── py.typed        PEP 561 marker
```

### Dependency Flow (Internal)

```
types.py ──▶ guidance.py ──▶ error.py ──▶ classifier.py
                                │
                                ▼
                            result.py

sanitizer.py  (independent — no internal imports)
```

---

## Key Decisions

### Zero Runtime Dependencies

This package uses only the Python standard library. It sits at the bottom of
every dependency tree (`ado-workflows`, `jobsearch-rag`, `pdp-dev-mcp`, and
future projects all depend on it). A runtime dependency here would transitively
infect every consumer.

### Extensible ErrorType

`ErrorType(StrEnum)` defines 8 base categories (`AUTHENTICATION`, `CONFIGURATION`,
`CONNECTION`, `TIMEOUT`, `PERMISSION`, `VALIDATION`, `NOT_FOUND`, `INTERNAL`).

Python's `StrEnum` cannot be subclassed once it has members, so consumers extend
via composition — define their own `StrEnum` and pass values to `error_type`,
which accepts `ErrorType | str`:

```python
from enum import StrEnum
from actionable_errors import ActionableError

class RAGErrorType(StrEnum):
    EMBEDDING = "embedding"
    INDEX = "index"

error = ActionableError(
    error="Embedding failed",
    error_type=RAGErrorType.EMBEDDING,
    service="openai",
)
```

No registration, no plugin system — standard Python enums with duck-typed string values.

### ToolResult Envelope

Formalizes the ad-hoc `{"success": bool, "data"/"error": ...}` dict pattern.
`.ok()` / `.fail()` factory methods. `.to_dict()` for serialization. Optional
`ai_guidance` and `suggestion` fields.

### Credential Sanitizer

Regex-based redaction with 8+ built-in patterns (tokens, SAS keys, passwords,
connection strings). Consumers register additional patterns for domain-specific
secrets. Applied to error messages before logging or returning to external callers.
