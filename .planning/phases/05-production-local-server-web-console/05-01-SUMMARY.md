---
phase: 05-production-local-server-web-console
plan: 01
subsystem: local-server-and-ui
tags: [server, cli, uvicorn, fastapi, web-console, tailwind, hitl-modal, triage-demo]

requires:
  - phase: 04-diagnostics-evaluation-support-demo
    provides: FastAPI control API, Failure Capsules, TrajectoryEvaluator, SupportTriageWorkflow
provides:
  - "Production-ready local server runner with CLI entry point `agentops` and `python -m agent_ops`"
  - "Disk SQLite database persistence (`sqlite:///agent_ops.db`) and CORS middleware"
  - "Demo orchestration endpoints (`/v1/demo/triage/start` and `/v1/demo/triage/{run_id}/resume`)"
  - "Embedded, responsive Tailwind dark-mode web console served directly at `http://127.0.0.1:8000/` and `/console`"
  - "Interactive Human-in-the-Loop approval gate modal allowing reviewers to approve/reject protected actions in the browser"
  - "Live run inspector, monotonic event timeline viewer, safe projected state viewer, failure capsule exporter, and trajectory evaluator"
affects: []

actuals:
  tokens: 24000
  tasks: 2
  commits: 2

tech-stack:
  added: [uvicorn[standard]>=0.30]
  patterns: [Embedded single-page console, CLI server runner, Demo orchestration endpoints, CORS-enabled REST API]

key-files:
  created:
    - src/agent_ops/main.py
    - src/agent_ops/__main__.py
    - src/agent_ops/api/static/index.html
    - tests/integration/test_demo_routes.py
    - tests/integration/test_web_console.py
    - tests/unit/test_cli.py
  modified:
    - pyproject.toml
    - uv.lock
    - src/agent_ops/api/app.py
    - src/agent_ops/api/routes.py
    - src/agent_ops/api/schemas.py

key-decisions:
  - "Serve the interactive web console directly from the FastAPI application at `/` and `/console` so testing requires zero extra frontend build steps or separate node processes"
  - "Use SQLite disk persistence (`agent_ops.db`) by default with automatic schema initialization on startup"
  - "Enable full CORS middleware (`allow_origins=['*']`) to support external React/Next.js frontends or local browser fetch calls"
  - "Add dedicated demo orchestration routes (`/v1/demo/triage/start` and `/v1/demo/triage/{run_id}/resume`) that coordinate workflow progression, approval pauses, and resumption"

patterns-established:
  - "One-click preset triage testing in browser (Billing issue, Technical crash, General inquiry)"
  - "Real-time human-in-the-loop review card with server-side authorization role check (reviewer, admin, guest)"

requirements-completed:
  - LOCAL-01
  - LOCAL-02
  - UI-01
  - UI-02

coverage:
  - id: D1
    description: "Production server launcher with disk persistence, CORS, and CLI arguments"
    requirement: "LOCAL-01"
    verification:
      - kind: unit
        ref: "tests/unit/test_cli.py"
        status: pass
  - id: D2
    description: "Support triage demo orchestration endpoints with pause and resume"
    requirement: "LOCAL-02"
    verification:
      - kind: integration
        ref: "tests/integration/test_demo_routes.py"
        status: pass
  - id: D3
    description: "Embedded responsive web console dashboard with live runs, timeline, and state"
    requirement: "UI-01"
    verification:
      - kind: integration
        ref: "tests/integration/test_web_console.py"
        status: pass
  - id: D4
    description: "Interactive Human-in-the-Loop review gate modal, failure capsule exporter, and trajectory evaluator in browser"
    requirement: "UI-02"
    verification:
      - kind: integration
        ref: "tests/integration/test_web_console.py"
        status: pass
---

# Phase 5 Plan 01 Summary: Production Local Server & Web Console

Delivered the local production server and embedded interactive web console dashboard, allowing developers to test and demonstrate AgentOps immediately in their browser.

## Accomplishments

1. **Production-Ready Local Server Runner (`LOCAL-01`):**
   - Configured `uvicorn[standard]` and added CLI entry point `agentops` (`python -m agent_ops` or `uv run python -m agent_ops`).
   - Defaulted to persistent SQLite storage on disk (`agent_ops.db`) with automatic table initialization on startup.
   - Enabled `CORSMiddleware` for seamless cross-origin and browser interactions.
   - Provided rich startup banner with navigable URLs for the Web Console, Swagger Docs, and Redoc.

2. **Demo Orchestration Endpoints (`LOCAL-02`):**
   - Implemented `POST /v1/demo/triage/start`: initializes a support ticket run, registers allow-listed tools, advances through classification and customer lookup to draft creation, evaluates policy, and pauses at the T2 approval gate.
   - Implemented `POST /v1/demo/triage/{run_id}/resume`: checks reviewer decision, executes simulated email delivery (if approved) and transitions to `SUCCEEDED`, or cancels and guarantees protected action never runs (if rejected).

3. **Interactive Web Console Dashboard (`UI-01`, `UI-02`):**
   - Embedded a dark-mode responsive dashboard at `http://127.0.0.1:8000/` and `/console`.
   - **Ticket Launcher:** Preset buttons for Billing Refund, App Crash, and General Inquiry with instant one-click workflow launch.
   - **Runs Table:** Live run status badges (`CREATED`, `RUNNING`, pulsing `PAUSED`, `SUCCEEDED`, `FAILED`, `CANCELLED`).
   - **Event Timeline:** Ordered monotonic sequence cards (`#1`, `#2`, `#3`...) displaying node events, tool executions, and payloads.
   - **State Inspector:** Live JSON state tree with highlighted `[REDACTED]` credentials.
   - **Interactive HITL Approval Gate Modal:** Alerts reviewer when workflow pauses, presents draft email preview, allows reviewer role selection (`reviewer`, `admin`, `guest`), and provides one-click Approve & Send or Reject & Block actions.
   - **Diagnostics & Evaluator:** One-click Failure Capsule export modal and CI Trajectory Safety evaluation runner.

## Verification Results

- All 63 tests passing (`pytest`) across unit and integration suites
- **95%** overall code coverage across the entire project (`pytest-cov`)
- Strict type checking clean (`mypy`) with zero errors across all 32 modules
- Strict linting and formatting clean (`ruff`)
