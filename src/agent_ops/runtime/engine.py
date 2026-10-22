"""Workflow runtime engine for bounded, stateful step execution."""

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from agent_ops.domain.errors import (
    BudgetExceededError,
    InvalidTransitionError,
    TerminalStateError,
)
from agent_ops.domain.models import (
    TERMINAL_STATUSES,
    Run,
    RunStatus,
    Step,
)
from agent_ops.domain.state_machine import StateMachine

NodeAction = Callable[[dict[str, Any]], dict[str, Any]]


class WorkflowRuntime:
    """Manages bounded step execution, budget enforcement, and lifecycle progression."""

    def __init__(self, state_machine: type[StateMachine] = StateMachine) -> None:
        self.state_machine = state_machine

    def execute_step(
        self,
        run: Run,
        node_id: str,
        action: NodeAction,
    ) -> Step:
        """Execute a single bounded node action within budget limits."""
        # Check wall-clock timeout
        elapsed_seconds = (datetime.now(UTC) - run.created_at).total_seconds()
        if elapsed_seconds > run.budget.timeout_seconds:
            self.state_machine.transition(
                run, RunStatus.FAILED, error_code="BUDGET_EXCEEDED"
            )
            raise BudgetExceededError(
                f"Execution timeout of {run.budget.timeout_seconds}s exceeded "
                f"(elapsed {elapsed_seconds:.2f}s)",
                error_code="BUDGET_EXCEEDED",
            )

        # Check step count budget
        if run.step_count + 1 > run.budget.max_steps:
            self.state_machine.transition(
                run, RunStatus.FAILED, error_code="BUDGET_EXCEEDED"
            )
            raise BudgetExceededError(
                f"Execution step limit of {run.budget.max_steps} steps exceeded",
                error_code="BUDGET_EXCEEDED",
            )

        # Validate run status before executing step
        status_before = run.status
        if run.status == RunStatus.CREATED:
            self.state_machine.transition(run, RunStatus.RUNNING)
            status_before = RunStatus.RUNNING
        elif run.status == RunStatus.PAUSED:
            raise InvalidTransitionError(
                "Cannot execute step while run is PAUSED. Resume run first."
            )
        elif run.status in TERMINAL_STATUSES:
            raise TerminalStateError(
                f"Cannot execute step on terminal run {run.status.value}"
            )
        elif run.status != RunStatus.RUNNING:
            raise InvalidTransitionError(
                f"Cannot execute step in status {run.status.value}"
            )

        # Execute node action
        new_state = action(dict(run.state))
        run.state = new_state
        run.step_count += 1
        run.current_node = node_id
        run.updated_at = datetime.now(UTC)

        return Step(
            step_index=run.step_count - 1,
            node_id=node_id,
            status_before=status_before,
            status_after=run.status,
            timestamp=datetime.now(UTC),
        )

    def pause(self, run: Run) -> None:
        """Pause execution at a safe node boundary."""
        self.state_machine.transition(run, RunStatus.PAUSED)

    def resume(self, run: Run) -> None:
        """Resume execution of a paused run."""
        self.state_machine.transition(run, RunStatus.RUNNING)

    def complete(self, run: Run) -> None:
        """Mark a completed run as successfully finished."""
        self.state_machine.transition(run, RunStatus.SUCCEEDED)

    def fail(self, run: Run, error_code: str = "FAILED") -> None:
        """Mark a run as failed with a diagnostic error code."""
        self.state_machine.transition(run, RunStatus.FAILED, error_code=error_code)

    def cancel(self, run: Run) -> None:
        """Cancel a running or paused run."""
        self.state_machine.transition(run, RunStatus.CANCELLED)
