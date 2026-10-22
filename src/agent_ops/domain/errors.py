"""Domain exceptions for AgentOps workflows and lifecycle management."""


class AgentOpsError(Exception):
    """Base exception for all AgentOps domain errors."""

    error_code: str = "AGENT_OPS_ERROR"

    def __init__(self, message: str, error_code: str | None = None) -> None:
        super().__init__(message)
        if error_code is not None:
            self.error_code = error_code


class InvalidTransitionError(AgentOpsError):
    """Raised when an illegal lifecycle transition is requested."""

    error_code: str = "INVALID_TRANSITION"


class TerminalStateError(AgentOpsError):
    """Raised when attempting to transition or resume from a terminal state."""

    error_code: str = "TERMINAL_STATE_VIOLATION"


class BudgetExceededError(AgentOpsError):
    """Raised when a workflow run exceeds its step counter or execution budget."""

    error_code: str = "BUDGET_EXCEEDED"


class ValidationError(AgentOpsError):
    """Raised when workflow input or state fails schema validation."""

    error_code: str = "VALIDATION_ERROR"
