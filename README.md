# AgentOps

**A reliable, observable developer control plane for stateful AI workflows.**

AgentOps provides explicit state machines, monotonic event sequencing, durable checkpoints with crash recovery, allow-listed tool execution with risk tiers, server-side human-in-the-loop (HITL) approval gates, recursive credential redaction in failure capsules, offline mock replay, and an interactive agentic node canvas console.

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
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Production Deployment with Docker

AgentOps includes an enterprise-grade multi-stage `Dockerfile` and `docker-compose.yml` pre-configured with PostgreSQL:

```bash
# Build and start AgentOps with PostgreSQL
docker compose up -d --build

# View container logs
docker compose logs -f agentops

# Health status
curl http://localhost:8000/health
```

---

## Database Migrations (Alembic)

AgentOps uses Alembic to manage database schema migrations across environments:

```bash
# Run migrations up to latest version
uv run python -m alembic upgrade head

# Rollback to previous version
uv run python -m alembic downgrade -1

# Create a new migration revision
uv run python -m alembic revision --autogenerate -m "add new table"
```

---

## Interactive Agentic Web Console

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser to experience the **VoltAgent** and **n8n agentic workflow interface**:

1. **Infinite Dot-Grid Canvas:**
   - Smooth pan & zoom controls (`+`, `-`, `Fit`, `100%`).
   - 7 connected workflow nodes:
     - `Customer Ticket Trigger` (Inbound payload)
     - `classify_ticket` (T0 Tool: category & sentiment)
     - `lookup_customer` (T1 Tool: CRM lookup)
     - `draft_reply` (T0 LLM Tool: response drafting)
     - `HITL Policy Gate` (T2 Guardrail: human review required)
     - `send_customer_reply` (T2 Protected Tool: simulated dispatch)
     - `SUCCEEDED` (Terminal Outcome)
   - Dynamic curved bezier connection lines that animate active data flow.

2. **One-Click Presets & Test Workflow:**
   - 💳 **Double Charge Refund** (triggers billing classification & high-urgency reply)
   - 💥 **App Crash on Save** (triggers technical bug triage workflow)
   - ❓ **General Query** (triggers customer statement workflow)

3. **Human-in-the-Loop Review Gate:**
   - The workflow pauses automatically at the `HITL Policy Gate` before executing protected mutations (`send_customer_reply`).
   - An authorization modal displays the proposed response preview, customer details, and policy rationale.
   - Authorize with role (`reviewer` or `admin`) to approve and deliver, or reject to halt execution without side effects.

4. **Collapsible Bottom Drawer:**
   - **Event Timeline:** Ordered monotonic execution events (`#1`, `#2`, `#3`...).
   - **Node Inspector:** Click any canvas node to inspect its specific inputs and projected outputs with automatic masking indicators.
   - **Execution State:** Inspect the full serialized workflow state.
   - **Safety Invariants & Capsule:** Run Golden Trajectory evaluations with a single click and export sanitized failure capsules.

---

## CLI Options

```bash
# Custom host and port
uv run agentops --host 0.0.0.0 --port 8080

# Connect to a PostgreSQL database
uv run agentops --db "postgresql+psycopg://user:pass@localhost:5432/agentops"

# Enable auto-reload on code change
uv run agentops --reload
```

---

## REST Control API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | System health check (database ping & version) |
| `GET`  | `/v1/health` | Comprehensive observability & uptime check |
| `POST` | `/v1/runs` | Create a new run (supports `idempotency_key`) |
| `GET`  | `/v1/runs` | List runs with optional `workflow_id` & `status` filters |
| `GET`  | `/v1/runs/{id}` | Get run summary and status |
| `GET`  | `/v1/runs/{id}/events` | Get ordered monotonic event timeline |
| `GET`  | `/v1/runs/{id}/state` | Get safe, redacted state projection |
| `POST` | `/v1/runs/{id}/pause` | Pause an active run at a safe boundary |
| `POST` | `/v1/runs/{id}/resume` | Resume execution of a paused run |
| `POST` | `/v1/runs/{id}/cancel` | Cancel an active or paused run |
| `GET`  | `/v1/approvals` | List pending approval requests |
| `POST` | `/v1/approvals/{id}/decision` | Submit decision (`X-Actor`, `X-Actor-Roles: reviewer`) |
| `POST` | `/v1/runs/{id}/failure-capsule` | Export redacted diagnostic failure capsule |
| `POST` | `/v1/evaluations/run` | Run golden trajectory safety assertions on a run |
| `POST` | `/v1/demo/triage/start` | Launch support triage demo to approval gate |
| `POST` | `/v1/demo/triage/{id}/resume` | Resume demo run following approval decision |

---

## Verification & Testing

AgentOps includes a comprehensive test suite with **96% code coverage**, strict type safety (`strict = true`), and zero live network dependencies:

```bash
# Run all unit and integration tests with coverage
uv run pytest --cov=agent_ops

# Run strict type checking
uv run mypy src

# Lint and check formatting
uv run ruff check .
uv run ruff format --check .

# Build distributable wheel package
uv build
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
├── services/          # Idempotency store, RunService, and EventBus
└── api/               # FastAPI application, control plane REST routes, and web console static files
alembic/               # Database migrations environment and versioned migration scripts
```
