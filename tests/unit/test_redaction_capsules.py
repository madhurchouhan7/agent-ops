"""Unit tests for credential redaction and failure capsule export."""

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from sqlalchemy.orm import Session

from agent_ops.diagnostics import CapsuleService, FailureCapsule, RedactionEngine
from agent_ops.domain.errors import AgentOpsError
from agent_ops.domain.models import Run, RunStatus
from agent_ops.storage import (
    CheckpointService,
    EventRepository,
    create_db_engine,
    get_session,
    get_session_factory,
    init_db,
)
from agent_ops.storage.models import RunModel


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """In-memory database session fixture."""
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)
    with get_session(session_factory) as session:
        yield session


def test_redaction_engine_scrubs_sensitive_keys_and_tokens() -> None:
    raw_payload = {
        "user": "alice",
        "api_key": "sk-secret1234567890abcdef12345",
        "nested": {
            "oauth_token": "ghp_123456789012345678901234567890123456",
            "password_hash": "my_super_secret_pw",
            "public_id": "item-99",
        },
        "items": [
            {"auth_header": "Bearer token.value.here"},
            "Clean string",
            "Contact sk-live12345678901234567890 for billing",
        ],
    }

    redacted = RedactionEngine.redact(raw_payload)

    # Assert sensitive keys are masked
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["oauth_token"] == "[REDACTED]"
    assert redacted["nested"]["password_hash"] == "[REDACTED]"
    assert redacted["nested"]["public_id"] == "item-99"

    # Assert strings with bearer or sk- tokens are masked
    assert redacted["items"][0]["auth_header"] == "[REDACTED]"
    assert redacted["items"][1] == "Clean string"
    assert "sk-live" not in redacted["items"][2]
    assert "[REDACTED]" in redacted["items"][2]


def test_export_capsule_on_failed_run_sanitizes_all_fields(
    db_session: Session,
) -> None:
    run_id = "failed-run-001"
    now = datetime.now(UTC)

    # Create a failed RunModel with seeded secrets
    run_model = RunModel(
        id=run_id,
        workflow_id="support_triage",
        workflow_version="1.0",
        status="FAILED",
        current_node="draft_reply",
        step_count=3,
        state_json={
            "ticket_id": "TICKET-1",
            "api_key": "sk-12345678901234567890",
            "customer": {
                "name": "Acme Corp",
                "secret_notes": "Internal executive token 1234",
            },
        },
        error_code="TIMEOUT_BREACH",
        created_at=now,
        updated_at=now,
    )
    db_session.add(run_model)

    # Seed events with sensitive headers
    EventRepository.append_event(
        session=db_session,
        run_id=run_id,
        event_type="node.started",
        node_id="draft_reply",
        payload={"auth_token": "Bearer secret.jwt.here", "node": "draft_reply"},
    )
    EventRepository.append_event(
        session=db_session,
        run_id=run_id,
        event_type="node.failed",
        node_id="draft_reply",
        payload={"error": "Exceeded timeout", "client_secret": "sensitive_val"},
    )

    # Seed a checkpoint
    seed_run = Run(
        id=run_id,
        workflow_id="support_triage",
        status=RunStatus.FAILED,
        state={"step": 2, "access_token": "seed_token_value"},
    )
    CheckpointService.save_checkpoint(
        session=db_session,
        run=seed_run,
        sequence_no=1,
    )
    db_session.flush()

    capsule = CapsuleService.export_capsule(db_session, run_id)

    assert isinstance(capsule, FailureCapsule)
    assert capsule.run_id == run_id
    assert capsule.error_code == "TIMEOUT_BREACH"
    assert capsule.redacted is True
    assert len(capsule.timeline) == 2
    assert len(capsule.checkpoints) == 1

    # Verify no seeded secrets exist anywhere in the capsule
    capsule_json = capsule.model_dump_json()
    assert "sk-12345678901234567890" not in capsule_json
    assert "secret.jwt.here" not in capsule_json
    assert "sensitive_val" not in capsule_json
    assert "seed_token_value" not in capsule_json


def test_export_capsule_on_active_or_succeeded_run_fails_closed(
    db_session: Session,
) -> None:
    run_id = "succeeded-run-002"
    now = datetime.now(UTC)

    run_model = RunModel(
        id=run_id,
        workflow_id="support_triage",
        workflow_version="1.0",
        status="SUCCEEDED",
        created_at=now,
        updated_at=now,
    )
    db_session.add(run_model)
    db_session.flush()

    with pytest.raises(AgentOpsError) as exc_info:
        CapsuleService.export_capsule(db_session, run_id)

    assert exc_info.value.error_code == "INVALID_RUN_STATE"
    assert "Only FAILED runs produce failure capsules" in str(exc_info.value)


def test_export_capsule_unknown_run_fails(db_session: Session) -> None:
    with pytest.raises(AgentOpsError) as exc_info:
        CapsuleService.export_capsule(db_session, "nonexistent-run")

    assert exc_info.value.error_code == "NOT_FOUND"
