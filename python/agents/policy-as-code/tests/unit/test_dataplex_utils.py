import unittest
from unittest.mock import MagicMock

from policy_as_code_agent.dataplex_utils import convert_proto_to_dict, entry_to_dict


class TestDataplexUtils(unittest.TestCase):
    def test_convert_proto_to_dict_simple(self):
        # Mock a proto-like object (e.g. MapComposite)
        proto = {"key": "value", "nested": {"a": 1}}
        result = convert_proto_to_dict(proto)
        self.assertEqual(result, {"key": "value", "nested": {"a": 1}})

    def test_convert_proto_to_dict_repeated(self):
        # Mock a RepeatedComposite (list-like)
        proto = [{"a": 1}, {"b": 2}]
        result = convert_proto_to_dict(proto)
        self.assertEqual(result, [{"a": 1}, {"b": 2}])

    def test_entry_to_dict(self):
        # Mock a Dataplex Entry object
        mock_entry = MagicMock()
        mock_entry.name = "projects/p/locations/l/entryGroups/g/entries/e"
        mock_entry.entry_type = "table"
        mock_entry.fully_qualified_name = "bigquery:p.d.t"
        mock_entry.parent_entry = "parent"

        # Mock entry source
        mock_entry.entry_source.resource = "resource"
        mock_entry.entry_source.system = "BIGQUERY"
        mock_entry.entry_source.platform = "GCP"
        mock_entry.entry_source.display_name = "table1"
        mock_entry.entry_source.location = "us-central1"
        mock_entry.entry_source.labels = {"env": "prod"}

        # Mock aspects
        mock_aspect = MagicMock()
        mock_aspect.aspect_type = "schema"
        mock_aspect.data = {"fields": [{"name": "id"}]}
        mock_entry.aspects = {"schema_aspect": mock_aspect}

        result = entry_to_dict(mock_entry)

        self.assertEqual(result["name"], mock_entry.name)
        self.assertEqual(result["entryType"], "table")
        self.assertEqual(result["entrySource"]["system"], "BIGQUERY")
        self.assertEqual(result["entrySource"]["labels"], {"env": "prod"})
        self.assertEqual(result["aspects"]["schema_aspect"]["aspectType"], "schema")
        self.assertEqual(
            result["aspects"]["schema_aspect"]["data"], {"fields": [{"name": "id"}]}
        )


if __name__ == "__main__":
    unittest.main()
