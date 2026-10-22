"""FastAPI control plane route definitions for runs, events, approvals, and capsules."""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from datetime import UTC, datetime
import time
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_ops.api.schemas import (
    ApprovalDecisionRequest,
    ApprovalResponse,
    CreateRunRequest,
    EvaluateRunRequest,
    EventResponse,
    RunResponse,
    StartDemoRequest,
)
from agent_ops.diagnostics import CapsuleService, FailureCapsule, RedactionEngine
from agent_ops.domain.errors import AgentOpsError
from agent_ops.domain.models import Run, RunStatus
from agent_ops.evaluations import EvaluationResult, TrajectoryEvaluator
from agent_ops.runtime.engine import WorkflowRuntime
from agent_ops.services import (
    RunService,
    global_event_bus,
    global_idempotency_manager,
)
from agent_ops.storage import (
    ApprovalService,
    EventRepository,
)
from agent_ops.storage.models import ApprovalModel, RunEventModel, RunModel
from agent_ops.tools import PolicyGate, ToolRegistry
from agent_ops.workflows import SupportTriageWorkflow

router = APIRouter(prefix="/v1")


def get_db_session(request: Request) -> Generator[Session, None, None]:
    """Dependency to retrieve database session with guaranteed teardown."""
    session_factory = request.app.state.session_factory
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.close()


DbSession = Annotated[Session, Depends(get_db_session)]


def serialize_run(run_model: RunModel) -> RunResponse:
    """Convert a RunModel to a clean RunResponse schema."""
    created_str = (
        run_model.created_at.isoformat()
        if isinstance(run_model.created_at, datetime)
        else str(run_model.created_at)
    )
    updated_str = (
        run_model.updated_at.isoformat()
        if isinstance(run_model.updated_at, datetime)
        else str(run_model.updated_at)
    )
    return RunResponse(
        run_id=run_model.id,
        workflow_id=run_model.workflow_id,
        workflow_version=run_model.workflow_version,
        status=run_model.status,
        current_node=run_model.current_node,
        step_count=run_model.step_count,
        state=RedactionEngine.redact(run_model.state_json),
        created_at=created_str,
        updated_at=updated_str,
    )


def serialize_approval(app_model: ApprovalModel) -> ApprovalResponse:
    """Convert an ApprovalModel to an ApprovalResponse schema."""
    created_str = (
        app_model.created_at.isoformat()
        if isinstance(app_model.created_at, datetime)
        else str(app_model.created_at)
    )
    decided_str = (
        app_model.decided_at.isoformat()
        if isinstance(app_model.decided_at, datetime)
        else (str(app_model.decided_at) if app_model.decided_at else None)
    )
    return ApprovalResponse(
        id=app_model.id,
        run_id=app_model.run_id,
        tool_name=app_model.tool_name,
        arguments=RedactionEngine.redact(app_model.arguments_json),
        status=app_model.status,
        policy_reason=app_model.policy_reason,
        decision_actor=app_model.decision_actor,
        decision_reason=app_model.decision_reason,
        created_at=created_str,
        decided_at=decided_str,
    )


# ---------------------------------------------------------------------------
# Run Lifecycle Routes
# ---------------------------------------------------------------------------


@router.post("/runs", response_model=RunResponse, status_code=201)
def create_run(
    req: CreateRunRequest,
    session: DbSession,
) -> RunResponse:
    """Create a new workflow run with thread-safe TTL idempotency key support."""
    if req.idempotency_key:
        record = global_idempotency_manager.get(req.idempotency_key)
        if record:
            existing = session.get(RunModel, record.run_id)
            if existing:
                return serialize_run(existing)

    run_model = RunService.create_run(
        session=session,
        workflow_id=req.workflow_id,
        input_data=req.input,
    )

    if req.idempotency_key:
        global_idempotency_manager.register(
            req.idempotency_key, run_id=run_model.id, status="COMPLETED"
        )

    return serialize_run(run_model)


@router.get("/runs", response_model=list[RunResponse])
def list_runs(
    session: DbSession,
    workflow_id: str | None = None,
    status: str | None = None,
    limit: Annotated[int, Query(le=100)] = 50,
) -> list[RunResponse]:
    """List workflow runs with optional filtering by workflow and status."""
    query = select(RunModel)
    if workflow_id:
        query = query.where(RunModel.workflow_id == workflow_id)
    if status:
        query = query.where(RunModel.status == status)
    query = query.order_by(RunModel.created_at.desc()).limit(limit)

    results = session.scalars(query).all()
    return [serialize_run(r) for r in results]


@router.get("/runs/{run_id}", response_model=RunResponse)
def get_run(
    run_id: str,
    session: DbSession,
) -> RunResponse:
    """Retrieve details and current status of a run."""
    run_model = session.get(RunModel, run_id)
    if not run_model:
        raise HTTPException(status_code=404, detail="RUN_NOT_FOUND")
    return serialize_run(run_model)


