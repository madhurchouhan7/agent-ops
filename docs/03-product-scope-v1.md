# Product Scope — V1 Features

| Feature | V1 behavior | Acceptance evidence |
|---|---|---|
| Workflow runtime | Explicit graph and bounded steps | Unit tests |
| State machine | Transition table and terminal enforcement | Transition tests |
| Retry | Retry classified transient failures only | Fault-injection tests |
| Pause/resume | Approval boundary and authorized resume | Integration tests |
| Checkpoints | Versioned snapshots and restart recovery | Recovery test |
| Event timeline | Ordered events and tool outcomes | DB/API tests |
| Tool registry | Allow-list and strict schemas | Unknown-tool tests |
| Policy gate | Authorization and risk checks outside prompts | Security tests |
| Approval inbox | Pending actions, decision, actor | UI/API tests |
| Dashboard | Run list, timeline, safe state | End-to-end demo |
| Failure Capsule | Versioned redacted export | Secret-leak test |
| Mock replay | Replay outputs without external calls | Network-disabled test |
| Evaluation | Golden trajectory assertions | CI gate |
| Observability | Structured logs and core metrics | Inspection |
| Documentation | Setup, architecture, limitations | Clean-clone review |

## V1.1 candidates
MCP client integration, Redis queue/worker, OpenTelemetry tracing, more model adapters, workflow-version UI, multi-user workspaces after authorization is tested.

## V2 candidates
Visual workflow builder, distributed durable backend, cost budgets, enterprise identity, hosted SaaS, browser automation adapter.

## Not V1
Arbitrary host code execution, live support replies, automatic production remediation, and unsupported claims of exactly-once execution.

**Prioritization rule:** a feature enters V1 only if it directly supports the demo workflow, observability, safety, recovery, or evaluation.
