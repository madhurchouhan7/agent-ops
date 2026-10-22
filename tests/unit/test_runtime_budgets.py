"""Unit tests for the bounded workflow runtime and step execution."""

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from agent_ops.domain.errors import (
    BudgetExceededError,
    InvalidTransitionError,
    TerminalStateError,
)
from agent_ops.domain.models import BudgetConfig, Run, RunStatus
from agent_ops.runtime.engine import WorkflowRuntime


def test_runtime_happy_path_execution() -> None:
    """Execute a realistic multi-step workflow from CREATED to SUCCEEDED."""
    runtime = WorkflowRuntime()
    run = Run(
        id="run-happy-1",
        workflow_id="support-triage-v1",
        state={"ticket_id": "TICKET-101"},
    )
    assert run.status == RunStatus.CREATED

    # Step 1: classify ticket
    def classify_action(state: dict[str, Any]) -> dict[str, Any]:
        state["category"] = "billing"
        state["urgency"] = "high"
        return state

    step1 = runtime.execute_step(run, "classify_ticket", classify_action)
    assert run.status == RunStatus.RUNNING
    assert run.current_node == "classify_ticket"
    assert run.step_count == 1
    assert step1.node_id == "classify_ticket"
    assert run.state["category"] == "billing"

    # Step 2: lookup customer info
    def lookup_action(state: dict[str, Any]) -> dict[str, Any]:
        state["customer_plan"] = "enterprise"
        return state

    step2 = runtime.execute_step(run, "lookup_ticket", lookup_action)
    assert run.step_count == 2
    assert step2.step_index == 1
    assert run.state["customer_plan"] == "enterprise"

    # Pause before protected action
    runtime.pause(run)
    assert run.status == RunStatus.PAUSED

    # Paused run cannot execute steps
    with pytest.raises(InvalidTransitionError):
        runtime.execute_step(run, "send_reply", lambda s: s)

    # Resume after approval
    runtime.resume(run)
    assert run.status == RunStatus.RUNNING

    # Step 3: execute simulated send_reply
    def send_action(state: dict[str, Any]) -> dict[str, Any]:
        state["reply_sent"] = True
        return state

    runtime.execute_step(run, "send_reply", send_action)
    assert run.step_count == 3
    assert run.state["reply_sent"] is True

    # Complete workflow
    runtime.complete(run)
    assert run.status == RunStatus.SUCCEEDED


def test_runtime_max_steps_budget_enforcement() -> None:
    """Workflows exceeding max_steps halt and transition to FAILED."""
    runtime = WorkflowRuntime()
    run = Run(
        id="run-loop-1",
        workflow_id="infinite-loop-test",
        budget=BudgetConfig(max_steps=3),
    )

    def dummy_action(state: dict[str, Any]) -> dict[str, Any]:
        return state

    # Step 1
    runtime.execute_step(run, "node_1", dummy_action)
    assert run.step_count == 1

    # Step 2
    runtime.execute_step(run, "node_2", dummy_action)
    assert run.step_count == 2

    # Step 3
    runtime.execute_step(run, "node_3", dummy_action)
    assert run.step_count == 3

    # Step 4: exceeds max_steps=3
    with pytest.raises(BudgetExceededError) as exc_info:
        runtime.execute_step(run, "node_4", dummy_action)

    assert exc_info.value.error_code == "BUDGET_EXCEEDED"
    assert run.status == RunStatus.FAILED
    assert run.error_code == "BUDGET_EXCEEDED"

    # Subsequent step attempts fail due to terminal state
    with pytest.raises(TerminalStateError):
        runtime.execute_step(run, "node_5", dummy_action)


def test_runtime_timeout_budget_enforcement() -> None:
    """Workflows exceeding timeout_seconds halt and transition to FAILED."""
    runtime = WorkflowRuntime()
    past_time = datetime.now(UTC) - timedelta(seconds=500)
    run = Run(
        id="run-timeout-1",
        workflow_id="timeout-test",
        created_at=past_time,
        budget=BudgetConfig(timeout_seconds=300.0),
    )

    with pytest.raises(BudgetExceededError) as exc_info:
        runtime.execute_step(run, "first_node", lambda s: s)

    assert exc_info.value.error_code == "BUDGET_EXCEEDED"
    assert run.status == RunStatus.FAILED
    assert run.error_code == "BUDGET_EXCEEDED"


def test_runtime_cancel_and_fail_helpers() -> None:
    """WorkflowRuntime cancellation and explicit failure transitions operate cleanly."""
    runtime = WorkflowRuntime()
    run = Run(id="run-cancel-1", workflow_id="cancel-test")

    runtime.cancel(run)
    assert run.status == RunStatus.CANCELLED

    with pytest.raises(TerminalStateError):
        runtime.resume(run)

    run2 = Run(id="run-fail-1", workflow_id="fail-test")
    runtime.fail(run2, error_code="SYNTHETIC_FAILURE")
    assert run2.status == RunStatus.FAILED
    assert run2.error_code == "SYNTHETIC_FAILURE"


def test_runtime_step_on_terminal_raises_terminal_error() -> None:
    """Executing a step on an already terminal run raises TerminalStateError."""
    runtime = WorkflowRuntime()
    run = Run(id="run-term", workflow_id="test-wf")
    runtime.execute_step(run, "start_node", lambda s: s)
    assert run.status == RunStatus.RUNNING
    runtime.complete(run)
    assert run.status == RunStatus.SUCCEEDED

    with pytest.raises(TerminalStateError):
        runtime.execute_step(run, "some_node", lambda s: s)

    run_fail = Run(id="run-term-fail", workflow_id="test-wf")
    runtime.fail(run_fail)
    with pytest.raises(TerminalStateError):
        runtime.execute_step(run_fail, "some_node", lambda s: s)

    run_canc = Run(id="run-term-canc", workflow_id="test-wf")
    runtime.cancel(run_canc)
    with pytest.raises(TerminalStateError):
        runtime.execute_step(run_canc, "some_node", lambda s: s)
