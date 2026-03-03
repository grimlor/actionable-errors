"""BDD specs for actionable_errors.result — ToolResult envelope.

Covers:
    TestToolResultSuccess — .ok() factory produces a success envelope
    TestToolResultFailure — .fail() factory from string or ActionableError
    TestToolResultSerialization — to_dict excludes None, includes all present fields,
        includes suggestion when present (conditional formatting — added for 100% coverage),
        includes ai_guidance when present (conditional formatting — added for 100% coverage)

Public API surface (from src/actionable_errors/result.py):
    ToolResult:
        success: bool
        data: Any | None
        error: str | None
        error_type: str | None
        suggestion: str | None
        ai_guidance: dict[str, Any] | None

        @classmethod ok(cls, data=None, suggestion=None, ai_guidance=None) -> ToolResult
        @classmethod fail(cls, error: str | ActionableError, suggestion=None, ai_guidance=None) -> ToolResult
        .to_dict() -> dict[str, Any]
"""

from __future__ import annotations

from actionable_errors.error import ActionableError
from actionable_errors.guidance import AIGuidance
from actionable_errors.result import ToolResult
from actionable_errors.types import ErrorType


class TestToolResultSuccess:
    """
    REQUIREMENT: .ok() factory produces a success envelope with optional data.

    WHO: Tool implementations returning successful results
    WHAT: ToolResult.ok() sets success=True, error=None, error_type=None; data
          is optional; suggestion and ai_guidance are optional
    WHY: Formalizes the ad-hoc {"success": True, ...} dict pattern used across
         12+ PDP tool files into a typed, self-documenting envelope

    MOCK BOUNDARY:
        Mock:  nothing — pure dataclass construction
        Real:  ToolResult instance and its fields
        Never: inspect internal implementation details
    """

    def test_ok_sets_success_true(self) -> None:
        """
        When ToolResult.ok() is called with no arguments
        Then success is True
        """
        # When: creating a success result
        result = ToolResult.ok()

        # Then: success is True
        assert result.success is True, (
            f"ok() should set success=True, got {result.success!r}"
        )

    def test_ok_with_data(self) -> None:
        """
        Given data to include in the result
        When ToolResult.ok(data=...) is called
        Then the data is stored on the result
        """
        # Given: some data
        data = {"tables": ["users", "orders"], "count": 2}

        # When: creating a success result with data
        result = ToolResult.ok(data=data)

        # Then: data is present
        assert result.data == data, (
            f"ok(data=...) should store data.\n"
            f"Expected: {data!r}\n"
            f"Got:      {result.data!r}"
        )

    def test_ok_error_fields_are_none(self) -> None:
        """
        When ToolResult.ok() is called
        Then error and error_type are None
        """
        # When: creating a success result
        result = ToolResult.ok()

        # Then: error fields are None
        assert result.error is None, (
            f"ok() should set error=None, got {result.error!r}"
        )
        assert result.error_type is None, (
            f"ok() should set error_type=None, got {result.error_type!r}"
        )

    def test_ok_with_suggestion(self) -> None:
        """
        Given a suggestion to accompany the success
        When ToolResult.ok(suggestion=...) is called
        Then the suggestion is stored
        """
        # Given: a suggestion
        suggestion = "Consider caching this result for repeated queries."

        # When: creating a success result with suggestion
        result = ToolResult.ok(suggestion=suggestion)

        # Then: suggestion is stored
        assert result.suggestion == suggestion, (
            f"ok(suggestion=...) should store suggestion, got {result.suggestion!r}"
        )

    def test_ok_with_ai_guidance(self) -> None:
        """
        Given AIGuidance to accompany the success
        When ToolResult.ok(ai_guidance=...) is called
        Then the ai_guidance dict is stored
        """
        # Given: AI guidance
        guidance = AIGuidance(action_required="Review the results")
        guidance_dict = guidance.to_dict()

        # When: creating a success result with guidance
        result = ToolResult.ok(ai_guidance=guidance_dict)

        # Then: guidance is stored
        assert result.ai_guidance == guidance_dict, (
            f"ok(ai_guidance=...) should store guidance dict, got {result.ai_guidance!r}"
        )


