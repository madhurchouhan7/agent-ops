"""Unit tests for offline mock replay runner."""

from agent_ops.diagnostics import MockReplayRunner, ReplayReport


def test_mock_replay_reconstructs_state_successfully() -> None:
    events = [
        {
            "sequence_no": 1,
            "event_type": "node.completed",
            "node_id": "classify",
            "payload": {"state": {"ticket_id": "T-100", "category": "billing"}},
        },
        {
            "sequence_no": 2,
            "event_type": "node.completed",
            "node_id": "lookup_customer",
            "payload": {"state_diff": {"customer_tier": "gold"}},
        },
        {
            "sequence_no": 3,
            "event_type": "node.completed",
            "node_id": "draft_reply",
            "payload": {"state_diff": {"draft": "Your refund is processing"}},
        },
    ]

    checkpoints = [
        {
            "sequence_no": 1,
            "state": {"ticket_id": "T-100", "category": "billing"},
        },
        {
            "sequence_no": 3,
            "state": {
                "ticket_id": "T-100",
                "category": "billing",
                "customer_tier": "gold",
                "draft": "Your refund is processing",
            },
        },
    ]

    report = MockReplayRunner.replay_run(
        run_id="run-replay-001",
        events=events,
        checkpoints=checkpoints,
    )

    assert isinstance(report, ReplayReport)
    assert report.success is True
    assert report.total_steps == 3
    assert report.replayed_events == 3
    assert report.matched_checkpoints == 2
    assert len(report.divergences) == 0
    assert report.final_replayed_state["customer_tier"] == "gold"
    assert report.final_replayed_state["draft"] == "Your refund is processing"


def test_mock_replay_detects_state_divergence() -> None:
    events = [
        {
            "sequence_no": 1,
            "event_type": "node.completed",
            "payload": {"state": {"val": 10}},
        },
    ]

    # Checkpoint expects val: 20
    checkpoints = [
        {
            "sequence_no": 1,
            "state": {"val": 20},
        },
    ]

    report = MockReplayRunner.replay_run(
        run_id="run-replay-divergence",
        events=events,
        checkpoints=checkpoints,
    )

    assert report.success is False
    assert len(report.divergences) == 1
    assert "State divergence at sequence 1" in report.divergences[0]
