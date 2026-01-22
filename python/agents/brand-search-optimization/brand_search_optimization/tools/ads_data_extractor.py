# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Fetches and processes Google Ads performance data from BigQuery."""

from google.cloud import bigquery
import pandas as pd

# Initialize BigQuery client
try:
  CLIENT = bigquery.Client()
except Exception as e:
  print(f"Error initializing BigQuery client: {e}")
  CLIENT = None


def get_ad_performance_data(project_id: str, dataset_id: str,
                            table_id: str) -> pd.DataFrame | None:
  """Fetches ad performance data from a BigQuery table.

  Args:
    project_id: The Google Cloud project ID.
    dataset_id: The BigQuery dataset ID.
    table_id: The BigQuery table ID.

  Returns:
    A pandas DataFrame containing the ad performance data with Clicks,
    Impressions, Cost, Conversions, Campaign Name, Ad Group Name, Date, and CTR.
    Returns None or an empty DataFrame if client initialization failed or
    the query fails.
  """
  if CLIENT is None:
    print("BigQuery client not initialized. Cannot fetch data.")
    return None

  # Construct the SQL query
  # Using generic column names as the exact schema is unknown.
  # CTR is calculated as Clicks / Impressions, handling division by zero.
  query = f"""
    SELECT
      clicks_column AS Clicks,
      impressions_column AS Impressions,
      cost_column AS Cost,
      conversions_column AS Conversions,
      campaign_name_column AS CampaignName,
      ad_group_name_column AS AdGroupName,
      date_column AS Date,
      CASE
        WHEN impressions_column = 0 THEN 0
        ELSE clicks_column / impressions_column
      END AS CTR
    FROM
      `{project_id}.{dataset_id}.{table_id}`
  """

  try:
    # Execute the query
    query_job = CLIENT.query(query)
    # Fetch results into a pandas DataFrame
    df = query_job.to_dataframe()
    return df
  except Exception as e:
    print(f"Error executing BigQuery query: {e}")
    return pd.DataFrame()  # Return an empty DataFrame on error


if __name__ == "__main__":
  # Example usage:
  # Replace with your actual project_id, dataset_id, and table_id
  example_project_id = "your-gcp-project"
  example_dataset_id = "your_dataset"
  example_table_id = "google_ads_performance_table"

  print(f"Attempting to fetch data from: "
        f"{example_project_id}.{example_dataset_id}.{example_table_id}")

  # Note: This example will likely fail if the table doesn't exist or
  # if BigQuery client setup (e.g., authentication) is not complete
  # in the environment where this script is run directly.
  performance_df = get_ad_performance_data(example_project_id,
                                           example_dataset_id, example_table_id)

  if performance_df is not None and not performance_df.empty:
    print("Successfully fetched ad performance data:")
    print(performance_df.head())
  elif performance_df is not None and performance_df.empty:
    print("Query executed, but returned no data or an error occurred during query execution.")
  else:
    print("Failed to fetch ad performance data due to client initialization issue.")
