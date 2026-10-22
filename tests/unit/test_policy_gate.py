"""Unit tests for the PolicyGate risk tier evaluation."""

from pydantic import BaseModel

from agent_ops.tools import PolicyGate, RiskTier, ToolDefinition


class EmptySchema(BaseModel):
    pass


def dummy_handler() -> None:
    pass


def test_policy_gate_allows_t0_and_t1() -> None:
    gate = PolicyGate()

    t0_tool = ToolDefinition(
        name="test_fixture",
        description="Local fixture",
        risk_tier=RiskTier.T0,
        input_schema=EmptySchema,
        handler=dummy_handler,
    )
    decision_t0 = gate.evaluate(t0_tool)
    assert decision_t0.allowed is True
    assert decision_t0.requires_approval is False
    assert decision_t0.reason == "ALLOWED"

    t1_tool = ToolDefinition(
        name="query_db",
        description="Read-only query",
        risk_tier=RiskTier.T1,
        input_schema=EmptySchema,
        handler=dummy_handler,
    )
    decision_t1 = gate.evaluate(t1_tool)
    assert decision_t1.allowed is True
    assert decision_t1.requires_approval is False
    assert decision_t1.reason == "ALLOWED"


def test_policy_gate_requires_approval_for_t2() -> None:
    gate = PolicyGate()

    t2_tool = ToolDefinition(
        name="send_reply",
        description="Send customer response",
        risk_tier=RiskTier.T2,
        input_schema=EmptySchema,
        handler=dummy_handler,
    )
    decision_t2 = gate.evaluate(t2_tool)
    assert decision_t2.allowed is True
    assert decision_t2.requires_approval is True
    assert decision_t2.reason == "T2_REQUIRES_HUMAN_APPROVAL"


def test_policy_gate_denies_t3_unconditionally() -> None:
    gate = PolicyGate()

    t3_tool = ToolDefinition(
        name="delete_account",
        description="Irreversible destructive action",
        risk_tier=RiskTier.T3,
        input_schema=EmptySchema,
        handler=dummy_handler,
    )
    decision_t3 = gate.evaluate(t3_tool)
    assert decision_t3.allowed is False
    assert decision_t3.requires_approval is False
    assert decision_t3.reason == "T3_TOOLS_DISABLED_IN_V1"
