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

"""price_agent for getting the user's portfolio."""

import json
import yfinance as yf
from google.adk import Agent

from . import prompt

MODEL = "gemini-2.5-pro"


def get_yahoo_finance_price(ticker: str) -> str:
    """Returns the current and recent historical stock price data for a given ticker.

    Args:
        ticker: The stock ticker symbol (e.g., AAPL, GOOGL).
    """
    try:
        stock = yf.Ticker(ticker)
        # Fetch the last 5 days of history to get current price and trend
        hist = stock.history(period="5d")
        
        if hist.empty:
             return json.dumps({"error": f"No price data found for ticker {ticker}. It might be invalid or delisted."})
            
        current_data = hist.iloc[-1]
        previous_data = hist.iloc[-2] if len(hist) > 1 else current_data
        five_days_ago = hist.iloc[0]

        price_data = {
            "ticker": ticker,
            "current_price": round(current_data["Close"], 2),
            "today_high": round(current_data["High"], 2),
            "today_low": round(current_data["Low"], 2),
            "previous_close": round(previous_data["Close"], 2),
            "recent_trend": {
                "start_price_5d": round(five_days_ago["Close"], 2),
                "end_price_5d": round(current_data["Close"], 2)
            }
        }
        return json.dumps(price_data)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch data for {ticker}: {str(e)}"})


price_agent = Agent(
    model=MODEL,
    name="price_agent",
    instruction=prompt.PRICE_AGENT_PROMPT,
    output_key="price_agent_output",
    tools=[get_yahoo_finance_price],
)
