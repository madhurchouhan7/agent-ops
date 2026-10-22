"""CLI server launcher and entry point for AgentOps."""

from __future__ import annotations

import argparse
import os

import uvicorn


def print_banner(host: str, port: int) -> None:
    """Print startup banner and navigable console URLs."""
    banner = f"""
    ======================================================================
       ___                     _    ____
      / _ | ___ ____ ___  ___ / /_ / __ \\ ___   ___
     / __ |/ _ `/ -_) _ \\/ _// __// /_/ // _ \\ (_-<
    /_/ |_|\\_, /\\__/_//_/_//_/\\__/ \\____// .__//___/
          /___/                         /_/

      Reliable, Observable Developer Control Plane for AI Workflows
    ======================================================================
      * Web Console:        http://{host}:{port}/
      * Interactive API:    http://{host}:{port}/docs
      * Alternative Docs:   http://{host}:{port}/redoc
    ======================================================================
    """
    print(banner)


def main() -> None:
    """Run the AgentOps server CLI."""
    parser = argparse.ArgumentParser(
        description="AgentOps Control Plane Server",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind socket host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Bind socket port (default: 8000)",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Database connection URL (defaults to sqlite:///agent_ops.db)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code change",
    )

    args = parser.parse_args()

    if args.db:
        os.environ["DATABASE_URL"] = args.db

    print_banner(args.host, args.port)

    uvicorn.run(
        "agent_ops.api.app:create_app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        factory=True,
    )


if __name__ == "__main__":
    main()
