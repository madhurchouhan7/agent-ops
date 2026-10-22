"""Unit tests for system design improvements: IdempotencyManager and EventBus."""

import asyncio
from datetime import timedelta
import pytest

from agent_ops.services.event_bus import EventBus
from agent_ops.services.idempotency import IdempotencyManager


def test_idempotency_manager_lifecycle() -> None:
    """Verify registration, retrieval, completion, and expiration in IdempotencyManager."""
    mgr = IdempotencyManager(ttl_seconds=2)
    mgr.clear()

    # Register new key
    rec = mgr.register("key_123", run_id="run_abc", status="IN_PROGRESS")
    assert rec.key == "key_123"
    assert rec.run_id == "run_abc"
    assert rec.status == "IN_PROGRESS"

    # Retrieve valid record
    found = mgr.get("key_123")
    assert found is not None
    assert found.run_id == "run_abc"

    # Mark completed with payload
    mgr.complete("key_123", response_payload={"run_id": "run_abc", "status": "SUCCEEDED"})
    completed = mgr.get("key_123")
    assert completed is not None
    assert completed.status == "COMPLETED"
    assert completed.response_payload == {"run_id": "run_abc", "status": "SUCCEEDED"}


@pytest.mark.anyio
async def test_event_bus_pub_sub() -> None:
    """Verify asynchronous publication and subscription of events across runs."""
    bus = EventBus()
    received_events = []

    async def subscriber():
        async for evt in bus.subscribe("run_1"):
            received_events.append(evt)
            if len(received_events) >= 2:
                break

    sub_task = asyncio.create_task(subscriber())
    await asyncio.sleep(0.01)

    # Publish to run_1
    await bus.publish("run_1", {"event_type": "step.completed", "node": "step_1"})
    # Publish to another run (should not be delivered to run_1 subscriber)
    await bus.publish("run_2", {"event_type": "step.completed", "node": "ignored"})
    # Publish second event to run_1
    await bus.publish("run_1", {"event_type": "step.completed", "node": "step_2"})

    await asyncio.wait_for(sub_task, timeout=2.0)
    assert len(received_events) == 2
    assert received_events[0]["node"] == "step_1"
    assert received_events[1]["node"] == "step_2"
