# AgentOps

**A reliable, observable developer control plane for stateful AI workflows.**

AgentOps provides explicit state machines, monotonic event sequencing, durable checkpoints with crash recovery, allow-listed tool execution with risk tiers, server-side human-in-the-loop (HITL) approval gates, recursive credential redaction in failure capsules, offline mock replay, and an interactive web console.

---

## Quick Start (Run Locally)

Start the production-ready server and interactive web console with a single command:

```bash
uv run python -m agent_ops
```
*(or using the installed CLI entry point: `uv run agentops`)*

This starts the FastAPI server with disk persistence (`agent_ops.db`) and opens access to:
- **Interactive Web Console:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger Interactive API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Reference:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Testing in the Web Console

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser:

1. **Launch a Support Ticket:**
   - Click one of the preset buttons:
     - 💳 **Double Charge Refund** (triggers billing classification & high-urgency reply)
     - 💥 **App Crash on Save** (triggers technical bug workflow)
     - ❓ **Invoice History** (triggers general query)
   - Click **"Launch Triage Workflow"**.

2. **Observe the Approval Gate:**
   - The workflow executes steps (`classify`, `lookup_customer`, `draft_reply`) and automatically transitions to **`PAUSED`** before executing the protected `send_customer_reply` action (`T2` risk tier).
   - The **Human-in-the-Loop Review Banner** appears with the proposed email preview, customer recipient, and policy rule.

3. **Approve or Reject:**
   - Select reviewer identity (`alice_lead`) and role (`reviewer`).
   - Click **"Approve & Send Reply"**: resumes execution, delivers simulated reply, and marks the run **`SUCCEEDED`**.
   - Or click **"Reject & Block Tool"**: cancels the run, strictly guarantees the protected tool never executes, and marks the run **`CANCELLED`**.

4. **Inspect Execution Timeline & Projected State:**
   - **Event Timeline:** View ordered execution events (`#1`, `#2`, `#3`...) with full monotonic sequence numbers.
   - **Projected State:** View safe state with sensitive credentials (`api_key`, `token`, `password`) automatically scrubbed and displayed as `[REDACTED]`.

5. **Diagnostics & CI Evaluations:**
   - Click **"Run Trajectory CI Safety Suite"** to verify that intermediate states, ordering, and human approval invariants were honored.
   - For failed runs, click **"Export Redacted Capsule"** to inspect a self-contained, sanitized failure capsule.

---

## CLI Options

```bash
# Custom host and port
uv run agentops --host 0.0.0.0 --port 8080

# Connect to a PostgreSQL database
uv run agentops --db "postgresql+psycopg2://user:pass@localhost:5432/agentops"

# Enable auto-reload on code change
uv run agentops --reload
```

---

## REST Control API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/runs` | Create a new run (supports `idempotency_key`) |
| `GET` | `/v1/runs` | List runs with optional `workflow_id` & `status` filters |
| `GET` | `/v1/runs/{id}` | Get run summary and status |
| `GET` | `/v1/runs/{id}/events` | Get ordered monotonic event timeline |
| `GET` | `/v1/runs/{id}/state` | Get safe, redacted state projection |
| `POST` | `/v1/runs/{id}/pause` | Pause an active run at a safe boundary |
| `POST` | `/v1/runs/{id}/resume` | Resume execution of a paused run |
| `POST` | `/v1/runs/{id}/cancel` | Cancel an active or paused run |
| `GET` | `/v1/approvals` | List pending approval requests |
| `POST` | `/v1/approvals/{id}/decision` | Submit decision (`X-Actor`, `X-Actor-Roles: reviewer`) |
| `POST` | `/v1/runs/{id}/failure-capsule` | Export redacted diagnostic failure capsule |
| `POST` | `/v1/evaluations/run` | Run golden trajectory safety assertions on a run |
| `POST` | `/v1/demo/triage/start` | Launch support triage demo to approval gate |
| `POST` | `/v1/demo/triage/{id}/resume` | Resume demo run following approval decision |

---

## Verification & Testing

AgentOps includes a test suite with **95% code coverage**, strict type safety (`strict = true`), and zero live network dependencies:

```bash
# Run all unit and integration tests with coverage
uv run pytest --cov=agent_ops

# Run strict type checking
uv run mypy

# Lint and check formatting
uv run ruff check .
uv run ruff format --check .
```

---

## Architecture

```
src/agent_ops/
├── domain/            # Core state machine, models (Run, RunStatus), budgets, and errors
├── runtime/           # Step execution runtime and wall-clock timeout enforcement
├── storage/           # SQLAlchemy models, EventRepository, CheckpointService, RecoveryService
├── tools/             # Allow-listed ToolRegistry, Pydantic schemas, and PolicyGate (T0-T3)
├── diagnostics/       # RedactionEngine, FailureCapsule export, and MockReplayRunner
├── evaluations/       # TrajectoryEvaluator for CI safety and invariant checking
├── workflows/         # End-to-end runnable SupportTriageWorkflow demonstration
└── api/               # FastAPI application, control plane REST routes, and web console static files
```
