"""Unit tests for human-in-the-loop approvals, authorization, and rejection safety."""

from collections.abc import Generator
from typing import Any

import pytest
from pydantic import BaseModel
from sqlalchemy.orm import Session

from agent_ops.domain.errors import AgentOpsError
from agent_ops.domain.models import Run, RunStatus
from agent_ops.domain.state_machine import StateMachine
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
from agent_ops.tools import RiskTier, ToolDefinition, ToolRegistry


class EmailInput(BaseModel):
    recipient: str
    body: str


def send_email_handler(recipient: str, body: str) -> dict[str, Any]:
    return {"delivered": True, "to": recipient, "body": body}


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """In-memory database session fixture."""
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)
    with get_session(session_factory) as session:
        yield session


def test_request_approval_pauses_run_and_logs_event(
    db_session: Session,
) -> None:
    runtime = WorkflowRuntime()
    run = Run(id="run-approval-01", workflow_id="support_agent")
    StateMachine.transition(run, RunStatus.RUNNING)
    assert run.status == RunStatus.RUNNING

    # Add RunModel record to database
    run_model = RunModel(
        id=run.id,
        workflow_id=run.workflow_id,
        status=run.status.value,
    )
    db_session.add(run_model)
    db_session.flush()

    approval = ApprovalService.request_approval(
        session=db_session,
        run=run,
        tool_name="send_email",
        arguments={"recipient": "user@example.com", "body": "Your refund is ready"},
        reason="T2_REQUIRES_HUMAN_APPROVAL",
        runtime=runtime,
    )

    # Workflow run domain model and db record must be paused
    assert run.status == RunStatus.PAUSED
    assert run_model.status == RunStatus.PAUSED.value
    assert approval.status == ApprovalStatus.PENDING.value
    assert approval.tool_name == "send_email"
    assert approval.arguments_json["recipient"] == "user@example.com"

    # Event must be recorded
    events = EventRepository.get_events(db_session, run.id)
    assert len(events) == 1
    assert events[0].event_type == "approval.requested"
    assert events[0].payload_json["approval_id"] == approval.id


def test_submit_decision_unauthorized_fails_closed(
    db_session: Session,
) -> None:
    runtime = WorkflowRuntime()
    run = Run(id="run-approval-02", workflow_id="support_agent")
    StateMachine.transition(run, RunStatus.RUNNING)

    approval = ApprovalService.request_approval(
        session=db_session,
        run=run,
        tool_name="send_email",
        arguments={"recipient": "user@example.com", "body": "Hello"},
        reason="T2_REQUIRES_HUMAN_APPROVAL",
        runtime=runtime,
    )

    # An unauthorized caller (e.g. standard user or agent) must be rejected
    with pytest.raises(AgentOpsError) as exc_info:
        ApprovalService.submit_decision(
            session=db_session,
            approval_id=approval.id,
            actor="unauthorized_caller",
            actor_roles={"standard_user"},
            approved=True,
        )

    assert exc_info.value.error_code == "UNAUTHORIZED"

    # Approval must still be pending
    refreshed = ApprovalService.get_approval(db_session, approval.id)
    assert refreshed is not None
    assert refreshed.status == ApprovalStatus.PENDING.value


def test_submit_decision_rejected_guarantees_tool_cannot_execute(
    db_session: Session,
) -> None:
    runtime = WorkflowRuntime()
    run = Run(id="run-approval-03", workflow_id="support_agent")
    StateMachine.transition(run, RunStatus.RUNNING)

    tool = ToolDefinition(
        name="send_email",
        description="Send customer email",
        risk_tier=RiskTier.T2,
        input_schema=EmailInput,
        handler=send_email_handler,
    )
    registry = ToolRegistry()
    registry.register(tool)

    approval = ApprovalService.request_approval(
        session=db_session,
        run=run,
        tool_name="send_email",
        arguments={"recipient": "user@example.com", "body": "Refund granted"},
        reason="T2_REQUIRES_HUMAN_APPROVAL",
        runtime=runtime,
    )

    # Reviewer rejects the draft
    decided = ApprovalService.submit_decision(
        session=db_session,
        approval_id=approval.id,
        actor="lead_reviewer",
        actor_roles={"reviewer"},
        approved=False,
        reason="Incorrect refund calculation in draft text",
    )
    assert decided.status == ApprovalStatus.REJECTED.value
    assert decided.decision_actor == "lead_reviewer"
    assert decided.decision_reason == "Incorrect refund calculation in draft text"

    # Protected action check strictly returns False
    can_exec = ApprovalService.can_execute_protected_action(
        session=db_session,
        run_id=run.id,
        tool_name="send_email",
    )
    assert can_exec is False

    # Event logged
    events = EventRepository.get_events(db_session, run.id)
    assert len(events) == 2
    assert events[1].event_type == "approval.rejected"


