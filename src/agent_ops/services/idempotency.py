"""Thread-safe, TTL-based Idempotency Manager for workflow execution requests."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass
class IdempotencyRecord:
    key: str
    run_id: str
    created_at: datetime
    status: str  # "IN_PROGRESS" | "COMPLETED"
    response_payload: dict[str, Any] | None = None


class IdempotencyManager:
    """Manages idempotent request keys with expiration and status locking."""

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl = timedelta(seconds=ttl_seconds)
        self._store: dict[str, IdempotencyRecord] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> IdempotencyRecord | None:
        """Retrieve an idempotency record if valid and not expired."""
        with self._lock:
            self._purge_expired()
            return self._store.get(key)

    def register(
        self, key: str, run_id: str, status: str = "IN_PROGRESS"
    ) -> IdempotencyRecord:
        """Register a new key with initial status."""
        with self._lock:
            self._purge_expired()
            record = IdempotencyRecord(
                key=key,
                run_id=run_id,
                created_at=datetime.now(UTC),
                status=status,
            )
            self._store[key] = record
            return record

    def complete(
        self, key: str, response_payload: dict[str, Any] | None = None
    ) -> None:
        """Mark an idempotency key as completed with optional cached payload."""
        with self._lock:
            if key in self._store:
                self._store[key].status = "COMPLETED"
                self._store[key].response_payload = response_payload

    def _purge_expired(self) -> None:
        """Internal cleanup of expired records."""
        now = datetime.now(UTC)
        expired_keys = [
            k for k, v in self._store.items() if now - v.created_at > self.ttl
        ]
        for k in expired_keys:
            del self._store[k]

    def clear(self) -> None:
        """Clear all stored keys (useful for test fixtures)."""
        with self._lock:
            self._store.clear()


# Global instance
global_idempotency_manager = IdempotencyManager()
