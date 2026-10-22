"""End-to-end synthetic customer support triage workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel
from sqlalchemy.orm import Session

from agent_ops.domain.models import Run, RunStatus
from agent_ops.domain.state_machine import StateMachine
from agent_ops.runtime.engine import WorkflowRuntime
from agent_ops.storage import (
    ApprovalModel,
    ApprovalService,
    CheckpointService,
    EventRepository,
)
from agent_ops.storage.models import RunModel
from agent_ops.tools import (
    PolicyDecision,
    PolicyGate,
    RiskTier,
    ToolDefinition,
    ToolRegistry,
    ToolResult,
)

# ---------------------------------------------------------------------------
# Tool Input Schemas & Handlers
# ---------------------------------------------------------------------------


class ClassifyTicketInput(BaseModel):
    message: str


class LookupCustomerInput(BaseModel):
    customer_id: str


class DraftReplyInput(BaseModel):
    customer_name: str
    category: str
    urgency: str
    message: str


class SendCustomerReplyInput(BaseModel):
    customer_id: str
    reply_text: str


def classify_ticket_handler(message: str) -> dict[str, Any]:
    """T0 deterministic classification handler."""
    lower = message.lower()
    if "refund" in lower or "charge" in lower or "billing" in lower:
        category = "billing"
    elif "crash" in lower or "bug" in lower or "error" in lower:
        category = "technical"
    else:
        category = "general"

    urgency = "high" if ("urgent" in lower or "crash" in lower) else "normal"
    return {"category": category, "urgency": urgency}


def lookup_customer_handler(customer_id: str) -> dict[str, Any]:
    """T1 read-only customer record lookup."""
    tier = "enterprise" if customer_id.startswith("ENT") else "standard"
    return {
        "customer_id": customer_id,
        "customer_name": f"Customer-{customer_id}",
        "tier": tier,
        "account_status": "active",
    }


def draft_reply_handler(
    customer_name: str, category: str, urgency: str, message: str
) -> dict[str, Any]:
    """T0 reply drafting handler."""
    snippet = message[:50].strip()
    greeting = f"Hello {customer_name},"
    body = (
        f"Thank you for contacting us regarding: '{snippet}'. "
        f"We have flagged this as {urgency} priority."
    )
    closing = "Best regards,\nSupport Operations"
    return {"draft_text": f"{greeting}\n\n{body}\n\n{closing}"}


def send_customer_reply_handler(customer_id: str, reply_text: str) -> dict[str, Any]:
    """T2 simulated email delivery tool (requires approval)."""
    return {
        "delivered": True,
        "customer_id": customer_id,
        "reply_preview": reply_text[:60],
        "delivered_at": datetime.now(UTC).isoformat(),
    }


# ---------------------------------------------------------------------------
# Workflow Orchestration
# ---------------------------------------------------------------------------


class SupportTriageWorkflow:
    """Manages the full lifecycle of a synthetic support triage ticket run."""

    WORKFLOW_ID = "support_triage_v1"

    @classmethod
    def register_tools(cls, registry: ToolRegistry) -> None:
        """Register the 4 standard triage tools into a tool registry."""
        registry.register(
            ToolDefinition(
                name="classify_ticket",
                description="Classify customer message sentiment and category",
                risk_tier=RiskTier.T0,
                input_schema=ClassifyTicketInput,
                handler=classify_ticket_handler,
            )
        )
        registry.register(
            ToolDefinition(
                name="lookup_customer",
                description="Fetch customer account tier and status",
                risk_tier=RiskTier.T1,
                input_schema=LookupCustomerInput,
                handler=lookup_customer_handler,
            )
        )
        registry.register(
            ToolDefinition(
                name="draft_reply",
                description="Draft response based on ticket details",
                risk_tier=RiskTier.T0,
                input_schema=DraftReplyInput,
                handler=draft_reply_handler,
            )
        )
        registry.register(
            ToolDefinition(
                name="send_customer_reply",
                description="Deliver simulated email reply to customer",
                risk_tier=RiskTier.T2,
                input_schema=SendCustomerReplyInput,
                handler=send_customer_reply_handler,
            )
        )

    @classmethod
    def create_run(
        cls,
        session: Session,
        ticket_id: str,
        message: str,
        customer_id: str = "CUST-1001",
        run_id: str | None = None,
    ) -> Run:
        """Create and persist a new support triage run initialized in CREATED state."""
        run_uuid = run_id or f"run-triage-{uuid4().hex[:8]}"
        initial_state = {
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "raw_message": message,
        }

        domain_run = Run(
            id=run_uuid,
            workflow_id=cls.WORKFLOW_ID,
            state=initial_state,
        )

        now = datetime.now(UTC)
        run_model = RunModel(
            id=domain_run.id,
            workflow_id=cls.WORKFLOW_ID,
            workflow_version=domain_run.workflow_version,
            status=domain_run.status.value,
            current_node=None,
            step_count=0,
            state_json=initial_state,
            budget_json=domain_run.budget.model_dump(),
            created_at=now,
            updated_at=now,
        )
        session.add(run_model)
        EventRepository.append_event(
            session=session,
            run_id=domain_run.id,
            event_type="run.created",
            payload={"ticket_id": ticket_id, "customer_id": customer_id},
        )
        session.flush()
        return domain_run

    @classmethod
    def execute_until_approval(
        cls,
        session: Session,
        run: Run,
        runtime: WorkflowRuntime,
        registry: ToolRegistry,
        policy_gate: PolicyGate,
    ) -> ApprovalModel:
        """Execute classify, lookup, and draft nodes, then pause for approval."""
        if run.status == RunStatus.CREATED:
            StateMachine.transition(run, RunStatus.RUNNING)

        # 1. Node: classify
        EventRepository.append_event(
            session=session,
            run_id=run.id,
            event_type="node.started",
            node_id="classify",
        )
        classify_res = registry.execute(
            "classify_ticket", {"message": run.state["raw_message"]}
        )
        runtime.execute_step(
            run,
            node_id="classify",
            action=lambda s: {**s, **classify_res.data},
        )
        CheckpointService.save_checkpoint(session, run, sequence_no=run.step_count)

        # 2. Node: lookup_customer
        EventRepository.append_event(
            session=session,
            run_id=run.id,
            event_type="node.started",
            node_id="lookup_customer",
        )
        lookup_res = registry.execute(
            "lookup_customer", {"customer_id": run.state["customer_id"]}
        )
        runtime.execute_step(
            run,
            node_id="lookup_customer",
            action=lambda s: {**s, **lookup_res.data},
        )
        CheckpointService.save_checkpoint(session, run, sequence_no=run.step_count)

        # 3. Node: draft_reply
        EventRepository.append_event(
            session=session,
            run_id=run.id,
            event_type="node.started",
            node_id="draft_reply",
        )
        draft_args = {
            "customer_name": run.state.get("customer_name", "Valued Customer"),
            "category": run.state.get("category", "general"),
            "urgency": run.state.get("urgency", "normal"),
            "message": run.state.get("raw_message", ""),
        }
        draft_res = registry.execute("draft_reply", draft_args)
        runtime.execute_step(
            run,
            node_id="draft_reply",
            action=lambda s: {**s, **draft_res.data},
        )
        CheckpointService.save_checkpoint(session, run, sequence_no=run.step_count)

        # 4. Protected Action: evaluate policy for send_customer_reply
        tool_def = registry.get("send_customer_reply")
        assert tool_def is not None

        send_args = {
            "customer_id": run.state["customer_id"],
            "reply_text": run.state["draft_text"],
        }
        decision: PolicyDecision = policy_gate.evaluate(tool_def, send_args)
        assert decision.requires_approval is True

        # Pause and request approval
        approval = ApprovalService.request_approval(
            session=session,
            run=run,
            tool_name="send_customer_reply",
            arguments=send_args,
            reason=decision.reason,
            runtime=runtime,
        )
        session.commit()
        return approval

    @classmethod
    def resume_after_approval(
        cls,
        session: Session,
        run: Run,
        runtime: WorkflowRuntime,
        registry: ToolRegistry,
    ) -> ToolResult | None:
        """Resume execution following an approval decision.

        If approved, executes protected tool and marks run SUCCEEDED.
        If rejected, skips tool execution and marks run CANCELLED.
        """
        can_exec = ApprovalService.can_execute_protected_action(
            session, run.id, "send_customer_reply"
        )

        if not can_exec:
            # Rejection or unapproved: safe cancellation
            runtime.cancel(run)
            run_model = session.get(RunModel, run.id)
            if run_model:
                run_model.status = RunStatus.CANCELLED.value
                run_model.updated_at = datetime.now(UTC)
            EventRepository.append_event(
                session=session,
                run_id=run.id,
                event_type="workflow.cancelled_by_rejection",
                payload={"protected_tool": "send_customer_reply"},
            )
            session.commit()
            return None

        # Approval granted: resume and execute protected tool
        runtime.resume(run)
        run_model = session.get(RunModel, run.id)
        if run_model:
            run_model.status = RunStatus.RUNNING.value

        send_args = {
            "customer_id": run.state["customer_id"],
            "reply_text": run.state["draft_text"],
        }

        EventRepository.append_event(
            session=session,
            run_id=run.id,
            event_type="tool.invoked",
            node_id="send_customer_reply",
            payload={"tool_name": "send_customer_reply", "arguments": send_args},
        )

        result = registry.execute("send_customer_reply", send_args)

        runtime.execute_step(
            run,
            node_id="send_customer_reply",
            action=lambda s: {**s, **result.data},
        )
        CheckpointService.save_checkpoint(session, run, sequence_no=run.step_count)

        runtime.complete(run)
        if run_model:
            run_model.status = RunStatus.SUCCEEDED.value
            run_model.updated_at = datetime.now(UTC)

        EventRepository.append_event(
            session=session,
            run_id=run.id,
            event_type="tool.executed",
            node_id="send_customer_reply",
            payload={"tool_name": "send_customer_reply", "result": result.data},
        )
        session.commit()
        return result
