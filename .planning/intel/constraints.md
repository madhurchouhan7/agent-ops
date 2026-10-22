# Synthesized Constraints

## Architecture and Trust Boundaries
- source: docs/05-architecture.md
- type: protocol
- content: Architecture layers: Web Console -> FastAPI Control API -> Auth/Policy Gate -> Workflow Runtime -> Graph/State Machine -> Tool Policy Gate -> Allow-listed Tool Registry -> Adapters. Checkpoint & Event services persist to PostgreSQL. Trust boundaries: client to API, API to runtime, model output to tool registry, tool result to runtime, application to database. All external inputs, tool outputs, and model outputs are untrusted.

## Relational Schema Contracts
- source: docs/08-data-model.md
- type: schema
- content: Core entities: `runs` (id, workspace_id, workflow_id, workflow_version, status, current_node, input_json, state_json, state_version, attempt, step_count, idempotency_key, timestamps, error_code); `run_events` (id, run_id, sequence_no, event_type, node_id, payload_json, created_at, unique run_id + sequence_no); `checkpoints` (id, run_id, sequence_no, schema_version, state_json, created_at); `tool_calls` (id, run_id, event_sequence, tool_name, tool_version, arguments, result, status, timestamps, duration); `approvals` (id, run_id, action_summary, status [pending/approved/rejected/expired], policy_reason, decision_actor, timestamps); `evaluations` (id, suite_name, workflow_version, case_id, pass_flag, metrics).

## REST API Contracts
- source: docs/09-api-design.md
- type: api-contract
- content: Endpoints: POST /v1/runs, GET /v1/runs, GET /v1/runs/{run_id}, GET /v1/runs/{run_id}/events, GET /v1/runs/{run_id}/state, POST /v1/runs/{run_id}/pause, POST /v1/runs/{run_id}/resume, POST /v1/runs/{run_id}/cancel, GET /v1/approvals, POST /v1/approvals/{approval_id}/decision, POST /v1/runs/{run_id}/failure-capsule, POST /v1/evaluations, GET /v1/evaluations/{evaluation_id}. Stable error codes: RUN_NOT_FOUND, INVALID_TRANSITION, APPROVAL_REQUIRED, POLICY_DENIED, VERSION_CONFLICT.

## Runtime Invariants and Safety Rules
- source: docs/11-runtime-rules.md
- type: nfr
- content: 1. One status and one current node per run. 2. Every transition validated. 3. SUCCEEDED, FAILED, CANCELLED are terminal. 4. PAUSED cannot advance without valid decision. 5. Bounded step budgets and bounded retries. 6. Unknown/unauthorized tools fail closed. 7. Monotonic event sequence per run. 8. Checkpoints versioned and serializable. 9. Credentials never stored in state, events, logs, or capsules. 10. Replay makes zero external calls.

## Security Threat Mitigation and Risk Tiers
- source: docs/10-security-and-threat-model.md
- type: nfr
- content: Tool risk tiers: T0 (local deterministic fixtures), T1 (read-only external query), T2 (reversible write, approval/idempotency required), T3 (high-impact/irreversible, disabled in V1). All tool calls verified server-side outside model prompts.
