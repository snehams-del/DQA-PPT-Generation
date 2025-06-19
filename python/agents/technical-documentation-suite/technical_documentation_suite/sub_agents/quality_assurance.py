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

"""Quality Assurance agent for documentation review and validation"""

from google.adk.agents import Agent
from pydantic import BaseModel
from typing import List, Dict, Any

from technical_documentation_suite import prompt


class QualityAssessmentResult(BaseModel):
    """Structured result from quality assessment"""
    
    overall_quality_score: float
    content_accuracy_score: float
    completeness_score: float
    usability_score: float
    
    technical_accuracy_issues: List[str]
    missing_content_areas: List[str]
    formatting_issues: List[str]
    usability_concerns: List[str]
    
    code_example_validation: Dict[str, str]
    link_validation_results: List[str]
    
    improvement_recommendations: List[str]
    priority_fixes: List[str]
    
    approval_status: str  # "approved", "needs_revision", "rejected"
    quality_assessment_summary: str


json_response_config = {
    "response_mime_type": "application/json",
    "response_schema": QualityAssessmentResult.model_json_schema()
}


quality_assurance = Agent(
    model="gemini-2.5-flash",
    name="quality_assurance",
    description="Reviews and validates documentation for accuracy, completeness, and quality",
    instruction=prompt.QUALITY_ASSURANCE_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=QualityAssessmentResult,
    output_key="quality_assessment",
    generate_content_config=json_response_config,
) 