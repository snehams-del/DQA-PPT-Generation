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

# Imports
from google.adk.agents import SequentialAgent, LlmAgent
import logging
from .config import config
from .tools.initialize_state import initialize_state_var
from google.genai import types

# Prompt import
from .prompt import COMPETITIVE_INTELLIGENCE_PROMPT

# Sub agent imports
from .sub_agents.nl2sql.query_understanding_agent.agent import query_understanding_agent
from .sub_agents.nl2sql.query_generation_agent.agent import query_generation_agent
from .sub_agents.nl2sql.query_review_rewrite_agent.agent import (
    query_review_rewrite_agent,
)
from .sub_agents.nl2sql.query_execution_agent.agent import query_execution_agent
from .sub_agents.competitve_search.extract_datasheet_url_agent.agent import (
    extract_datasheet_url_agent,
)
from .sub_agents.competitve_search.specs_extractor_agent.agent import (
    specs_extractor_agent,
)
from .sub_agents.competitve_search.web_search_agent.agent import (
    websearch_agent,
)
from .sub_agents.competitve_search.summariser_agent.agent import (
    summarizer_agent,
)

"""Logging configuration"""
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


"""Agent Definition"""
logger.info("Starting with Agent initialisations.")

# This pipeline finds the datasheet URL. The user must check the output
# and then decide whether to run the next step.

nl2sql_pipeline = SequentialAgent(
    name="Step1_Find_Product_Details_or_Datasheet_URL",
    sub_agents=[
        query_understanding_agent,
        query_generation_agent,
        query_review_rewrite_agent,
        query_execution_agent,
    ],
    description="Runs the workflow to find a product details or datasheet URL of the product. The output of this pipeline should be used as input for the next step",
)

# This pipeline extracts specs from a URL. It assumes the output from the
# previous pipeline is provided as input.
extract_specs_pipeline = SequentialAgent(
    name="Step2_Extract_Specs_From_URL",
    sub_agents=[extract_datasheet_url_agent, 
                specs_extractor_agent],
    description="Extracts specifications from a given datasheet URL",
)

# final Agent call for summarization
web_search_pipeline = SequentialAgent(
    name="Step3_Web_Search_and_Summarize_Comparison",
    sub_agents=[websearch_agent, 
                summarizer_agent],
    description=" Perform google search to extract competitor product specifications after generating search query from the original product specifications & provides the summary of comparative analysis of original product with competitor product.",
)

# Optional logging.
logger.info("All pipelines defined.")

# Create the root_agent as a standalone Router
# or orchestrator
root_agent = LlmAgent(
    name="competitive_intelligence_router",
    model=config.pro_model,
    generate_content_config=types.GenerateContentConfig(
        temperature=config.temperature,
        top_p=config.top_p,
        seed=config.seed,
    ),
    instruction=COMPETITIVE_INTELLIGENCE_PROMPT,
    global_instruction="After every final response of each sub-agent, you MUST ask for user confirmation by explicitly suggesting the specific next step in the workflow (e.g., after finding the product URL in Step 1, explicitly ask if they want to extract details. After extracting details in Step 2, ask if they want to search for competitors). Do NOT passively wait for new tasks unless the entire 3-step workflow is complete.",
    sub_agents=[
        nl2sql_pipeline,
        extract_specs_pipeline,
        web_search_pipeline,
    ],
    description="Main router. Choose 'Step1_Find_Product_Details_or_Datasheet_URL' first, then 'Step2_Extract_Specs_From_URL' with the output from Step 1, and finally Step3_Web_Search_and_Summarize_Comparison from output of Step 2.",
    before_agent_callback=initialize_state_var,
)
