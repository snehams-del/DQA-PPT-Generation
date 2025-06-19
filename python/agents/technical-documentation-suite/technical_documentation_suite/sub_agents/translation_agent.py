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

"""Translation agent for multi-language documentation support"""

from google.adk.agents import Agent
from pydantic import BaseModel
from typing import List, Dict, Any

from technical_documentation_suite import prompt


class TranslationResult(BaseModel):
    """Structured result from translation"""
    
    source_language: str
    target_languages: List[str]
    
    translated_content: Dict[str, str]  # language -> content
    translation_quality_scores: Dict[str, float]
    
    preserved_technical_terms: List[str]
    localization_notes: List[str]
    
    cultural_adaptations: List[str]
    regional_considerations: List[str]
    
    completeness_assessment: str
    recommendations: List[str]


json_response_config = {
    "response_mime_type": "application/json",
    "response_schema": TranslationResult.model_json_schema()
}


translation_agent = Agent(
    model="gemini-2.5-flash",
    name="translation_agent",
    description="Provides multi-language support for technical documentation",
    instruction=prompt.TRANSLATION_AGENT_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=TranslationResult,
    output_key="translation",
    generate_content_config=json_response_config,
) 