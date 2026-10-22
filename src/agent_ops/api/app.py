"""FastAPI application factory for the AgentOps control plane API."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
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
) -> FastAPI:
    """Create and configure the AgentOps FastAPI application instance."""
    app = FastAPI(
        title="AgentOps Control Plane API",
        version="0.1.0",
        description="Reliable, observable control plane for stateful AI workflows",
    )

    if session_factory is None:
        engine = create_db_engine("sqlite:///:memory:")
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
    return app