class TestToolResultFailure:
    """
    REQUIREMENT: .fail() factory produces a failure envelope from string or ActionableError.

    WHO: Tool implementations handling errors
    WHAT: ToolResult.fail() sets success=False and stores the error message;
          when called with an ActionableError, it also extracts error_type
          and suggestion; when called with a plain string, error_type is None
    WHY: Unifies error-response construction so all tool failures carry
         structured metadata for AI agents to reason over

    MOCK BOUNDARY:
        Mock:  nothing — pure dataclass construction
        Real:  ToolResult instance and its fields
        Never: inspect implementation internals
    """

    def test_fail_from_string_sets_success_false(self) -> None:
        """
        Given a plain error message string
        When ToolResult.fail(error=...) is called
        Then success is False
        """
        # Given: an error message
        msg = "Something went wrong"

        # When: creating a failure result
        result = ToolResult.fail(error=msg)

        # Then: success is False
        assert result.success is False, (
            f"fail() should set success=False, got {result.success!r}"
        )

    def test_fail_from_string_stores_message(self) -> None:
        """
        Given a plain error message string
        When ToolResult.fail(error=...) is called
        Then the error message is stored
        """
        # Given: an error message
        msg = "Query timed out after 30 seconds"

        # When: creating a failure result
        result = ToolResult.fail(error=msg)

        # Then: message is stored
        assert result.error == msg, (
            f"fail(error=str) should store the message, got {result.error!r}"
        )

    def test_fail_from_string_has_no_error_type(self) -> None:
        """
        Given a plain error message string
        When ToolResult.fail(error=...) is called
        Then error_type is None (no type can be inferred from a plain string)
        """
        # When: creating a failure from a string
        result = ToolResult.fail(error="generic error")

        # Then: no error_type
        assert result.error_type is None, (
            f"fail(error=str) should set error_type=None, got {result.error_type!r}"
        )

    def test_fail_from_actionable_error_extracts_type(self) -> None:
        """
        Given an ActionableError with a specific error_type
        When ToolResult.fail(error=...) is called with that ActionableError
        Then error_type is extracted from the ActionableError
        """
        # Given: an ActionableError
        err = ActionableError.authentication(
            service="Azure",
            raw_error="Token expired",
            suggestion="Refresh your token",
        )

        # When: creating a failure from the ActionableError
        result = ToolResult.fail(error=err)

        # Then: error_type is extracted
        assert result.error_type == str(ErrorType.AUTHENTICATION), (
            f"fail(ActionableError) should extract error_type, got {result.error_type!r}"
        )

    def test_fail_from_actionable_error_extracts_suggestion(self) -> None:
        """
        Given an ActionableError with a suggestion
        When ToolResult.fail(error=...) is called with that ActionableError
        Then the suggestion is extracted
        """
        # Given: an ActionableError with suggestion
        err = ActionableError.authentication(
            service="Azure",
            raw_error="Auth failed",
            suggestion="Check credentials",
        )

        # When: creating a failure
        result = ToolResult.fail(error=err)

        # Then: suggestion is extracted
        assert result.suggestion == "Check credentials", (
            f"fail(ActionableError) should extract suggestion, got {result.suggestion!r}"
        )

    def test_fail_from_actionable_error_stores_message(self) -> None:
        """
        Given an ActionableError with a message
        When ToolResult.fail(error=...) is called
        Then the error message is the string representation of the ActionableError message
        """
        # Given: an ActionableError
        err = ActionableError.timeout(
            service="Databricks",
            operation="query execution",
            timeout_seconds=30,
            suggestion="Optimize the query",
        )

        # When: creating a failure
        result = ToolResult.fail(error=err)

        # Then: message is stored
        assert "30" in str(result.error), (
            f"fail(ActionableError) should store the message, got {result.error!r}"
        )

    def test_fail_with_explicit_suggestion_overrides_error(self) -> None:
        """
        Given an ActionableError with its own suggestion
        When ToolResult.fail(error=..., suggestion=...) is called with an override
        Then the explicit suggestion takes precedence
        """
        # Given: an ActionableError with a suggestion
        err = ActionableError.authentication(
            service="Azure",
            raw_error="Auth failed",
            suggestion="Original suggestion",
        )
        override = "Overridden suggestion"

        # When: creating a failure with explicit suggestion
        result = ToolResult.fail(error=err, suggestion=override)

        # Then: explicit suggestion wins
        assert result.suggestion == override, (
            f"Explicit suggestion should override ActionableError's, got {result.suggestion!r}"
        )


