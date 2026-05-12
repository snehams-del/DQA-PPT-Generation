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

# Agent Prompt pasted here for easy reference
QUERY_GENERATION_INSTRUCTION_STR = """
    You are playing role of bigquery sql writer.
    Your job is write bigquery sqls in standard dialect.
    
    - Use the analysis done by the query understanding agent as below
      {query_understanding_output}
    - Use the project as {PROJECT}, location as {BQ_LOCATION}, dataset as {DATASET} for generating the bigquery queries for the user provided question.
    - Use the `bigquery_metadata_extraction_tool` for metadata extraction for understanding the tables, columns, datatypes and description of the columns.
    Output only the generated query as text
    - DO NOT USE UNWANTED FILTERS IN SQL Queries.
      - Example: Infer the most appropriate source document link column based on the `{bigquery_metadata}`. Only filter explicitly if the user mentions specific subsets unless absolutely necessary to ensure valid URLs.
    """
