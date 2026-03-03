"""BDD specs for actionable_errors.error — ActionableError dataclass and factories.

Covers:
    TestActionableErrorConstruction — basic construction, success=False, timestamp,
        real exception behavior via __post_init__
    TestActionableErrorSerialization — to_dict excludes None, includes present fields
    TestActionableErrorFactories — each base factory classmethod

Public API surface (from src/actionable_errors/error.py):
    ActionableError(Exception):
        error: str
        error_type: ErrorType
        service: str
        success: bool = False  (not in __init__)
        suggestion: str | None = None
        ai_guidance: AIGuidance | None = None
        troubleshooting: Troubleshooting | None = None
        context: dict[str, Any] | None = None
        timestamp: str  (auto-generated ISO format)
        .to_dict() -> dict[str, Any]
        .authentication(service, raw_error, *, suggestion?) -> ActionableError
        .configuration(field_name, reason, *, suggestion?) -> ActionableError
        .connection(service, url, raw_error, *, suggestion?) -> ActionableError
        .timeout(service, operation, timeout_seconds, *, suggestion?) -> ActionableError
        .permission(service, resource, raw_error, *, suggestion?) -> ActionableError
        .validation(service, field_name, reason, *, suggestion?) -> ActionableError
        .not_found(service, resource_type, resource_id, raw_error, *, suggestion?) -> ActionableError
        .internal(service, operation, raw_error, *, suggestion?) -> ActionableError
"""

from __future__ import annotations

from actionable_errors.error import ActionableError
from actionable_errors.guidance import AIGuidance, Troubleshooting
from actionable_errors.types import ErrorType


class TestActionableErrorConstruction:
    """
    REQUIREMENT: ActionableError is a dataclass that is also a real Exception.

    WHO: Calling code that catches exceptions by type for error routing
    WHAT: Construction sets required fields; success is always False; timestamp
          is auto-generated in ISO format; the instance is raiseable and catchable
          as an Exception; __post_init__ wires the error message to Exception
    WHY: If ActionableError is not a real Exception, callers must use a separate
         error-handling path for structured vs unstructured errors — doubles the
         error surface

    MOCK BOUNDARY:
        Mock:  nothing — pure dataclass construction
        Real:  ActionableError instances
        Never: patch __post_init__ or Exception.__init__
    """

    def test_required_fields_are_set(self) -> None:
        """
        When an ActionableError is constructed with required fields
        Then error, error_type, and service are accessible
        """
        # Given: required constructor arguments

        # When: constructing
        err = ActionableError(
            error="Something broke",
            error_type=ErrorType.INTERNAL,
            service="test-service",
        )

        # Then: required fields are set
        assert err.error == "Something broke", (
            f"error mismatch: {err.error!r}"
        )
        assert err.error_type == ErrorType.INTERNAL, (
            f"error_type mismatch: {err.error_type!r}"
        )
        assert err.service == "test-service", (
            f"service mismatch: {err.service!r}"
        )

    def test_success_is_always_false(self) -> None:
        """
        When an ActionableError is constructed
        Then success is False and cannot be set via constructor
        """
        # Given: an error instance

        # When: checking success
        err = ActionableError(
            error="Database connection pool exhausted",
            error_type=ErrorType.INTERNAL,
            service="connection-pool",
        )

        # Then: success is always False
        assert err.success is False, (
            f"success should always be False, got {err.success!r}"
        )

    def test_timestamp_is_auto_generated_iso_format(self) -> None:
        """
        When an ActionableError is constructed
        Then timestamp is a non-empty ISO format string
        """
        # Given: an error instance

        # When: checking timestamp
        err = ActionableError(
            error="Schema validation failed for config file",
            error_type=ErrorType.INTERNAL,
            service="config-validator",
        )

        # Then: timestamp is present and looks like ISO format
        assert isinstance(err.timestamp, str), (
            f"timestamp should be a string, got {type(err.timestamp)}"
        )
        assert len(err.timestamp) > 0, "timestamp should not be empty"
        assert "T" in err.timestamp, (
            f"timestamp should be ISO format (contain 'T'), got {err.timestamp!r}"
        )

    def test_is_a_real_exception(self) -> None:
        """
        When an ActionableError is constructed
        Then it is an instance of Exception and can be raised/caught
        """
        # Given: an error instance
        err = ActionableError(
            error="Auth failed",
            error_type=ErrorType.AUTHENTICATION,
            service="Azure",
        )

        # When: checking type
        is_exception = isinstance(err, Exception)

        # Then: it's a real exception
        assert is_exception, (
            f"ActionableError should be an Exception, bases are "
            f"{type(err).__mro__}"
        )

    def test_can_be_raised_and_caught(self) -> None:
        """
        Given an ActionableError instance
        When it is raised
        Then it can be caught as an ActionableError or as an Exception
        """
        # Given: an error
        err = ActionableError(
            error="Token expired",
            error_type=ErrorType.AUTHENTICATION,
            service="Azure DevOps",
        )

        # When/Then: raise and catch as ActionableError
        caught = False
        try:
            raise err
        except ActionableError as caught_err:
            caught = True
            assert str(caught_err) == "Token expired", (
                f"Exception message should be the error field, got {str(caught_err)!r}"
            )

        assert caught, "ActionableError should be catchable"

    def test_optional_fields_default_to_none(self) -> None:
        """
        When an ActionableError is constructed with only required fields
        Then suggestion, ai_guidance, troubleshooting, and context are None
        """
        # Given: minimal construction

        # When: checking optional fields
        err = ActionableError(
            error="Rate limit exceeded on embedding API",
            error_type=ErrorType.INTERNAL,
            service="embedding-service",
        )

        # Then: all optional fields are None
        assert err.suggestion is None, (
            f"suggestion should default to None, got {err.suggestion!r}"
        )
        assert err.ai_guidance is None, (
            f"ai_guidance should default to None, got {err.ai_guidance!r}"
        )
        assert err.troubleshooting is None, (
            f"troubleshooting should default to None, got {err.troubleshooting!r}"
        )
        assert err.context is None, (
            f"context should default to None, got {err.context!r}"
        )


