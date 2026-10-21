# User Flows

## A. Create and inspect a run
```mermaid
flowchart TD
    A[Open console] --> B[Submit synthetic ticket]
    B --> C[Validate request]
    C -->|Invalid| D[Show validation error]
    C -->|Valid| E[Create run and event]
    E --> F[Execute bounded step]
    F --> G[Persist event and checkpoint]
    G --> H{Run state}
    H -->|Running| F
    H -->|Paused| I[Show pending approval]
    H -->|Succeeded| J[Show completed timeline]
    H -->|Failed| K[Show error and capsule option]
```

## B. Human approval
```mermaid
sequenceDiagram
    participant R as Runtime
    participant D as Database
    participant U as Approval UI
    participant H as Reviewer

    R->>D: Persist approval request and paused checkpoint
    U->>D: Query pending approvals
    D-->>U: Return action details and scope
    H->>U: Approve or reject
    U->>R: Submit decision and reviewer identity
    R->>D: Validate authorization and persist decision

    alt Approved
        R->>D: Record approval
        R->>D: Resume paused checkpoint
        R->>D: Record simulated action outcome
    else Rejected
        R->>D: Record rejection
        R->>D: Mark protected action as not executed
    end
```

## C. Failure diagnosis
```mermaid
flowchart TD
    A[Open failed run] --> B[Inspect timeline and safe state]
    B --> C[Export redacted capsule]
    C --> D[Validate redaction]
    D --> E[Mock replay]
    E --> F[Create regression test]
    F --> G[Run evaluation suite]
    G --> H{Critical assertions pass?}
    H -->|No| I[Fix and rerun]
    H -->|Yes| J[Record evidence and commit]
    I --> G
```

## UX rules
- Show lifecycle status separately from current node.
- Show exact action and scope before approval.
- Distinguish trace replay from live execution.
- Show timestamps, retries, errors, and policy decisions.
- Do not use color alone for status.
- Provide loading, empty, and failure states.

For rejection, choose one consistent safe terminal behavior (`CANCELLED` or a workflow rejection result) and document it in code/tests.
