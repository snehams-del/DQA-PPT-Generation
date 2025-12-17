import unittest

from policy_as_code_agent.llm_utils import get_json_schema_from_content


class TestUtils(unittest.TestCase):
    def test_get_json_schema_simple(self):
        content = '[{"name": "Alice", "age": 30}]'
        schema = get_json_schema_from_content(content)
        expected = {"name": "str", "age": "int"}
        self.assertEqual(schema, expected)

    def test_get_json_schema_nested(self):
        content = '[{"user": {"id": 1, "details": {"active": true}}}]'
        schema = get_json_schema_from_content(content)
        expected = {"user": {"id": "int", "details": {"active": "bool"}}}
        self.assertEqual(schema, expected)

    def test_get_json_schema_list(self):
        content = '[{"tags": ["a", "b"]}]'
        schema = get_json_schema_from_content(content)
        # The util merges list schemas, usually taking the first item's type
        expected = {"tags": ["str"]}
        self.assertEqual(schema, expected)

    def test_get_json_schema_jsonl(self):
        content = '{"a": 1}\n{"b": 2}'
        schema = get_json_schema_from_content(content)
        # It merges keys from both lines
        expected = {"a": "int", "b": "int"}
        self.assertEqual(schema, expected)


if __name__ == "__main__":
    unittest.main()
