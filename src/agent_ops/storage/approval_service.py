"""Human-in-the-loop approval management with server-side authorization."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ops.domain.errors import AgentOpsError
from agent_ops.domain.models import Run, RunStatus
from agent_ops.runtime.engine import WorkflowRuntime
from agent_ops.storage.event_repository import EventRepository
from agent_ops.storage.models import ApprovalModel, RunModel

AUTHORIZED_APPROVAL_ROLES = frozenset({"reviewer", "admin"})


class ApprovalStatus(StrEnum):
    """Lifecycle states for human-in-the-loop approval requests."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApprovalService:
    """Manages approval request persistence, authorization, and gating."""

    @staticmethod
    def request_approval(
        session: Session,
        run: Run,
        tool_name: str,
        arguments: dict[str, Any],
        reason: str,
        runtime: WorkflowRuntime,
    ) -> ApprovalModel:
        """Pause a workflow run and persist a pending approval request."""
        if run.status != RunStatus.PAUSED:
            runtime.pause(run)

        run_model = session.get(RunModel, run.id)
        if run_model is not None:
            run_model.status = run.status.value
            run_model.updated_at = datetime.now(UTC)

        approval_id = uuid4().hex
        approval = ApprovalModel(
            id=approval_id,
            run_id=run.id,
            tool_name=tool_name,
            arguments_json=arguments,
            status=ApprovalStatus.PENDING.value,
            policy_reason=reason,
            created_at=datetime.now(UTC),
        )
        session.add(approval)

        EventRepository.append_event(
            session=session,
            run_id=run.id,
            event_type="approval.requested",
            node_id=run.current_node,
            payload={
                "approval_id": approval_id,
                "tool_name": tool_name,
                "reason": reason,
                "arguments": arguments,
            },
        )
        session.flush()
        return approval

    @staticmethod
    def submit_decision(
        session: Session,
        approval_id: str,
        actor: str,
        actor_roles: set[str],
        approved: bool,
        reason: str | None = None,
    ) -> ApprovalModel:
        """Record an authorized human reviewer decision for a pending approval."""
        approval = session.get(ApprovalModel, approval_id)
        if approval is None:
            raise AgentOpsError(
                f"Approval request '{approval_id}' not found",
                error_code="NOT_FOUND",
            )

        if approval.status != ApprovalStatus.PENDING.value:
            raise AgentOpsError(
                f"Approval '{approval_id}' is already decided ({approval.status})",
                error_code="INVALID_STATE",
            )

        if not actor_roles.intersection(AUTHORIZED_APPROVAL_ROLES):
            raise AgentOpsError(
                f"Actor '{actor}' lacks authorized role for approval decisions",
                error_code="UNAUTHORIZED",
            )

        now = datetime.now(UTC)
        approval.decision_actor = actor
        approval.decision_reason = reason
        approval.decided_at = now
        approval.status = (
            ApprovalStatus.APPROVED.value if approved else ApprovalStatus.REJECTED.value
        )

        event_type = "approval.approved" if approved else "approval.rejected"
        EventRepository.append_event(
            session=session,
            run_id=approval.run_id,
            event_type=event_type,
            payload={
                "approval_id": approval_id,
                "actor": actor,
                "approved": approved,
                "reason": reason,
            },
        )
        session.flush()
        return approval

    @staticmethod
    def can_execute_protected_action(
        session: Session,
        run_id: str,
        tool_name: str,
    ) -> bool:
        """Check if a protected tool action is authorized to execute."""
        query = (
            select(ApprovalModel)
            .where(
                ApprovalModel.run_id == run_id,
                ApprovalModel.tool_name == tool_name,
            )
            .order_by(ApprovalModel.created_at.desc())
        )
        latest_decision = session.scalar(query)
        if latest_decision is None:
            return False
        return latest_decision.status == ApprovalStatus.APPROVED.value

    @staticmethod
    def get_approval(session: Session, approval_id: str) -> ApprovalModel | None:
        """Fetch an approval record by ID."""
        return session.get(ApprovalModel, approval_id)

    @staticmethod
    def list_approvals_for_run(session: Session, run_id: str) -> list[ApprovalModel]:
        """Fetch all approval requests recorded for a workflow run."""
        query = (
            select(ApprovalModel)
            .where(ApprovalModel.run_id == run_id)
            .order_by(ApprovalModel.created_at.asc())
        )
        return list(session.scalars(query).all())
