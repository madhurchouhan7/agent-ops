# System Design

## Run model
A run stores `run_id`, workflow ID/version, lifecycle status, current node, serializable state, retry/step counters, last event sequence, timestamps, and error code. Runtime executes one bounded node/action per step.

## Persistence consistency
For each step, define when an action starts, how in-flight state is represented, when the result/event/checkpoint is committed, and how recovery handles a crash between those points. If an external action may have succeeded but confirmation was not persisted, record an unknown outcome and reconcile before retrying.

## Event ordering
Use a monotonic `sequence_no` per run and a unique database constraint on `(run_id, sequence_no)`. Do not rely solely on timestamps for order.

## Concurrency
- Use optimistic version checks or row locks for competing transitions.
- Make approval decisions idempotent.
- Duplicate create requests with the same idempotency key must not create duplicate runs.
- Define cancellation behavior while a tool is in flight.

## Scaling path
1. Local single process and test persistence.
2. FastAPI + PostgreSQL with a controlled worker.
3. Separate API/worker and queue if justified.
4. Evaluate Temporal or another durable orchestration engine for distributed execution and long waits.
5. Add quotas, backpressure, and capacity tests before increasing complexity.

## Error categories
- `VALIDATION_ERROR`: do not retry.
- `POLICY_DENIED`: do not retry.
- `TRANSIENT_TOOL_ERROR`: bounded retry.
- `TIMEOUT`: outcome may be uncertain.
- `MODEL_OUTPUT_INVALID`: bounded correction or fail.
- `PERSISTENCE_ERROR`: stop/reconcile.
- `UNKNOWN_OUTCOME`: reconcile before another side effect.
- `BUDGET_EXCEEDED`: stop safely.

## Production targets to define
Expected concurrency, API latency, run duration, recovery point objective (RPO), recovery time objective (RTO), retention, and tool/provider failure behavior. Set targets from intended use and measurements, not guesses.
