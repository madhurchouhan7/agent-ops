---
phase: 04-diagnostics-evaluation-support-demo
plan: 01
subsystem: diagnostics-and-control-plane
tags: [diagnostics, failure-capsule, redaction, mock-replay, trajectory-evaluation, support-demo, fastapi, idempotency]

requires:
  - phase: 01-domain-models-state-machine-runtime
    provides: Domain models and bounded WorkflowRuntime
  - phase: 02-persisted-timeline-checkpoints-recovery
    provides: PostgreSQL/SQLite persistence, EventRepository, CheckpointService
  - phase: 03-tool-registry-policy-gate-approvals
    provides: ToolRegistry, PolicyGate, ApprovalService, and reviewer authorization
provides:
  - "RedactionEngine recursively scrubbing passwords, tokens, API keys, and sensitive headers"
  - "FailureCapsule export service serializing sanitized timelines, checkpoints, and final states on run failure"
  - "MockReplayRunner executing pure offline replay with 0 external network requests or side effects"
  - "TrajectoryEvaluator asserting intermediate states, ordering, and human-in-the-loop safety invariants in CI"
  - "SupportTriageWorkflow demonstrating end-to-end classification, customer lookup, drafting, approval pause, and simulated delivery"
  - "FastAPI control plane API exposing REST endpoints for runs, events, state, approvals, failure capsules, and evaluations with idempotency"
affects: []

actuals:
  tokens: 28000
  tasks: 4
  commits: 4

tech-stack:
  added: [fastapi>=0.110, httpx>=0.27]
  patterns: [Recursive credential scrubbing, Offline mock replay, Golden trajectory assertion, Idempotent REST API]

key-files:
  created:
    - src/agent_ops/diagnostics/redactor.py
    - src/agent_ops/diagnostics/capsule.py
    - src/agent_ops/diagnostics/replay.py
    - src/agent_ops/evaluations/evaluator.py
    - src/agent_ops/workflows/support_triage.py
    - src/agent_ops/api/schemas.py
    - src/agent_ops/api/routes.py
    - src/agent_ops/api/app.py
    - tests/unit/test_redaction_capsules.py
    - tests/unit/test_mock_replay.py
    - tests/unit/test_evaluator.py
    - tests/unit/test_support_workflow.py
    - tests/integration/test_api_endpoints.py
  modified:
    - pyproject.toml
    - uv.lock
    - src/agent_ops/storage/database.py
    - src/agent_ops/storage/approval_service.py
    - src/agent_ops/api/__init__.py
    - src/agent_ops/diagnostics/__init__.py
    - src/agent_ops/evaluations/__init__.py
    - src/agent_ops/workflows/__init__.py

key-decisions:
  - "RedactionEngine employs case-insensitive key detection and regex patterns for bearer tokens and token shapes"
  - "Only runs in FAILED status can export Failure Capsules; other states fail closed with INVALID_RUN_STATE"
  - "MockReplayRunner performs deterministic in-memory replay purely from recorded events and checkpoints with zero socket calls"
  - "TrajectoryEvaluator strictly flags any T2 tool execution that lacks a prior approval.approved event"
  - "FastAPI control API uses SQLite StaticPool for reliable in-memory multi-session testing"
  - "POST /v1/runs enforces idempotency via client idempotency_key"

patterns-established:
  - "Failure capsule format (versioned, self-contained, sanitized)"
  - "Golden trajectory assertion framework for agent CI pipelines"
  - "Multi-tier support triage workflow pattern (T0 -> T1 -> T0 -> T2 approval -> T2 action)"

requirements-completed:
  - DIAG-01
  - DIAG-02
  - DIAG-03
  - DEMO-01
  - API-01

coverage:
  - id: D1
    description: "Recursive redaction engine and failure capsule export"
    requirement: "DIAG-01"
    verification:
      - kind: unit
        ref: "tests/unit/test_redaction_capsules.py"
        status: pass
  - id: D2
    description: "Offline mock replay runner and golden trajectory evaluator"
    requirement: "DIAG-02, DIAG-03"
    verification:
      - kind: unit
        ref: "tests/unit/test_mock_replay.py"
        status: pass
      - kind: unit
        ref: "tests/unit/test_evaluator.py"
        status: pass
  - id: D3
    description: "End-to-end synthetic customer support triage workflow"
    requirement: "DEMO-01"
    verification:
      - kind: unit
        ref: "tests/unit/test_support_workflow.py"
        status: pass
  - id: D4
    description: "FastAPI REST control plane endpoints with idempotency and role authorization"
    requirement: "API-01"
    verification:
      - kind: integration
        ref: "tests/integration/test_api_endpoints.py"
        status: pass
---

# Phase 4 Plan 01 Summary: Diagnostics, Evaluation & Support Demo

Delivered the complete diagnostic, evaluation, and REST interface layer for AgentOps, culminating in an end-to-end runnable support triage demonstration.

## Accomplishments

1. **Redaction Engine & Failure Capsule Export (`DIAG-01`):**
   - Implemented `RedactionEngine` performing recursive scrubbing of dictionary keys (`api_key`, `token`, `secret`, `password`, `auth`) and regex string tokens (`bearer`, `sk-`, `ghp_`).
   - Implemented `CapsuleService.export_capsule` generating portable, sanitized diagnostic bundles for failed workflow runs.

2. **Offline Mock Replay & Golden Trajectory Evaluation (`DIAG-02`, `DIAG-03`):**
   - Implemented `MockReplayRunner` reconstructing execution states purely from historical events and validating checkpoints with zero external socket or side-effect calls.
   - Implemented `TrajectoryEvaluator` asserting node execution sequence, catching forbidden nodes, and verifying that protected tools cannot execute without prior human approval or following a rejection.

3. **Synthetic Support Triage Workflow (`DEMO-01`):**
   - Implemented `SupportTriageWorkflow` tying together `classify_ticket` (T0), `lookup_customer` (T1), `draft_reply` (T0), and `send_customer_reply` (T2).
   - Demonstrated complete end-to-end execution: ticket creation -> automated triage -> policy evaluation -> workflow pause -> human reviewer signoff -> simulated delivery -> run completion.

4. **FastAPI Control Plane API (`API-01`):**
   - Built full REST API with endpoints for run creation, listing, detail, timeline events, state projection, pause/resume/cancel, approval decision submission, failure capsule export, and trajectory evaluation.
   - Implemented request deduplication via `idempotency_key`.
   - Enforced server-side reviewer authorization via `X-Actor` and `X-Actor-Roles` headers.

## Verification Results

- All 56 tests passing (`pytest`) across unit and integration suites
- **96%** code coverage across the entire `src/agent_ops` repository (`pytest-cov`)
- Strict type checking clean (`mypy`) with zero errors across all 29 modules
- Linting and formatting clean (`ruff`)
