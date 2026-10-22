"""Pydantic schemas for FastAPI control plane request and response bodies."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateRunRequest(BaseModel):
    """Payload to initiate a new workflow run."""

    workflow_id: str = "support_triage_v1"
    input: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str | None = None


class RunResponse(BaseModel):
    """Structured representation of a workflow run."""

    run_id: str
    workflow_id: str
    workflow_version: str = "1.0"
    status: str
    current_node: str | None = None
    step_count: int = 0
    state: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class EventResponse(BaseModel):
    """Serialized execution event from the timeline."""

    id: str
    sequence_no: int
    event_type: str
    node_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class ApprovalResponse(BaseModel):
    """Serialized human-in-the-loop approval record."""

    id: str
    run_id: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: str
    policy_reason: str
    decision_actor: str | None = None
    decision_reason: str | None = None
    created_at: str
    decided_at: str | None = None


class ApprovalDecisionRequest(BaseModel):
    """Payload submitted by a reviewer to approve or reject an action."""

    approved: bool
    reason: str | None = None


class EvaluateRunRequest(BaseModel):
    """Request payload to execute golden trajectory evaluation on a run."""

    run_id: str
    expected_node_order: list[str] | None = None
    require_hitl_approval_for: list[str] | None = None
    forbidden_nodes: list[str] | None = None