class TestActionableErrorSerialization:
    """
    REQUIREMENT: to_dict() produces compact JSON-ready dicts excluding None values.

    WHO: MCP tool return values, API responses, log entries that consume error dicts
    WHAT: to_dict() always includes success, error, error_type, service, timestamp;
          None-valued optional fields are excluded; nested guidance objects are
          serialized via their own to_dict()
    WHY: None-polluted dicts waste LLM context tokens and break consumers that check
         key presence instead of value truthiness

    MOCK BOUNDARY:
        Mock:  nothing — pure serialization logic
        Real:  ActionableError instances and their to_dict() output
        Never: construct expected dicts and assert equality without calling to_dict()
    """

    def test_minimal_dict_has_required_keys(self) -> None:
        """
        Given an ActionableError with only required fields
        When to_dict() is called
        Then the dict contains exactly the required keys
        """
        # Given: minimal error
        err = ActionableError(
            error="Pipeline stage timed out after 120s",
            error_type=ErrorType.INTERNAL,
            service="data-pipeline",
        )

        # When: serializing
        result = err.to_dict()

        # Then: required keys present
        required_keys = {"success", "error", "error_type", "service", "timestamp"}
        assert set(result.keys()) == required_keys, (
            f"Expected keys {required_keys}, got {set(result.keys())}"
        )

    def test_none_valued_optional_fields_are_excluded(self) -> None:
        """
        Given an ActionableError with no optional fields set
        When to_dict() is called
        Then suggestion, ai_guidance, troubleshooting, context are absent
        """
        # Given: minimal error
        err = ActionableError(
            error="Index rebuild failed due to lock contention",
            error_type=ErrorType.INTERNAL,
            service="search-indexer",
        )

        # When: serializing
        result = err.to_dict()

        # Then: optional keys are absent
        for key in ("suggestion", "ai_guidance", "troubleshooting", "context"):
            assert key not in result, (
                f"None-valued '{key}' should be excluded from dict, "
                f"but it was present with value {result.get(key)!r}"
            )

    def test_populated_optional_fields_are_included(self) -> None:
        """
        Given an ActionableError with all optional fields set
        When to_dict() is called
        Then all fields appear in the result
        """
        # Given: fully populated error
        err = ActionableError(
            error="Auth failed",
            error_type=ErrorType.AUTHENTICATION,
            service="Azure",
            suggestion="Run az login",
            ai_guidance=AIGuidance(action_required="Re-authenticate"),
            troubleshooting=Troubleshooting(steps=["Run az login"]),
            context={"attempt": 3},
        )

        # When: serializing
        result = err.to_dict()

        # Then: all optional keys are present
        assert "suggestion" in result, "suggestion should be in dict"
        assert result["suggestion"] == "Run az login", (
            f"suggestion mismatch: {result['suggestion']!r}"
        )
        assert "ai_guidance" in result, "ai_guidance should be in dict"
        assert result["ai_guidance"]["action_required"] == "Re-authenticate", (
            f"ai_guidance not serialized correctly: {result['ai_guidance']!r}"
        )
        assert "troubleshooting" in result, "troubleshooting should be in dict"
        assert "context" in result, "context should be in dict"
        assert result["context"] == {"attempt": 3}, (
            f"context mismatch: {result['context']!r}"
        )

    def test_error_type_serialized_as_string_value(self) -> None:
        """
        Given an ActionableError
        When to_dict() is called
        Then error_type is the string value, not the enum member repr
        """
        # Given: an error with a typed error_type
        err = ActionableError(
            error="OAuth token refresh failed",
            error_type=ErrorType.AUTHENTICATION,
            service="auth-gateway",
        )

        # When: serializing
        result = err.to_dict()

        # Then: error_type is the plain string value
        assert result["error_type"] == "authentication", (
            f"error_type should be 'authentication', got {result['error_type']!r}"
        )

    def test_success_is_false_in_dict(self) -> None:
        """
        When to_dict() is called on any ActionableError
        Then success is False in the result
        """
        # Given: any error
        err = ActionableError(
            error="Webhook delivery failed after 3 retries",
            error_type=ErrorType.INTERNAL,
            service="notification-service",
        )

        # When: serializing
        result = err.to_dict()

        # Then: success is False
        assert result["success"] is False, (
            f"success should be False in dict, got {result['success']!r}"
        )


