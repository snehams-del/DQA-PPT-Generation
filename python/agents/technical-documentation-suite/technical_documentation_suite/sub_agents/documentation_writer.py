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

"""Documentation Writer agent for comprehensive content creation"""

from google.adk.agents import Agent
from pydantic import BaseModel
from typing import List, Dict, Any

from technical_documentation_suite import prompt


class DocumentationResult(BaseModel):
    """Structured result from documentation generation"""
    
    documentation_type: str
    content_sections: Dict[str, str]
    
    readme_content: str
    api_documentation: str
    architecture_guide: str
    user_guide: str
    installation_guide: str
    
    code_examples: List[Dict[str, str]]
    usage_patterns: List[str]
    
    cross_references: List[str]
    external_links: List[str]
    
    content_quality_score: float
    completeness_assessment: str
    
    recommendations: List[str]


json_response_config = {
    "response_mime_type": "application/json",
    "response_schema": DocumentationResult.model_json_schema()
}


documentation_writer = Agent(
    model="gemini-2.5-flash",
    name="documentation_writer",
    description="Creates comprehensive technical documentation based on code analysis",
    instruction=prompt.DOCUMENTATION_WRITER_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=DocumentationResult,
    output_key="documentation",
    generate_content_config=json_response_config,
) 