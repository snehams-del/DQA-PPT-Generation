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
from unittest.mock import patch, MagicMock
from backend.tools.big_query_tools import bigquery_metdata_extraction_tool, bigquery_execution_tool

@patch('backend.tools.big_query_tools.bigquery.Client')
def test_bigquery_metadata_extraction_tool(mock_client_class):
    # Setup mock
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_query_job = MagicMock()
    # Mocking rows as dictionaries with items() method (similar to BigQuery Row)
    mock_row1 = MagicMock()
    mock_row1.items.return_value = [('table_name', 'table1'), ('column_name', 'col1')]
    mock_row2 = MagicMock()
    mock_row2.items.return_value = [('table_name', 'table1'), ('column_name', 'col2')]
    
    mock_query_job.__iter__.return_value = [mock_row1, mock_row2]
    mock_client.query.return_value = mock_query_job

    # Execute
    result = bigquery_metdata_extraction_tool(PROJECT="test_proj", DATASET="test_dt")

    # Assert
    assert len(result) == 2
    assert result[0] == {'table_name': 'table1', 'column_name': 'col1'}
    assert result[1] == {'table_name': 'table1', 'column_name': 'col2'}
    mock_client.query.assert_called_once()
    assert "INFORMATION_SCHEMA.COLUMN_FIELD_PATHS" in mock_client.query.call_args[0][0]

@patch('backend.tools.big_query_tools.bigquery.Client')
def test_bigquery_execution_tool(mock_client_class):
    # Setup mock
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_query_job = MagicMock()
    mock_row1 = MagicMock()
    mock_row1.items.return_value = [('result_col', 'result_val')]
    
    mock_query_job.__iter__.return_value = [mock_row1]
    mock_client.query.return_value = mock_query_job

    # Execute
    result = bigquery_execution_tool(PROJECT="test_proj", query="SELECT * FROM test")

    # Assert
    assert len(result) == 1
    assert result[0] == {'result_col': 'result_val'}
    mock_client.query.assert_called_once_with("SELECT * FROM test")
