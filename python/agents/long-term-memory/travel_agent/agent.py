import asyncio
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

import cognee
from cognee_integration_google_adk import add_tool, search_tool
from constant import MY_PREFERENCE, INSTRUCTIONS

from dotenv import load_dotenv
load_dotenv()

root_agent = Agent(
    model="gemini-2.5-flash",
    name="executive_assistant",
    description="You are a Personal Executive Assistant who remembers my preference to plan my itinerary accordingly",
    instruction=INSTRUCTIONS,
    tools=[add_tool, search_tool],
)

async def main():
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    
    runner = InMemoryRunner(agent=root_agent)
    events = await runner.run_debug(f"""Remember:
                                    {MY_PREFERENCE}
                                    """
    )
    
    for event in events:
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text)
    
    query = "plan 3 days Itinerary for Rome along with restaurants to try food."
    events = await runner.run_debug(
        query
    )
    
    for event in events:
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text)

if __name__ == "__main__":
    asyncio.run(main())