"""Core domain models for workflow execution, state tracking, and budgets."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RunStatus(StrEnum):
    """Lifecycle statuses for a workflow run."""

    CREATED = "CREATED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


TERMINAL_STATUSES: frozenset[RunStatus] = frozenset(
    {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED}
)


class BudgetConfig(BaseModel):
    """Execution budgets to bound runtime execution and prevent runaway workflows."""

    model_config = ConfigDict(frozen=True)

    max_steps: int = Field(
        default=50,
        ge=1,
        description="Maximum allowed node execution steps.",
    )
    timeout_seconds: float = Field(
        default=300.0,
        gt=0.0,
        description="Maximum wall-clock execution time in seconds.",
    )


class Step(BaseModel):
    """Record of a single node transition step executed in a workflow run."""

    model_config = ConfigDict(frozen=True)

    step_index: int = Field(
        ge=0,
        description="Monotonic index of the step within the run.",
    )
    node_id: str = Field(
        min_length=1,
        description="Identifier of the executed workflow node.",
    )
    status_before: RunStatus = Field(
        description="Run status prior to step execution.",
    )
    status_after: RunStatus = Field(
        description="Run status following step execution.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when the step executed.",
    )


class Run(BaseModel):
    """A single stateful workflow execution run."""

    id: str = Field(
        min_length=1,
        description="Unique identifier of the run.",
    )
    workflow_id: str = Field(
        min_length=1,
        description="Identifier of the workflow definition.",
    )
    workflow_version: str = Field(
        default="1.0",
        description="Version of the workflow.",
    )
    status: RunStatus = Field(
        default=RunStatus.CREATED,
        description="Current lifecycle status.",
    )
    current_node: str | None = Field(
        default=None,
        description="Current or last-executed workflow node identifier.",
    )
    step_count: int = Field(
        default=0,
        ge=0,
        description="Total count of completed execution steps.",
    )
    state: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary serializable workflow application state.",
    )
    budget: BudgetConfig = Field(
        default_factory=BudgetConfig,
        description="Budget configuration governing this run.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when the run was initialized.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp of the most recent transition or state update.",
    )
    error_code: str | None = Field(
        default=None,
        description="Diagnostic error code if the run failed.",
    )
