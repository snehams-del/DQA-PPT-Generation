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
"""Runs a demo workflow for fetching and visualizing Google Ads data."""

import os
import pandas as pd

# Attempt to import from the tools package.
# If this script is run directly, these imports might fail if the package
# structure is not correctly recognized by the Python path.
try:
  from brand_search_optimization.tools.ads_data_extractor import get_ad_performance_data
  from brand_search_optimization.tools.ads_data_visualizer import (
      create_performance_trend_line_chart,
      create_campaign_distribution_pie_chart,
      create_ad_group_comparison_bar_chart)
except ImportError:
  print(
      "ImportError: Could not import from brand_search_optimization.tools. "
      "Ensure the script is run from the parent directory of 'brand_search_optimization' "
      "or that the package is correctly installed."
  )
  # Provide dummy functions if imports fail, so the script can be partially tested
  # or if the primary goal is to test the script's structure itself.
  def get_ad_performance_data(project_id, dataset_id, table_id):
    print("Warning: Using dummy get_ad_performance_data due to import error.")
    return None

  def create_performance_trend_line_chart(df, output_path):
    print(
        f"Warning: Using dummy create_performance_trend_line_chart for {output_path}."
    )

  def create_campaign_distribution_pie_chart(df, metric_column, output_path):
    print(
        f"Warning: Using dummy create_campaign_distribution_pie_chart for {output_path}."
    )

  def create_ad_group_comparison_bar_chart(df, metric_column, output_path):
    print(
        f"Warning: Using dummy create_ad_group_comparison_bar_chart for {output_path}."
    )


def _get_sample_ads_data() -> pd.DataFrame:
  """Creates a sample pandas DataFrame with dummy ads data."""
  data = {
      'date_column': pd.to_datetime([
          '2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02',
          '2024-01-03', '2024-01-03', '2024-01-04', '2024-01-04',
          '2024-01-05', '2024-01-05'
      ]),
      'clicks_column': [100, 150, 120, 180, 90, 110, 200, 220, 130, 160],
      'impressions_column':
          [1000, 1200, 1100, 1500, 950, 1050, 2000, 2500, 1150, 1400],
      'cost_column': [50, 70, 60, 80, 40, 50, 100, 120, 65, 75],
      'campaign_name_column': [
          'Winter Sale Campaign', 'Brand Awareness Q1', 'Winter Sale Campaign',
          'Brand Awareness Q1', 'Winter Sale Campaign', 'Brand Awareness Q1',
          'Spring Promo', 'New Product Launch', 'Spring Promo',
          'New Product Launch'
      ],
      'ad_group_name_column': [
          'Ad Group Ski', 'Ad Group General', 'Ad Group Snowboard',
          'Ad Group Video', 'Ad Group Boots', 'Ad Group Social',
          'Ad Group Flowers', 'Ad Group Gadget A', 'Ad Group Garden',
          'Ad Group Gadget B'
      ],
      'conversions_column': [10, 12, 11, 15, 8, 9, 20, 22, 12, 14]
  }
  sample_df = pd.DataFrame(data)

  # Calculate ctr_column for the sample DataFrame
  # Ensure impressions_column is not zero to avoid division by zero error
  sample_df['ctr_column'] = 0.0  # Initialize column
  safe_impressions = sample_df['impressions_column'].replace(0, pd.NA
                                                            )  # Temporarily mark 0 as NA
  sample_df['ctr_column'] = (
      sample_df['clicks_column'] / safe_impressions) * 100
  sample_df['ctr_column'] = sample_df['ctr_column'].fillna(
      0)  # Fill NA (original zeros) with 0 CTR

  # Ensure column names match exactly what visualization functions expect
  # (e.g. ads_data_extractor might return 'CampaignName', visualizer expects 'campaign_name_column')
  # For this demo, we assume ads_data_extractor.py also uses these "_column" suffixed names
  # or that a mapping step would occur here if they differed.
  # The sample data here ALREADY uses the "_column" suffix.

  return sample_df


