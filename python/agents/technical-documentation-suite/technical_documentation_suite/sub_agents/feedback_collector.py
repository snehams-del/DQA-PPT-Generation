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

"""Feedback Collector agent for user feedback and continuous improvement"""

from google.adk.agents import Agent
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from technical_documentation_suite import prompt


class FeedbackResult(BaseModel):
    """Structured result from feedback collection"""
    
    user_satisfaction_score: Optional[float] = None
    feedback_categories: Dict[str, List[str]]
    
    positive_feedback: List[str]
    improvement_suggestions: List[str]
    pain_points: List[str]
    feature_requests: List[str]
    
    feedback_patterns: List[str]
    priority_improvements: List[str]
    
    user_engagement_metrics: Dict[str, Any]
    satisfaction_trends: List[str]
    
    actionable_insights: List[str]
    process_improvements: List[str]
    
    feedback_summary: str
    next_steps: List[str]


json_response_config = {
    "response_mime_type": "application/json",
    "response_schema": FeedbackResult.model_json_schema()
}


feedback_collector = Agent(
    model="gemini-2.5-flash",
    name="feedback_collector",
    description="Collects user feedback and identifies improvement opportunities",
    instruction=prompt.FEEDBACK_COLLECTOR_INSTR,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    output_schema=FeedbackResult,
    output_key="feedback",
    generate_content_config=json_response_config,
) 