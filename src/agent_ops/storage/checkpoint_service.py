"""Checkpoint service managing versioned snapshots at safe execution boundaries."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ops.domain.models import Run
from agent_ops.storage.models import CheckpointModel, RunModel


class CheckpointService:
    """Manages saving and querying versioned snapshots of workflow run states."""

    @staticmethod
    def save_checkpoint(
        session: Session,
        run: Run,
        sequence_no: int,
        schema_version: str = "1.0",
        checkpoint_id: str | None = None,
    ) -> CheckpointModel:
        """Persist a state snapshot for a run at a given sequence number."""
        checkpoint = CheckpointModel(
            id=checkpoint_id or uuid4().hex,
            run_id=run.id,
            sequence_no=sequence_no,
            schema_version=schema_version,
            state_json=dict(run.state),
            created_at=datetime.now(UTC),
        )
        session.add(checkpoint)

        # Synchronize run record in database with the checkpointed state
        run_record = session.get(RunModel, run.id)
        if run_record is not None:
            run_record.current_node = run.current_node
            run_record.step_count = run.step_count
            run_record.state_json = dict(run.state)
            run_record.status = run.status.value
            run_record.updated_at = datetime.now(UTC)

        session.flush()
        return checkpoint

    @staticmethod
    def get_latest_checkpoint(session: Session, run_id: str) -> CheckpointModel | None:
        """Retrieve the most recent checkpoint snapshot for a given run."""
        query = (
            select(CheckpointModel)
            .where(CheckpointModel.run_id == run_id)
            .order_by(CheckpointModel.sequence_no.desc())
            .limit(1)
        )
        return session.scalars(query).first()

    @staticmethod
    def list_checkpoints(session: Session, run_id: str) -> list[CheckpointModel]:
        """List all saved checkpoints for a run in ascending sequence order."""
        query = (
            select(CheckpointModel)
            .where(CheckpointModel.run_id == run_id)
            .order_by(CheckpointModel.sequence_no.asc())
        )
        return list(session.scalars(query).all())
