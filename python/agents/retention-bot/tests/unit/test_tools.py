from unittest.mock import patch

from retention_bot_agent.agent import archive_datasets, get_retention_datasets


class TestRetentionTools:

    @patch("retention_bot_agent.agent.DataplexRetentionAgent")
    def test_get_retention_datasets_success(self, MockAgent):
        # 1. Setup Mock Data
        mock_instance = MockAgent.return_value
        expected_data = [{"dataset": "test_ds", "days_old": 100}]
        mock_instance.analyze_datasets.return_value = expected_data

        # 2. Execute Tool Function
        result = get_retention_datasets(retention_period_days=90)

        # 3. Assert Logic
        assert result == expected_data
        # Verify the internal logic passed the correct threshold
        mock_instance.analyze_datasets.assert_called_once_with(90)

    @patch("retention_bot_agent.agent.DataflowFlexTemplateLauncher")
    def test_archive_datasets_logic(self, MockLauncher):
        # 1. Setup Inputs
        # The LLM is expected to generate this list of dicts
        input_config = [
            {"bq_dataset": "finance_raw", "delete_source_data": True},
            {"bq_dataset": "finance_stg", "delete_source_data": False},
        ]

        mock_instance = MockLauncher.return_value
        mock_instance.execute_pipeline.return_value = "job_id_123"

        # 2. Execute
        responses = archive_datasets(input_config)

        # 3. Assert Trajectory (Loop Logic)
        assert len(responses) == 2
        assert MockLauncher.call_count == 2

        # Verify specific calls
        # Check if the first call had delete_source_data=True
        call_args_list = MockLauncher.call_args_list
        assert call_args_list[0].kwargs["bigquery_dataset"] == "finance_raw"
        assert call_args_list[0].kwargs["delete_source_data"] is True
