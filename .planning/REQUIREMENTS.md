# Requirements: AgentOps

**Defined:** 2026-10-22  
**Core Value:** Deterministic, observable execution with explicit state transitions, durable checkpoints for restart recovery, and code-enforced human-in-the-loop safety gates.

## v1 Requirements

### Runtime and State Machine
- [x] **STATE-01**: Explicit workflow state machine with states CREATED, RUNNING, PAUSED, SUCCEEDED, FAILED, and CANCELLED.
- [x] **STATE-02**: Transitions are validated against the workflow definition; invalid transitions and transitions from terminal states raise explicit domain errors.
- [x] **STATE-03**: Maximum step counter and execution wall-clock budgets strictly prevent runaway execution.

### Persistence and Recovery
- [x] **PERSIST-01**: Every execution fact is recorded as an immutable event with a unique monotonic sequence number `(run_id, sequence_no)`.
- [x] **PERSIST-02**: Versioned checkpoints record serializable workflow state at safe boundaries.
- [x] **PERSIST-03**: A fresh process can restore from a saved checkpoint and continue execution cleanly.
- [x] **PERSIST-04**: PostgreSQL durable storage layer with SQLAlchemy models and Alembic migrations.

### Tools and Policy Gate
- [x] **TOOL-01**: Allow-listed tool registry with strict input/output schemas and execution timeouts.
- [x] **TOOL-02**: Policy gate enforces tool permissions, argument validation, and risk tiers (T0-T3) in code before invocation.
- [x] **TOOL-03**: Unknown, unauthorized, or malformed tool invocations fail closed without crashing the runtime.

### Human-in-the-Loop Approvals
- [x] **HITL-01**: Workflow automatically pauses before executing protected actions (e.g., simulated `send_reply`) and persists an approval request.
- [x] **HITL-02**: Server-side authorization check ensures only authorized reviewers can approve or reject pending actions.
- [x] **HITL-03**: Paused runs cannot advance without an explicit decision; rejected actions guarantee the protected action never executes.

### Diagnostics and Evaluation
- [x] **DIAG-01**: Export versioned Failure Capsules on run failure with credentials and secrets completely redacted.
- [x] **DIAG-02**: Offline mock replay executes recorded outputs without making any external network requests or side effects.
- [x] **DIAG-03**: Golden trajectory evaluation suite runs in CI to verify intermediate states, tool invocations, and policy adherence.

### Demo and Control API
- [x] **DEMO-01**: End-to-end runnable support triage workflow: ticket submitted -> classified -> ticket looked up -> reply drafted -> paused for approval -> simulated reply sent -> completed.
- [x] **API-01**: FastAPI control endpoints for runs, events, checkpoints, approvals, and failure capsules with idempotent operations.

### Modern Frontend & Landing Page (Phase 6)
- [x] **UI-VERTEX-01**: High-fidelity Vertex-style monochrome landing page featuring dynamic hero agent run cards, cross-grid corner marks, partner marquee, interactive bento feature cards, metrics counters, side-by-side pricing matrix, collapsible FAQ accordion, and concentric glow CTA.
- [x] **UI-CONSOLE-01**: Sleek black & white interactive React console with live runs, step budgets, monotonic event timeline, policy gate approvals, failure capsules, and evaluation triggers.
- [x] **UI-INTEG-01**: Modern React + Vite + Tailwind CSS + Framer Motion setup with rich animations, seamless proxying to FastAPI backend, and production static build.

## v2 Requirements
- **V2-01**: General-purpose visual workflow builder in Next.js console.
- **V2-02**: Distributed durable execution with Temporal or multi-worker queues.
- **V2-03**: Multi-tenant enterprise workspaces and RBAC policies.
- **V2-04**: Broad MCP server client integration.

## Out of Scope
| Feature | Reason |
|---------|--------|
| Arbitrary host code/shell execution | Critical security risk; V1 executes only allow-listed tools. |
| Live external side effects | V1 uses simulated actions to prevent accidental real-world side effects. |
| Multi-agent swarm orchestration | Focus is on single-workflow reliability, observability, and recovery first. |
| Unbounded autonomous loops | Loops must be bounded by step and wall-clock budgets. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| STATE-01 | Phase 1 | Complete |
| STATE-02 | Phase 1 | Complete |
| STATE-03 | Phase 1 | Complete |
| PERSIST-01 | Phase 2 | Complete |
| PERSIST-02 | Phase 2 | Complete |
| PERSIST-03 | Phase 2 | Complete |
| PERSIST-04 | Phase 2 | Complete |
| TOOL-01 | Phase 3 | Complete |
| TOOL-02 | Phase 3 | Complete |
| TOOL-03 | Phase 3 | Complete |
| HITL-01 | Phase 3 | Complete |
| HITL-02 | Phase 3 | Complete |
| HITL-03 | Phase 3 | Complete |
| DIAG-01 | Phase 4 | Complete |
| DIAG-02 | Phase 4 | Complete |
| DIAG-03 | Phase 4 | Complete |
| DEMO-01 | Phase 4 | Complete |
| API-01 | Phase 4 | Complete |
| UI-VERTEX-01 | Phase 6 | Complete |
| UI-CONSOLE-01 | Phase 6 | Complete |
| UI-INTEG-01 | Phase 6 | Complete |