class TestToolResultSerialization:
    """
    REQUIREMENT: ToolResult.to_dict() produces a clean JSON-serializable dict.

    WHO: MCP tool handlers returning results to the agent framework
    WHAT: to_dict() always includes 'success'; includes 'data' on success,
          'error'/'error_type' on failure; excludes None-valued optional fields
    WHY: Clean serialization reduces noise in agent context windows and
         ensures downstream consumers get a predictable shape

    MOCK BOUNDARY:
        Mock:  nothing — pure function
        Real:  to_dict() output
        Never: inspect internal state
    """

    def test_success_dict_includes_success_true(self) -> None:
        """
        Given a success ToolResult
        When to_dict() is called
        Then the dict contains success=True
        """
        # Given: a success result
        result = ToolResult.ok(data={"count": 5})

        # When: serializing
        d = result.to_dict()

        # Then: success is True
        assert d["success"] is True, (
            f"to_dict() should include success=True, got {d!r}"
        )

    def test_success_dict_includes_data(self) -> None:
        """
        Given a success ToolResult with data
        When to_dict() is called
        Then the dict contains the data
        """
        # Given: success with data
        data = {"rows": [1, 2, 3]}
        result = ToolResult.ok(data=data)

        # When: serializing
        d = result.to_dict()

        # Then: data is present
        assert d["data"] == data, (
            f"to_dict() should include data, got {d!r}"
        )

    def test_success_dict_excludes_none_optional_fields(self) -> None:
        """
        Given a success ToolResult with no suggestion or ai_guidance
        When to_dict() is called
        Then suggestion and ai_guidance keys are absent
        """
        # Given: minimal success
        result = ToolResult.ok()

        # When: serializing
        d = result.to_dict()

        # Then: None fields are excluded
        assert "suggestion" not in d, (
            f"None suggestion should be excluded from dict, got keys: {list(d.keys())}"
        )
        assert "ai_guidance" not in d, (
            f"None ai_guidance should be excluded from dict, got keys: {list(d.keys())}"
        )

    def test_success_dict_includes_ai_guidance_when_present(self) -> None:
        """
        Given a success ToolResult with ai_guidance
        When to_dict() is called
        Then the ai_guidance appears in the dict
        """
        # Given: success with ai_guidance
        guidance = {"action_required": "Review the results"}
        result = ToolResult.ok(ai_guidance=guidance)

        # When: serializing
        d = result.to_dict()

        # Then: ai_guidance is present
        assert d["ai_guidance"] == guidance, (
            f"ai_guidance should appear in dict, got {d!r}"
        )

    def test_failure_dict_includes_error_and_type(self) -> None:
        """
        Given a failure ToolResult from an ActionableError
        When to_dict() is called
        Then the dict contains error, error_type, and success=False
        """
        # Given: failure from ActionableError
        err = ActionableError.not_found(
            service="Azure DevOps",
            resource_type="Table",
            resource_id="users",
            raw_error="Table 'users' not found",
            suggestion="Check table name",
        )
        result = ToolResult.fail(error=err)

        # When: serializing
        d = result.to_dict()

        # Then: error fields present
        assert d["success"] is False, (
            f"to_dict() should have success=False, got {d!r}"
        )
        assert "error" in d, (
            f"to_dict() should include 'error' key, got keys: {list(d.keys())}"
        )
        assert "error_type" in d, (
            f"to_dict() should include 'error_type' key, got keys: {list(d.keys())}"
        )

    def test_success_dict_includes_suggestion_when_present(self) -> None:
        """
        Given a success ToolResult with a suggestion
        When to_dict() is called
        Then the suggestion appears in the dict
        """
        # Given: success with suggestion
        result = ToolResult.ok(suggestion="Cache this result")

        # When: serializing
        d = result.to_dict()

        # Then: suggestion is present
        assert d["suggestion"] == "Cache this result", (
            f"suggestion should appear in dict, got {d!r}"
        )

    def test_failure_dict_excludes_none_data(self) -> None:
        """
        Given a failure ToolResult (no data)
        When to_dict() is called
        Then the 'data' key is absent
        """
        # Given: failure result (no data)
        result = ToolResult.fail(error="Something failed")

        # When: serializing
        d = result.to_dict()

        # Then: data key is absent
        assert "data" not in d, (
            f"None data should be excluded from failure dict, got keys: {list(d.keys())}"
        )
