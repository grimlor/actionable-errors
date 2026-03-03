"""BDD specs for actionable_errors.guidance — AIGuidance and Troubleshooting dataclasses.

Covers:
    TestAIGuidanceCreation — frozen dataclass, to_dict excludes None
    TestTroubleshootingCreation — frozen dataclass, to_dict returns steps,
        rejects empty steps list (defensive guard — added for 100% coverage)

Public API surface (from src/actionable_errors/guidance.py):
    AIGuidance(frozen=True):
        action_required: str
        command: str | None = None
        discovery_tool: str | None = None
        checks: list[str] | None = None
        steps: list[str] | None = None
        optimization_tips: list[str] | None = None
        .to_dict() -> dict[str, Any]

    Troubleshooting(frozen=True):
        steps: list[str]   # raises ValueError if empty
        .to_dict() -> dict[str, Any]
"""

from __future__ import annotations

import pytest

from actionable_errors.guidance import AIGuidance, Troubleshooting


class TestAIGuidanceCreation:
    """
    REQUIREMENT: AIGuidance provides machine-readable recovery guidance as a frozen dataclass.

    WHO: AI agents consuming error responses to decide on next tool calls
    WHAT: AIGuidance is immutable after creation; to_dict() includes only non-None
          fields; all optional fields default to None; action_required is mandatory
    WHY: Mutable guidance could be silently altered after creation, breaking the
         contract between error producer and AI consumer; None-polluted dicts
         waste context window tokens

    MOCK BOUNDARY:
        Mock:  nothing — pure dataclass
        Real:  AIGuidance instances
        Never: construct dicts manually to compare against
    """

    def test_minimal_guidance_requires_only_action(self) -> None:
        """
        When AIGuidance is created with only action_required
        Then it succeeds with all optional fields as None
        """
        # Given: only the required field

        # When: constructing with minimal args
        guidance = AIGuidance(action_required="Re-authenticate via terminal")

        # Then: required field is set, optionals are None
        assert guidance.action_required == "Re-authenticate via terminal", (
            f"action_required mismatch: {guidance.action_required!r}"
        )
        assert guidance.command is None, (
            f"command should default to None, got {guidance.command!r}"
        )
        assert guidance.steps is None, (
            f"steps should default to None, got {guidance.steps!r}"
        )

    def test_full_guidance_with_all_fields(self) -> None:
        """
        When AIGuidance is created with all fields populated
        Then all fields are accessible
        """
        # Given: all fields provided

        # When: constructing with everything
        guidance = AIGuidance(
            action_required="Fix credentials",
            command="az login",
            discovery_tool="list_accounts()",
            checks=["Check token expiry", "Verify subscription"],
            steps=["Open terminal", "Run az login"],
            optimization_tips=["Use cached tokens"],
        )

        # Then: all fields match
        assert guidance.command == "az login", (
            f"command mismatch: {guidance.command!r}"
        )
        assert guidance.discovery_tool == "list_accounts()", (
            f"discovery_tool mismatch: {guidance.discovery_tool!r}"
        )
        assert guidance.checks == ["Check token expiry", "Verify subscription"], (
            f"checks mismatch: {guidance.checks!r}"
        )
        assert guidance.optimization_tips == ["Use cached tokens"], (
            f"optimization_tips mismatch: {guidance.optimization_tips!r}"
        )

    def test_guidance_is_frozen(self) -> None:
        """
        Given a created AIGuidance instance
        When a field is modified
        Then a FrozenInstanceError is raised
        """
        # Given: an immutable guidance
        guidance = AIGuidance(action_required="Do something")

        # When/Then: mutation attempt raises
        with pytest.raises(AttributeError):
            guidance.action_required = "Do something else"  # type: ignore[misc]

    def test_to_dict_excludes_none_values(self) -> None:
        """
        Given an AIGuidance with some optional fields as None
        When to_dict() is called
        Then None-valued fields are excluded from the result
        """
        # Given: minimal guidance
        guidance = AIGuidance(action_required="Re-authenticate")

        # When: serializing
        result = guidance.to_dict()

        # Then: only action_required is present
        assert result == {"action_required": "Re-authenticate"}, (
            f"Expected only action_required in dict, got {result!r}"
        )
        assert "command" not in result, (
            "None-valued 'command' should be excluded from dict"
        )
        assert "steps" not in result, (
            "None-valued 'steps' should be excluded from dict"
        )

    def test_to_dict_includes_all_populated_fields(self) -> None:
        """
        Given an AIGuidance with all fields populated
        When to_dict() is called
        Then all fields appear in the result
        """
        # Given: fully populated guidance
        guidance = AIGuidance(
            action_required="Fix it",
            command="az login",
            discovery_tool="list_tables()",
            checks=["check1"],
            steps=["step1", "step2"],
            optimization_tips=["tip1"],
        )

        # When: serializing
        result = guidance.to_dict()

        # Then: all six fields are present
        assert len(result) == 6, (
            f"Expected 6 keys in dict, got {len(result)}: {list(result.keys())}"
        )
        assert result["command"] == "az login", (
            f"command mismatch in dict: {result.get('command')!r}"
        )


class TestTroubleshootingCreation:
    """
    REQUIREMENT: Troubleshooting provides sequential human-readable recovery steps.

    WHO: Human operators reading error output to resolve issues manually
    WHAT: Troubleshooting is frozen after creation; steps is a required list of
          strings; to_dict() returns a dict with a "steps" key
    WHY: Without structured steps, operators get a wall of text and must figure
         out the order themselves — slower MTTR

    MOCK BOUNDARY:
        Mock:  nothing — pure dataclass
        Real:  Troubleshooting instances
        Never: construct dicts manually to compare against
    """

    def test_troubleshooting_requires_steps(self) -> None:
        """
        When Troubleshooting is created with a list of steps
        Then the steps are accessible
        """
        # Given: recovery steps

        # When: constructing
        ts = Troubleshooting(steps=["Check logs", "Restart service", "Retry"])

        # Then: steps are stored
        assert ts.steps == ["Check logs", "Restart service", "Retry"], (
            f"steps mismatch: {ts.steps!r}"
        )

    def test_troubleshooting_rejects_empty_steps(self) -> None:
        """
        When Troubleshooting is created with an empty steps list
        Then a ValueError is raised
        """
        # Given: empty steps

        # When/Then: construction raises
        with pytest.raises(ValueError, match="at least one step"):
            Troubleshooting(steps=[])

    def test_troubleshooting_is_frozen(self) -> None:
        """
        Given a created Troubleshooting instance
        When a field is modified
        Then a FrozenInstanceError is raised
        """
        # Given: immutable troubleshooting
        ts = Troubleshooting(steps=["Step 1"])

        # When/Then: mutation attempt raises
        with pytest.raises(AttributeError):
            ts.steps = ["Modified"]  # type: ignore[misc]

    def test_to_dict_returns_steps(self) -> None:
        """
        When to_dict() is called on a Troubleshooting instance
        Then it returns a dict with a "steps" key containing the step list
        """
        # Given: troubleshooting with steps
        ts = Troubleshooting(steps=["Open terminal", "Run az login", "Retry"])

        # When: serializing
        result = ts.to_dict()

        # Then: dict has steps key
        assert "steps" in result, (
            f"Expected 'steps' key in dict, got keys: {list(result.keys())}"
        )
        assert result["steps"] == ["Open terminal", "Run az login", "Retry"], (
            f"steps content mismatch: {result['steps']!r}"
        )
