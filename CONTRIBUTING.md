# Contributing

Thanks for your interest in contributing to actionable-errors. This document
covers the development setup, coding standards, testing philosophy, and
PR process.

---

## Development Setup

```bash
# Clone
git clone https://github.com/grimlor/actionable-errors.git
cd actionable-errors

# Install with dev dependencies (creates .venv automatically)
uv sync --extra dev

# Optional: auto-activate venv
direnv allow
```

## Running Checks

All checks must pass before submitting a PR:

```bash
task check          # runs lint → type → test
```

Or individually:

```bash
task lint           # ruff check src/ tests/
task format         # ruff format src/ tests/
task type           # mypy strict mode
task test           # pytest -v
```

## Code Style

- **Python 3.11+** — use modern syntax (`X | Y` unions, `@dataclass`).
- **`from __future__ import annotations`** at the top of every module.
- **ruff** handles formatting and import sorting. Don't fight it.
- **mypy strict** — all functions need type annotations. No `Any` unless
  you have a good reason and document it.
- **Line length:** 99 characters (configured in `pyproject.toml`).
- **Quote style:** double quotes.

## Zero-Dependency Constraint

This package has **zero runtime dependencies** — stdlib only. This is a
hard architectural constraint, not a preference. `actionable-errors` sits
at the bottom of every dependency tree. Adding a runtime dependency would
transitively infect every consumer.

Dev dependencies (ruff, mypy, pytest, etc.) are fine — they don't ship.

## Testing Standards

Tests are the living specification. Every test class documents a behavioral
requirement, not a code structure.

### Test Class Structure

```python
class TestYourFeature:
    """
    REQUIREMENT: One-sentence summary of the behavioral contract.

    WHO: Who depends on this behavior (calling code, operator, AI agent)
    WHAT: What the behavior is, including failure modes
    WHY: What breaks if this contract is violated

    MOCK BOUNDARY:
        Mock:  nothing — this package is pure computation
        Real:  all classes and functions under test
        Never: construct expected output and assert on the construction
    """

    def test_descriptive_name_of_scenario(self) -> None:
        """
        Given some precondition
        When an action is taken
        Then an observable outcome occurs
        """
        ...
```

### Key Principles

1. **Mock I/O boundaries, not implementation.** Since this package has no
   I/O (stdlib only, no network, no filesystem), most tests will have
   `Mock: nothing` in their mock boundary contract.

2. **Failure specs matter.** For every happy path, ask: what goes wrong?
   Write specs for those failure modes. An unspecified failure is an
   unhandled failure.

3. **Missing spec = missing requirement.** If you find a bug, the first
   step is always adding the test that should have caught it, then fixing
   the code to pass that test.

4. **Every assertion includes a diagnostic message.** Bare assertions are
   not permitted.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the three-audience
error design philosophy and module responsibilities.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add credential sanitizer with configurable patterns

- Eight built-in regex patterns for common credential formats
- Consumer-extensible pattern registration
- 15 tests covering all built-in patterns and custom registration
```

Common prefixes: `feat:`, `fix:`, `test:`, `docs:`, `build:`, `refactor:`,
`style:`, `ci:`, `chore:`.

## Pull Requests

1. **Branch from `main`.**
2. **All checks must pass** — `task check` (lint + type + test).
3. **Include tests** for any new behavior or bug fix.
4. **One concern per PR** — don't mix a new feature with unrelated refactoring.
5. **No runtime dependencies** — this is a hard constraint.
6. **Describe what and why** in the PR description.

## Reporting Issues

When filing an issue:

- **Bug:** Include the error message, what you expected, and steps to
  reproduce. Include the Python version and how actionable-errors was
  installed.
- **Feature request:** Describe the problem you're trying to solve, not
  just the solution you have in mind. Note whether it can be done with
  stdlib only.
