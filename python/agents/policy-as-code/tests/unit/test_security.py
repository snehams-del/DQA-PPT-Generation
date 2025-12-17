import unittest

from policy_as_code_agent.simulation import validate_code_safety


class TestSecurity(unittest.TestCase):
    def test_safe_code(self):
        code = """
def check_policy(metadata):
    return []
"""
        errors = validate_code_safety(code)
        self.assertEqual(errors, [])

    def test_unsafe_imports(self):
        unsafe_codes = [
            "import os",
            "import sys",
            "import subprocess",
            "from os import path",
            "import requests",
        ]
        for code in unsafe_codes:
            with self.subTest(code=code):
                errors = validate_code_safety(code)
                self.assertTrue(len(errors) > 0, f"Expected error for: {code}")
                self.assertIn("Security Violation", errors[0])

    def test_unsafe_builtins(self):
        unsafe_codes = [
            "eval('print(1)')",
            "exec('print(1)')",
            "open('/etc/passwd')",
            "compile('print(1)', '', 'exec')",
        ]
        for code in unsafe_codes:
            with self.subTest(code=code):
                errors = validate_code_safety(code)
                self.assertTrue(len(errors) > 0, f"Expected error for: {code}")
                self.assertIn("Security Violation", errors[0])


if __name__ == "__main__":
    unittest.main()
