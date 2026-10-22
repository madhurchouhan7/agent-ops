"""Allow-listed tool registry, schemas, and execution timeout wrapper."""

from __future__ import annotations

import concurrent.futures
import time
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from agent_ops.domain.errors import AgentOpsError, ValidationError


class RiskTier(StrEnum):
    """Tool risk classification tiers.

    T0: Sandboxed local fixture or deterministic calculation.
    T1: Read-only external query (search, lookup).
    T2: Reversible write or state modification (requires human approval).
    T3: High-impact or irreversible action (disabled in V1).
    """

    T0 = "T0"
    T1 = "T1"
    T2 = "T2"
    T3 = "T3"


class ToolDefinition(BaseModel):
    """Schema and execution metadata for a registered tool."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    version: str = "1.0"
    risk_tier: RiskTier
    input_schema: type[BaseModel]
    timeout_seconds: float = 10.0
    handler: Callable[..., Any]


class ToolResult(BaseModel):
    """Structured result returned from executing a registered tool."""

    tool_name: str
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    duration_ms: float = 0.0


class ToolRegistry:
    """Explicit allow-list registry for executing validated tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool definition into the allow-list."""
        self._tools[tool.name] = tool

    def get(self, tool_name: str) -> ToolDefinition | None:
        """Retrieve a tool definition by name, or None if not registered."""
        return self._tools.get(tool_name)

    def list_tools(self) -> list[ToolDefinition]:
        """Return all registered tool definitions."""
        return list(self._tools.values())

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> ToolResult:
        """Execute a registered tool within its timeout budget.

        Raises:
            AgentOpsError: If the tool is not registered (code UNKNOWN_TOOL).
            ValidationError: If the arguments do not conform to the tool's input schema.
        """
        tool = self.get(tool_name)
        if tool is None:
            raise AgentOpsError(
                f"Unknown tool: '{tool_name}' is not registered in allow-list",
                error_code="UNKNOWN_TOOL",
            )

        try:
            validated_input = tool.input_schema.model_validate(arguments)
        except Exception as exc:
            raise ValidationError(
                f"Invalid arguments for tool '{tool_name}': {exc}"
            ) from exc

        kwargs = validated_input.model_dump()
        start_time = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(tool.handler, **kwargs)
            try:
                output = future.result(timeout=tool.timeout_seconds)
                duration_ms = (time.perf_counter() - start_time) * 1000.0

                if isinstance(output, ToolResult):
                    output.duration_ms = round(duration_ms, 2)
                    return output

                if isinstance(output, dict):
                    data = output
                else:
                    data = {"result": output}

                return ToolResult(
                    tool_name=tool_name,
                    success=True,
                    data=data,
                    duration_ms=round(duration_ms, 2),
                )
            except concurrent.futures.TimeoutError:
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return ToolResult(
                    tool_name=tool_name,
                    success=False,
                    error=f"Tool '{tool_name}' timed out after {tool.timeout_seconds}s",
                    duration_ms=round(duration_ms, 2),
                )
            except Exception as exc:
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return ToolResult(
                    tool_name=tool_name,
                    success=False,
                    error=str(exc),
                    duration_ms=round(duration_ms, 2),
                )
