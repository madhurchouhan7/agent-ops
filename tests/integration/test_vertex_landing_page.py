"""Integration tests for Vertex-inspired landing page and static assets."""

from collections.abc import Generator
from pathlib import Path

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


def test_landing_page_serves_html_with_metadata(api_client: TestClient) -> None:
    """Verify landing page serves index.html with AgentOps branding."""
    resp = api_client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "AgentOps Control Plane" in resp.text
    assert "Stateful AI Agent Governance" in resp.text
    assert "/assets/index-" in resp.text


def test_console_alias_serves_html(api_client: TestClient) -> None:
    """Verify /console alias returns index.html for React SPA routing."""
    resp = api_client.get("/console")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Support Triage Demo" in resp.text
    assert "Event Timeline" in resp.text


def test_static_assets_mounted_and_accessible(api_client: TestClient) -> None:
    """Verify built CSS and JS assets are directly accessible via /assets/."""
    static_assets = Path("src/agent_ops/api/static/assets")
    assert static_assets.exists(), "assets directory must exist"

    asset_files = list(static_assets.glob("*"))
    assert len(asset_files) >= 2, "must have at least JS and CSS bundles"

    for asset in asset_files:
        resp = api_client.get(f"/assets/{asset.name}")
        assert resp.status_code == 200, f"Asset /assets/{asset.name} failed to load"
        if asset.name.endswith(".js"):
            assert "javascript" in resp.headers["content-type"]
        elif asset.name.endswith(".css"):
            assert "css" in resp.headers["content-type"]
