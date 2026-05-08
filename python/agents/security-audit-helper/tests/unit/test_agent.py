from security_audit_helper import root_agent


def test_agent_exists():
    assert root_agent is not None
    assert root_agent.name == "security_audit_helper"
