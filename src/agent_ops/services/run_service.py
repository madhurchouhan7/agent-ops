"""Domain service managing workflow run lifecycle, execution, and event dispatching."""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from agent_ops.domain.errors import AgentOpsError
from agent_ops.domain.models import Run, RunStatus
from agent_ops.runtime.engine import WorkflowRuntime
from agent_ops.services.event_bus import global_event_bus
from agent_ops.storage.event_repository import EventRepository
from agent_ops.storage.models import ApprovalModel, RunModel
from agent_ops.tools import PolicyGate, ToolRegistry
from agent_ops.workflows.support_triage import SupportTriageWorkflow

logger = logging.getLogger(__name__)


class RunService:
    """Orchestrates workflow creation, execution, and real-time event publishing."""

    @staticmethod
    def create_run(
        session: Session,
        workflow_id: str,
        input_data: dict[str, Any],
        max_steps: int = 25,
        timeout_seconds: float = 60.0,
        run_id: str | None = None,
    ) -> RunModel:
        """Create a new run record and emit run.created event."""
        run_id = run_id or f"run_{uuid4().hex[:12]}"
        now = datetime.now(UTC)

        run_model = RunModel(
            id=run_id,
            workflow_id=workflow_id,
            workflow_version="1.0",
            status=RunStatus.CREATED.value,
            current_node=None,
            step_count=0,
            state_json=input_data,
            budget_json={"max_steps": max_steps, "timeout_seconds": timeout_seconds},
            created_at=now,
            updated_at=now,
        )
        session.add(run_model)

        event = EventRepository.append_event(
            session=session,
            run_id=run_id,
            event_type="run.created",
            payload={"input": input_data},
        )
        session.commit()

        # Emit to event bus non-blockingly
        RunService._dispatch_event(
            run_id,
            "run.created",
            {"input": input_data, "sequence_no": event.sequence_no},
        )

        return run_model

    @staticmethod
    def pause_run(session: Session, run_id: str) -> RunModel:
        """Pause an active run and dispatch run.paused event."""
        run_model = session.get(RunModel, run_id)
        if not run_model:
            raise AgentOpsError(f"Run {run_id} not found", error_code="NOT_FOUND")

        runtime = WorkflowRuntime()
        domain_run = Run(
            id=run_model.id,
            workflow_id=run_model.workflow_id,
            status=RunStatus(run_model.status),
            state=run_model.state_json,
        )
        runtime.pause(domain_run)

        run_model.status = domain_run.status.value
        run_model.updated_at = datetime.now(UTC)
        event = EventRepository.append_event(
            session=session,
            run_id=run_id,
            event_type="run.paused",
        )
        session.commit()

        RunService._dispatch_event(
            run_id, "run.paused", {"sequence_no": event.sequence_no}
        )
        return run_model

    @staticmethod
    def resume_run(session: Session, run_id: str) -> RunModel:
        """Resume a paused run and dispatch run.resumed event."""
        run_model = session.get(RunModel, run_id)
        if not run_model:
            raise AgentOpsError(f"Run {run_id} not found", error_code="NOT_FOUND")

        runtime = WorkflowRuntime()
        domain_run = Run(
            id=run_model.id,
            workflow_id=run_model.workflow_id,
            status=RunStatus(run_model.status),
            state=run_model.state_json,
        )
        runtime.resume(domain_run)

        run_model.status = domain_run.status.value
        run_model.updated_at = datetime.now(UTC)
        event = EventRepository.append_event(
            session=session,
            run_id=run_id,
            event_type="run.resumed",
        )
        session.commit()

        RunService._dispatch_event(
            run_id, "run.resumed", {"sequence_no": event.sequence_no}
        )
        return run_model

    @staticmethod
    def cancel_run(session: Session, run_id: str) -> RunModel:
        """Cancel an active or paused run and dispatch run.cancelled event."""
        run_model = session.get(RunModel, run_id)
        if not run_model:
            raise AgentOpsError(f"Run {run_id} not found", error_code="NOT_FOUND")

        runtime = WorkflowRuntime()
        domain_run = Run(
            id=run_model.id,
            workflow_id=run_model.workflow_id,
            status=RunStatus(run_model.status),
            state=run_model.state_json,
        )
        runtime.cancel(domain_run)

        run_model.status = domain_run.status.value
        run_model.updated_at = datetime.now(UTC)
        event = EventRepository.append_event(
            session=session,
            run_id=run_id,
            event_type="run.cancelled",
        )
        session.commit()

        RunService._dispatch_event(
            run_id, "run.cancelled", {"sequence_no": event.sequence_no}
        )
        return run_model

    @staticmethod
    def start_demo_triage(
        session: Session,
        ticket_id: str,
        message: str,
        customer_id: str,
    ) -> tuple[RunModel, ApprovalModel]:
        """Orchestrate the synthetic support triage demo until the approval gate."""
        registry = ToolRegistry()
        SupportTriageWorkflow.register_tools(registry)
        policy_gate = PolicyGate()
        runtime = WorkflowRuntime()

        run = SupportTriageWorkflow.create_run(
            session=session,
            ticket_id=ticket_id,
            message=message,
            customer_id=customer_id,
        )

        approval = SupportTriageWorkflow.execute_until_approval(
            session=session,
            run=run,
            runtime=runtime,
            registry=registry,
            policy_gate=policy_gate,
        )

        run_model = session.get(RunModel, run.id)
        assert run_model is not None

        RunService._dispatch_event(
            run.id,
            "demo.approval_required",
            {
                "approval_id": approval.id,
                "tool_name": approval.tool_name,
                "status": run_model.status,
            },
        )

        return run_model, approval

    @staticmethod
    def resume_demo_triage(
        session: Session,
        run_id: str,
    ) -> tuple[RunModel, Any | None]:
        """Resume demo run after an approval or rejection decision."""
        run_model = session.get(RunModel, run_id)
        if not run_model:
            raise AgentOpsError(f"Run {run_id} not found", error_code="NOT_FOUND")

        domain_run = Run(
            id=run_model.id,
            workflow_id=run_model.workflow_id,
            status=RunStatus(run_model.status),
            state=run_model.state_json,
        )

        registry = ToolRegistry()
        SupportTriageWorkflow.register_tools(registry)
        runtime = WorkflowRuntime()

        result = SupportTriageWorkflow.resume_after_approval(
            session=session,
            run=domain_run,
            runtime=runtime,
            registry=registry,
        )

        refreshed_model = session.get(RunModel, run_id)
        assert refreshed_model is not None

        RunService._dispatch_event(
            run_id,
            "demo.resumed",
            {
                "status": refreshed_model.status,
                "executed": result is not None,
            },
        )

        return refreshed_model, (result.data if result else None)

    @staticmethod
    def _dispatch_event(run_id: str, event_type: str, payload: dict[str, Any]) -> None:
        """Safely schedule event publication on the running asyncio loop"""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                global_event_bus.publish(
                    run_id, {"event_type": event_type, "payload": payload}
                )
            )
        except RuntimeError:
            # No running event loop in thread; skip async dispatch safely
            pass
