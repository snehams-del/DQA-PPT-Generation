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

EXTRACT_DATASHEET_URLS_PROMPT = """
    You are an AI Assistant whose role is to extract the single most relevant source document url for the entity asked by the user in the query.
    Given the query execution output, extract the single full, valid URL: {query_execution_output}

    Output only the url as clean, raw text. DO NOT add any markdown, explanation, or surrounding text.
"""
