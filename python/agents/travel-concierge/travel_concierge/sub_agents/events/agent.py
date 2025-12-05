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

"""Events agent. Get's formatted events for given location and timerange."""


from google.adk.agents import Agent, LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from google.adk.tools import google_search
from travel_concierge.shared_libraries import types
from travel_concierge.sub_agents.events import prompt
from travel_concierge.tools.memory import memorize
from pydantic import BaseModel, Field
from typing import Optional



class EventsInput(BaseModel):
    destination: str = Field(description="Event location.")
    start_date: str = Field(description="Event start date in mm/dd/yy format.")
    end_date: str = Field(description="Event start date in mm/dd/yy format.")
    event: Optional[str] = Field(description="Event location.")
    category: Optional[str] = Field(description="Event category.")


class Event(BaseModel):
    name: str = Field(description="Event name.")
    description: str = Field(description="Event description.")
    start_date: str = Field(description="Event start date in mm/dd/yy format.")
    end_date: str = Field(description="Event start date in mm/dd/yy format.")
    location: str = Field(description="Event location.")
    url: str = Field(description="Event URL link. Include ticket links, info links etc.")
    category: str = Field(description="Event category.")

class EventsOutput(BaseModel):
    events : list[Event] = Field(description="List of events.")


google_events_data_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="google_events_data_agent",
    description="Answers user questions about the current events based on Google grounding.",
    instruction=prompt.EVENTS_AGENT_PROMPT,
    tools=[google_search],
    generate_content_config=GenerateContentConfig(
        temperature=0.1
    ),
    input_schema=EventsInput,
    output_key="DATA"
)

event_formatter_agent = LlmAgent(
    model="gemini-2.0-flash-001",
    name="event_formatter_agent",
    description="Answers user questions about the current events based on Google grounding.",
    instruction="""You are an agent that formats events data from DATA and returns output.
      """,
    output_schema=EventsOutput
)

events_agent = SequentialAgent(
    description="""Helps get events in structured format that can be used as an API.""",
    name="EventAgent",
    sub_agents=[google_events_data_agent, event_formatter_agent]
)