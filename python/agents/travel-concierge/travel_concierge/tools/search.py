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

"""Wrapper to Google Search Grounding with custom prompt."""

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from google.adk.tools.google_search_tool import google_search

from pydantic import BaseModel
from serpapi import GoogleSearch
import asyncio
import logging
import os

# Initialize Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


SERP_API_KEY = os.getenv("SERP_API_KEY", "2401ef526cd713e2c5c72160b5d1026efd9f0eb18d561ab586c73dd1730e56a6")


_search_agent = Agent(
    model="gemini-2.5-flash",
    name="google_search_grounding",
    description="An agent providing Google-search grounding capability",
    instruction=""",
    Answer the user's question directly using google_search grounding tool; Provide a brief but concise response. 
    Rather than a detail response, provide the immediate actionable item for a tourist or traveler, in a single sentence.
    Do not ask the user to check or look up information for themselves, that's your role; do your best to be informative.
    """,
    tools=[google_search],
)

google_search_grounding = AgentTool(agent=_search_agent)



class FlightRequest(BaseModel):
    origin: str
    destination: str
    outbound_date: str

class FlightInfo(BaseModel):
    airline: str
    price: str
    duration: str
    stops: str
    departure: str
    arrival: str
    travel_class: str
    airline_logo: str

class FlightsSelection(BaseModel):
    """A list of flights from the search."""
    flights: list[FlightInfo]

# ==============================================
# 🛫 Fetch Data from SerpAPI
# ==============================================
async def run_search(params):
    """Generic function to run SerpAPI searches asynchronously."""
    try:
        return await asyncio.to_thread(lambda: GoogleSearch(params).get_dict())
    except Exception as e:
        logger.exception(f"SerpAPI search error: {str(e)}")
        # raise HTTPException(status_code=500, detail=f"Search API error: {str(e)}")

async def search_flights(flight_request: FlightRequest):
    """Fetch real-time flight details from Google Flights using SerpAPI."""
    logger.info(f"Searching flights: {flight_request.origin} to {flight_request.destination}")

    params = {
        "api_key": SERP_API_KEY,
        "engine": "google_flights",
        "type": 2,
        "stops": 1,
        "hl": "en",
        "gl": "us",
        "departure_id": flight_request.origin.strip().upper(),
        "arrival_id": flight_request.destination.strip().upper(),
        "outbound_date": flight_request.outbound_date,
        "currency": "USD"
    }
    logger.info(f"params:\n {params}")
    search_results = await run_search(params)
    # search_results = search.get_dict()
    # logger.info(search_results)
    if "error" in search_results:
        logger.error(f"Flight search error: {search_results['error']}")
        return {"error": search_results["error"]}

    if search_results and 'other_flights' in search_results:
        print(f"Found {len(search_results.get('other_flights', []))} flights")
        from pprint import pprint
        pprint(search_results.get('other_flights', []))
    best_flights = search_results.get("other_flights", [])

    formatted_flights = []
    for flight in best_flights:
        if not flight.get("flights") or len(flight["flights"]) == 0:
            continue

        first_leg = flight["flights"][0]
        formatted_flights.append(FlightInfo(
            airline=first_leg.get("airline", "Unknown Airline"),
            price=str(flight.get("price", "N/A")),
            duration=f"{flight.get('total_duration', 'N/A')} min",
            stops="Nonstop" if len(flight["flights"]) == 1 else f"{len(flight['flights']) - 1} stop(s)",
            departure=f"{first_leg.get('departure_airport', {}).get('name', 'Unknown')} ({first_leg.get('departure_airport', {}).get('id', '???')}) at {first_leg.get('departure_airport', {}).get('time', 'N/A')}",
            arrival=f"{first_leg.get('arrival_airport', {}).get('name', 'Unknown')} ({first_leg.get('arrival_airport', {}).get('id', '???')}) at {first_leg.get('arrival_airport', {}).get('time', 'N/A')}",
            travel_class=first_leg.get("travel_class", "Economy"),
            airline_logo=first_leg.get("airline_logo", "")
        ))

    logger.info(f"Found {len(formatted_flights)} flights")
    return formatted_flights
