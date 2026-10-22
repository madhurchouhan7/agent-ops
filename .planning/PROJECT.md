# AgentOps

## What This Is

AgentOps is a developer control plane for running, inspecting, debugging, and recovering stateful AI agent workflows. It treats AI workflows as deterministic, observable, and auditable distributed state machines rather than opaque chat loops.

## Core Value

Deterministic, observable execution with explicit state transitions, durable checkpoints for restart recovery, and code-enforced human-in-the-loop safety gates.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] REQ-runtime-state-machine: Explicit workflow runtime and state machine with bounded step execution.
- [ ] REQ-persisted-timeline-and-checkpoints: Ordered event timeline and versioned checkpoints for restart recovery.
- [ ] REQ-tool-registry-and-policy-gate: Allow-listed tool registry with strict schemas and code-level policy enforcement.
- [ ] REQ-hitl-pause-and-approval: Pause before protected actions requiring authorized human approval.
- [ ] REQ-failure-capsule-and-mock-replay: Redacted failure capsule export and offline mock replay.
- [ ] REQ-control-api-and-storage: FastAPI REST control plane backed by PostgreSQL durable storage.
- [ ] REQ-synthetic-support-demo: End-to-end synthetic support ticket triage demo workflow.
- [ ] REQ-trajectory-evaluation-and-testing: Golden trajectory evaluation suite and CI release gates.

### Out of Scope

- General-purpose visual workflow builder — not required for core developer control plane.
- Arbitrary host code/shell execution — severe security risk; execution strictly bounded to registry.
- Live external side effects (real emails, payment processing) — V1 focuses on simulated/safe boundaries.
- Full multi-agent swarm orchestration — V1 prioritizes single observable workflow reliability.
- Unbounded autonomous loops — loops are strictly capped by step and wall-clock budgets.

## Context

AI agent applications in production suffer from opaque execution, in-memory state loss on crashes, duplicate side effects on retries, and inability to reproduce failures as regression tests. AgentOps provides the operational control plane to address these issues.

## Constraints

- **Tech Stack**: Python 3.11+, Pydantic, pytest, FastAPI, PostgreSQL (SQLAlchemy + Alembic), Next.js + TypeScript.
- **Typing & Linting**: Strict mypy (`strict = true`) and Ruff (88-char limit, strict formatting).
- **Safety**: Policy checks and authorization must be enforced in code outside model prompts.
- **Replay**: Replay mode must be mock-only/read-only with zero external side effects.
- **Redaction**: Credentials and secrets must never be stored in state, events, logs, or capsules.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python 3.11+ / Pydantic / FastAPI | Ecosystem maturity, strict typing, native async support, and OpenAPI documentation. | ✓ Good |
| PostgreSQL + Monotonic Sequences | Relational integrity and monotonic `(run_id, sequence_no)` constraints guarantee event order. | ✓ Good |
| Code-level Policy Gate | Prompt-based instructions are susceptible to prompt injection; authorization belongs in code. | ✓ Good |
| Mock-Only Replay | Guarantees regression testing without risking repeated external side effects. | ✓ Good |

---
*Last updated: 2026-10-22 after doc ingest*
