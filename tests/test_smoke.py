"""Basic checks that the AgentOps package loads correctly."""

import agent_ops


def test_package_imports() -> None:
    """The package should import and expose its version."""
    assert agent_ops.__version__ == "0.1.0"
