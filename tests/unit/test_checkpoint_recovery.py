"""Unit tests for checkpoint persistence and fresh-process restart recovery."""

from datetime import UTC, datetime
from typing import Any

import pytest

from agent_ops.domain.errors import AgentOpsError, TerminalStateError
from agent_ops.domain.models import Run, RunStatus
from agent_ops.runtime.engine import WorkflowRuntime
from agent_ops.storage.checkpoint_service import CheckpointService
from agent_ops.storage.database import (
    create_db_engine,
    get_session,
    get_session_factory,
    init_db,
)
from agent_ops.storage.event_repository import EventRepository
from agent_ops.storage.models import RunModel
from agent_ops.storage.recovery import RecoveryService


@pytest.fixture
def session_factory():
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    return get_session_factory(engine)


def test_checkpoint_service_crud(session_factory) -> None:
    """CheckpointService saves and queries versioned checkpoints correctly."""
    run_id = "run-cp-test"
    now = datetime.now(UTC)

    with get_session(session_factory) as session:
        session.add(
            RunModel(
                id=run_id,
                workflow_id="support-wf",
                status="RUNNING",
                created_at=now,
                updated_at=now,
            )
        )

    run = Run(
        id=run_id,
        workflow_id="support-wf",
        status=RunStatus.RUNNING,
        state={"step": 1},
    )

    with get_session(session_factory) as session:
        cp1 = CheckpointService.save_checkpoint(session, run, sequence_no=1)
        assert cp1.sequence_no == 1
        assert cp1.state_json == {"step": 1}

        # Update state and save sequence 2
        run.state["step"] = 2
        cp2 = CheckpointService.save_checkpoint(session, run, sequence_no=2)
        assert cp2.sequence_no == 2
        assert cp2.state_json == {"step": 2}

    with get_session(session_factory) as session:
        latest = CheckpointService.get_latest_checkpoint(session, run_id)
        assert latest is not None
        assert latest.sequence_no == 2
        assert latest.state_json == {"step": 2}

        all_cps = CheckpointService.list_checkpoints(session, run_id)
        assert len(all_cps) == 2
        assert [c.sequence_no for c in all_cps] == [1, 2]


def test_restart_recovery_from_simulated_crash(session_factory) -> None:
    """A fresh process restores from the latest checkpoint and continues execution."""
    run_id = "crash-sim-run"
    now = datetime.now(UTC)

    # --- PROCESS 1: Run workflow, save checkpoints, then 'crash' ---
    runtime1 = WorkflowRuntime()
    run1 = Run(
        id=run_id,
        workflow_id="triage-v1",
        status=RunStatus.CREATED,
        created_at=now,
        updated_at=now,
    )

    with get_session(session_factory) as session:
        session.add(
            RunModel(
                id=run_id,
                workflow_id="triage-v1",
                status="RUNNING",
                current_node="classify_ticket",
                step_count=1,
                state_json={"category": "billing"},
                created_at=now,
                updated_at=now,
            )
        )
        # Execute step 1 in Process 1
        runtime1.execute_step(
            run1, "classify_ticket", lambda s: {"category": "billing"}
        )
        EventRepository.append_event(
            session, run_id, "node.completed", "classify_ticket"
        )
        CheckpointService.save_checkpoint(session, run1, sequence_no=1)

        # Execute step 2 in Process 1
        def lookup_action(s: dict[str, Any]) -> dict[str, Any]:
            s["plan"] = "enterprise"
            return s

        runtime1.execute_step(run1, "lookup_ticket", lookup_action)
        EventRepository.append_event(session, run_id, "node.completed", "lookup_ticket")
        CheckpointService.save_checkpoint(session, run1, sequence_no=2)

    # --- SIMULATE CRASH: Process 1 memory is destroyed ---
    del run1
    del runtime1

    # --- PROCESS 2: Fresh process starts up and recovers the run ---
    with get_session(session_factory) as session:
        recovered_run = RecoveryService.recover_run(session, run_id)

        assert recovered_run.id == run_id
        assert recovered_run.status == RunStatus.RUNNING
        assert recovered_run.current_node == "lookup_ticket"
        assert recovered_run.state == {
            "category": "billing",
            "plan": "enterprise",
        }

        # Verify run.recovered event was appended
        events = EventRepository.get_events(session, run_id)
        assert events[-1].event_type == "run.recovered"
        assert events[-1].sequence_no == 3
        assert events[-1].payload_json["restored_sequence_no"] == 2

    # Resume execution with a brand new runtime engine in Process 2
    runtime2 = WorkflowRuntime()

    def reply_action(s: dict[str, Any]) -> dict[str, Any]:
        s["sent"] = True
        return s

    step3 = runtime2.execute_step(recovered_run, "send_reply", reply_action)
    assert step3.node_id == "send_reply"
    assert recovered_run.state["sent"] is True

    runtime2.complete(recovered_run)
    assert recovered_run.status == RunStatus.SUCCEEDED


def test_recovery_without_checkpoints_uses_run_state(session_factory) -> None:
    """When no checkpoints exist, recovery falls back to the RunModel state."""
    run_id = "no-cp-run"
    now = datetime.now(UTC)

    with get_session(session_factory) as session:
        session.add(
            RunModel(
                id=run_id,
                workflow_id="wf-1",
                status="RUNNING",
                current_node="init_node",
                step_count=0,
                state_json={"initial": "data"},
                created_at=now,
                updated_at=now,
            )
        )

    with get_session(session_factory) as session:
        recovered = RecoveryService.recover_run(session, run_id)
        assert recovered.id == run_id
        assert recovered.state == {"initial": "data"}


def test_recovery_rejects_terminal_runs(session_factory) -> None:
    """RecoveryService rejects restoring runs that have already terminated."""
    run_id = "term-run"
    now = datetime.now(UTC)

    with get_session(session_factory) as session:
        session.add(
            RunModel(
                id=run_id,
                workflow_id="wf-1",
                status="SUCCEEDED",
                created_at=now,
                updated_at=now,
            )
        )

    with pytest.raises(TerminalStateError):
        with get_session(session_factory) as session:
            RecoveryService.recover_run(session, run_id)


def test_recovery_nonexistent_run_raises_not_found(session_factory) -> None:
    """Attempting to recover a non-existent run raises AgentOpsError(RUN_NOT_FOUND)."""
    with pytest.raises(AgentOpsError) as exc_info:
        with get_session(session_factory) as session:
            RecoveryService.recover_run(session, "ghost-run-404")

    assert exc_info.value.error_code == "RUN_NOT_FOUND"
