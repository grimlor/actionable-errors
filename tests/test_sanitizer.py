"""BDD specs for actionable_errors.sanitizer — credential redaction.

Covers:
    TestBuiltInPatterns — each built-in pattern redacts known credential formats
    TestCustomPatternRegistration — consumers register additional patterns
    TestSanitizerEdgeCases — empty strings, no matches, multiple matches in one string,
        module-level register_pattern applies to default (public API — added for 100% coverage)

Public API surface (from src/actionable_errors/sanitizer.py):
    CredentialSanitizer:
        .sanitize(text: str) -> str
        .register_pattern(name: str, pattern: str | re.Pattern[str], replacement: str = "***") -> None

    sanitize(text: str) -> str  (module-level convenience using default instance)
    register_pattern(name: str, pattern: str | re.Pattern[str], replacement: str = "***") -> None
"""

from __future__ import annotations

import re

from actionable_errors.sanitizer import CredentialSanitizer, register_pattern, sanitize


class TestBuiltInPatterns:
    """
    REQUIREMENT: Built-in patterns redact common credential formats from text.

    WHO: Error producers logging or returning messages that may contain leaked secrets
    WHAT: The sanitizer redacts passwords, API keys, bearer tokens, SAS tokens,
          connection strings, Azure account keys, base64 secrets, and generic
          token assignments; redacted text replaces the secret portion only,
          preserving surrounding context
    WHY: Error messages propagate through logs, MCP responses, and AI agent context —
         any of these channels could leak credentials if not redacted

    MOCK BOUNDARY:
        Mock:  nothing — pure regex transformation
        Real:  CredentialSanitizer instance and its output
        Never: inspect internal pattern list directly
    """

    def test_password_in_assignment_is_redacted(self) -> None:
        """
        Given text containing a password assignment like password="secret123"
        When sanitize() is called
        Then the password value is replaced with a redaction marker
        """
        # Given: text with a password
        text = 'Connection failed: password="s3cret!Pass"'

        # When: sanitizing
        result = sanitize(text)

        # Then: password value is redacted
        assert "s3cret!Pass" not in result, (
            f"Password should be redacted, got: {result!r}"
        )
        assert "password" in result.lower(), (
            f"Context around password should be preserved, got: {result!r}"
        )

    def test_api_key_is_redacted(self) -> None:
        """
        Given text containing an API key like api_key="abc123xyz"
        When sanitize() is called
        Then the key value is redacted
        """
        # Given: text with an API key
        text = 'Error: api_key="sk-proj-abc123def456"'

        # When: sanitizing
        result = sanitize(text)

        # Then: key is redacted
        assert "sk-proj-abc123def456" not in result, (
            f"API key should be redacted, got: {result!r}"
        )

    def test_bearer_token_is_redacted(self) -> None:
        """
        Given text containing a Bearer token in an Authorization header
        When sanitize() is called
        Then the token is redacted
        """
        # Given: text with a bearer token
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.sig"

        # When: sanitizing
        result = sanitize(text)

        # Then: token is redacted
        assert "eyJhbGciOiJ" not in result, (
            f"Bearer token should be redacted, got: {result!r}"
        )
        assert "Bearer" in result, (
            f"'Bearer' prefix should be preserved, got: {result!r}"
        )

    def test_sas_token_is_redacted(self) -> None:
        """
        Given text containing an Azure SAS token (?sv=...&sig=...)
        When sanitize() is called
        Then the SAS signature is redacted
        """
        # Given: text with a SAS token
        text = "URL: https://storage.blob.core.windows.net/container?sv=2021-06-08&sig=abc123signature"

        # When: sanitizing
        result = sanitize(text)

        # Then: SAS signature is redacted
        assert "abc123signature" not in result, (
            f"SAS signature should be redacted, got: {result!r}"
        )

    def test_connection_string_password_is_redacted(self) -> None:
        """
        Given text containing a connection string with Password=
        When sanitize() is called
        Then the password portion is redacted
        """
        # Given: text with a connection string
        text = "Server=tcp:myserver;Database=mydb;Password=MyP@ssw0rd;User=admin"

        # When: sanitizing
        result = sanitize(text)

        # Then: password is redacted
        assert "MyP@ssw0rd" not in result, (
            f"Connection string password should be redacted, got: {result!r}"
        )

    def test_azure_account_key_is_redacted(self) -> None:
        """
        Given text containing an Azure storage AccountKey=
        When sanitize() is called
        Then the key is redacted
        """
        # Given: text with an account key
        text = "AccountName=myaccount;AccountKey=abc123def456ghi789+base64key==;EndpointSuffix=core.windows.net"

        # When: sanitizing
        result = sanitize(text)

        # Then: account key is redacted
        assert "abc123def456ghi789+base64key==" not in result, (
            f"Account key should be redacted, got: {result!r}"
        )

    def test_generic_token_assignment_is_redacted(self) -> None:
        """
        Given text containing a token assignment like token="abc123"
        When sanitize() is called
        Then the token value is redacted
        """
        # Given: text with a generic token
        text = 'Failed with token="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"'

        # When: sanitizing
        result = sanitize(text)

        # Then: token value is redacted
        assert "ghp_" not in result, (
            f"Token value should be redacted, got: {result!r}"
        )

    def test_secret_assignment_is_redacted(self) -> None:
        """
        Given text containing a secret assignment like secret="value"
        When sanitize() is called
        Then the secret value is redacted
        """
        # Given: text with a secret
        text = 'client_secret="my-super-secret-value-123"'

        # When: sanitizing
        result = sanitize(text)

        # Then: secret is redacted
        assert "my-super-secret-value-123" not in result, (
            f"Secret value should be redacted, got: {result!r}"
        )


