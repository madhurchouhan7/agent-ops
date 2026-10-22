"""Unit tests for the event repository and monotonic sequence number invariants."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from agent_ops.storage.database import (
    create_db_engine,
    get_session,
    get_session_factory,
    init_db,
)
from agent_ops.storage.event_repository import EventRepository
from agent_ops.storage.models import RunEventModel, RunModel


@pytest.fixture
def session_factory():
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    return get_session_factory(engine)


def test_monotonic_sequence_numbering(session_factory) -> None:
    """Appending events assigns sequence numbers monotonically: 1, 2, 3..."""
    run_id = "run-seq-test"
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

    with get_session(session_factory) as session:
        e1 = EventRepository.append_event(
            session, run_id, "run.created", payload={"input": "test"}
        )
        assert e1.sequence_no == 1

        e2 = EventRepository.append_event(
            session, run_id, "node.started", node_id="classify_ticket"
        )
        assert e2.sequence_no == 2

        e3 = EventRepository.append_event(
            session, run_id, "node.completed", node_id="classify_ticket"
        )
        assert e3.sequence_no == 3

    with get_session(session_factory) as session:
        events = EventRepository.get_events(session, run_id)
        assert [e.sequence_no for e in events] == [1, 2, 3]
        assert [e.event_type for e in events] == [
            "run.created",
            "node.started",
            "node.completed",
        ]
        assert EventRepository.get_event_count(session, run_id) == 3


def test_unique_constraint_enforces_monotonicity(session_factory) -> None:
    """Attempting to write a duplicate (run_id, sequence_no) raises IntegrityError."""
    run_id = "run-dup-test"
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
        # Add event sequence 1
        session.add(
            RunEventModel(
                id="evt-1",
                run_id=run_id,
                sequence_no=1,
                event_type="test.event",
                created_at=now,
            )
        )

    # In a new session, attempt to write duplicate sequence 1
    with pytest.raises(IntegrityError):
        with get_session(session_factory) as session:
            session.add(
                RunEventModel(
                    id="evt-2",
                    run_id=run_id,
                    sequence_no=1,
                    event_type="duplicate.event",
                    created_at=now,
                )
            )


def test_multi_run_sequence_isolation(session_factory) -> None:
    """Separate runs maintain isolated sequence number spaces starting from 1."""
    now = datetime.now(UTC)
    with get_session(session_factory) as session:
        session.add(
            RunModel(
                id="run-A",
                workflow_id="wf-1",
                status="RUNNING",
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            RunModel(
                id="run-B",
                workflow_id="wf-1",
                status="RUNNING",
                created_at=now,
                updated_at=now,
            )
        )

    with get_session(session_factory) as session:
        a1 = EventRepository.append_event(session, "run-A", "event.1")
        b1 = EventRepository.append_event(session, "run-B", "event.1")
        a2 = EventRepository.append_event(session, "run-A", "event.2")

        assert a1.sequence_no == 1
        assert b1.sequence_no == 1
        assert a2.sequence_no == 2
