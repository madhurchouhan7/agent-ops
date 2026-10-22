"""Failure capsule data model and export service for failed run diagnostics."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ops.diagnostics.redactor import RedactionEngine
from agent_ops.domain.errors import AgentOpsError
from agent_ops.storage.event_repository import EventRepository
from agent_ops.storage.models import CheckpointModel, RunModel


class FailureCapsule(BaseModel):
    """Self-contained, redacted diagnostic artifact exported upon workflow failure."""

    capsule_version: str = "1.0"
    run_id: str
    workflow_id: str
    workflow_version: str = "1.0"
    error_code: str
    error_message: str | None = None
    created_at: datetime
    failed_at: datetime
    timeline: list[dict[str, Any]] = Field(default_factory=list)
    checkpoints: list[dict[str, Any]] = Field(default_factory=list)
    final_state: dict[str, Any] = Field(default_factory=dict)
    redacted: bool = True


class CapsuleService:
    """Exports redacted failure capsules from persisted run records."""

    @classmethod
    def export_capsule(cls, session: Session, run_id: str) -> FailureCapsule:
        """Export a sanitized FailureCapsule for a failed workflow run.

        Raises:
            AgentOpsError: If the run does not exist (NOT_FOUND) or is not in
                           FAILED status (INVALID_RUN_STATE).
        """
        run_model = session.get(RunModel, run_id)
        if run_model is None:
            raise AgentOpsError(
                f"Run '{run_id}' not found",
                error_code="NOT_FOUND",
            )

        if run_model.status != "FAILED":
            raise AgentOpsError(
                f"Cannot export capsule for status '{run_model.status}'. "
                "Only FAILED runs produce failure capsules.",
                error_code="INVALID_RUN_STATE",
            )

        raw_events = EventRepository.get_events(session, run_id)
        timeline: list[dict[str, Any]] = []
        for event in raw_events:
            event_data = {
                "id": event.id,
                "sequence_no": event.sequence_no,
                "event_type": event.event_type,
                "node_id": event.node_id,
                "payload": event.payload_json,
                "created_at": (
                    event.created_at.isoformat()
                    if isinstance(event.created_at, datetime)
                    else str(event.created_at)
                ),
            }
            timeline.append(event_data)

        cp_query = (
            select(CheckpointModel)
            .where(CheckpointModel.run_id == run_id)
            .order_by(CheckpointModel.sequence_no.asc())
        )
        raw_cps = session.scalars(cp_query).all()
        checkpoints: list[dict[str, Any]] = []
        for cp in raw_cps:
            cp_data = {
                "id": cp.id,
                "sequence_no": cp.sequence_no,
                "schema_version": cp.schema_version,
                "state": cp.state_json,
                "created_at": (
                    cp.created_at.isoformat()
                    if isinstance(cp.created_at, datetime)
                    else str(cp.created_at)
                ),
            }
            checkpoints.append(cp_data)

        # Apply comprehensive recursive redaction
        redacted_timeline = RedactionEngine.redact(timeline)
        redacted_checkpoints = RedactionEngine.redact(checkpoints)
        redacted_state = RedactionEngine.redact(run_model.state_json)

        created_at = run_model.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        updated_at = run_model.updated_at
        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=UTC)

        return FailureCapsule(
            capsule_version="1.0",
            run_id=run_model.id,
            workflow_id=run_model.workflow_id,
            workflow_version=run_model.workflow_version,
            error_code=run_model.error_code or "UNKNOWN_FAILURE",
            error_message=RedactionEngine.redact_string(
                run_model.error_code or "Run failed"
            ),
            created_at=created_at,
            failed_at=updated_at,
            timeline=redacted_timeline,
            checkpoints=redacted_checkpoints,
            final_state=redacted_state,
            redacted=True,
        )
