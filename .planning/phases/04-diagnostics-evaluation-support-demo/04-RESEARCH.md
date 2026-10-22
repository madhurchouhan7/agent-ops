# Phase 4: Diagnostics, Evaluation & Support Demo - Research

## Executive Summary

Phase 4 completes the AgentOps MVP by delivering the observability, diagnostic, and interface surfaces:
1. **Redacted Failure Capsules (`DIAG-01`):** Diagnostic bundles exported upon run failure that recursively scrub API keys, tokens, passwords, and sensitive credentials across states, events, and checkpoints.
2. **Offline Mock Replay (`DIAG-02`):** Pure offline replay engine that reconstructs workflow execution from recorded tool outputs with zero external network requests or side effects.
3. **Golden Trajectory CI Evaluation (`DIAG-03`):** Trajectory evaluation suite that asserts strict ordering, intermediate state invariants, and policy adherence (e.g., catching skipped human approvals).
4. **Synthetic Support Triage Demo (`DEMO-01`):** An end-to-end runnable support triage workflow exercising the full control plane (classification, customer lookup, draft generation, HITL approval gate, and simulated delivery).
5. **FastAPI Control Endpoints (`API-01`):** REST API control plane providing idempotent run creation, timeline queries, state projection, approval decision dispatch, failure capsule export, and evaluation execution.

---

## 1. Failure Capsule Export & Recursive Redaction

### Requirements
- Export a portable, versioned JSON document whenever a workflow fails (`DIAG-01`).
- Completely redact all credentials, authorization headers, API keys, passwords, and secrets before exporting or persisting.

### Architecture
- **Redaction Engine (`agent_ops.diagnostics.redactor`):**
  - Case-insensitive key matching against sensitive terms: `api_key`, `token`, `secret`, `password`, `auth`, `authorization`, `cookie`, `access_token`, `private_key`.
  - Regex pattern matching against string values: `(?i)bearer\s+[a-z0-9_\-\.]+`, `sk-[a-zA-Z0-9]{20,}`, `ghp_[a-zA-Z0-9]{36}`.
  - Recursive scrubbing over nested dicts, lists, tuples, and primitives.
- **Failure Capsule Schema (`agent_ops.diagnostics.capsule`):**
  ```python
  class FailureCapsule(BaseModel):
      capsule_version: str = "1.0"
      run_id: str
      workflow_id: str
      workflow_version: str
      error_code: str
      error_message: str | None = None
      created_at: datetime
      failed_at: datetime
      timeline: list[dict[str, Any]]
      checkpoints: list[dict[str, Any]]
      final_state: dict[str, Any]
      redacted: bool = True
  ```

### Pitfalls & Mitigations
- *Trap:* Shallow redaction only checks top-level keys in event payloads, leaving secrets exposed in nested tool arguments or nested state dicts.
  *Mitigation:* Deep recursive traversal with a maximum depth limit (e.g., 20) and circular reference protection.
- *Trap:* Exporting capsules for non-failed runs.
  *Mitigation:* Verify `run.status == RunStatus.FAILED` or raise an explicit error (`AgentOpsError("Run is not in FAILED state", error_code="INVALID_RUN_STATE")`).

---

## 2. Offline Mock Replay Runner

### Requirements
- Execute recorded outputs without making any external network requests or side effects (`DIAG-02`).
- Verify that recorded tool outcomes deterministically reproduce the state machine sequence.

### Architecture
- **MockReplayRunner (`agent_ops.diagnostics.replay`):**
  - Accepts a `FailureCapsule` or a recorded run timeline.
  - Extracts the sequence of node executions and tool results from the events.
  - Replays node transitions by injecting recorded tool results into node actions rather than invoking external handlers or networks.
  - Compares replayed state at each step against recorded checkpoints.
  - Enforces network isolation: if any step attempts a real network call or unregistered side effect, replay immediately halts and flags a replay divergence.

---

## 3. Golden Trajectory Evaluation

### Requirements
- Evaluate intermediate states, tool invocations, and policy adherence in CI (`DIAG-03`).
- Detect skipped safety checks or human approvals.

### Architecture
- **Trajectory Evaluator (`agent_ops.evaluations.evaluator`):**
  - `TrajectoryRule`:
    - `required_nodes: list[str]` (must execute in specified sequence)
    - `forbidden_nodes: list[str]` (e.g. nodes that should not execute on failure)
    - `safety_invariants`:
      - "If tool with `risk_tier == T2` is invoked, an `approval.approved` event MUST occur prior to invocation."
      - "No transition to `SUCCEEDED` if unapproved protected actions exist."
  - Evaluates `RunEventModel` timeline against rules and produces a structured `EvaluationResult`:
    ```python
    class EvaluationResult(BaseModel):
        run_id: str
        passed: bool
        score: float  # 0.0 to 1.0
        violations: list[str] = Field(default_factory=list)
        evaluated_rules: int = 0
    ```

---

## 4. Synthetic Support Triage Demo

### Requirements
- Complete runnable workflow (`DEMO-01`):
  1. Ticket submitted (`input`: customer message, ticket ID).
  2. Classified (`T0` tool: sentiment, category).
  3. Customer looked up (`T1` tool: customer tier, account status).
  4. Reply drafted (`T0` tool: drafted response).
  5. Paused for approval (`T2` tool: `send_customer_reply` triggers `PolicyGate` -> `ApprovalService.request_approval` -> `RunStatus.PAUSED`).
  6. Human reviewer submits decision.
  7. If approved: resumes -> simulated reply delivered -> completes (`RunStatus.SUCCEEDED`).
  8. If rejected: resumes -> reply cancelled -> completes (`RunStatus.CANCELLED`).

---

## 5. FastAPI Control API

### Requirements
- REST endpoints covering runs, events, state, approvals, failure capsules, and evaluations (`API-01`).
- Idempotency support for run creation using an `idempotency_key`.
- Header-based simulated authentication/authorization (`X-Actor`, `X-Actor-Roles`).

### Endpoints
- `POST /v1/runs`: Create and start run (idempotent).
- `GET /v1/runs`: List runs.
- `GET /v1/runs/{run_id}`: Get run summary.
- `GET /v1/runs/{run_id}/events`: Get run event timeline.
- `GET /v1/runs/{run_id}/state`: Get safe projected state.
- `POST /v1/runs/{run_id}/pause`: Pause run.
- `POST /v1/runs/{run_id}/resume`: Resume run.
- `POST /v1/runs/{run_id}/cancel`: Cancel run.
- `GET /v1/approvals`: List pending approvals.
- `POST /v1/approvals/{approval_id}/decision`: Submit approval decision (`X-Actor`, `X-Actor-Roles`).
- `POST /v1/runs/{run_id}/failure-capsule`: Export redacted failure capsule.
- `POST /v1/evaluations/run`: Evaluate run trajectory against golden rules.
