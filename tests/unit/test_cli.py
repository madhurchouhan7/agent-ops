"""Unit tests for the CLI server runner."""

import os
from unittest.mock import patch

from agent_ops.main import main, print_banner


def test_print_banner_outputs_urls(capsys: object) -> None:
    print_banner("127.0.0.1", 8000)
    # capsys fixture from pytest
    # Captured output contains localhost URLs
    assert "127.0.0.1:8000" in capsys.readouterr().out


def test_main_cli_arguments_parser() -> None:
    with (
        patch(
            "sys.argv",
            [
                "agentops",
                "--host",
                "0.0.0.0",
                "--port",
                "9000",
                "--db",
                "sqlite:///test.db",
            ],
        ),
        patch("uvicorn.run") as mock_uvicorn,
    ):
        main()
        assert os.environ.get("DATABASE_URL") == "sqlite:///test.db"
        mock_uvicorn.assert_called_once_with(
            "agent_ops.api.app:create_app",
            host="0.0.0.0",
            port=9000,
            reload=False,
            factory=True,
        )