@router.get("/runs/{run_id}/events", response_model=list[EventResponse])
def get_run_events(
    run_id: str,
    session: DbSession,
) -> list[EventResponse]:
    """Retrieve ordered execution event history for a run."""
    run_model = session.get(RunModel, run_id)
    if not run_model:
        raise HTTPException(status_code=404, detail="RUN_NOT_FOUND")

    events = EventRepository.get_events(session, run_id)
    out: list[EventResponse] = []
    for ev in events:
        c_str = (
            ev.created_at.isoformat()
            if isinstance(ev.created_at, datetime)
            else str(ev.created_at)
        )
        out.append(
            EventResponse(
                id=ev.id,
                sequence_no=ev.sequence_no,
                event_type=ev.event_type,
                node_id=ev.node_id,
                payload=RedactionEngine.redact(ev.payload_json),
                created_at=c_str,
            )
        )
    return out


@router.get("/runs/{run_id}/state")
def get_run_state(
    run_id: str,
    session: DbSession,
) -> dict[str, Any]:
    """Retrieve safe, redacted state projection for a run."""
    run_model = session.get(RunModel, run_id)
    if not run_model:
        raise HTTPException(status_code=404, detail="RUN_NOT_FOUND")
    state = RedactionEngine.redact(run_model.state_json)
    assert isinstance(state, dict)
    return state


@router.post("/runs/{run_id}/pause", response_model=RunResponse)
def pause_run(
    run_id: str,
    session: DbSession,
) -> RunResponse:
    """Pause an active run at a safe node boundary."""
    try:
        run_model = RunService.pause_run(session, run_id)
        return serialize_run(run_model)
    except AgentOpsError as exc:
        if exc.error_code == "NOT_FOUND":
            raise HTTPException(status_code=404, detail="RUN_NOT_FOUND") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/runs/{run_id}/resume", response_model=RunResponse)
def resume_run(
    run_id: str,
    session: DbSession,
) -> RunResponse:
    """Resume execution of a paused run."""
    try:
        run_model = RunService.resume_run(session, run_id)
        return serialize_run(run_model)
    except AgentOpsError as exc:
        if exc.error_code == "NOT_FOUND":
            raise HTTPException(status_code=404, detail="RUN_NOT_FOUND") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/runs/{run_id}/cancel", response_model=RunResponse)
def cancel_run(
    run_id: str,
    session: DbSession,
) -> RunResponse:
    """Cancel a running or paused run."""
    try:
        run_model = RunService.cancel_run(session, run_id)
        return serialize_run(run_model)
    except AgentOpsError as exc:
        if exc.error_code == "NOT_FOUND":
            raise HTTPException(status_code=404, detail="RUN_NOT_FOUND") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Approvals Routes
# ---------------------------------------------------------------------------


@router.get("/approvals", response_model=list[ApprovalResponse])
def list_approvals(
    session: DbSession,
    run_id: str | None = None,
    status: str | None = None,
) -> list[ApprovalResponse]:
    """List pending or past approval requests."""
    query = select(ApprovalModel)
    if run_id:
        query = query.where(ApprovalModel.run_id == run_id)
    if status:
        query = query.where(ApprovalModel.status == status)
    query = query.order_by(ApprovalModel.created_at.desc())

    approvals = session.scalars(query).all()
    return [serialize_approval(a) for a in approvals]


@router.post(
    "/approvals/{approval_id}/decision",
    response_model=ApprovalResponse,
)
def submit_approval_decision(
    approval_id: str,
    body: ApprovalDecisionRequest,
    session: DbSession,
    x_actor: Annotated[str, Header(alias="X-Actor")] = "anonymous",
    x_actor_roles: Annotated[str, Header(alias="X-Actor-Roles")] = "",
) -> ApprovalResponse:
    """Submit an authorized human approval or rejection decision."""
    roles = {r.strip().lower() for r in x_actor_roles.split(",") if r.strip()}

    try:
        updated = ApprovalService.submit_decision(
            session=session,
            approval_id=approval_id,
            actor=x_actor,
            actor_roles=roles,
            approved=body.approved,
            reason=body.reason,
        )
        session.commit()
        return serialize_approval(updated)
    except AgentOpsError as exc:
        if exc.error_code == "UNAUTHORIZED":
            raise HTTPException(
                status_code=403, detail="UNAUTHORIZED_REVIEWER"
            ) from exc
        if exc.error_code == "NOT_FOUND":
            raise HTTPException(status_code=404, detail="APPROVAL_NOT_FOUND") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Diagnostics & Evaluations Routes
# ---------------------------------------------------------------------------


