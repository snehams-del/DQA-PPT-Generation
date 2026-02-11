import os
from typing import Dict, List

from google.adk.agents import Agent
from google.adk.apps.app import App
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

from .prompt import AGENT_INSTRUCTION
from .tools.dataplex_archive import DataflowFlexTemplateLauncher
from .tools.dataplex_retention import DataplexRetentionAgent


def get_retention_datasets(retention_period_days: int = 90) -> List[Dict[str, str]]:
    """Retrieves the list of datasets beyond the retention period"""
    print(f"--- Tool: get_retention_datasets for {retention_period_days} ---")

    try:

        # Configuration
        retention_threshold_days = retention_period_days

        print(f"Retention Threshold : {retention_threshold_days}")

        dataplex_tool = DataplexRetentionAgent()
        result_json = dataplex_tool.analyze_datasets(retention_threshold_days)

        return result_json

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error fetching  data: {str(e)}",
        }


def archive_datasets(dataset_configs: List[Dict[str, bool]]) -> str:
    """Archives the datasets from BQ to GCS based on the List of Dict provided"""
    print(f"--- Tool: trigger archival jobs for {dataset_configs} ---")
    response_list = []
    try:

        for config in dataset_configs:
            bigquery_dataset = config["bq_dataset"]
            delete_source_data = config["delete_source_data"]

            launcher = DataflowFlexTemplateLauncher(
                bigquery_dataset=bigquery_dataset, delete_source_data=delete_source_data
            )

            # Call the single public method to run the process
            response = launcher.execute_pipeline()

            print(f"\nProcessing dataset: {bigquery_dataset}")
            print(f"  - Delete source data: {delete_source_data}")

            response_list.append(response)

        return response_list

    except Exception as e:
        print(e)
        return {
            "status": "error",
            "error_message": f"Error fetching  data: {str(e)}",
        }


async def auto_save_session_to_memory_callback(callback_context):
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )


root_agent = Agent(
    name="retention_bot_agent",
    model=os.environ.get("GEMINI_MODEL_FLASH", "gemini-2.5-flash"),
    description="An agent that can look up the dataplex metadata and provide details on the bigquery datasets retention violations and perform archiving using the dataplex jobs",
    instruction=AGENT_INSTRUCTION,
    tools=[get_retention_datasets, archive_datasets, PreloadMemoryTool()],
    after_agent_callback=auto_save_session_to_memory_callback,
)


app = App(root_agent=root_agent, name="retention_bot_agent")
