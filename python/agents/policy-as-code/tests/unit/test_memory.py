import datetime
import unittest
from unittest.mock import MagicMock, patch

# Mock google.cloud.firestore before importing memory
with patch("google.cloud.firestore.Client") as MockFirestore:
    from policy_as_code_agent import memory


class TestMemory(unittest.TestCase):

    def setUp(self):
        memory.db = MagicMock()
        memory.EMBEDDING_MODEL_NAME = "test-model"

    @patch("policy_as_code_agent.memory.TextEmbeddingModel")
    def test_find_policy_in_memory_success(self, MockEmbeddingModel):
        mock_model = MockEmbeddingModel.from_pretrained.return_value
        mock_model.get_embeddings.return_value = [MagicMock(values=[0.1, 0.2, 0.3])]

        mock_collection = memory.db.collection.return_value
        mock_vector_query = mock_collection.find_nearest.return_value

        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            "policy_id": "123",
            "version": 1,
            "source": "gcs",
            "query": "test query",
            "embedding": [0.1, 0.2, 0.3],
            "similarity_distance": 0.1,
        }
        mock_doc.get.return_value = 0.1  # for similarity_distance if accessed via get

        mock_vector_query.stream.return_value = [mock_doc]

        result = memory.find_policy_in_memory("test query", "gcs")
        self.assertEqual(result["status"], "found")
        self.assertEqual(result["policy"]["policy_id"], "123")

    @patch("policy_as_code_agent.memory.TextEmbeddingModel")
    def test_save_policy_to_memory(self, MockEmbeddingModel):
        mock_model = MockEmbeddingModel.from_pretrained.return_value
        mock_model.get_embeddings.return_value = [MagicMock(values=[0.1, 0.2, 0.3])]

        result = memory.save_policy_to_memory("new query", "print('hello')", "gcs")

        self.assertEqual(result["status"], "success")
        memory.db.collection.assert_called_with("policies")

    def test_list_policy_versions(self):
        mock_doc1 = MagicMock()
        mock_doc1.to_dict.return_value = {"policy_id": "123", "version": 1}
        mock_doc2 = MagicMock()
        mock_doc2.to_dict.return_value = {"policy_id": "123", "version": 2}

        # Setup mock stream
        memory.db.collection.return_value.where.return_value.stream.return_value = [
            mock_doc1,
            mock_doc2,
        ]

        result = memory.list_policy_versions("123")

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["versions"]), 2)

    def test_log_policy_execution(self):
        # Setup Mocks
        mock_collection = memory.db.collection.return_value
        mock_stream = (
            mock_collection.where.return_value.where.return_value.limit.return_value.stream
        )

        # Mock policy doc for stats update
        mock_doc = MagicMock()
        mock_stream.return_value = [mock_doc]

        # Violations list
        violations = [
            {"violation": "test"},
            {"violation": "test2"},
            {"violation": "test3"},
            {"violation": "test4"},
            {"violation": "test5"},
        ]

        # Run Code
        result = memory.log_policy_execution(
            "123", 1, "violations_found", "gcs", violations, "test summary"
        )

        # Verify
        self.assertEqual(result["status"], "success")

        # Check add() call for execution log
        memory.db.collection.assert_any_call("policy_executions")
        args, _ = memory.db.collection("policy_executions").add.call_args
        data = args[0]
        self.assertEqual(data["policy_id"], "123")
        self.assertEqual(data["status"], "violations_found")
        self.assertEqual(data["violation_count"], 5)

        # Check update() call for policy aggregate stats
        mock_doc.reference.update.assert_called()
        update_args, _ = mock_doc.reference.update.call_args
        updates = update_args[0]
        self.assertIn("total_runs", updates)
        self.assertIn("total_violations_detected", updates)

    def test_get_execution_history(self):
        # Setup Mocks
        mock_collection = memory.db.collection.return_value

        # The chain is collection(..).where(..).order_by(..)
        mock_query = mock_collection.where.return_value.order_by.return_value

        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            "policy_id": "123",
            "timestamp": datetime.datetime.now(),
            "status": "success",
        }
        mock_query.stream.return_value = [mock_doc]

        # Run Code
        result = memory.get_execution_history(days=7, status="success", policy_id="123")

        # Verify
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["history"]), 1)
        self.assertEqual(result["history"][0]["policy_id"], "123")


if __name__ == "__main__":
    unittest.main()
