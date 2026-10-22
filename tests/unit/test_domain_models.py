"""Unit tests for domain models, status enums, and error contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from agent_ops.domain.errors import (
    AgentOpsError,
    BudgetExceededError,
    InvalidTransitionError,
    TerminalStateError,
    ValidationError,
)
from agent_ops.domain.models import (
    TERMINAL_STATUSES,
    BudgetConfig,
    Run,
    RunStatus,
    Step,
)


def test_run_status_members() -> None:
    """RunStatus must define all 6 required lifecycle statuses."""
    expected = {"CREATED", "RUNNING", "PAUSED", "SUCCEEDED", "FAILED", "CANCELLED"}
    assert {s.value for s in RunStatus} == expected


def test_terminal_statuses() -> None:
    """TERMINAL_STATUSES must match exactly SUCCEEDED, FAILED, and CANCELLED."""
    assert TERMINAL_STATUSES == {
        RunStatus.SUCCEEDED,
        RunStatus.FAILED,
        RunStatus.CANCELLED,
    }


def test_budget_config_defaults_and_validation() -> None:
    """BudgetConfig enforces positive values and sensible defaults."""
    cfg = BudgetConfig()
    assert cfg.max_steps == 50
    assert cfg.timeout_seconds == 300.0

    with pytest.raises(PydanticValidationError):
        BudgetConfig(max_steps=0)

    with pytest.raises(PydanticValidationError):
        BudgetConfig(timeout_seconds=-10.0)


def test_step_model_instantiation() -> None:
    """Step records step execution facts accurately."""
    now = datetime.now(UTC)
    step = Step(
        step_index=0,
        node_id="classify_ticket",
        status_before=RunStatus.CREATED,
        status_after=RunStatus.RUNNING,
        timestamp=now,
    )
    assert step.step_index == 0
    assert step.node_id == "classify_ticket"
    assert step.status_before == RunStatus.CREATED
    assert step.status_after == RunStatus.RUNNING
    assert step.timestamp == now


def test_run_model_defaults_and_serialization() -> None:
    """Run model initializes with expected defaults and serializes cleanly."""
    run = Run(id="run-123", workflow_id="support-triage-v1")
    assert run.id == "run-123"
    assert run.workflow_id == "support-triage-v1"
    assert run.workflow_version == "1.0"
    assert run.status == RunStatus.CREATED
    assert run.current_node is None
    assert run.step_count == 0
    assert run.state == {}
    assert run.budget.max_steps == 50
    assert run.error_code is None

    dumped = run.model_dump()
    assert dumped["id"] == "run-123"
    assert dumped["status"] == "CREATED"
    restored = Run.model_validate(dumped)
    assert restored.id == run.id
    assert restored.status == RunStatus.CREATED


def test_domain_exceptions_hierarchy_and_codes() -> None:
    """Domain exceptions inherit from AgentOpsError and provide stable error codes."""
    inv = InvalidTransitionError("Cannot transition from CREATED to SUCCEEDED")
    assert isinstance(inv, AgentOpsError)
    assert inv.error_code == "INVALID_TRANSITION"

    term = TerminalStateError("Terminal state cannot be modified")
    assert isinstance(term, AgentOpsError)
    assert term.error_code == "TERMINAL_STATE_VIOLATION"

    budget = BudgetExceededError("Max steps reached")
    assert isinstance(budget, AgentOpsError)
    assert budget.error_code == "BUDGET_EXCEEDED"

    val = ValidationError("Invalid payload")
    assert isinstance(val, AgentOpsError)
    assert val.error_code == "VALIDATION_ERROR"
