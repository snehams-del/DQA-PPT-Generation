# Quickstart Guide: Ads Performance Visualization Demo

This guide outlines the steps to run the ads performance visualization demo.

## 1. Environment Setup

*   **Prerequisites:**
    *   Ensure you have Python 3.11+ and Poetry installed.
    *   You should be in the `python/agents/brand-search-optimization/` directory.
*   **Install Dependencies:**
    Run the main setup script for this agent (this usually installs dependencies using Poetry based on `pyproject.toml`):
    ```bash
    sh deployment/run.sh
    ```
    Alternatively, if you only want to install dependencies:
    ```bash
    poetry install
    ```
    This will install all necessary libraries, including `google-cloud-bigquery`, `pandas`, and `matplotlib`.

## 2. Configuration (for Live BigQuery Data)

This demo script can fetch live data from BigQuery or use a sample dataset if live data access fails or is not configured.

*   **`.env` File:**
    *   Ensure you have a `.env` file in the `python/agents/brand-search-optimization/` directory (you can copy `env.example` to `.env` if it doesn't exist).
    *   Update the following BigQuery connection details in your `.env` file if you intend to use live data:
        *   `GOOGLE_CLOUD_PROJECT="your-gcp-project-id"`
        *   `DATASET_ID="your_bigquery_dataset_id"`
        *   **(Important)** You will also need to provide the ID of the BigQuery table containing the Google Ads performance data. The demo script `run_ads_demo_workflow.py` expects this as an argument.

*   **Authentication:**
    Ensure you are authenticated with Google Cloud:
    ```bash
    gcloud auth application-default login
    ```

## 3. Running the Demo Workflow

The main script for this demo is `run_ads_demo_workflow.py`.

*   **Navigate to the script's directory:**
    It's assumed you are already in `python/agents/brand-search-optimization/` if you followed step 1.
    If not, `cd` into it:
    ```bash
    cd python/agents/brand-search-optimization
    ```
*   **Execute the script:**
    The `run_ads_demo_workflow.py` script as it currently stands (from previous subtasks) uses hardcoded placeholder values for BQ project, dataset, and table ID when its `if __name__ == "__main__":` block is executed. To use specific IDs passed from the command line, the script would need to be modified to parse `sys.argv`.

    Assuming the script `run_ads_demo_workflow.py` is modified to accept command-line arguments for BQ details (e.g., `sys.argv[1]`, `sys.argv[2]`, `sys.argv[3]`):
    ```bash
    python run_ads_demo_workflow.py <your-gcp-project-id> <your_bigquery_dataset_id> <your_google_ads_performance_table_id>
    ```
    For example:
    ```bash
    python run_ads_demo_workflow.py my-gcp-project-123 ads_data google_ads_metrics_table
    ```

    *   **Current Behavior (No Script Modification):** If you run the script as created in the previous subtask (`python run_ads_demo_workflow.py`), it will use its internal placeholder values for BigQuery details (`TEST_BQ_PROJECT_ID`, etc.). This will likely trigger the fallback mechanism to use sample data, unless these placeholders happen to point to a valid, accessible BigQuery table.
    *   **Fallback:** If the script cannot fetch data from BigQuery (e.g., due to incorrect configuration, or if placeholder values are used and they don't point to a real table), it will automatically use a built-in sample dataset to generate the visualizations. A message will be printed indicating whether live or sample data is being used.

## 4. Expected Output

The script will perform the following actions:
*   Attempt to connect to BigQuery and fetch ad performance data using the provided (or hardcoded) IDs.
*   If data fetching fails, it will use a sample dataset.
*   Generate the following visualizations as PNG files:
    *   `performance_trend.png` (Line chart: Clicks and Impressions over time)
    *   `campaign_cost_distribution.png` (Pie chart: Cost distribution by Campaign)
    *   `campaign_clicks_distribution.png` (Pie chart: Clicks distribution by Campaign)
    *   `ad_group_ctr_comparison.png` (Bar chart: CTR comparison across Ad Groups)
    *   `ad_group_conversions_comparison.png` (Bar chart: Conversion rate comparison across Ad Groups)
*   Print messages to the console indicating its progress and where the charts are saved.

## 5. Locating Visualizations

The generated PNG chart files will be saved in a directory named `ads_demo_visualizations_output` (or `ads_demo_visualizations` if the `output_dir` argument in `run_demo` was changed from its default in `if __name__ == "__main__"`) within the `python/agents/brand-search-optimization/` directory. Based on the `run_ads_demo_workflow.py` script created, the default output directory in the `if __name__ == "__main__"` block is `ads_demo_visualizations_output`.

```
python/agents/brand-search-optimization/
├── ads_demo_visualizations_output/  # Or your specified output directory
│   ├── performance_trend.png
│   ├── campaign_cost_distribution.png
│   ├── campaign_clicks_distribution.png
│   ├── ad_group_ctr_comparison.png
│   └── ad_group_conversions_comparison.png
└── ... (other files and directories)
```

You can then use these image files in your demo presentation.
```
