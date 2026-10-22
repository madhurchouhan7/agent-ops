"""State machine logic governing run lifecycle transitions and invariant checks."""

from datetime import UTC, datetime

from agent_ops.domain.errors import InvalidTransitionError, TerminalStateError
from agent_ops.domain.models import TERMINAL_STATUSES, Run, RunStatus

ALLOWED_TRANSITIONS: dict[RunStatus, frozenset[RunStatus]] = {
    RunStatus.CREATED: frozenset(
        {RunStatus.RUNNING, RunStatus.FAILED, RunStatus.CANCELLED}
    ),
    RunStatus.RUNNING: frozenset(
        {
            RunStatus.PAUSED,
            RunStatus.SUCCEEDED,
            RunStatus.FAILED,
            RunStatus.CANCELLED,
        }
    ),
    RunStatus.PAUSED: frozenset(
        {RunStatus.RUNNING, RunStatus.FAILED, RunStatus.CANCELLED}
    ),
    RunStatus.SUCCEEDED: frozenset(),
    RunStatus.FAILED: frozenset(),
    RunStatus.CANCELLED: frozenset(),
}


class StateMachine:
    """Finite State Machine enforcing legal lifecycle transitions for workflow runs."""

    @staticmethod
    def can_transition(from_status: RunStatus, to_status: RunStatus) -> bool:
        """Check whether a transition between two statuses is permissible."""
        if from_status in TERMINAL_STATUSES:
            return False
        return to_status in ALLOWED_TRANSITIONS.get(from_status, frozenset())

    @classmethod
    def validate_transition(cls, from_status: RunStatus, to_status: RunStatus) -> None:
        """Validate a transition, raising a domain error if illegal or terminal."""
        if from_status in TERMINAL_STATUSES:
            raise TerminalStateError(
                f"Cannot transition from terminal state {from_status.value} to "
                f"{to_status.value}"
            )

        allowed = ALLOWED_TRANSITIONS.get(from_status, frozenset())
        if to_status not in allowed:
            raise InvalidTransitionError(
                f"Illegal transition from {from_status.value} to {to_status.value}"
            )

    @classmethod
    def transition(
        cls,
        run: Run,
        to_status: RunStatus,
        error_code: str | None = None,
    ) -> Run:
        """Execute and record a status transition on a run instance."""
        cls.validate_transition(run.status, to_status)
        run.status = to_status
        run.updated_at = datetime.now(UTC)
        if error_code is not None:
            run.error_code = error_code
        return run
