"""BDD specs for actionable_errors.types — ErrorType base categories and extensibility.

Covers:
    TestErrorTypeBaseCategories — base enum values exist and are StrEnum
    TestErrorTypeExtensibility — consumers can extend with domain-specific values

Public API surface (from src/actionable_errors/types.py):
    ErrorType(StrEnum) — base categories:
        AUTHENTICATION, CONFIGURATION, CONNECTION, TIMEOUT,
        PERMISSION, VALIDATION, NOT_FOUND, INTERNAL
"""

from __future__ import annotations

from enum import StrEnum

from actionable_errors.error import ActionableError
from actionable_errors.types import ErrorType


class TestErrorTypeBaseCategories:
    """
    REQUIREMENT: ErrorType provides base recovery-path categories as a StrEnum.

    WHO: Calling code that routes errors by type (retry? escalate? ignore?)
    WHAT: All eight base categories exist as StrEnum members with lowercase
          string values; ErrorType is iterable and its values are plain strings
    WHY: Without typed categories, consumers must parse error messages to decide
         what to do — fragile and unportable across projects

    MOCK BOUNDARY:
        Mock:  nothing — pure enum definition
        Real:  ErrorType enum
        Never: construct enum members manually
    """

    def test_authentication_category_exists(self) -> None:
        """
        When ErrorType.AUTHENTICATION is accessed
        Then it has the string value "authentication"
        """
        # Given: the ErrorType enum

        # When: accessing the AUTHENTICATION member
        value = ErrorType.AUTHENTICATION

        # Then: it has the correct string value
        assert value == "authentication", f"Expected 'authentication', got {value!r}"

    def test_configuration_category_exists(self) -> None:
        """
        When ErrorType.CONFIGURATION is accessed
        Then it has the string value "configuration"
        """
        # Given: the ErrorType enum

        # When: accessing the CONFIGURATION member
        value = ErrorType.CONFIGURATION

        # Then: it has the correct string value
        assert value == "configuration", f"Expected 'configuration', got {value!r}"

    def test_connection_category_exists(self) -> None:
        """
        When ErrorType.CONNECTION is accessed
        Then it has the string value "connection"
        """
        # Given: the ErrorType enum

        # When: accessing the CONNECTION member
        value = ErrorType.CONNECTION

        # Then: it has the correct string value
        assert value == "connection", f"Expected 'connection', got {value!r}"

    def test_timeout_category_exists(self) -> None:
        """
        When ErrorType.TIMEOUT is accessed
        Then it has the string value "timeout"
        """
        # Given: the ErrorType enum

        # When: accessing the TIMEOUT member
        value = ErrorType.TIMEOUT

        # Then: it has the correct string value
        assert value == "timeout", f"Expected 'timeout', got {value!r}"

    def test_permission_category_exists(self) -> None:
        """
        When ErrorType.PERMISSION is accessed
        Then it has the string value "permission"
        """
        # Given: the ErrorType enum

        # When: accessing the PERMISSION member
        value = ErrorType.PERMISSION

        # Then: it has the correct string value
        assert value == "permission", f"Expected 'permission', got {value!r}"

    def test_validation_category_exists(self) -> None:
        """
        When ErrorType.VALIDATION is accessed
        Then it has the string value "validation"
        """
        # Given: the ErrorType enum

        # When: accessing the VALIDATION member
        value = ErrorType.VALIDATION

        # Then: it has the correct string value
        assert value == "validation", f"Expected 'validation', got {value!r}"

    def test_not_found_category_exists(self) -> None:
        """
        When ErrorType.NOT_FOUND is accessed
        Then it has the string value "not_found"
        """
        # Given: the ErrorType enum

        # When: accessing the NOT_FOUND member
        value = ErrorType.NOT_FOUND

        # Then: it has the correct string value
        assert value == "not_found", f"Expected 'not_found', got {value!r}"

    def test_internal_category_exists(self) -> None:
        """
        When ErrorType.INTERNAL is accessed
        Then it has the string value "internal"
        """
        # Given: the ErrorType enum

        # When: accessing the INTERNAL member
        value = ErrorType.INTERNAL

        # Then: it has the correct string value
        assert value == "internal", f"Expected 'internal', got {value!r}"

    def test_error_type_is_str_enum(self) -> None:
        """
        When ErrorType is inspected
        Then it is a subclass of StrEnum
        """
        # Given: the ErrorType class

        # When: checking its base classes
        is_str_enum = issubclass(ErrorType, StrEnum)

        # Then: it inherits from StrEnum
        assert is_str_enum, (
            f"ErrorType should be a StrEnum subclass, bases are {ErrorType.__bases__}"
        )

    def test_error_type_has_exactly_eight_base_categories(self) -> None:
        """
        When the base ErrorType members are counted
        Then there are exactly eight
        """
        # Given: the ErrorType enum

        # When: counting members
        members = list(ErrorType)

        # Then: exactly eight base categories exist
        assert len(members) == 8, (
            f"Expected 8 base categories, got {len(members)}: {[m.name for m in members]}"
        )

    def test_error_type_values_are_usable_as_plain_strings(self) -> None:
        """
        When an ErrorType member is used in a string context
        Then it behaves as a plain string without .value access
        """
        # Given: an ErrorType member
        error_type = ErrorType.AUTHENTICATION

        # When: using it in string concatenation
        result = "type:" + error_type

        # Then: it works as a plain string
        assert result == "type:authentication", f"Expected 'type:authentication', got {result!r}"


