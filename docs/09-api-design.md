# API Design

These are proposed V1 contracts, not implemented endpoints.

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/runs` | Create run |
| GET | `/v1/runs` | List/filter runs |
| GET | `/v1/runs/{run_id}` | Run summary |
| GET | `/v1/runs/{run_id}/events` | Ordered timeline |
| GET | `/v1/runs/{run_id}/state` | Safe state projection |
| POST | `/v1/runs/{run_id}/pause` | Pause at safe boundary |
| POST | `/v1/runs/{run_id}/resume` | Resume if policy permits |
| POST | `/v1/runs/{run_id}/cancel` | Request cancellation |
| GET | `/v1/approvals` | List pending approvals |
| POST | `/v1/approvals/{approval_id}/decision` | Approve/reject |
| POST | `/v1/runs/{run_id}/failure-capsule` | Export redacted capsule |
| POST | `/v1/evaluations` | Start evaluation suite |
| GET | `/v1/evaluations/{evaluation_id}` | Evaluation result |

## Example request
```json
{
  "workflow_id": "support-triage-v1",
  "input": {
    "ticket_id": "DEMO-1001",
    "message": "The app crashes when I open settings."
  },
  "idempotency_key": "demo-ticket-1001-v1"
}
```

## Example response
```json
{
  "run_id": "run_example",
  "status": "CREATED",
  "current_node": "validate_input",
  "workflow_version": "1",
  "created_at": "2026-10-21T10:00:00Z"
}
```

## Rules
- Validate request and response schemas.
- Use stable errors: `RUN_NOT_FOUND`, `INVALID_TRANSITION`, `APPROVAL_REQUIRED`, `POLICY_DENIED`, `VERSION_CONFLICT`.
- Never return raw tracebacks or secrets.
- Paginate events.
- Authorize every resource server-side.
- Use idempotency for create/decision operations.
- Use version checks for concurrent state changes.
