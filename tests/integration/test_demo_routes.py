"""Integration tests for support triage demo orchestration routes."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from agent_ops.api import create_app
from agent_ops.storage import (
    create_db_engine,
    get_session_factory,
    init_db,
)


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    """Test client configured with in-memory SQLite database."""
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)
    app = create_app(session_factory=session_factory)

    with TestClient(app) as client:
        yield client


def test_demo_triage_start_and_pause(api_client: TestClient) -> None:
    resp = api_client.post(
        "/v1/demo/triage/start",
        json={
            "ticket_id": "TICKET-DEMO-01",
            "message": "Double billed for monthly subscription renewal",
            "customer_id": "ENT-4040",
        },
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "PAUSED_WAITING_FOR_APPROVAL"
    assert data["run"]["status"] == "PAUSED"
    assert data["approval"]["status"] == "PENDING"
    assert data["approval"]["tool_name"] == "send_customer_reply"
    assert "Double billed" in data["run"]["state"]["draft_text"]


def test_demo_triage_approval_and_resume_succeeds(
    api_client: TestClient,
) -> None:
    # 1. Start demo
    start_resp = api_client.post(
        "/v1/demo/triage/start",
        json={
            "ticket_id": "TICKET-DEMO-02",
            "message": "Crash on click save button",
            "customer_id": "CUST-100",
        },
    )
    run_id = start_resp.json()["run"]["run_id"]
    approval_id = start_resp.json()["approval"]["id"]

    # 2. Reviewer approves
    decision_resp = api_client.post(
        f"/v1/approvals/{approval_id}/decision",
        json={"approved": True, "reason": "Draft verified"},
        headers={"X-Actor": "lead_agent", "X-Actor-Roles": "reviewer"},
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["status"] == "APPROVED"

    # 3. Resume workflow
    resume_resp = api_client.post(f"/v1/demo/triage/{run_id}/resume")
    assert resume_resp.status_code == 200
    data = resume_resp.json()
    assert data["executed"] is True
    assert data["result"]["delivered"] is True
    assert data["run"]["status"] == "SUCCEEDED"


def test_demo_triage_rejection_and_resume_cancels(
    api_client: TestClient,
) -> None:
    start_resp = api_client.post(
        "/v1/demo/triage/start",
        json={
            "ticket_id": "TICKET-DEMO-03",
            "message": "Delete my user account immediately",
            "customer_id": "CUST-200",
        },
    )
    run_id = start_resp.json()["run"]["run_id"]
    approval_id = start_resp.json()["approval"]["id"]

    # Reviewer rejects
    decision_resp = api_client.post(
        f"/v1/approvals/{approval_id}/decision",
        json={"approved": False, "reason": "Requires manual confirmation"},
        headers={"X-Actor": "compliance_officer", "X-Actor-Roles": "reviewer"},
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["status"] == "REJECTED"

    # Resume workflow
    resume_resp = api_client.post(f"/v1/demo/triage/{run_id}/resume")
    assert resume_resp.status_code == 200
    data = resume_resp.json()
    assert data["executed"] is False
    assert data["result"] is None
    assert data["run"]["status"] == "CANCELLED"