class TestErrorTypeExtensibility:
    """
    REQUIREMENT: Consumers can define domain-specific error types alongside ErrorType.

    WHO: Downstream projects (jobsearch-rag, ado-workflows, pdp-dev-mcp) that
         need domain-specific error categories beyond the base eight
    WHAT: ActionableError accepts any str for error_type, not just ErrorType members;
          consumers define their own StrEnum alongside ErrorType; both base and
          consumer types can be used in the same codebase
    WHY: Python StrEnum with members cannot be subclassed, so composability is
         achieved by accepting str — consumers get type-safe enums in their own
         domain without breaking the base contract

    MOCK BOUNDARY:
        Mock:  nothing — pure enum + string behavior
        Real:  ErrorType, consumer StrEnum, ActionableError
        Never: monkey-patch ErrorType members at runtime
    """

    def test_consumer_can_define_domain_specific_enum(self) -> None:
        """
        Given a consumer defines their own StrEnum with domain-specific values
        When the enum is used alongside ErrorType
        Then both produce valid string values
        """

        # Given: a consumer defines their own error types
        class RAGErrorType(StrEnum):
            EMBEDDING = "embedding"
            INDEX = "index"

        # When: using both
        base_val = str(ErrorType.AUTHENTICATION)
        custom_val = str(RAGErrorType.EMBEDDING)

        # Then: both are valid strings
        assert base_val == "authentication", (
            f"Base member should be 'authentication', got {base_val!r}"
        )
        assert custom_val == "embedding", (
            f"Custom member should be 'embedding', got {custom_val!r}"
        )

    def test_actionable_error_accepts_custom_str_error_type(self) -> None:
        """
        Given a consumer uses a custom StrEnum value as error_type
        When constructing an ActionableError
        Then the error_type is accepted and stored
        """

        class RAGErrorType(StrEnum):
            EMBEDDING = "embedding"

        # Given: a consumer error type

        # When: constructing with the custom type
        err = ActionableError(
            error="Embedding failed",
            error_type=RAGErrorType.EMBEDDING,
            service="Ollama",
        )

        # Then: error_type is stored
        assert str(err.error_type) == "embedding", (
            f"Custom error_type should be accepted, got {err.error_type!r}"
        )

    def test_custom_error_type_appears_in_to_dict(self) -> None:
        """
        Given an ActionableError with a custom StrEnum error_type
        When to_dict() is called
        Then error_type appears as its string value
        """

        class ADOErrorType(StrEnum):
            WORK_ITEM = "work_item"

        # Given: error with custom type
        err = ActionableError(
            error="Work item not found",
            error_type=ADOErrorType.WORK_ITEM,
            service="Azure DevOps",
        )

        # When: serializing
        result = err.to_dict()

        # Then: custom type serialized as string
        assert result["error_type"] == "work_item", (
            f"Custom error_type should serialize as 'work_item', got {result['error_type']!r}"
        )
