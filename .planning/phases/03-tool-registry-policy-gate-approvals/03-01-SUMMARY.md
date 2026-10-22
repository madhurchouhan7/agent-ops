---
phase: 03-tool-registry-policy-gate-approvals
plan: 01
subsystem: tools-and-approvals
tags: [tools, policy-gate, risk-tiers, hitl, approvals, authorization]

requires:
  - phase: 01-domain-models-state-machine-runtime
    provides: Domain models (Run, RunStatus) and WorkflowRuntime
  - phase: 02-persisted-timeline-checkpoints-recovery
    provides: SQLAlchemy storage models and EventRepository
provides:
  - "Allow-listed ToolRegistry with Pydantic schema validation and execution timeouts"
  - "Code-level PolicyGate evaluating risk tiers (T0-T3) outside model control"
  - "ApprovalModel and ApprovalService managing HITL approval requests, pausing runs, and server-side reviewer authorization"
  - "Rejection safety guarantee: can_execute_protected_action strictly blocks tool execution upon rejection"
affects: [api, demo, eval]

actuals:
  tokens: 22000
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns: [Allow-list pattern, Risk-tier policy gating, Fail-closed human-in-the-loop authorization]

key-files:
  created:
    - src/agent_ops/tools/registry.py
    - src/agent_ops/tools/policy.py
    - src/agent_ops/storage/approval_service.py
    - tests/unit/test_tool_registry.py
    - tests/unit/test_policy_gate.py
    - tests/unit/test_approvals.py
  modified:
    - src/agent_ops/tools/__init__.py
    - src/agent_ops/storage/models.py
    - src/agent_ops/storage/__init__.py

key-decisions:
  - "Unknown tools fail closed with UNKNOWN_TOOL error code"
  - "T3 tools are disabled unconditionally in V1"
  - "Protected T2 tools automatically pause workflow runs and emit approval.requested events"
  - "Approval decisions require server-side authorization role check (reviewer or admin)"
  - "can_execute_protected_action checks latest decision for the tool and strictly fails closed on rejection or pending status"

patterns-established:
  - "Risk tiers: T0 (fixture/sandbox), T1 (read-only query), T2 (reversible mutation / HITL), T3 (destructive/disabled)"
  - "Workflow runtime pausing and resumption coordinated through ApprovalService and StateMachine"

requirements-completed:
  - TOOL-01
  - TOOL-02
  - TOOL-03
  - HITL-01
  - HITL-02
  - HITL-03

coverage:
  - id: D1
    description: "Allow-listed ToolRegistry, Pydantic argument schemas, and execution timeouts"
    requirement: "TOOL-01, TOOL-03"
    verification:
      - kind: unit
        ref: "tests/unit/test_tool_registry.py"
        status: pass
  - id: D2
    description: "PolicyGate risk tier evaluation (T0-T3) and unconditional T3 block"
    requirement: "TOOL-02"
    verification:
      - kind: unit
        ref: "tests/unit/test_policy_gate.py"
        status: pass
  - id: D3
    description: "ApprovalService, reviewer role authorization, run pausing, and rejection safety guarantees"
    requirement: "HITL-01, HITL-02, HITL-03"
    verification:
      - kind: unit
        ref: "tests/unit/test_approvals.py"
        status: pass
---

# Phase 3 Plan 01 Summary: Tool Registry, Policy Gate & Approvals

Delivered the tool execution control plane, policy safety layer, and human-in-the-loop (HITL) approval lifecycle.

## Accomplishments

1. **Allow-Listed Tool Registry & Schemas (`TOOL-01`, `TOOL-03`):**
   - Created `ToolRegistry` enforcing allow-listed tool definitions.
   - Enforced Pydantic v2 input schema validation; unregistered tools and malformed payloads fail closed immediately.
   - Enforced per-tool execution timeouts using bounded worker threads.

2. **Policy Gate & Risk Tiers (`TOOL-02`):**
   - Implemented `PolicyGate` with four discrete risk tiers:
     - `T0`: Local deterministic fixtures / calculations (allowed, no approval).
     - `T1`: Safe read-only queries (allowed, no approval).
     - `T2`: Reversible mutations / external communications (allowed, requires human approval).
     - `T3`: Destructive / high-impact actions (unconditionally denied in V1).

3. **HITL Approvals & Rejection Safety Guarantees (`HITL-01`, `HITL-02`, `HITL-03`):**
   - Added `ApprovalModel` to SQLAlchemy storage schema for persistent audit trails.
   - Implemented `ApprovalService.request_approval` which pauses the workflow run domain model and records `approval.requested` events in `run_events`.
   - Implemented `ApprovalService.submit_decision` enforcing server-side authorization: only callers with `reviewer` or `admin` roles can approve or reject.
   - Implemented `ApprovalService.can_execute_protected_action` verifying that rejected or pending actions strictly block protected tool execution.

## Verification Results

- All 38 tests passing (`pytest`)
- 99% test coverage across `src/agent_ops` (`pytest-cov`)
- Strict static typing clean (`mypy`)
- Strict code style and formatting clean (`ruff`)
