# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.cloud import bigquery
from typing import List, Dict, Any, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def bigquery_metdata_extraction_tool(
    PROJECT: str, DATASET: str
) -> List[Dict[str, Any]]:
    """
    This program extracts BigQuery tables and columns metadata (name, type, description)
    for the given dataset and returns the information as a list of dictionaries.

    Args:
    PROJECT (str): GCP Project to execute the query on.
    # BQ_LOCATION (str): BigQuery Location (Not used in the current implementation).
    DATASET (str): Name of the dataset.

    Returns:
    List[Dict[str, Any]]: A list of dictionaries. Each dictionary contains the keys
                         'table_name', 'column_name', 'data_type', and 'description' of the column.
    """
    client = bigquery.Client(project=PROJECT)

    # Note: Using INFORMATION_SCHEMA.COLUMNS is often better/faster for basic metadata
    # than COLUMN_FIELD_PATHS unless you need deep path info for nested columns.
    # Sticking to the original:
    query = f"""
        SELECT table_name, column_name, data_type, description
        FROM `{PROJECT}.{DATASET}.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`
        WHERE table_name NOT LIKE '%__UNNESTED%' -- Optionally filter out unnested views
    """

    query_job = client.query(query)
    query_list = []

    logger.info(f"Executing BQ Metadata Extraction Query for Dataset: {DATASET}")
    try:
        # C-compiled list comprehension eliminates costly Python `append` method lookups 
        return [dict(row.items()) for row in query_job]
    except Exception as e:
        logger.error(f"Error executing BigQuery metadata extraction: {e}")
        return []


def bigquery_execution_tool(
    PROJECT: str,
    query: str,
):
    """
    Executes a BigQuery SQL query and returns the results as a Pandas DataFrame.

    Args:
    PROJECT (str): GCP Project to execute the query on.
    query (str): The SQL query string to execute.

    Returns:
    pandas.DataFrame: A DataFrame containing the query result.
                      Returns an empty DataFrame on error.
    """

    client = bigquery.Client(project=PROJECT)

    logger.info(f"Executing BQ Query:\n{query}")
    query_job = client.query(query)
    query_list = []

    try:
        # Utilizing list comprehension operates significantly faster dynamically over large SQL return sets
        return [dict(row.items()) for row in query_job]
    except Exception as e:
        logger.error(f"Error executing BigQuery SQL Execution: {e}")
        return []
