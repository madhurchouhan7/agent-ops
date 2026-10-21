# Problem and Solution

## Problem
Agents can work in demos but are difficult to operate reliably. Opaque chat loops hide state and make failures hard to diagnose.

Typical problems:
- A crash loses in-memory state.
- A retry duplicates a side effect.
- The model requests a tool it should not access.
- A required approval or verification is skipped.
- Logs show only a final exception, not the decision path.
- A plausible final answer hides unsafe intermediate actions.
- A failure cannot be reproduced as a regression test.

## Users
**Primary:** agent developer who needs to inspect execution, tool calls, failures, and state.  
**Secondary:** small engineering team needing shared run visibility, approvals, tests, and an audit trail.

## Solution
- **Runtime:** validates transitions and executes bounded steps.
- **State/checkpoints:** serializable state saved at safe boundaries.
- **Events:** ordered history of execution facts.
- **Tool policy gate:** checks tool identity, arguments, scope, and risk.
- **Approvals:** pauses before protected actions.
- **Console:** shows runs, events, state, errors, and approvals.
- **Failure Capsules:** redacted evidence plus safe mock replay.
- **Trajectory evaluation:** verifies intermediate actions and policy compliance.

## Value
AgentOps helps developers answer: What happened? Why? What state was the run in? Was the tool call allowed? Can the failure be reproduced without repeating side effects? Did a fix prevent regression?

## Limitations
AgentOps cannot guarantee model reasoning correctness. A crash between an external action and persistence can leave an uncertain outcome. Tool results are untrusted and may contain prompt injection. Checkpointing alone does not guarantee exactly-once external side effects.
