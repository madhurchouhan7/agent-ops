"""Restart recovery service for reconstructing runs from saved checkpoints."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_ops.domain.errors import AgentOpsError, TerminalStateError
from agent_ops.domain.models import TERMINAL_STATUSES, BudgetConfig, Run, RunStatus
from agent_ops.storage.checkpoint_service import CheckpointService
from agent_ops.storage.event_repository import EventRepository
from agent_ops.storage.models import RunModel


class RecoveryService:
    """Restores interrupted or crashed workflow runs from durable database state."""

    @staticmethod
    def recover_run(session: Session, run_id: str) -> Run:
        """Reconstruct an in-flight domain Run from its latest checkpoint."""
        query = select(RunModel).where(RunModel.id == run_id)
        run_record = session.scalar(query)
        if run_record is None:
            raise AgentOpsError(
                f"Run '{run_id}' not found in database",
                error_code="RUN_NOT_FOUND",
            )

        status = RunStatus(run_record.status)
        if status in TERMINAL_STATUSES:
            raise TerminalStateError(
                f"Cannot recover or resume run '{run_id}' in terminal state "
                f"{status.value}"
            )

        latest_checkpoint = CheckpointService.get_latest_checkpoint(session, run_id)
        if latest_checkpoint is not None:
            state = dict(latest_checkpoint.state_json)
            restored_seq = latest_checkpoint.sequence_no
        else:
            state = dict(run_record.state_json)
            restored_seq = 0

        budget_data = run_record.budget_json or {}
        budget = BudgetConfig(**budget_data) if budget_data else BudgetConfig()

        created_at = run_record.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        domain_run = Run(
            id=run_record.id,
            workflow_id=run_record.workflow_id,
            workflow_version=run_record.workflow_version,
            status=status,
            current_node=run_record.current_node,
            step_count=run_record.step_count,
            state=state,
            budget=budget,
            created_at=created_at,
            updated_at=datetime.now(UTC),
            error_code=run_record.error_code,
        )

        # Record recovery fact in the monotonic event timeline
        EventRepository.append_event(
            session=session,
            run_id=run_id,
            event_type="run.recovered",
            node_id=domain_run.current_node,
            payload={
                "restored_sequence_no": restored_seq,
                "restored_state_keys": list(state.keys()),
            },
        )

        return domain_run
