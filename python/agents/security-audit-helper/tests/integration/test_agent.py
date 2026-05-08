from security_audit_helper import root_agent


def test_agent_integration():
    assert root_agent.name == "security_audit_helper"
