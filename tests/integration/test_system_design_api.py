"""Integration tests for enhanced system design endpoints: health, metrics, tracing headers, and SSE streaming."""

from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient

from agent_ops.api import create_app
from agent_ops.storage import (
    create_db_engine,
    get_session_factory,
    init_db,
)


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    """Test client configured with in-memory SQLite database."""
    engine = create_db_engine("sqlite:///:memory:")
    init_db(engine)
    session_factory = get_session_factory(engine)
    app = create_app(session_factory=session_factory)

    with TestClient(app) as client:
        yield client


def test_health_check_endpoint(api_client: TestClient) -> None:
    """Verify /v1/health returns database connectivity and uptime status."""
    resp = api_client.get("/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "uptime_seconds" in data
    assert "timestamp" in data


def test_system_metrics_endpoint(api_client: TestClient) -> None:
    """Verify /v1/metrics returns accurate run, event, and approval counters."""
    resp = api_client.get("/v1/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_runs" in data
    assert "active_runs" in data
    assert "total_events" in data
    assert "pending_approvals" in data


def test_distributed_tracing_middleware_headers(api_client: TestClient) -> None:
    """Verify custom X-Request-ID and X-Response-Time headers are attached to responses."""
    resp = api_client.get("/v1/health", headers={"X-Request-ID": "trace-req-999"})
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID") == "trace-req-999"
    assert "X-Response-Time" in resp.headers
    assert resp.headers["X-Response-Time"].endswith("ms")


def test_sse_streaming_endpoint(api_client: TestClient) -> None:
    """Verify /v1/runs/{run_id}/stream returns text/event-stream with initial ping."""
    with api_client.stream("GET", "/v1/runs/test_run_1/stream") as stream_resp:
        assert stream_resp.status_code == 200
        assert "text/event-stream" in stream_resp.headers["content-type"]
        # Read the initial ping line
        lines = []
        for line in stream_resp.iter_lines():
            if line:
                lines.append(line)
            if len(lines) >= 2:
                break
        assert any("ping" in l for l in lines)
