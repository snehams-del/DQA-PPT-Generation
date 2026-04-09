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

from google.adk.agents import LlmAgent
from .prompt import EXTRACT_PRODUCTS_SPECIFICATION_FROM_DATASHEET_PROMPT
from ....tools.document_downloader import download_and_upload_datasheets_tool
from ....config import config
from google.genai import types

specs_extractor_agent = LlmAgent(
    model=config.extractor_model,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
        max_output_tokens=config.max_output_tokens,
        seed=config.seed,
    ),
    name="specs_extractor_agent",
    description="Agent that first downloads a datasheet URL and uploads it to GCS, then extracts the product specification from the GCS document and presents the result as a markdwon table.",
    instruction=EXTRACT_PRODUCTS_SPECIFICATION_FROM_DATASHEET_PROMPT,
    tools=[download_and_upload_datasheets_tool],
    output_key="query_specs_extracted_output",
)
