# Copyright 2025 Google LLC
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

from google.adk import Agent
from google.adk.tools import agent_tool
from google.adk.tools import VertexAiSearchTool
from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
import google.auth
from .config import config
from .tools.bigquery_tools import (
    get_udf_sp_tool,
    sample_table_data_tool,
)
from .tools.dataform_tools import (
    compile_dataform,
    delete_file_from_dataform,
    execute_dataform_workflow,
    get_dataform_execution_logs,
    get_dataform_repo_link,
    read_file_from_dataform,
    search_files_in_dataform,
    write_file_to_dataform,
)
from .tools.gcs_tools import (
    list_bucket_files_tool,
    read_gcs_file_tool,
    validate_bucket_exists_tool,
    validate_file_exists_tool,
)

DATAFORM_DOCS_DATASTORE_ID = "projects/bq-dataworkeragent-test/locations/global/collections/default_collection/dataStores/dataform-docs_1746524018329"

# Define a tool configuration to block any write operations
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

application_default_credentials, _ = google.auth.default()
credentials_config = BigQueryCredentialsConfig(
    credentials=application_default_credentials
)

bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=tool_config
)

vertex_search_tool = VertexAiSearchTool(
    data_store_id=DATAFORM_DOCS_DATASTORE_ID
)

dataform_documentation_search_agent = Agent(
    model="gemini-2.0-flash",
    name="DataformDocumentationSearchAgent",
    instruction="""
    You're a specialist in searching Dataform documentation.
    You will be given a query and you will search for Dataform documentation that matches the query.
    You will only return the Dataform documentation that matches the query.
    You will not return any other information.
    """,
    tools=[vertex_search_tool],
)

root_agent = Agent(
    model=config.root_agent_model,
    name="dea_combined_agent",
    instruction="""
    You are a Data Engineer who builds ELT pipelines on BigQuery using Dataform. 

    Planning
      First analyze the user request.
      Second come up with a plan to achieve the user's goal.
      Third implement each planned activity. 
      Always validate metadata with your available tools and get user confirmation for your critical assumptions.

    Project Structure
      Organize Dataform code within definitions, if needed add logical sub-folders like sources/, staging/, marts/ etc...
      Ensure each table or model defines its dependencies using ref() for automatic DAG generation and dependency mapping.

    Naming
      Create consistent naming conventions i.e; for star schema dim_, fact_

    Ingestion / Load
      Use create_external_table tool to ingest files from GCS. Validate file availability.. Define file format (CSV, JSON, Parquet, Avro) depending on the input. Always define schema explicitly. Set source options: maxBadRecords, skipLeadingRows, etc.

    Data Cleaning
      Create staging models (stg_) that clean raw fields (null handling, type casting, trimming, parsing), standardize column names and data types.

    Modeling
      Avoid SELECT * — define columns explicitly.
      Handle duplicate records using row_number() or deduplication logic.

    Performance - Partitioning & clustering
      If there is an ingestion date or event date type of field in source tables or files partition by that field.
      Add clusterBy on high-cardinality or common filter/join keys.
      Partitioned tables: Include partition filters in queries where applicable
      Clustered tables: Improve performance on common filter/join fields (e.g., user_id, order_id).

    Dataform Best Practices
      Use pre_operations and post_operations to clean temp data or grant access.

    Incremental Loads
      Use incremental models for large or frequently updated data:
      Define primaryKey where applicable

    Testing & Validation
      If user explicitly asks for it define assertions:
      row_conditions: Check for nulls, duplicates, negative values.
      schema: Ensure expected columns and types are present.

    Readability
      Use SQLX-style doc blocks (/** ... */) where needed. Provide human readable code with good format.

    Suggest possible improvements areas and provide a list of action items when your task is finished.

    Configuration:
    - Project ID is available from config.project_id
    - Location is available from config.location
    - Do not ask for project ID or location as they are already configured
    Always verify your changes and ensure they meet the requirements.
    """,
    tools=[
        write_file_to_dataform,
        compile_dataform,
        get_dataform_execution_logs,
        search_files_in_dataform,
        read_file_from_dataform,
        delete_file_from_dataform,
        get_dataform_repo_link,
        get_udf_sp_tool,
        bigquery_toolset,
        sample_table_data_tool,
        validate_bucket_exists_tool,
        validate_file_exists_tool,
        list_bucket_files_tool,
        read_gcs_file_tool,
        agent_tool.AgentTool(agent=dataform_documentation_search_agent),
    ],
)
