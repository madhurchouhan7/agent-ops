"""Integration tests for the FastAPI control plane API endpoints."""

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from agent_ops.api import create_app
from agent_ops.domain.models import RunStatus
from agent_ops.storage import (
    ApprovalModel,
    EventRepository,
    RunModel,
    create_db_engine,
    get_session_factory,
    init_db,
)


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    """Test client fixture configured with in-memory database."""
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)
    app = create_app(session_factory=session_factory)

    with TestClient(app) as client:
        yield client


def test_create_run_and_idempotency(api_client: TestClient) -> None:
    payload = {
        "workflow_id": "support_triage_v1",
        "input": {"ticket_id": "TICKET-99", "message": "Help needed"},
        "idempotency_key": "idemp-key-abc-001",
    }

    # 1. Create run
    resp1 = api_client.post("/v1/runs", json=payload)
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["workflow_id"] == "support_triage_v1"
    assert data1["status"] == "CREATED"
    run_id = data1["run_id"]

    # 2. Duplicate create request with same idempotency_key must return same run
    resp2 = api_client.post("/v1/runs", json=payload)
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["run_id"] == run_id

    # 3. List runs should contain only 1 run
    list_resp = api_client.get("/v1/runs")
    assert list_resp.status_code == 200
    runs = list_resp.json()
    assert len(runs) == 1
    assert runs[0]["run_id"] == run_id


def test_get_run_and_timeline_events(api_client: TestClient) -> None:
    create_resp = api_client.post(
        "/v1/runs",
        json={"workflow_id": "support_triage_v1", "input": {"api_key": "sk-secret99"}},
    )
    run_id = create_resp.json()["run_id"]

    # Query details
    get_resp = api_client.get(f"/v1/runs/{run_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["run_id"] == run_id

    # Query safe state: secret must be redacted
    state_resp = api_client.get(f"/v1/runs/{run_id}/state")
    assert state_resp.status_code == 200
    assert state_resp.json()["api_key"] == "[REDACTED]"

    # Query timeline events
    events_resp = api_client.get(f"/v1/runs/{run_id}/events")
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert len(events) >= 1
    assert events[0]["event_type"] == "run.created"


def test_lifecycle_pause_resume_cancel(api_client: TestClient) -> None:
    create_resp = api_client.post("/v1/runs", json={"workflow_id": "support_triage_v1"})
    run_id = create_resp.json()["run_id"]

    # Advance run to RUNNING state so it can be paused
    session_factory = api_client.app.state.session_factory
    session: Session = session_factory()
    try:
        run_model = session.get(RunModel, run_id)
        assert run_model is not None
        run_model.status = "RUNNING"
        session.commit()
    finally:
        session.close()

    # Pause
    pause_resp = api_client.post(f"/v1/runs/{run_id}/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "PAUSED"

    # Resume
    resume_resp = api_client.post(f"/v1/runs/{run_id}/resume")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "RUNNING"

    # Cancel
    cancel_resp = api_client.post(f"/v1/runs/{run_id}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"


def test_approvals_authorization_and_decision(api_client: TestClient) -> None:
    create_resp = api_client.post("/v1/runs", json={"workflow_id": "support_triage_v1"})
    run_id = create_resp.json()["run_id"]

    # Manually inject a pending approval into the session
    session_factory = api_client.app.state.session_factory
    session: Session = session_factory()
    try:
        approval = ApprovalModel(
            id="appr-12345",
            run_id=run_id,
            tool_name="send_customer_reply",
            arguments_json={"message": "Test response"},
            status="PENDING",
            policy_reason="T2_REQUIRES_HUMAN_APPROVAL",
            created_at=datetime.now(UTC),
        )
        session.add(approval)
        session.commit()
    finally:
        session.close()

    # 1. Query pending approvals
    list_appr = api_client.get("/v1/approvals")
    assert list_appr.status_code == 200
    approvals = list_appr.json()
    assert len(approvals) == 1
    assert approvals[0]["id"] == "appr-12345"
    assert approvals[0]["status"] == "PENDING"

    # 2. Decision by unauthorized caller must fail with 403
    unauth_resp = api_client.post(
        "/v1/approvals/appr-12345/decision",
        json={"approved": True},
        headers={"X-Actor": "guest_user", "X-Actor-Roles": "guest"},
    )
    assert unauth_resp.status_code == 403

    # 3. Decision by authorized reviewer succeeds
    auth_resp = api_client.post(
        "/v1/approvals/appr-12345/decision",
        json={"approved": True, "reason": "Looks good"},
        headers={"X-Actor": "lead_reviewer", "X-Actor-Roles": "reviewer"},
    )
    assert auth_resp.status_code == 200
    data = auth_resp.json()
    assert data["status"] == "APPROVED"
    assert data["decision_actor"] == "lead_reviewer"


def test_failure_capsule_export_via_api(api_client: TestClient) -> None:
    session_factory = api_client.app.state.session_factory
    session: Session = session_factory()
    run_id = "failed-api-run-001"
    now = datetime.now(UTC)

    try:
        run_model = RunModel(
            id=run_id,
            workflow_id="support_triage_v1",
            status=RunStatus.FAILED.value,
            state_json={"auth_token": "secret-auth-value"},
            error_code="TIMEOUT_EXCEEDED",
            created_at=now,
            updated_at=now,
        )
        session.add(run_model)
        EventRepository.append_event(
            session=session,
            run_id=run_id,
            event_type="run.failed",
            payload={"api_key": "sk-12345678901234567890"},
        )
        session.commit()
    finally:
        session.close()

    # Export failure capsule
    capsule_resp = api_client.post(f"/v1/runs/{run_id}/failure-capsule")
    assert capsule_resp.status_code == 200
    capsule = capsule_resp.json()
    assert capsule["run_id"] == run_id
    assert capsule["error_code"] == "TIMEOUT_EXCEEDED"
    assert capsule["redacted"] is True

    # Assert secret redaction
    assert "sk-12345678901234567890" not in str(capsule)
    assert "secret-auth-value" not in str(capsule)


def test_evaluation_run_via_api(api_client: TestClient) -> None:
    create_resp = api_client.post("/v1/runs", json={"workflow_id": "support_triage_v1"})
    run_id = create_resp.json()["run_id"]

    eval_resp = api_client.post(
        "/v1/evaluations/run",
        json={"run_id": run_id, "expected_node_order": ["classify"]},
    )
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["run_id"] == run_id
    assert "passed" in eval_data
    assert "score" in eval_data
