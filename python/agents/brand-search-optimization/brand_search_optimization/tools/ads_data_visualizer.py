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
"""Creates visualizations for Google Ads performance data."""

import matplotlib.pyplot as plt
import pandas as pd
# Not using Plotly for now to keep focus on core requirements.
# import plotly.express as px

# Ensure matplotlib uses a non-interactive backend to prevent issues in environments without a display server
import matplotlib
matplotlib.use('Agg')


def create_performance_trend_line_chart(
    df: pd.DataFrame, output_path: str = "performance_trend.png") -> None:
  """Creates a line chart showing clicks and impressions over time.

  Args:
    df: Pandas DataFrame with 'date_column', 'clicks_column', and
      'impressions_column'.
    output_path: Path to save the chart image.
  """
  if not all(col in df.columns for col in
             ['date_column', 'clicks_column', 'impressions_column']):
    print("DataFrame is missing required columns for performance trend chart.")
    return

  try:
    # Convert 'date_column' to datetime if it's not already
    df['date_column'] = pd.to_datetime(df['date_column'])

    # Group by date and sum clicks and impressions
    daily_data = df.groupby('date_column')[[
        'clicks_column', 'impressions_column'
    ]].sum().reset_index()

    plt.figure(figsize=(12, 6))
    plt.plot(
        daily_data['date_column'],
        daily_data['clicks_column'],
        label='Clicks',
        marker='o')
    plt.plot(
        daily_data['date_column'],
        daily_data['impressions_column'],
        label='Impressions',
        marker='x')

    plt.title('Performance Trends Over Time')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close() # Close the figure to free memory
    print(f"Performance trend chart saved to {output_path}")
  except Exception as e:
    print(f"Error creating performance trend chart: {e}")


def create_campaign_distribution_pie_chart(
    df: pd.DataFrame,
    metric_column: str = 'clicks_column',
    output_path: str = "campaign_distribution.png") -> None:
  """Creates a pie chart showing the distribution of a metric by campaign.

  Args:
    df: Pandas DataFrame with 'campaign_name_column' and the `metric_column`.
    metric_column: The column to be aggregated (e.g., 'clicks_column',
      'cost_column').
    output_path: Path to save the chart image.
  """
  if not all(col in df.columns
             for col in ['campaign_name_column', metric_column]):
    print("DataFrame is missing required columns for campaign distribution chart.")
    return

  try:
    campaign_data = df.groupby('campaign_name_column')[metric_column].sum()

    # Filter out campaigns with zero or negative sum for pie chart
    campaign_data = campaign_data[campaign_data > 0]

    if campaign_data.empty:
        print(f"No positive data available for {metric_column} to plot campaign distribution.")
        return

    plt.figure(figsize=(10, 8))
    plt.pie(
        campaign_data,
        labels=campaign_data.index,
        autopct='%1.1f%%',
        startangle=90)
    plt.title(f'Campaign Distribution by {metric_column}')
    plt.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close() # Close the figure to free memory
    print(f"Campaign distribution pie chart saved to {output_path}")
  except Exception as e:
    print(f"Error creating campaign distribution pie chart: {e}")


def create_ad_group_comparison_bar_chart(
    df: pd.DataFrame,
    metric_column: str = 'ctr_column',
    output_path: str = "ad_group_comparison.png") -> None:
  """Creates a bar chart comparing a metric across different ad groups.

  Args:
    df: Pandas DataFrame with 'ad_group_name_column' and the `metric_column`.
    metric_column: The column to be aggregated/compared (e.g., 'ctr_column',
      'conversions_column').
    output_path: Path to save the chart image.
  """
  if not all(col in df.columns
             for col in ['ad_group_name_column', metric_column]):
    print("DataFrame is missing required columns for ad group comparison chart.")
    return

  try:
    # For metrics like CTR, average is more appropriate. For counts, sum might be.
    # Here, we'll use average, assuming CTR or similar rate-based metric.
    if 'ctr' in metric_column.lower() or 'rate' in metric_column.lower():
        ad_group_data = df.groupby('ad_group_name_column')[metric_column].mean()
    else: # For counts like clicks, cost, conversions, sum is usually better
        ad_group_data = df.groupby('ad_group_name_column')[metric_column].sum()

    ad_group_data = ad_group_data.sort_values(ascending=False)

    if ad_group_data.empty:
        print(f"No data available for {metric_column} to plot ad group comparison.")
        return

    plt.figure(figsize=(12, 7))
    ad_group_data.plot(kind='bar')
    plt.title(f'Ad Group Comparison by {metric_column}')
    plt.xlabel('Ad Group')
    plt.ylabel(metric_column.replace("_column", "").capitalize())
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close() # Close the figure to free memory
    print(f"Ad group comparison bar chart saved to {output_path}")
  except Exception as e:
    print(f"Error creating ad group comparison bar chart: {e}")


if __name__ == "__main__":
  # Create a sample DataFrame for demonstration
  data = {
      'date_column': pd.to_datetime([
          '2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02',
          '2024-01-03', '2024-01-03', '2024-01-01', '2024-01-02'
      ]),
      'clicks_column': [100, 150, 120, 180, 90, 110, 200, 220],
      'impressions_column': [1000, 1200, 1100, 1500, 950, 1050, 2000, 2500],
      'cost_column': [50, 70, 60, 80, 40, 50, 100, 120],
      'campaign_name_column': [
          'Campaign A', 'Campaign B', 'Campaign A', 'Campaign B',
          'Campaign A', 'Campaign B', 'Campaign C', 'Campaign C'
      ],
      'ad_group_name_column': [
          'Ad Group 1', 'Ad Group X', 'Ad Group 1', 'Ad Group X',
          'Ad Group 2', 'Ad Group Y', 'Ad Group Z', 'Ad Group Z'
      ],
      'conversions_column': [10, 12, 11, 15, 8, 9, 20, 22]
  }
  sample_df = pd.DataFrame(data)

  # Calculate ctr_column for the sample DataFrame
  sample_df['ctr_column'] = (
      sample_df['clicks_column'] / sample_df['impressions_column']
  ) * 100 # As percentage

  print("Sample DataFrame for testing visualizations:")
  print(sample_df.head())
  print("\n --- Running Visualization Functions ---")

  # Test performance trend line chart
  create_performance_trend_line_chart(
      sample_df, output_path="sample_performance_trend.png")

  # Test campaign distribution pie chart (using cost_column)
  create_campaign_distribution_pie_chart(
      sample_df,
      metric_column='cost_column',
      output_path="sample_campaign_cost_distribution.png")

  # Test campaign distribution pie chart (using clicks_column)
  create_campaign_distribution_pie_chart(
      sample_df,
      metric_column='clicks_column',
      output_path="sample_campaign_clicks_distribution.png")

  # Test ad group comparison bar chart (using ctr_column)
  create_ad_group_comparison_bar_chart(
      sample_df,
      metric_column='ctr_column',
      output_path="sample_ad_group_ctr_comparison.png")

  # Test ad group comparison bar chart (using conversions_column)
  create_ad_group_comparison_bar_chart(
      sample_df,
      metric_column='conversions_column',
      output_path="sample_ad_group_conversions_comparison.png")

  print("\n --- Visualization Functions Execution Complete ---")
  print("Please check for .png files in the script's directory.")
