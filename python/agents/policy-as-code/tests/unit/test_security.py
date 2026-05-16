import pytest

from policy_as_code_agent.simulation import run_simulation, validate_code_safety


def test_safe_code():
    code = """
def check_policy(metadata):
    return []
"""
    errors = validate_code_safety(code)
    assert errors == []


@pytest.mark.parametrize(
    "code",
    [
        "import os",
        "import sys",
        "import subprocess",
        "from os import path",
        "import requests",
    ],
)
def test_unsafe_imports(code):
    errors = validate_code_safety(code)
    assert len(errors) > 0, f"Expected error for: {code}"
    assert "Security Violation" in errors[0]


@pytest.mark.parametrize(
    "code",
    [
        "eval('print(1)')",
        "exec('print(1)')",
        "open('/etc/passwd')",
        "compile('print(1)', '', 'exec')",
    ],
)
def test_unsafe_builtins(code):
    errors = validate_code_safety(code)
    assert len(errors) > 0, f"Expected error for: {code}"
    assert "Security Violation" in errors[0]


def test_sandbox_blocks_import_via_builtins_subscript():
    """__builtins__['__import__'] should not be available in the sandbox."""
    code = """
def check_policy(metadata):
    os_mod = __builtins__['__import__']('os')
    return [{'policy': 'pwned', 'violation': os_mod.popen('id').read()}]
"""
    result = run_simulation(code, [{}])
    assert len(result) == 1
    assert result[0]["policy"] == "Execution Error"
