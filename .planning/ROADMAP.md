# Roadmap: AgentOps

## Overview

AgentOps is built across four focused phases to deliver a reliable, observable developer control plane for stateful AI agent workflows. We start with the core domain state machine and bounded execution runtime (the walking skeleton), layer on durable PostgreSQL persistence and restart recovery from versioned checkpoints, build the allow-listed tool registry and policy-enforced human-in-the-loop approval gates, and culminate with redacted failure capsules, offline mock replay, and the full synthetic support triage demo.

## Phases

- [x] **Phase 1: Domain Models & State Machine Runtime** - In-memory workflow execution with strict state transitions and step budgets.
- [ ] **Phase 2: Persisted Timeline, Checkpoints & Recovery** - Durable PostgreSQL storage, monotonic event sequence, and restart recovery.
- [ ] **Phase 3: Tool Registry, Policy Gate & Approvals** - Allow-listed tools, code-level policy enforcement, and human approval pause/resume.
- [ ] **Phase 4: Diagnostics, Evaluation & Support Demo** - Failure capsule export, offline mock replay, golden trajectory suite, and end-to-end support demo.

## Phase Details

### Phase 1: Domain Models & State Machine Runtime
**Goal:** As a developer building tool-using AI workflows, I want to execute a bounded workflow with explicit state transitions and step budgets, so that I have a reliable foundation for recovery and inspection.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: STATE-01, STATE-02, STATE-03
**Success Criteria** (what must be TRUE):
  1. A workflow run can be initialized in `CREATED` state and advance through legal transitions to `RUNNING`, `PAUSED`, `SUCCEEDED`, `FAILED`, and `CANCELLED`.
  2. Illegal state transitions and transitions from terminal states immediately fail with explicit domain errors.
  3. Execution step limits and timeouts cleanly halt execution and transition the run to `FAILED` with a `BUDGET_EXCEEDED` error code.
**Plans**: 1 plan

Plans:
- [x] 01-01: Domain models, state machine, and bounded execution runtime

### Phase 2: Persisted Timeline, Checkpoints & Recovery
**Goal**: Persist execution events and checkpoints to PostgreSQL so that runs survive process restarts and restore cleanly.
**Depends on**: Phase 1
**Requirements**: PERSIST-01, PERSIST-02, PERSIST-03, PERSIST-04
**Success Criteria** (what must be TRUE):
  1. Every execution fact is recorded as an immutable event with a monotonic sequence number `(run_id, sequence_no)`.
  2. Versioned checkpoints save serializable state at safe node boundaries.
  3. A fresh process can restore an in-flight run from a checkpoint and resume execution without data loss.
**Plans**: TBD

### Phase 3: Tool Registry, Policy Gate & Approvals
**Goal**: Restrict tool execution to allow-listed schemas with code-enforced policies, pausing before protected actions for human approval.
**Depends on**: Phase 2
**Requirements**: TOOL-01, TOOL-02, TOOL-03, HITL-01, HITL-02, HITL-03
**Success Criteria** (what must be TRUE):
  1. Only registered tools with schema validation can execute; unknown or unauthorized tools fail closed.
  2. Workflows automatically transition to `PAUSED` when a protected action requires human approval.
  3. Approvals are checked server-side for authorization, and rejected actions guarantee the protected tool never executes.
**Plans**: TBD

### Phase 4: Diagnostics, Evaluation & Support Demo
**Goal**: Deliver failure capsule export, offline mock replay, trajectory CI evaluation, and the complete support triage demo.
**Depends on**: Phase 3
**Requirements**: DIAG-01, DIAG-02, DIAG-03, DEMO-01, API-01
**Success Criteria** (what must be TRUE):
  1. Failed runs export redacted Failure Capsules with credentials and secrets stripped.
  2. Offline mock replay reproduces the execution trajectory with zero external network requests.
  3. Golden trajectory evaluations run in CI and catch skipped safety or approval steps.
  4. The synthetic support triage demo executes end-to-end via FastAPI endpoints with idempotent create operations.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Domain Models & State Machine Runtime | 1/1 | Complete | 2026-10-22 |
| 2. Persisted Timeline, Checkpoints & Recovery | 0/1 | Not started | - |
| 3. Tool Registry, Policy Gate & Approvals | 0/1 | Not started | - |
| 4. Diagnostics, Evaluation & Support Demo | 0/1 | Not started | - |