class TestCustomPatternRegistration:
    """
    REQUIREMENT: Consumers can register additional credential patterns.

    WHO: Downstream projects with domain-specific secret formats
    WHAT: register_pattern() adds a new regex pattern to the sanitizer;
          subsequent sanitize() calls apply the new pattern alongside built-ins
    WHY: The built-in patterns cover common formats, but each project may have
         secrets in custom formats (e.g., Databricks tokens, custom API keys)

    MOCK BOUNDARY:
        Mock:  nothing — pure function calls
        Real:  CredentialSanitizer with custom patterns
        Never: inspect internal pattern storage directly
    """

    def test_custom_pattern_is_applied(self) -> None:
        """
        Given a consumer registers a custom pattern for Databricks tokens
        When sanitize() is called on text containing that token format
        Then the custom token is redacted
        """
        # Given: a fresh sanitizer with a custom pattern
        s = CredentialSanitizer()
        s.register_pattern(
            name="databricks_token",
            pattern=r"dapi[a-f0-9]{32}",
            replacement="***DATABRICKS_TOKEN***",
        )

        # When: sanitizing text with a Databricks token
        text = "Connecting with dapi0123456789abcdef0123456789abcdef to cluster"
        result = s.sanitize(text)

        # Then: custom token is redacted
        assert "dapi0123456789abcdef" not in result, (
            f"Databricks token should be redacted, got: {result!r}"
        )
        assert "***DATABRICKS_TOKEN***" in result, (
            f"Custom replacement should appear, got: {result!r}"
        )

    def test_custom_pattern_works_alongside_builtins(self) -> None:
        """
        Given a consumer registers a custom pattern
        When sanitize() is called on text with both custom and built-in secrets
        Then both are redacted
        """
        # Given: sanitizer with custom pattern
        s = CredentialSanitizer()
        s.register_pattern(
            name="custom_key",
            pattern=r"CUSTOM-[A-Z0-9]{16}",
            replacement="***CUSTOM***",
        )

        # When: text has both types
        text = 'password="hunter2" and key=CUSTOM-ABCDEFGH12345678'
        result = s.sanitize(text)

        # Then: both are redacted
        assert "hunter2" not in result, (
            f"Built-in password pattern should still work, got: {result!r}"
        )
        assert "CUSTOM-ABCDEFGH12345678" not in result, (
            f"Custom pattern should also work, got: {result!r}"
        )

    def test_register_with_compiled_regex(self) -> None:
        """
        Given a consumer registers a pattern using a compiled re.Pattern
        When sanitize() is called
        Then the compiled pattern is applied
        """
        # Given: compiled regex pattern
        s = CredentialSanitizer()
        pattern = re.compile(r"MYSECRET-\d{6}")
        s.register_pattern(name="my_secret", pattern=pattern)

        # When: sanitizing
        text = "Error with MYSECRET-123456"
        result = s.sanitize(text)

        # Then: pattern is applied
        assert "MYSECRET-123456" not in result, (
            f"Compiled pattern should be applied, got: {result!r}"
        )


