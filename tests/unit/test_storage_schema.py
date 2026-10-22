"""Unit tests for SQLAlchemy storage models and database setup."""

from datetime import UTC, datetime

from sqlalchemy import select

from agent_ops.storage.database import (
    create_db_engine,
    get_session,
    get_session_factory,
    init_db,
)
from agent_ops.storage.models import RunModel


def test_schema_init_and_run_roundtrip() -> None:
    """Verify tables can be initialized and a RunModel record persisted and queried."""
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)

    run_id = "test-run-001"
    now = datetime.now(UTC)

    with get_session(session_factory) as session:
        run = RunModel(
            id=run_id,
            workflow_id="support-triage-v1",
            workflow_version="1.0",
            status="CREATED",
            current_node=None,
            step_count=0,
            state_json={"ticket": "T123"},
            budget_json={"max_steps": 50},
            error_code=None,
            created_at=now,
            updated_at=now,
        )
        session.add(run)

    # Query back in a new session
    with get_session(session_factory) as session:
        result = session.execute(
            select(RunModel).where(RunModel.id == run_id)
        ).scalar_one_or_none()
        assert result is not None
        assert result.id == run_id
        assert result.workflow_id == "support-triage-v1"
        assert result.status == "CREATED"
        assert result.state_json == {"ticket": "T123"}
