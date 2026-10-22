"""Event repository managing append-only, monotonically sequenced execution events."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_ops.storage.models import RunEventModel


class EventRepository:
    """Manages append-only event logging with strict monotonic sequence numbering."""

    @staticmethod
    def append_event(
        session: Session,
        run_id: str,
        event_type: str,
        node_id: str | None = None,
        payload: dict[str, Any] | None = None,
        event_id: str | None = None,
    ) -> RunEventModel:
        """Atomically append a new execution event with the next sequence number."""
        next_seq_query = select(
            func.coalesce(func.max(RunEventModel.sequence_no), 0)
        ).where(RunEventModel.run_id == run_id)
        current_max = session.scalar(next_seq_query) or 0
        sequence_no = current_max + 1

        event = RunEventModel(
            id=event_id or uuid4().hex,
            run_id=run_id,
            sequence_no=sequence_no,
            event_type=event_type,
            node_id=node_id,
            payload_json=payload or {},
            created_at=datetime.now(UTC),
        )
        session.add(event)
        session.flush()
        return event

    @staticmethod
    def get_events(session: Session, run_id: str) -> list[RunEventModel]:
        """Fetch all events for a run, ordered strictly ascending by sequence_no."""
        query = (
            select(RunEventModel)
            .where(RunEventModel.run_id == run_id)
            .order_by(RunEventModel.sequence_no.asc())
        )
        return list(session.scalars(query).all())

    @staticmethod
    def get_event_count(session: Session, run_id: str) -> int:
        """Count total events recorded for a given run."""
        query = select(func.count(RunEventModel.id)).where(
            RunEventModel.run_id == run_id
        )
        return int(session.scalar(query) or 0)
