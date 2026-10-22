"""FastAPI application factory for the AgentOps control plane API."""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, sessionmaker

from agent_ops.api.routes import router
from agent_ops.domain.errors import AgentOpsError
from agent_ops.storage import (
    create_db_engine,
    get_session_factory,
    init_db,
)


def create_app(
    session_factory: sessionmaker[Session] | None = None,
    database_url: str | None = None,
) -> FastAPI:
    """Create and configure the AgentOps FastAPI application instance."""
    app = FastAPI(
        title="AgentOps Control Plane API",
        version="0.1.0",
        description="Reliable, observable control plane for stateful AI workflows",
    )

    # Enable CORS for browser-based testing and standalone web apps
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if session_factory is None:
        db_url = database_url or os.environ.get(
            "DATABASE_URL", "sqlite:///agent_ops.db"
        )
        engine = create_db_engine(db_url)
        init_db(engine)
        session_factory = get_session_factory(engine)

    app.state.session_factory = session_factory

    @app.exception_handler(AgentOpsError)
    async def agent_ops_error_handler(
        request: Request, exc: AgentOpsError
    ) -> JSONResponse:
        del request
        status_code = 400
        if exc.error_code == "NOT_FOUND":
            status_code = 404
        elif exc.error_code == "UNAUTHORIZED":
            status_code = 403
        elif exc.error_code in {
            "INVALID_TRANSITION",
            "INVALID_STATE",
            "INVALID_RUN_STATE",
            "TERMINAL_STATE_VIOLATION",
            "BUDGET_EXCEEDED",
            "UNKNOWN_TOOL",
            "VALIDATION_ERROR",
        }:
            status_code = 400

        return JSONResponse(
            status_code=status_code,
            content={"error": exc.error_code, "message": str(exc)},
        )

    app.include_router(router)

    # Mount static assets and serve interactive web console
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", include_in_schema=False, response_model=None)
    @app.get("/console", include_in_schema=False, response_model=None)
    async def serve_console() -> Response:
        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return HTMLResponse(
            "<!DOCTYPE html><html><body>"
            "<h1>AgentOps Control Plane</h1>"
            "<p>API is active at <a href='/docs'>/docs</a>.</p>"
            "</body></html>"
        )

    return app