class TestActionableErrorFactories:
    """
    REQUIREMENT: Factory classmethods create correctly-typed errors with sensible defaults.

    WHO: Code that creates errors at failure points without needing to know the
         full guidance structure for each error type
    WHAT: Each factory sets the correct ErrorType, constructs a descriptive error
          message, provides default suggestion and AI guidance; caller-supplied
          suggestion overrides the default
    WHY: Without factories, every call site must construct AIGuidance and
         Troubleshooting manually — verbose, inconsistent, and error-prone

    MOCK BOUNDARY:
        Mock:  nothing — pure factory construction
        Real:  ActionableError factory output
        Never: assert on internal factory implementation details
    """

    def test_authentication_factory_produces_auth_typed_error_with_guidance(self) -> None:
        """
        When ActionableError.authentication() is called
        Then it produces an AUTHENTICATION-typed error with guidance
        """
        # Given: authentication failure parameters

        # When: using the factory
        err = ActionableError.authentication(
            service="Azure DevOps",
            raw_error="Token expired",
        )

        # Then: correctly typed with guidance
        assert err.error_type == ErrorType.AUTHENTICATION, (
            f"Expected AUTHENTICATION, got {err.error_type!r}"
        )
        assert "Azure DevOps" in err.error, (
            f"Error message should mention service: {err.error!r}"
        )
        assert "Token expired" in err.error, (
            f"Error message should include raw error: {err.error!r}"
        )
        assert err.suggestion is not None, "Factory should provide a default suggestion"
        assert err.ai_guidance is not None, "Factory should provide AI guidance"

    def test_authentication_factory_with_custom_suggestion(self) -> None:
        """
        Given a caller provides a custom suggestion
        When ActionableError.authentication() is called
        Then the custom suggestion overrides the default
        """
        # Given: custom suggestion

        # When: using the factory with suggestion override
        err = ActionableError.authentication(
            service="GitHub",
            raw_error="Bad credentials",
            suggestion="Check your PAT token",
        )

        # Then: custom suggestion is used
        assert err.suggestion == "Check your PAT token", (
            f"Custom suggestion should override default, got {err.suggestion!r}"
        )

    def test_configuration_factory_produces_config_typed_error_with_field_name(self) -> None:
        """
        When ActionableError.configuration() is called
        Then it produces a CONFIGURATION-typed error with the field name in the message
        """
        # Given: configuration error parameters

        # When: using the factory
        err = ActionableError.configuration(
            field_name="database_url",
            reason="must not be empty",
        )

        # Then: correctly typed
        assert err.error_type == ErrorType.CONFIGURATION, (
            f"Expected CONFIGURATION, got {err.error_type!r}"
        )
        assert "database_url" in err.error, (
            f"Error should mention the field name: {err.error!r}"
        )
        assert err.suggestion is not None, "Factory should provide a default suggestion"

    def test_connection_factory_produces_connection_typed_error_with_url(self) -> None:
        """
        When ActionableError.connection() is called
        Then it produces a CONNECTION-typed error with service and URL in the message
        """
        # Given: connection failure parameters

        # When: using the factory
        err = ActionableError.connection(
            service="Ollama",
            url="http://localhost:11434",
            raw_error="Connection refused",
        )

        # Then: correctly typed with URL in message
        assert err.error_type == ErrorType.CONNECTION, (
            f"Expected CONNECTION, got {err.error_type!r}"
        )
        assert "Ollama" in err.error, (
            f"Error should mention service: {err.error!r}"
        )
        assert "localhost:11434" in err.error, (
            f"Error should mention URL: {err.error!r}"
        )

    def test_timeout_factory_produces_timeout_typed_error_with_duration(self) -> None:
        """
        When ActionableError.timeout() is called
        Then it produces a TIMEOUT-typed error with duration in the message
        """
        # Given: timeout parameters

        # When: using the factory
        err = ActionableError.timeout(
            service="Databricks",
            operation="query execution",
            timeout_seconds=120,
        )

        # Then: correctly typed with duration
        assert err.error_type == ErrorType.TIMEOUT, (
            f"Expected TIMEOUT, got {err.error_type!r}"
        )
        assert "120" in err.error, (
            f"Error should mention timeout seconds: {err.error!r}"
        )

    def test_permission_factory_produces_permission_typed_error_with_resource(self) -> None:
        """
        When ActionableError.permission() is called
        Then it produces a PERMISSION-typed error with resource in the message
        """
        # Given: permission error parameters

        # When: using the factory
        err = ActionableError.permission(
            service="Azure DevOps",
            resource="pull_request/12345",
            raw_error="403 Forbidden",
        )

        # Then: correctly typed
        assert err.error_type == ErrorType.PERMISSION, (
            f"Expected PERMISSION, got {err.error_type!r}"
        )
        assert "pull_request/12345" in err.error, (
            f"Error should mention resource: {err.error!r}"
        )

    def test_validation_factory_produces_validation_typed_error_with_field(self) -> None:
        """
        When ActionableError.validation() is called
        Then it produces a VALIDATION-typed error with field and reason
        """
        # Given: validation error parameters

        # When: using the factory
        err = ActionableError.validation(
            service="API",
            field_name="page_size",
            reason="must be between 1 and 100",
        )

        # Then: correctly typed
        assert err.error_type == ErrorType.VALIDATION, (
            f"Expected VALIDATION, got {err.error_type!r}"
        )
        assert "page_size" in err.error, (
            f"Error should mention field: {err.error!r}"
        )

    def test_not_found_factory_produces_not_found_typed_error_with_resource_info(self) -> None:
        """
        When ActionableError.not_found() is called
        Then it produces a NOT_FOUND-typed error with resource info
        """
        # Given: not found parameters

        # When: using the factory
        err = ActionableError.not_found(
            service="Azure DevOps",
            resource_type="Pull Request",
            resource_id="99999",
            raw_error="404 Not Found",
        )

        # Then: correctly typed with resource details
        assert err.error_type == ErrorType.NOT_FOUND, (
            f"Expected NOT_FOUND, got {err.error_type!r}"
        )
        assert "Pull Request" in err.error, (
            f"Error should mention resource type: {err.error!r}"
        )
        assert "99999" in err.error, (
            f"Error should mention resource id: {err.error!r}"
        )

    def test_internal_factory_produces_internal_typed_error_with_operation(self) -> None:
        """
        When ActionableError.internal() is called
        Then it produces an INTERNAL-typed error with operation context
        """
        # Given: unexpected error parameters

        # When: using the factory
        err = ActionableError.internal(
            service="Pipeline",
            operation="score_listings",
            raw_error="NoneType has no attribute 'title'",
        )

        # Then: correctly typed
        assert err.error_type == ErrorType.INTERNAL, (
            f"Expected INTERNAL, got {err.error_type!r}"
        )
        assert "score_listings" in err.error, (
            f"Error should mention operation: {err.error!r}"
        )

    def test_all_factories_produce_actionable_errors(self) -> None:
        """
        When any factory method is called
        Then the result is an ActionableError with success=False and a timestamp
        """
        # Given: errors from all factories
        errors: list[ActionableError] = [
            ActionableError.authentication("svc", "err"),
            ActionableError.configuration("field", "reason"),
            ActionableError.connection("svc", "url", "err"),
            ActionableError.timeout("svc", "op", 60),
            ActionableError.permission("svc", "res", "err"),
            ActionableError.validation("svc", "field", "reason"),
            ActionableError.not_found("svc", "Type", "id", "err"),
            ActionableError.internal("svc", "op", "err"),
        ]

        # When/Then: each is a valid ActionableError
        for i, err in enumerate(errors):
            assert isinstance(err, ActionableError), (
                f"Factory {i} did not return an ActionableError: {type(err)}"
            )
            assert err.success is False, (
                f"Factory {i} has success={err.success!r}, expected False"
            )
            assert len(err.timestamp) > 0, (
                f"Factory {i} has empty timestamp"
            )
