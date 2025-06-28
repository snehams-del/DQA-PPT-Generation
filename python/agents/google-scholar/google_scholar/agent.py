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

"""Academic_Research: A multi-agent system for finding scholarly articles, news, 
and author information."""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools import agent_tool

from . import prompt
from .tools.find_papers import find_papers_tool
from .tools.find_news import find_news_tool
from .tools.find_author import find_author_tool
from .tools.find_author_details import find_author_details_tool
MODEL = "gemini-2.5-pro"


google_search_agent = LlmAgent(
    name="google_search_agent",
    model=MODEL,
    description=(
       """An agent that performs a general Google search when an author's 
       Google Scholar profile cannot be found."""
    ),
    instruction="You're a specialist in searching authors using Google Search",
    tools=[
        google_search
    ],
    )

root_agent = LlmAgent(
    name="root_agent",
    model=MODEL,
    description=(
       "A multi-purpose research assistant agent. It can find academic papers, news, "
        "general information, and author information."
    ),
    instruction=prompt.RESEARCH_AGENT_PROMPT,
    tools=[
        find_papers_tool,
        find_news_tool,
        find_author_tool,
        find_author_details_tool,
        agent_tool.AgentTool(agent=google_search_agent)
    ],
    )

agent = root_agent