def run_demo(bq_project_id: str,
             bq_dataset_id: str,
             bq_ads_table_id: str,
             output_dir: str = "ads_demo_visualizations") -> None:
  """
  Runs the ads data extraction and visualization demo workflow.

  Args:
    bq_project_id: BigQuery project ID.
    bq_dataset_id: BigQuery dataset ID.
    bq_ads_table_id: BigQuery table ID for ads performance data.
    output_dir: Directory to save generated charts.
  """
  print(f"Starting Ads Demo Workflow...")
  print(f"Output directory for charts: {output_dir}")

  # Create the output directory if it doesn't exist
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created output directory: {output_dir}")

  # --- 1. Fetch Ad Performance Data ---
  print(
      f"\nAttempting to fetch data from BigQuery: "
      f"{bq_project_id}.{bq_dataset_id}.{bq_ads_table_id}"
  )
  ads_df = get_ad_performance_data(bq_project_id, bq_dataset_id,
                                   bq_ads_table_id)

  data_source = "BigQuery"
  if ads_df is None or ads_df.empty:
    print(
        "Failed to fetch data from BigQuery or table is empty. "
        "Using sample hardcoded data for visualizations."
    )
    ads_df = _get_sample_ads_data()
    data_source = "Sample Hardcoded Data"
    # Ensure the sample data has all necessary columns, especially calculated ones like CTR
    if 'ctr_column' not in ads_df.columns and 'clicks_column' in ads_df.columns and 'impressions_column' in ads_df.columns:
        ads_df['ctr_column'] = (ads_df['clicks_column'] / ads_df['impressions_column'].replace(0, pd.NA)).fillna(0) * 100

  print(f"\nUsing data from: {data_source}")
  print("Sample of the data being used for visualizations (first 5 rows):")
  print(ads_df.head())

  # --- 2. Generate Visualizations ---
  print("\n--- Generating Visualizations ---")

  # Chart 1: Performance Trend Line Chart
  trend_chart_path = os.path.join(output_dir, "performance_trend.png")
  print(f"Generating performance trend line chart: {trend_chart_path}")
  create_performance_trend_line_chart(ads_df, output_path=trend_chart_path)

  # Chart 2: Campaign Cost Distribution Pie Chart
  cost_dist_path = os.path.join(output_dir, "campaign_cost_distribution.png")
  print(f"Generating campaign cost distribution pie chart: {cost_dist_path}")
  create_campaign_distribution_pie_chart(
      ads_df, metric_column='cost_column', output_path=cost_dist_path)

  # Chart 3: Campaign Clicks Distribution Pie Chart
  clicks_dist_path = os.path.join(output_dir,
                                  "campaign_clicks_distribution.png")
  print(f"Generating campaign clicks distribution pie chart: {clicks_dist_path}")
  create_campaign_distribution_pie_chart(
      ads_df, metric_column='clicks_column', output_path=clicks_dist_path)

  # Chart 4: Ad Group CTR Comparison Bar Chart
  # Ensure 'ctr_column' exists, especially if using sample data that might not have it pre-calculated.
  if 'ctr_column' not in ads_df.columns:
      if 'clicks_column' in ads_df.columns and 'impressions_column' in ads_df.columns:
          print("Calculating 'ctr_column' as it's missing...")
          # Avoid division by zero, then multiply by 100 for percentage
          ads_df['ctr_column'] = (ads_df['clicks_column'] * 100.0 / ads_df['impressions_column'].replace(0, float('nan'))).fillna(0.0)
      else:
          print("Cannot generate CTR chart as 'clicks_column' or 'impressions_column' is missing.")
          # Create a dummy 'ctr_column' if it doesn't exist to prevent crash, though chart will be meaningless
          if 'ad_group_name_column' in ads_df.columns: # check if other necessary column exists for the chart
             ads_df['ctr_column'] = 0.0

  if 'ctr_column' in ads_df.columns:
    ad_group_ctr_path = os.path.join(output_dir, "ad_group_ctr_comparison.png")
    print(
        f"Generating ad group CTR comparison bar chart: {ad_group_ctr_path}")
    create_ad_group_comparison_bar_chart(
        ads_df, metric_column='ctr_column', output_path=ad_group_ctr_path)
  else:
    print("Skipping Ad Group CTR comparison chart as 'ctr_column' could not be prepared.")


  # Chart 5: Ad Group Conversions Comparison Bar Chart
  ad_group_conv_path = os.path.join(output_dir,
                                    "ad_group_conversions_comparison.png")
  print(f"Generating ad group conversions comparison bar chart: {ad_group_conv_path}")
  create_ad_group_comparison_bar_chart(
      ads_df,
      metric_column='conversions_column',
      output_path=ad_group_conv_path)

  print("\n--- All Visualizations Attempted ---")
  print(f"Please check the '{output_dir}' directory for the generated charts.")


if __name__ == "__main__":
  # --- Configuration for testing ---
  # These should be replaced with actual values if testing against a live BQ environment.
  # For local testing without BQ access, the script will use the fallback sample data.
  TEST_BQ_PROJECT_ID = "your-gcp-project-id"  # Placeholder
  TEST_BQ_DATASET_ID = "your_ads_dataset"  # Placeholder
  TEST_BQ_ADS_TABLE_ID = "ads_performance_table"  # Placeholder
  DEMO_OUTPUT_DIRECTORY = "ads_demo_visualizations_output"

  print("Running demo workflow with test/placeholder BigQuery parameters.")
  print(
      "If BigQuery connection fails or is not configured, "
      "the script will use hardcoded sample data."
  )

  run_demo(
      bq_project_id=TEST_BQ_PROJECT_ID,
      bq_dataset_id=TEST_BQ_DATASET_ID,
      bq_ads_table_id=TEST_BQ_ADS_TABLE_ID,
      output_dir=DEMO_OUTPUT_DIRECTORY)
```
