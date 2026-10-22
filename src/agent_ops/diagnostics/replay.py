"""Offline mock replay engine reconstructing execution from historical traces."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ReplayReport(BaseModel):
    """Diagnostic report produced by offline trace replay."""

    run_id: str
    success: bool
    total_steps: int = 0
    replayed_events: int = 0
    matched_checkpoints: int = 0
    divergences: list[str] = Field(default_factory=list)
    final_replayed_state: dict[str, Any] = Field(default_factory=dict)


class MockReplayRunner:
    """Replays recorded workflow executions offline with zero external side effects."""

    @classmethod
    def replay_run(
        cls,
        run_id: str,
        events: list[dict[str, Any]],
        checkpoints: list[dict[str, Any]] | None = None,
    ) -> ReplayReport:
        """Replay recorded workflow execution and verify state invariants.

        Reconstructs the state trajectory purely from event payloads and compares
        it against checkpointed states without executing live tools or network calls.
        """
        current_state: dict[str, Any] = {}
        total_steps = 0
        matched_checkpoints = 0
        divergences: list[str] = []

        # Sort events by sequence_no if available
        sorted_events = sorted(events, key=lambda e: e.get("sequence_no", 0))

        cp_map: dict[int, dict[str, Any]] = {}
        if checkpoints:
            for cp in checkpoints:
                seq = cp.get("sequence_no")
                state = cp.get("state") or cp.get("state_json") or {}
                if seq is not None and isinstance(state, dict):
                    cp_map[int(seq)] = state

        for event in sorted_events:
            event_type = event.get("event_type", "")
            payload = event.get("payload") or {}

            # Process state mutations recorded in events
            if "state" in payload and isinstance(payload["state"], dict):
                current_state.update(payload["state"])
            elif "state_diff" in payload and isinstance(payload["state_diff"], dict):
                current_state.update(payload["state_diff"])

            if event_type in {"node.completed", "step.executed", "step.completed"}:
                total_steps += 1

            seq_no = event.get("sequence_no")
            if seq_no is not None and int(seq_no) in cp_map:
                expected_cp_state = cp_map[int(seq_no)]
                for k, expected_v in expected_cp_state.items():
                    if current_state.get(k) != expected_v:
                        replayed_v = current_state.get(k)
                        divergences.append(
                            f"State divergence at sequence {seq_no} for key '{k}': "
                            f"expected '{expected_v}', replayed '{replayed_v}'"
                        )
                matched_checkpoints += 1

        is_success = len(divergences) == 0
        return ReplayReport(
            run_id=run_id,
            success=is_success,
            total_steps=total_steps,
            replayed_events=len(sorted_events),
            matched_checkpoints=matched_checkpoints,
            divergences=divergences,
            final_replayed_state=current_state,
        )