@router.post("/runs/{run_id}/failure-capsule", response_model=FailureCapsule)
def export_failure_capsule(
    run_id: str,
    session: DbSession,
) -> FailureCapsule:
    """Export a redacted failure capsule for a failed workflow run."""
    try:
        return CapsuleService.export_capsule(session, run_id)
    except AgentOpsError as exc:
        if exc.error_code == "NOT_FOUND":
            raise HTTPException(status_code=404, detail="RUN_NOT_FOUND") from exc
        if exc.error_code == "INVALID_RUN_STATE":
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/evaluations/run", response_model=EvaluationResult)
def evaluate_run(
    req: EvaluateRunRequest,
    session: DbSession,
) -> EvaluationResult:
    """Execute golden trajectory evaluation against a completed run."""
    run_model = session.get(RunModel, req.run_id)
    if not run_model:
        raise HTTPException(status_code=404, detail="RUN_NOT_FOUND")

    events = EventRepository.get_events(session, req.run_id)
    events_data = [
        {
            "sequence_no": e.sequence_no,
            "event_type": e.event_type,
            "node_id": e.node_id,
            "payload": e.payload_json,
        }
        for e in events
    ]

    require_set = (
        set(req.require_hitl_approval_for) if req.require_hitl_approval_for else None
    )
    forbidden_set = set(req.forbidden_nodes) if req.forbidden_nodes else None

    return TrajectoryEvaluator.evaluate_trajectory(
        run_id=req.run_id,
        events=events_data,
        expected_node_order=req.expected_node_order,
        require_hitl_approval_for=require_set,
        forbidden_nodes=forbidden_set,
    )


# ---------------------------------------------------------------------------
# Interactive Demo Endpoints
# ---------------------------------------------------------------------------


@router.post("/demo/triage/start")
def start_triage_demo(
    req: StartDemoRequest,
    session: DbSession,
) -> dict[str, Any]:
    """Initialize and advance the synthetic support triage demo to approval gate."""
    run_model, approval = RunService.start_demo_triage(
        session=session,
        ticket_id=req.ticket_id,
        message=req.message,
        customer_id=req.customer_id,
    )

    return {
        "run": serialize_run(run_model),
        "approval": serialize_approval(approval),
        "status": "PAUSED_WAITING_FOR_APPROVAL",
    }


@router.post("/demo/triage/{run_id}/resume")
def resume_triage_demo(
    run_id: str,
    session: DbSession,
) -> dict[str, Any]:
    """Resume execution of a paused triage demo run following approval or rejection."""
    try:
        refreshed_model, result_data = RunService.resume_demo_triage(
            session=session,
            run_id=run_id,
        )
    except AgentOpsError as exc:
        if exc.error_code == "NOT_FOUND":
            raise HTTPException(status_code=404, detail="RUN_NOT_FOUND") from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "run": serialize_run(refreshed_model),
        "result": result_data,
        "executed": result_data is not None,
    }


# ---------------------------------------------------------------------------
# Real-Time Telemetry & SSE Streaming
# ---------------------------------------------------------------------------


@router.get("/runs/{run_id}/stream", response_class=StreamingResponse)
async def stream_run_events(run_id: str) -> StreamingResponse:
    """Stream live execution events for a specific run in real time via SSE."""
    return StreamingResponse(
        global_event_bus.sse_stream(run_id=run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/events/stream", response_class=StreamingResponse)
async def stream_all_events() -> StreamingResponse:
    """Stream all global platform events in real time via Server-Sent Events."""
    return StreamingResponse(
        global_event_bus.sse_stream(run_id=None),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# System Observability & Health Check Routes
# ---------------------------------------------------------------------------


@router.get("/health")
def health_check(
    request: Request,
    session: DbSession,
) -> dict[str, Any]:
    """Comprehensive readiness and system health check."""
    db_ok = True
    try:
        session.execute(select(1)).scalar()
    except Exception:
        db_ok = False

    uptime_seconds = (
        time.time() - request.app.state.start_time
        if hasattr(request.app.state, "start_time")
        else 0.0
    )

    return {
        "status": "healthy" if db_ok else "unhealthy",
        "service": "agent-ops-control-plane",
        "version": "0.1.0",
        "database": "connected" if db_ok else "disconnected",
        "uptime_seconds": round(uptime_seconds, 2),
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/metrics")
def system_metrics(session: DbSession) -> dict[str, Any]:
    """Operational metrics: runs, events, approvals, and queue statistics."""
    total_runs = session.scalar(select(func.count(RunModel.id))) or 0
    active_runs = (
        session.scalar(
            select(func.count(RunModel.id)).where(
                RunModel.status.in_([RunStatus.RUNNING.value, RunStatus.PAUSED.value])
            )
        )
        or 0
    )
    total_events = session.scalar(select(func.count(RunEventModel.id))) or 0
    pending_approvals = (
        session.scalar(
            select(func.count(ApprovalModel.id)).where(
                ApprovalModel.status == "PENDING"
            )
        )
        or 0
    )

    return {
        "total_runs": total_runs,
        "active_runs": active_runs,
        "total_events": total_events,
        "pending_approvals": pending_approvals,
        "timestamp": datetime.now(UTC).isoformat(),
    }
