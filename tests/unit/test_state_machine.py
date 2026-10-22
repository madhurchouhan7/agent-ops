"""Exhaustive transition matrix tests for the AgentOps Finite State Machine."""

import itertools

import pytest

from agent_ops.domain.errors import InvalidTransitionError, TerminalStateError
from agent_ops.domain.models import TERMINAL_STATUSES, Run, RunStatus
from agent_ops.domain.state_machine import ALLOWED_TRANSITIONS, StateMachine


def test_transition_matrix_exhaustive() -> None:
    """Test all 36 status transition permutations against the specification."""
    all_statuses = list(RunStatus)

    for from_status, to_status in itertools.product(all_statuses, all_statuses):
        is_allowed = to_status in ALLOWED_TRANSITIONS.get(from_status, frozenset())

        if from_status in TERMINAL_STATUSES:
            # Transitions from terminal states must strictly raise TerminalStateError
            assert not StateMachine.can_transition(from_status, to_status)
            with pytest.raises(TerminalStateError) as exc_info:
                StateMachine.validate_transition(from_status, to_status)
            assert exc_info.value.error_code == "TERMINAL_STATE_VIOLATION"
        elif is_allowed:
            # Legal transition
            assert StateMachine.can_transition(from_status, to_status)
            # Should not raise
            StateMachine.validate_transition(from_status, to_status)
        else:
            # Illegal transition from non-terminal state
            assert not StateMachine.can_transition(from_status, to_status)
            with pytest.raises(InvalidTransitionError) as exc_info:
                StateMachine.validate_transition(from_status, to_status)
            assert exc_info.value.error_code == "INVALID_TRANSITION"


def test_state_machine_transition_execution() -> None:
    """StateMachine.transition updates status, timestamp, and optional error code."""
    run = Run(id="run-test-1", workflow_id="support-v1")
    assert run.status == RunStatus.CREATED
    old_updated = run.updated_at

    # CREATED -> RUNNING
    StateMachine.transition(run, RunStatus.RUNNING)
    assert run.status == RunStatus.RUNNING
    assert run.updated_at >= old_updated

    # RUNNING -> PAUSED
    StateMachine.transition(run, RunStatus.PAUSED)
    assert run.status == RunStatus.PAUSED

    # PAUSED -> RUNNING
    StateMachine.transition(run, RunStatus.RUNNING)
    assert run.status == RunStatus.RUNNING

    # RUNNING -> FAILED with error_code
    StateMachine.transition(run, RunStatus.FAILED, error_code="POLICY_DENIED")
    assert run.status == RunStatus.FAILED
    assert run.error_code == "POLICY_DENIED"

    # Attempting to resume from FAILED must raise TerminalStateError
    with pytest.raises(TerminalStateError):
        StateMachine.transition(run, RunStatus.RUNNING)
