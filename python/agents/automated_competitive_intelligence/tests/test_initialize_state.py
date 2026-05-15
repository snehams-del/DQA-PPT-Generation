# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import os
from unittest.mock import MagicMock, patch
from backend.tools.initialize_state import initialize_state_var

class MockState(dict):
    """Simple dictionary extension mimicking state delta tracking."""
    pass

class MockCallbackContext:
    def __init__(self):
        self.state = MockState()

@patch.dict(os.environ, {"PROJECT": "test_proj", "BQ_LOCATION": "test_loc", "DATASET": "test_data"}, clear=True)
@patch('backend.tools.initialize_state.bigquery_metdata_extraction_tool')
def test_initialize_state_var(mock_bq_tool):
    """
    Verifies that all context variables are strictly spawned with default values
    to permanently prevent KeyError crashes during prompt template insertions.
    """
    # Setup
    mock_context = MockCallbackContext()
    mock_bq_tool.return_value = [{"table_name": "mock"}]

    # Execution
    initialize_state_var(mock_context)

    # Verification: Validate fixed environment keys
    assert mock_context.state["PROJECT"] == "test_proj"
    assert mock_context.state["BQ_LOCATION"] == "test_loc"
    assert mock_context.state["DATASET"] == "test_data"
    
    # Verification: Validate LLM output trace default values for KeyError blocks
    expected_defaults = [
        "query_understanding_output",
        "query_generation_output",
        "query_review_rewrite_output",
        "query_execution_output",
        "extract_datasheet_url_output",
        "specs_extractor_output",
        "web_search_output",
        "summarizer_output"
    ]
    for key in expected_defaults:
        assert key in mock_context.state
        assert mock_context.state[key] == ""

    # Verification: Validate BQ metadata caching wrapper
    mock_bq_tool.assert_called_once_with(PROJECT="test_proj", DATASET="test_data")
    assert mock_context.state["bigquery_metadata"] == [{"table_name": "mock"}]