def test_submit_decision_approved_allows_execution(
    db_session: Session,
) -> None:
    runtime = WorkflowRuntime()
    run = Run(id="run-approval-04", workflow_id="support_agent")
    StateMachine.transition(run, RunStatus.RUNNING)

    tool = ToolDefinition(
        name="send_email",
        description="Send customer email",
        risk_tier=RiskTier.T2,
        input_schema=EmailInput,
        handler=send_email_handler,
    )
    registry = ToolRegistry()
    registry.register(tool)

    approval = ApprovalService.request_approval(
        session=db_session,
        run=run,
        tool_name="send_email",
        arguments={"recipient": "user@example.com", "body": "Thank you"},
        reason="T2_REQUIRES_HUMAN_APPROVAL",
        runtime=runtime,
    )

    # Reviewer approves
    ApprovalService.submit_decision(
        session=db_session,
        approval_id=approval.id,
        actor="admin_user",
        actor_roles={"admin"},
        approved=True,
        reason="Tone and information verified",
    )

    # Protected action check succeeds
    can_exec = ApprovalService.can_execute_protected_action(
        session=db_session,
        run_id=run.id,
        tool_name="send_email",
    )
    assert can_exec is True

    # Tool can now safely be executed
    result = registry.execute(tool.name, approval.arguments_json)
    assert result.success is True
    assert result.data["delivered"] is True

    # Workflow runtime resumes
    runtime.resume(run)
    assert run.status == RunStatus.RUNNING


def test_deciding_already_decided_approval_fails(
    db_session: Session,
) -> None:
    runtime = WorkflowRuntime()
    run = Run(id="run-approval-05", workflow_id="support_agent")
    StateMachine.transition(run, RunStatus.RUNNING)

    approval = ApprovalService.request_approval(
        session=db_session,
        run=run,
        tool_name="send_email",
        arguments={"recipient": "user@example.com", "body": "Hi"},
        reason="T2_REQUIRES_HUMAN_APPROVAL",
        runtime=runtime,
    )

    ApprovalService.submit_decision(
        session=db_session,
        approval_id=approval.id,
        actor="admin_user",
        actor_roles={"admin"},
        approved=True,
    )

    with pytest.raises(AgentOpsError) as exc_info:
        ApprovalService.submit_decision(
            session=db_session,
            approval_id=approval.id,
            actor="admin_user",
            actor_roles={"admin"},
            approved=False,
        )

    assert exc_info.value.error_code == "INVALID_STATE"


def test_approval_unknown_id_fails(db_session: Session) -> None:
    with pytest.raises(AgentOpsError) as exc_info:
        ApprovalService.submit_decision(
            session=db_session,
            approval_id="nonexistent-id",
            actor="admin_user",
            actor_roles={"admin"},
            approved=True,
        )

    assert exc_info.value.error_code == "NOT_FOUND"


def test_approval_persistence_across_sessions() -> None:
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)

    runtime = WorkflowRuntime()
    run = Run(id="run-approval-06", workflow_id="support_agent")
    StateMachine.transition(run, RunStatus.RUNNING)

    approval_id: str
    with get_session(session_factory) as session1:
        run_model = RunModel(
            id=run.id,
            workflow_id=run.workflow_id,
            status=run.status.value,
        )
        session1.add(run_model)
        session1.flush()

        approval = ApprovalService.request_approval(
            session=session1,
            run=run,
            tool_name="send_email",
            arguments={"recipient": "persisted@example.com", "body": "Persisted"},
            reason="T2_REQUIRES_HUMAN_APPROVAL",
            runtime=runtime,
        )
        approval_id = approval.id
        session1.commit()

    with get_session(session_factory) as session2:
        retrieved = ApprovalService.get_approval(session2, approval_id)
        assert retrieved is not None
        assert retrieved.status == ApprovalStatus.PENDING.value
        assert retrieved.tool_name == "send_email"
        assert retrieved.arguments_json["recipient"] == "persisted@example.com"

        approvals_list = ApprovalService.list_approvals_for_run(session2, run.id)
        assert len(approvals_list) == 1
