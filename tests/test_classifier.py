"""
BDD specs for actionable_errors.classifier — from_exception() auto-classification.

Covers:
    TestExceptionClassification — keyword-based routing from raw exceptions to typed errors
    TestClassifierSuggestionPreservation — caller-supplied suggestions override defaults

Public API surface (from src/actionable_errors/classifier.py):
    from_exception(
        error: Exception,
        service: str,
        operation: str,
        *,
        suggestion: str | None = None,
    ) -> ActionableError
"""

from __future__ import annotations

from actionable_errors.classifier import from_exception
from actionable_errors.error import ActionableError
from actionable_errors.types import ErrorType


class TestExceptionClassification:
    """
    REQUIREMENT: from_exception() auto-classifies exceptions by keyword patterns.

    WHO: Code at I/O boundaries that catches generic exceptions and needs to
         produce typed ActionableErrors without manual classification
    WHAT: Authentication keywords (unauthorized, 401, credential, token) route to
          AUTHENTICATION; permission keywords (forbidden, 403) route to PERMISSION;
          timeout keywords route to TIMEOUT; connection keywords route to CONNECTION;
          not-found keywords route to NOT_FOUND; validation keywords route to
          VALIDATION; unrecognized exceptions route to INTERNAL
    WHY: Without auto-classification, every except block must manually decide the
         error type — inconsistent and easily forgotten

    MOCK BOUNDARY:
        Mock:  nothing — pure keyword matching
        Real:  from_exception function and its output
        Never: patch the keyword sets inside the classifier
    """

    def test_unauthorized_routes_to_authentication(self) -> None:
        """
        Given an exception whose message contains "unauthorized"
        When from_exception() classifies it
        Then the result is an AUTHENTICATION-typed error
        """
        # Given: an auth-related exception
        exc = Exception("HTTP 401 Unauthorized")

        # When: classifying
        result = from_exception(exc, service="Azure DevOps", operation="get_pr")

        # Then: routed to AUTHENTICATION
        assert result.error_type == ErrorType.AUTHENTICATION, (
            f"Expected AUTHENTICATION for '401 Unauthorized', got {result.error_type!r}"
        )

    def test_credential_keyword_routes_to_authentication(self) -> None:
        """
        Given an exception mentioning "credential"
        When from_exception() classifies it
        Then the result is an AUTHENTICATION-typed error
        """
        # Given: credential error
        exc = Exception("DefaultAzureCredential failed to obtain a token")

        # When: classifying
        result = from_exception(exc, service="Azure", operation="auth")

        # Then: routed to AUTHENTICATION
        assert result.error_type == ErrorType.AUTHENTICATION, (
            f"Expected AUTHENTICATION for credential error, got {result.error_type!r}"
        )

    def test_forbidden_routes_to_permission(self) -> None:
        """
        Given an exception whose message contains "forbidden"
        When from_exception() classifies it
        Then the result is a PERMISSION-typed error
        """
        # Given: permission error
        exc = Exception("403 Forbidden: Access denied to resource")

        # When: classifying
        result = from_exception(exc, service="Azure DevOps", operation="update_pr")

        # Then: routed to PERMISSION
        assert result.error_type == ErrorType.PERMISSION, (
            f"Expected PERMISSION for '403 Forbidden', got {result.error_type!r}"
        )

    def test_timeout_routes_to_timeout(self) -> None:
        """
        Given an exception whose message contains "timed out"
        When from_exception() classifies it
        Then the result is a TIMEOUT-typed error
        """
        # Given: timeout error
        exc = TimeoutError("Operation timed out after 60s")

        # When: classifying
        result = from_exception(exc, service="Databricks", operation="query")

        # Then: routed to TIMEOUT
        assert result.error_type == ErrorType.TIMEOUT, (
            f"Expected TIMEOUT for timeout error, got {result.error_type!r}"
        )

    def test_connection_refused_routes_to_connection(self) -> None:
        """
        Given an exception whose message contains "connection refused"
        When from_exception() classifies it
        Then the result is a CONNECTION-typed error
        """
        # Given: connection error
        exc = ConnectionError("Connection refused by server")

        # When: classifying
        result = from_exception(exc, service="Ollama", operation="embed")

        # Then: routed to CONNECTION
        assert result.error_type == ErrorType.CONNECTION, (
            f"Expected CONNECTION for 'connection refused', got {result.error_type!r}"
        )

    def test_not_found_routes_to_not_found(self) -> None:
        """
        Given an exception whose message contains "not found"
        When from_exception() classifies it
        Then the result is a NOT_FOUND-typed error
        """
        # Given: not found error
        exc = Exception("Resource not found: PR 99999 does not exist")

        # When: classifying
        result = from_exception(exc, service="Azure DevOps", operation="get_pr")

        # Then: routed to NOT_FOUND
        assert result.error_type == ErrorType.NOT_FOUND, (
            f"Expected NOT_FOUND for 'not found', got {result.error_type!r}"
        )

    def test_validation_keyword_routes_to_validation(self) -> None:
        """
        Given an exception whose message contains "invalid"
        When from_exception() classifies it
        Then the result is a VALIDATION-typed error
        """
        # Given: validation error
        exc = ValueError("Invalid value for 'page_size': must be positive")

        # When: classifying
        result = from_exception(exc, service="API", operation="list_items")

        # Then: routed to VALIDATION
        assert result.error_type == ErrorType.VALIDATION, (
            f"Expected VALIDATION for 'invalid', got {result.error_type!r}"
        )

    def test_unrecognized_exception_routes_to_internal(self) -> None:
        """
        Given an exception with no recognized keywords
        When from_exception() classifies it
        Then the result is an INTERNAL-typed error
        """
        # Given: generic error with no keywords
        exc = RuntimeError("Something completely unexpected happened")

        # When: classifying
        result = from_exception(exc, service="Pipeline", operation="process")

        # Then: falls through to INTERNAL
        assert result.error_type == ErrorType.INTERNAL, (
            f"Expected INTERNAL for unrecognized error, got {result.error_type!r}"
        )

    def test_no_accounts_routes_to_authentication(self) -> None:
        """
        Given an exception mentioning "no accounts" (Azure credential cache miss)
        When from_exception() classifies it
        Then the result is an AUTHENTICATION-typed error
        """
        # Given: Azure credential cache miss
        exc = Exception("No accounts were found in the cache")

        # When: classifying
        result = from_exception(exc, service="App Insights", operation="query")

        # Then: routed to AUTHENTICATION
        assert result.error_type == ErrorType.AUTHENTICATION, (
            f"Expected AUTHENTICATION for 'no accounts', got {result.error_type!r}"
        )

    def test_token_keyword_routes_to_authentication(self) -> None:
        """
        Given an exception mentioning "token"
        When from_exception() classifies it
        Then the result is an AUTHENTICATION-typed error
        """
        # Given: token error
        exc = Exception("Failed to acquire token for resource")

        # When: classifying
        result = from_exception(exc, service="Azure", operation="auth")

        # Then: routed to AUTHENTICATION
        assert result.error_type == ErrorType.AUTHENTICATION, (
            f"Expected AUTHENTICATION for 'token', got {result.error_type!r}"
        )

    def test_classification_is_case_insensitive(self) -> None:
        """
        Given an exception with mixed-case keywords
        When from_exception() classifies it
        Then it still matches the keyword pattern
        """
        # Given: mixed case
        exc = Exception("HTTP 401 UNAUTHORIZED ACCESS")

        # When: classifying
        result = from_exception(exc, service="svc", operation="op")

        # Then: case-insensitive match
        assert result.error_type == ErrorType.AUTHENTICATION, (
            f"Expected AUTHENTICATION for uppercase keyword, got {result.error_type!r}"
        )

    def test_result_is_actionable_error_instance(self) -> None:
        """
        When from_exception() classifies any exception
        Then the result is always an ActionableError with the service and operation preserved
        """
        # Given: any exception
        exc = Exception("anything")

        # When: classifying
        result = from_exception(exc, service="TestService", operation="test_op")

        # Then: it's an ActionableError with correct fields
        assert isinstance(result, ActionableError), f"Expected ActionableError, got {type(result)}"
        assert result.service == "TestService", (
            f"service should be preserved, got {result.service!r}"
        )


