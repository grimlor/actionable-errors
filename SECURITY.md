# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it
responsibly by emailing the maintainer directly rather than opening a public
issue.

## Scope

This package is a pure-Python error framework with zero runtime dependencies
and no I/O. The primary security consideration is the credential sanitizer:

- **Credential sanitizer** — `actionable_errors.sanitizer` redacts tokens,
  SAS keys, passwords, and connection strings from error messages. If you
  discover a credential pattern that is not caught by the built-in rules,
  please report it as a security vulnerability.
- **Error messages** — `ActionableError` instances may carry exception
  messages from upstream code. Consumers should be aware that `to_dict()`
  output may contain sensitive context unless the sanitizer is applied first.

## Best Practices

- Always pass error messages through the sanitizer before logging or returning
  them to external callers (AI agents, API responses, etc.)
- Register additional credential patterns for domain-specific secrets your
  application handles
- Do not include raw credentials in `suggestion` or `AIGuidance` fields
