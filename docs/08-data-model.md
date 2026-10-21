# Data Model

Planned conceptual schema; actual migrations become authoritative once implemented.

## `runs`
`id`, `workspace_id`, `workflow_id`, `workflow_version`, `status`, `current_node`, `input_json`, `state_json`, `state_version`, `attempt`, `step_count`, `idempotency_key`, timestamps, `error_code`.

## `run_events`
`id`, `run_id`, `sequence_no`, `event_type`, `node_id`, redacted `payload_json`, `created_at`. Unique `(run_id, sequence_no)`.

## `checkpoints`
`id`, `run_id`, `sequence_no`, `schema_version`, `state_json`, `created_at`.

## `tool_calls`
`id`, `run_id`, `event_sequence`, `tool_name`, `tool_version`, redacted arguments/result, status, timestamps, duration, optional idempotency key.

## `approvals`
`id`, `run_id`, action summary, status (`pending`, `approved`, `rejected`, `expired`), policy reason, decision actor/reason, created/expiry/decision timestamps.

## `evaluations`
`id`, suite name, workflow version, case ID, expected/actual trajectory, pass flag, metrics, created timestamp.

## Integrity rules
- Event sequence is unique and monotonic per run.
- Status and `finished_at` must be consistent.
- Workspace-scoped resources require authorization on every read/write.
- Checkpoints are versioned.
- Tool data is redacted before persistence.
- Events are append-oriented.
- Credentials are never stored in state or events.
