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

"""Code Analyzer agent for repository structure analysis"""

from google.adk.agents import Agent
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from technical_documentation_suite import prompt


class CodeAnalysisResult(BaseModel):
    """Structured result from code analysis"""
    
    repository_url: Optional[str] = None
    primary_language: str
    languages_detected: List[str]
    framework_patterns: List[str]
    architecture_type: str
    
    file_structure: Dict[str, Any]
    total_files: int
    code_files: int
    
    classes_found: int
    functions_found: int
    api_endpoints: List[str]
    
    dependencies: List[str]
    external_integrations: List[str]
    
    documentation_coverage: str
    complexity_assessment: str
    
    key_components: List[str]
    missing_documentation: List[str]
    
    recommended_doc_types: List[str]
    estimated_scope: str


json_response_config = {
    "response_mime_type": "application/json",
    "response_schema": CodeAnalysisResult.model_json_schema()
}


code_analyzer = Agent(
    model="gemini-2.5-flash",
    name="code_analyzer",
    description="Analyzes code repositories to extract structure and documentation requirements",
    instruction=prompt.CODE_ANALYZER_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=CodeAnalysisResult,
    output_key="analysis",
    generate_content_config=json_response_config,
) 