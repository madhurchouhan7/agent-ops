"""Integration tests for web console serving and static asset delivery."""

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


def test_serve_console_root_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "AgentOps" in resp.text
    assert "Control Plane" in resp.text


def test_serve_console_alias_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/console")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Support Triage Demo" in resp.text
    assert "Event Timeline" in resp.text