class TestClassifierSuggestionPreservation:
    """
    REQUIREMENT: Caller-supplied suggestions always override classifier defaults.

    WHO: Code at I/O boundaries that has context the generic classifier cannot infer
    WHAT: When a suggestion is passed to from_exception(), it appears on the
          resulting ActionableError regardless of which error type was detected
    WHY: The caller knows the domain context (e.g., "Check your PAT in settings.toml")
         that the keyword classifier cannot derive from the exception message alone

    MOCK BOUNDARY:
        Mock:  nothing — pure function call
        Real:  from_exception output
        Never: patch classifier internals
    """

    def test_custom_suggestion_is_preserved_on_auth_error(self) -> None:
        """
        Given a caller provides a custom suggestion
        When from_exception() classifies an auth error
        Then the custom suggestion overrides the default
        """
        # Given: custom suggestion
        exc = Exception("401 Unauthorized")

        # When: classifying with custom suggestion
        result = from_exception(
            exc,
            service="GitHub",
            operation="get_repo",
            suggestion="Regenerate your PAT at github.com/settings/tokens",
        )

        # Then: custom suggestion is used
        assert result.suggestion == "Regenerate your PAT at github.com/settings/tokens", (
            f"Custom suggestion should be preserved, got {result.suggestion!r}"
        )

    def test_custom_suggestion_is_preserved_on_fallback_error(self) -> None:
        """
        Given a caller provides a custom suggestion
        When from_exception() falls through to INTERNAL
        Then the custom suggestion is still preserved
        """
        # Given: unrecognized error with custom suggestion
        exc = RuntimeError("weird stuff")

        # When: classifying
        result = from_exception(
            exc,
            service="svc",
            operation="op",
            suggestion="Contact the on-call engineer",
        )

        # Then: custom suggestion preserved
        assert result.suggestion == "Contact the on-call engineer", (
            f"Custom suggestion should be preserved on fallback, got {result.suggestion!r}"
        )
