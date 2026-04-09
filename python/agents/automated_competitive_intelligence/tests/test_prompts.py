# Copyright 2026 Google LLC
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

import pytest
from backend.prompt import COMPETITIVE_INTELLIGENCE_PROMPT
from backend.sub_agents.nl2sql.query_understanding_agent.prompt import QUERY_UNDERSTANDING_PROMPT_STR
from backend.sub_agents.nl2sql.query_generation_agent.prompt import QUERY_GENERATION_INSTRUCTION_STR
from backend.sub_agents.nl2sql.query_review_rewrite_agent.prompt import QUERY_REVIEW_REWRITE_INSTRUCTION_STR
from backend.sub_agents.nl2sql.query_execution_agent.prompt import QUERY_EXECUTION_INSTRUCTION_STR
from backend.sub_agents.competitve_search.extract_datasheet_url_agent.prompt import EXTRACT_DATASHEET_URLS_PROMPT
from backend.sub_agents.competitve_search.specs_extractor_agent.prompt import EXTRACT_PRODUCTS_SPECIFICATION_FROM_DATASHEET_PROMPT
from backend.sub_agents.competitve_search.web_search_agent.prompt import WEBSEARCH_PROMPT
from backend.sub_agents.competitve_search.summariser_agent.prompt import SUMMARIZE_COMPARATIVE_ANALYSIS

PROMPTS = [
    COMPETITIVE_INTELLIGENCE_PROMPT,
    QUERY_UNDERSTANDING_PROMPT_STR,
    QUERY_GENERATION_INSTRUCTION_STR,
    QUERY_REVIEW_REWRITE_INSTRUCTION_STR,
    QUERY_EXECUTION_INSTRUCTION_STR,
    EXTRACT_DATASHEET_URLS_PROMPT,
    EXTRACT_PRODUCTS_SPECIFICATION_FROM_DATASHEET_PROMPT,
    WEBSEARCH_PROMPT,
    SUMMARIZE_COMPARATIVE_ANALYSIS
]

DOMAIN_SPECIFIC_TERMS = [
    "mechanical"
]

def test_prompts_domain_agnostic():
    """Ensure prompts do not contain hardcoded domain-specific terminology."""
    for prompt in PROMPTS:
        # Ignore case for 'voltage' just in case, though Voltage with capital V is what was removed
        lower_prompt = prompt.lower()
        for term in DOMAIN_SPECIFIC_TERMS:
            assert term.lower() not in lower_prompt, f"Term '{term}' found in prompt: {prompt[:50]}..."

def test_query_understanding_formatting():
    """Test format injection for QUERY_UNDERSTANDING_PROMPT_STR."""
    formatted = QUERY_UNDERSTANDING_PROMPT_STR.format(bigquery_metadata="mock_metadata")
    assert "mock_metadata" in formatted

def test_query_generation_formatting():
    """Test format injection for QUERY_GENERATION_INSTRUCTION_STR."""
    formatted = QUERY_GENERATION_INSTRUCTION_STR.format(
        query_understanding_output="mock_under",
        PROJECT="mock_proj",
        BQ_LOCATION="mock_loc",
        DATASET="mock_data",
        bigquery_metadata="mock_metadata"
    )
    assert "mock_under" in formatted
    assert "mock_proj" in formatted

def test_query_review_formatting():
    """Test format injection for QUERY_REVIEW_REWRITE_INSTRUCTION_STR."""
    formatted = QUERY_REVIEW_REWRITE_INSTRUCTION_STR.format(
        query_understanding_output="mock_under",
        query_generation_output="mock_gen",
        PROJECT="mock_proj",
        BQ_LOCATION="mock_loc",
        DATASET="mock_data"
    )
    assert "mock_gen" in formatted

def test_query_execution_formatting():
    """Test format injection for QUERY_EXECUTION_INSTRUCTION_STR."""
    formatted = QUERY_EXECUTION_INSTRUCTION_STR.format(query_review_rewrite_output="mock_review")
    assert "mock_review" in formatted

def test_extract_url_formatting():
    """Test format injection for EXTRACT_DATASHEET_URLS_PROMPT."""
    formatted = EXTRACT_DATASHEET_URLS_PROMPT.format(query_execution_output="mock_exec")
    assert "mock_exec" in formatted

def test_specs_extractor_formatting():
    """Test format injection for EXTRACT_PRODUCTS_SPECIFICATION_FROM_DATASHEET_PROMPT."""
    formatted = EXTRACT_PRODUCTS_SPECIFICATION_FROM_DATASHEET_PROMPT.format(query_extract_datasheet_output="mock_url")
    assert "mock_url" in formatted

def test_web_search_formatting():
    """Test format injection for WEBSEARCH_PROMPT."""
    formatted = WEBSEARCH_PROMPT.format(query_specs_extracted_output="mock_specs")
    assert "mock_specs" in formatted

def test_summariser_formatting():
    """Test format injection for SUMMARIZE_COMPARATIVE_ANALYSIS."""
    formatted = SUMMARIZE_COMPARATIVE_ANALYSIS.format(query_competitor_specs_output="mock_comp")
    assert "mock_comp" in formatted
