"""Asynchronous Pub/Sub EventBus for real-time telemetry and SSE streaming."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class EventBus:
    """In-memory asynchronous Pub/Sub event bus for real-time run telemetry."""

    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[dict[str, Any]]]] = defaultdict(set)
        self._global_subscribers: set[asyncio.Queue[dict[str, Any]]] = set()
        self._lock = asyncio.Lock()

    async def publish(self, run_id: str, event_data: dict[str, Any]) -> None:
        """Publish an event to all subscribers listening to this run_id and global listeners."""
        # Ensure timestamp is set
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.now(UTC).isoformat()
        event_data["run_id"] = run_id

        async with self._lock:
            # Deliver to run-specific subscribers
            run_queues = list(self._subscribers.get(run_id, set()))
            # Deliver to global subscribers
            global_queues = list(self._global_subscribers)

        for q in run_queues + global_queues:
            try:
                q.put_nowait(event_data)
            except asyncio.QueueFull:
                logger.warning("Subscriber queue is full for run %s, dropping event", run_id)

    async def subscribe(self, run_id: str | None = None) -> AsyncGenerator[dict[str, Any], None]:
        """Subscribe to events for a specific run_id or all runs (if run_id is None)."""
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)

        async with self._lock:
            if run_id:
                self._subscribers[run_id].add(queue)
            else:
                self._global_subscribers.add(queue)

        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            async with self._lock:
                if run_id and run_id in self._subscribers:
                    self._subscribers[run_id].discard(queue)
                    if not self._subscribers[run_id]:
                        del self._subscribers[run_id]
                else:
                    self._global_subscribers.discard(queue)

    async def sse_stream(self, run_id: str | None = None) -> AsyncGenerator[str, None]:
        """Format events as standard Server-Sent Events (SSE)."""
        # Initial ping to establish connection
        yield f"event: ping\ndata: {json.dumps({'status': 'connected', 'timestamp': datetime.now(UTC).isoformat()})}\n\n"
        
        async for event in self.subscribe(run_id):
            event_type = event.get("event_type", "message")
            payload = json.dumps(event)
            yield f"event: {event_type}\ndata: {payload}\n\n"


# Singleton instance
global_event_bus = EventBus()
