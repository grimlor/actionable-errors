# CHANGELOG

<!-- version list -->

## v1.0.0 (2026-03-03)

### Build System

- Lower Python floor to >=3.11 and add CI version matrix\n\nNo 3.12-specific features are used —
  true floor is 3.11 (StrEnum,\ndatetime.UTC). Updated ruff target-version and mypy
  python_version\nto py311/3.11. CI now tests 3.11, 3.12, and 3.13 in a matrix\n(lint/type/badge
  only on 3.13). Added 3.11 classifier."
  ([`52ff09b`](https://github.com/grimlor/actionable-errors/commit/52ff09b698c26c195f3fced70d5b2860505823ea))

### Continuous Integration

- **release**: Add semantic-release config and automated release workflow
  ([`fc96028`](https://github.com/grimlor/actionable-errors/commit/fc9602806368941ea970f1675c65936bdca8703b))


## v0.1.0 (2026-03-03)

- Initial Release
