# Roadmap: AgentOps

## Overview

AgentOps is built across focused phases to deliver a reliable, observable developer control plane for stateful AI agent workflows. We start with the core domain state machine and bounded execution runtime, layer on durable PostgreSQL persistence and restart recovery from versioned checkpoints, build the allow-listed tool registry and policy-enforced human-in-the-loop approval gates, deliver failure capsules and evaluations, and culminate in a production-ready server and interactive web console for local testing.

## Phases

- [x] **Phase 1: Domain Models & State Machine Runtime** - In-memory workflow execution with strict state transitions and step budgets.
- [x] **Phase 2: Persisted Timeline, Checkpoints & Recovery** - Durable PostgreSQL storage, monotonic event sequence, and restart recovery.
- [x] **Phase 3: Tool Registry, Policy Gate & Approvals** - Allow-listed tools, code-level policy enforcement, and human approval pause/resume.
- [x] **Phase 4: Diagnostics, Evaluation & Support Demo** - Failure capsule export, offline mock replay, golden trajectory suite, and end-to-end support demo.
- [x] **Phase 5: Production Local Server & Web Console** - Production-ready FastAPI local server with disk persistence, demo runner routes, and an interactive frontend dashboard for browser testing.

## Phase Details

### Phase 1: Domain Models & State Machine Runtime
**Goal:** As a developer building tool-using AI workflows, I want to execute a bounded workflow with explicit state transitions and step budgets, so that I have a reliable foundation for recovery and inspection.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: STATE-01, STATE-02, STATE-03
**Plans**: 1 plan

Plans:
- [x] 01-01: Domain models, state machine, and bounded execution runtime

### Phase 2: Persisted Timeline, Checkpoints & Recovery
**Goal**: Persist execution events and checkpoints to PostgreSQL so that runs survive process restarts and restore cleanly.
**Depends on**: Phase 1
**Requirements**: PERSIST-01, PERSIST-02, PERSIST-03, PERSIST-04
**Plans**: 1 plan

Plans:
- [x] 02-01: Persistent timeline, checkpoints, and restart recovery

### Phase 3: Tool Registry, Policy Gate & Approvals
**Goal**: Restrict tool execution to allow-listed schemas with code-enforced policies, pausing before protected actions for human approval.
**Depends on**: Phase 2
**Requirements**: TOOL-01, TOOL-02, TOOL-03, HITL-01, HITL-02, HITL-03
**Plans**: 1 plan

Plans:
- [x] 03-01: Tool registry, policy gate, and human-in-the-loop approvals

### Phase 4: Diagnostics, Evaluation & Support Demo
**Goal**: Deliver failure capsule export, offline mock replay, trajectory CI evaluation, and the complete support triage demo.
**Depends on**: Phase 3
**Requirements**: DIAG-01, DIAG-02, DIAG-03, DEMO-01, API-01
**Plans**: 1 plan

Plans:
- [x] 04-01: Diagnostics, offline mock replay, trajectory CI evaluation, support triage demo, and FastAPI control API

### Phase 5: Production Local Server & Web Console
**Goal**: As a developer testing and demonstrating AgentOps locally, I want to run a production-ready server and open an interactive frontend console in my browser, so that I can submit support tickets, view live timelines, review and approve/reject protected actions, inspect redacted failure capsules, and evaluate trajectories.
**Mode**: mvp
**Depends on**: Phase 4
**Requirements**: LOCAL-01, LOCAL-02, UI-01, UI-02
**Success Criteria** (what must be TRUE):
  1. A single command starts the production-ready FastAPI server with disk SQLite database persistence and CORS enabled.
  2. The server provides dedicated demo orchestration endpoints (`/v1/demo/triage/start`, `/v1/demo/triage/{run_id}/resume`) that advance the synthetic workflow.
  3. An interactive frontend console opens in the browser, showing live run cards, status badges, monotonic event timelines, and safe projected state.
  4. The frontend UI provides an interactive review modal for pending approvals, allowing reviewers to approve or reject protected actions with server-side authorization.
  5. The frontend displays redacted Failure Capsules and one-click trajectory evaluation results.
**Plans**: 1 plan

Plans:
- [x] 05-01: Production local server, demo orchestration routes, and interactive frontend console

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Domain Models & State Machine Runtime | 1/1 | Complete | 2026-10-22 |
| 2. Persisted Timeline, Checkpoints & Recovery | 1/1 | Complete | 2026-10-22 |
| 3. Tool Registry, Policy Gate & Approvals | 1/1 | Complete | 2026-10-22 |
| 4. Diagnostics, Evaluation & Support Demo | 1/1 | Complete | 2026-10-22 |
| 5. Production Local Server & Web Console | 1/1 | Complete | 2026-10-22 |
