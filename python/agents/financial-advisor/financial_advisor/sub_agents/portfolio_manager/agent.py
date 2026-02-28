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

"""portfolio_manager_agent for getting the user's portfolio."""

import json
from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-pro"


def get_user_portfolio_positions() -> str:
    """Returns the user's current portfolio positions.

    Note: This is mock data for the current implementation.
    """
    mock_portfolio = {
        "positions": [
            {"ticker": "AAPL", "quantity": 150, "side": "LONG"},
            {"ticker": "GOOGL", "quantity": 60, "side": "LONG"},
            {"ticker": "MSFT", "quantity": 80, "side": "LONG"},
            {"ticker": "TSLA", "quantity": 25, "side": "LONG"},
        ]
    }
    return json.dumps(mock_portfolio)


portfolio_manager_agent = Agent(
    model=MODEL,
    name="portfolio_manager_agent",
    instruction=prompt.PORTFOLIO_MANAGER_PROMPT,
    output_key="portfolio_manager_output",
    tools=[get_user_portfolio_positions],
)
