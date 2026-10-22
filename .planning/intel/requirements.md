# Synthesized Requirements

## REQ-runtime-state-machine
- source: docs/01-mvp-contract.md
- description: Explicit workflow runtime and state machine with bounded step execution.
- acceptance: Lifecycle states CREATED, RUNNING, PAUSED, SUCCEEDED, FAILED, CANCELLED supported. Transitions validated against workflow definition. Terminal states cannot be resumed. Legal transitions succeed; illegal transitions are rejected. Maximum step counter and wall-clock budgets enforced.
- scope: Workflow Runtime, State Machine, Step Budgets, Lifecycle States

## REQ-persisted-timeline-and-checkpoints
- source: docs/01-mvp-contract.md
- description: Ordered event timeline and versioned checkpoints saved at safe boundaries.
- acceptance: Every execution fact recorded as an event with monotonic sequence_no per run and unique constraint (run_id, sequence_no). Checkpoints contain serializable state versioned and saved at safe boundaries. A fresh process can restore a checkpoint and continue execution.
- scope: Event Timeline, Monotonic Sequence, Checkpoint Service, Restart Recovery

## REQ-tool-registry-and-policy-gate
- source: docs/01-mvp-contract.md
- description: Allow-listed tool registry with strict schemas and code-level policy enforcement.
- acceptance: Model output cannot invoke arbitrary functions/imports. Tools registered with schemas, timeouts, risk tiers (T0-T3). Policy gate enforces authorization and arguments validation before tool execution. Unknown/unauthorized tools fail closed.
- scope: Tool Registry, Policy Gate, Schema Validation, Risk Tiers

## REQ-hitl-pause-and-approval
- source: docs/01-mvp-contract.md
- description: Pause before protected actions requiring human approval and resume upon authorization.
- acceptance: Workflow automatically transitions to PAUSED when a protected action (e.g. send_reply) requires approval. Approval request persisted with action details. Authorized reviewer can approve or reject. Approval survives process restart. Rejection guarantees protected action is never executed. Paused run cannot advance without valid decision.
- scope: Human-in-the-Loop, Pause/Resume, Approval Inbox, Reviewer Authorization

## REQ-failure-capsule-and-mock-replay
- source: docs/01-mvp-contract.md
- description: Export redacted failure capsules and offline replay without side effects.
- acceptance: On failure, export versioned failure capsule. Seeded credentials/secrets are completely redacted. Offline mock replay reproduces the execution trajectory using recorded outputs without making any external network requests.
- scope: Failure Capsule, Redaction, Offline Mock Replay

## REQ-control-api-and-storage
- source: docs/01-mvp-contract.md
- description: FastAPI control plane endpoints backed by PostgreSQL durable storage.
- acceptance: Endpoints for runs (create, get, list, pause, resume, cancel), events (ordered timeline), approvals (list, decide), and capsule export. Duplicate creates with same idempotency key return identical run without duplicate execution. Errors return stable codes without leaking tracebacks or credentials.
- scope: FastAPI, REST API, PostgreSQL, SQLAlchemy, Idempotency

## REQ-synthetic-support-demo
- source: docs/01-mvp-contract.md
- description: End-to-end runnable synthetic support ticket triage demo workflow.
- acceptance: Ticket submitted -> categorized -> lookup_ticket called -> suggested reply drafted -> paused for approval before send_reply -> approved -> simulated send completes run -> timeline and state viewable.
- scope: Support Triage Demo, Synthetic Fixtures, End-to-End Execution

## REQ-trajectory-evaluation-and-testing
- source: docs/01-mvp-contract.md
- description: Trajectory testing and safety verification gates.
- acceptance: Golden trajectory tests verify intermediate steps, tool calls, and policy compliance. Critical assertions run in CI. Unit, integration, fault-injection, and security tests pass before release.
- scope: Golden Trajectories, Evaluation Suite, CI Release Gates