class TestSanitizerEdgeCases:
    """
    REQUIREMENT: Sanitizer handles edge cases gracefully.

    WHO: Any code path that may pass unusual input to the sanitizer
    WHAT: Empty strings pass through unchanged; text with no credentials
          passes through unchanged; multiple credentials in one string are
          all redacted
    WHY: Edge cases that crash or corrupt output would undermine trust in the
         sanitizer and cause callers to skip redaction

    MOCK BOUNDARY:
        Mock:  nothing — pure function
        Real:  sanitize function and its output
        Never: mock regex engine internals
    """

    def test_empty_string_passes_through(self) -> None:
        """
        When sanitize() is called on an empty string
        Then it returns an empty string
        """
        # Given: empty input

        # When: sanitizing
        result = sanitize("")

        # Then: empty output
        assert result == "", (
            f"Empty input should return empty output, got {result!r}"
        )

    def test_text_without_credentials_passes_through_unchanged(self) -> None:
        """
        Given text that contains no credential patterns
        When sanitize() is called
        Then the text is returned unchanged
        """
        # Given: safe text
        text = "The query returned 42 rows from the users table."

        # When: sanitizing
        result = sanitize(text)

        # Then: unchanged
        assert result == text, (
            f"Safe text should pass through unchanged.\n"
            f"Expected: {text!r}\n"
            f"Got:      {result!r}"
        )

    def test_module_level_register_pattern_applies_to_default(self) -> None:
        """
        Given a pattern registered via the module-level register_pattern()
        When sanitize() is called on matching text
        Then the pattern is applied by the default sanitizer
        """
        # Given: register a custom pattern on the module-level default
        register_pattern(
            name="test_custom_global",
            pattern=r"GLOBALTEST-[A-Z0-9]{8}",
            replacement="***GLOBAL***",
        )

        # When: sanitizing via module-level function
        result = sanitize("Found GLOBALTEST-ABCD1234 in output")

        # Then: custom pattern was applied
        assert "GLOBALTEST-ABCD1234" not in result, (
            f"Module-level register_pattern should work, got: {result!r}"
        )
        assert "***GLOBAL***" in result, (
            f"Custom replacement should appear, got: {result!r}"
        )

    def test_multiple_credentials_in_one_string_are_all_redacted(self) -> None:
        """
        Given text containing multiple different credential patterns
        When sanitize() is called
        Then all credentials are redacted
        """
        # Given: text with multiple secrets
        text = (
            'password="secret1" and token="secret2" '
            "and Authorization: Bearer eyJtoken123.payload.sig"
        )

        # When: sanitizing
        result = sanitize(text)

        # Then: all secrets are gone
        assert "secret1" not in result, (
            f"First password should be redacted, got: {result!r}"
        )
        assert "secret2" not in result, (
            f"Second token should be redacted, got: {result!r}"
        )
        assert "eyJtoken123" not in result, (
            f"Bearer token should be redacted, got: {result!r}"
        )
