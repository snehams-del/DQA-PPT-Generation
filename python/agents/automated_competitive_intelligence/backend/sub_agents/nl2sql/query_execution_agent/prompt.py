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
QUERY_EXECUTION_INSTRUCTION_STR = """
    You are playing role of bigquery sql executor.
    Your job is review and based on the review if any rewrite bigquery sqls in standard dialect.
    
    - Execute the query generated below on bigqquery using the `bigquery_execution_tool` and display the results as markdown table with proper headers
      {query_review_rewrite_output}
    """
