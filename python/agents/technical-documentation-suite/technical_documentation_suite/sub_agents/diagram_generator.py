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

"""Diagram Generator agent for visual architecture representations"""

from google.adk.agents import Agent
from pydantic import BaseModel
from typing import List, Dict, Any

from technical_documentation_suite import prompt


class DiagramResult(BaseModel):
    """Structured result from diagram generation"""
    
    architecture_diagram: str  # Mermaid format
    data_flow_diagram: str     # Mermaid format
    component_diagram: str     # Mermaid format
    api_flow_diagram: str      # Mermaid format
    
    diagram_descriptions: Dict[str, str]
    diagram_types_generated: List[str]
    
    mermaid_definitions: List[str]
    plantuml_definitions: List[str]
    ascii_diagrams: List[str]
    
    integration_points: List[str]
    visual_complexity_score: float
    
    recommendations: List[str]


json_response_config = {
    "response_mime_type": "application/json",
    "response_schema": DiagramResult.model_json_schema()
}


diagram_generator = Agent(
    model="gemini-2.5-flash",
    name="diagram_generator",
    description="Creates visual diagrams and architecture representations",
    instruction=prompt.DIAGRAM_GENERATOR_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=DiagramResult,
    output_key="diagrams",
    generate_content_config=json_response_config,
) 