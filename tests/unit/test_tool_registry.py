"""Unit tests for the allow-listed ToolRegistry."""

import time
from typing import Any

import pytest
from pydantic import BaseModel, Field

from agent_ops.domain.errors import AgentOpsError, ValidationError
from agent_ops.tools import RiskTier, ToolDefinition, ToolRegistry


class AddInput(BaseModel):
    a: int
    b: int = 0


class SlowInput(BaseModel):
    delay: float = Field(gt=0)


def add_handler(a: int, b: int) -> dict[str, Any]:
    return {"sum": a + b}


def slow_handler(delay: float) -> str:
    time.sleep(delay)
    return "done"


def faulty_handler(a: int, b: int) -> dict[str, Any]:
    raise RuntimeError("Database connection lost")


def test_register_and_execute_success() -> None:
    registry = ToolRegistry()
    add_tool = ToolDefinition(
        name="calculator_add",
        description="Add two numbers",
        risk_tier=RiskTier.T0,
        input_schema=AddInput,
        handler=add_handler,
    )
    registry.register(add_tool)

    assert registry.get("calculator_add") is add_tool
    assert len(registry.list_tools()) == 1

    result = registry.execute("calculator_add", {"a": 10, "b": 25})
    assert result.success is True
    assert result.tool_name == "calculator_add"
    assert result.data == {"sum": 35}
    assert result.error is None
    assert result.duration_ms >= 0.0


def test_execute_unknown_tool_fails_closed() -> None:
    registry = ToolRegistry()
    with pytest.raises(AgentOpsError) as exc_info:
        registry.execute("unregistered_tool", {"a": 1})

    assert exc_info.value.error_code == "UNKNOWN_TOOL"
    assert "Unknown tool" in str(exc_info.value)


def test_execute_invalid_schema_fails_closed() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="calculator_add",
            description="Add two numbers",
            risk_tier=RiskTier.T0,
            input_schema=AddInput,
            handler=add_handler,
        )
    )

    with pytest.raises(ValidationError) as exc_info:
        registry.execute("calculator_add", {"a": "not_an_int"})

    assert exc_info.value.error_code == "VALIDATION_ERROR"


def test_execute_timeout_returns_failure_result() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="slow_operation",
            description="Simulate slow operation",
            risk_tier=RiskTier.T0,
            input_schema=SlowInput,
            timeout_seconds=0.05,
            handler=slow_handler,
        )
    )

    result = registry.execute("slow_operation", {"delay": 0.2})
    assert result.success is False
    assert result.tool_name == "slow_operation"
    assert "timed out" in (result.error or "")


def test_execute_faulty_handler_returns_failure_result() -> None:
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name="faulty_operation",
            description="Raises runtime error",
            risk_tier=RiskTier.T0,
            input_schema=AddInput,
            handler=faulty_handler,
        )
    )

    result = registry.execute("faulty_operation", {"a": 1, "b": 2})
    assert result.success is False
    assert result.tool_name == "faulty_operation"
    assert "Database connection lost" in (result.error or "")
