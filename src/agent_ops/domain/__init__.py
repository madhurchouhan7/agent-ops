"""Domain layer exposing models, status enums, state machine, and exceptions."""

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
from agent_ops.domain.state_machine import (
    ALLOWED_TRANSITIONS,
    StateMachine,
)

__all__ = [
    "ALLOWED_TRANSITIONS",
    "AgentOpsError",
    "BudgetConfig",
    "BudgetExceededError",
    "InvalidTransitionError",
    "Run",
    "RunStatus",
    "StateMachine",
    "Step",
    "TERMINAL_STATUSES",
    "TerminalStateError",
    "ValidationError",
]
