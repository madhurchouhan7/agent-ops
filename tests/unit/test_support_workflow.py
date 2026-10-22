"""Unit and end-to-end tests for the synthetic support triage workflow."""

from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session

from agent_ops.domain.models import RunStatus
from agent_ops.evaluations import TrajectoryEvaluator
from agent_ops.runtime.engine import WorkflowRuntime
from agent_ops.storage import (
    ApprovalService,
    ApprovalStatus,
    EventRepository,
    create_db_engine,
    get_session,
    get_session_factory,
    init_db,
)
from agent_ops.storage.models import RunModel
from agent_ops.tools import PolicyGate, ToolRegistry
from agent_ops.workflows import SupportTriageWorkflow


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """In-memory database session fixture."""
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)
    with get_session(session_factory) as session:
        yield session


def test_support_workflow_end_to_end_approved(db_session: Session) -> None:
    registry = ToolRegistry()
    SupportTriageWorkflow.register_tools(registry)
    policy_gate = PolicyGate()
    runtime = WorkflowRuntime()

    # 1. Initialize run
    run = SupportTriageWorkflow.create_run(
        session=db_session,
        ticket_id="TICKET-501",
        message="Billing issue: I was double charged on my invoice.",
        customer_id="ENT-9002",
    )
    assert run.status == RunStatus.CREATED

    # 2. Execute to approval gate
    approval = SupportTriageWorkflow.execute_until_approval(
        session=db_session,
        run=run,
        runtime=runtime,
        registry=registry,
        policy_gate=policy_gate,
    )

    assert run.status == RunStatus.PAUSED
    assert approval.status == ApprovalStatus.PENDING.value
    assert run.state["category"] == "billing"
    assert run.state["tier"] == "enterprise"
    assert "double charged" in run.state["draft_text"]

    # 3. Authorized reviewer approves
    ApprovalService.submit_decision(
        session=db_session,
        approval_id=approval.id,
        actor="senior_reviewer",
        actor_roles={"reviewer"},
        approved=True,
        reason="Draft response looks accurate and polite.",
    )

    # 4. Resume after approval
    result = SupportTriageWorkflow.resume_after_approval(
        session=db_session,
        run=run,
        runtime=runtime,
        registry=registry,
    )

    assert result is not None
    assert result.success is True
    assert result.data["delivered"] is True
    assert run.status == RunStatus.SUCCEEDED

    # Verify run model in DB
    run_model = db_session.get(RunModel, run.id)
    assert run_model is not None
    assert run_model.status == RunStatus.SUCCEEDED.value

    # Evaluate trajectory
    events = [
        {
            "sequence_no": e.sequence_no,
            "event_type": e.event_type,
            "payload": e.payload_json,
        }
        for e in EventRepository.get_events(db_session, run.id)
    ]
    eval_result = TrajectoryEvaluator.evaluate_trajectory(
        run_id=run.id,
        events=events,
        require_hitl_approval_for={"send_customer_reply"},
    )
    assert eval_result.passed is True
    assert eval_result.score == 1.0


def test_support_workflow_end_to_end_rejected(db_session: Session) -> None:
    registry = ToolRegistry()
    SupportTriageWorkflow.register_tools(registry)
    policy_gate = PolicyGate()
    runtime = WorkflowRuntime()

    run = SupportTriageWorkflow.create_run(
        session=db_session,
        ticket_id="TICKET-502",
        message="The application crashes when clicking save.",
        customer_id="CUST-3001",
    )

    approval = SupportTriageWorkflow.execute_until_approval(
        session=db_session,
        run=run,
        runtime=runtime,
        registry=registry,
        policy_gate=policy_gate,
    )
    assert run.status == RunStatus.PAUSED

    # Reviewer rejects the draft
    ApprovalService.submit_decision(
        session=db_session,
        approval_id=approval.id,
        actor="qa_lead",
        actor_roles={"reviewer"},
        approved=False,
        reason="Information incomplete; escalate to dev first.",
    )

    # Resume workflow after rejection
    result = SupportTriageWorkflow.resume_after_approval(
        session=db_session,
        run=run,
        runtime=runtime,
        registry=registry,
    )

    # Must be None, tool not executed, run cancelled
    assert result is None
    assert run.status == RunStatus.CANCELLED

    # Check DB record
    run_model = db_session.get(RunModel, run.id)
    assert run_model is not None
    assert run_model.status == RunStatus.CANCELLED.value

    # Verify trajectory safety: send_customer_reply tool NEVER executed
    events = EventRepository.get_events(db_session, run.id)
    tool_events = [
        e for e in events if e.event_type in {"tool.invoked", "tool.executed"}
    ]
    assert len(tool_events) == 0
