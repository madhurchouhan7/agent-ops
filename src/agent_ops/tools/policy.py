"""Code-enforced policy gate for tool risk tier evaluation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from agent_ops.tools.registry import RiskTier, ToolDefinition


class PolicyDecision(BaseModel):
    """Result of evaluating an action or tool against security policy."""

    allowed: bool
    requires_approval: bool = False
    reason: str = "ALLOWED"


class PolicyGate:
    """Deterministic, code-level policy enforcement layer outside model control."""

    def evaluate(
        self,
        tool: ToolDefinition,
        arguments: dict[str, Any] | None = None,
        caller_roles: set[str] | None = None,
    ) -> PolicyDecision:
        """Evaluate whether a tool can be executed directly or requires human signoff.

        Rules:
        - T3 tools are disabled in V1 (fail closed).
        - T2 tools represent mutating actions and require human approval.
        - T0 and T1 tools are safe and execute without human approval.
        """
        # Preserved for extensible argument-level policy in future versions
        del arguments, caller_roles

        if tool.risk_tier == RiskTier.T3:
            return PolicyDecision(
                allowed=False,
                requires_approval=False,
                reason="T3_TOOLS_DISABLED_IN_V1",
            )

        if tool.risk_tier == RiskTier.T2:
            return PolicyDecision(
                allowed=True,
                requires_approval=True,
                reason="T2_REQUIRES_HUMAN_APPROVAL",
            )

        return PolicyDecision(
            allowed=True,
            requires_approval=False,
            reason="ALLOWED",
        )
