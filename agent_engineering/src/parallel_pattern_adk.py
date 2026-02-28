import asyncio
from google.adk.agents import ParallelAgent, Agent, SequentialAgent
from google.adk.sessions import Session
from dotenv import load_dotenv

load_dotenv()

async def main():
    # ---------------------------------------------------------
    # The Parallelization Pattern (Fan-out / Fan-in) in ADK
    # ---------------------------------------------------------

    # 1. FAN-OUT (Parallel Tasks)
    # These agents will run at the exact same time
    analyze_pros = Agent(
        name="ProsAnalyzer",
        model="gemini-2.5-flash",
        instruction="What are the main advantages of {topic}? List 3 points briefly.",
        output_key="pros_analysis" # Result gets saved to session.state['pros_analysis']
    )

    analyze_cons = Agent(
        name="ConsAnalyzer",
        model="gemini-2.5-flash",
        instruction="What are the main disadvantages of {topic}? List 3 points briefly.",
        output_key="cons_analysis" # Result gets saved to session.state['cons_analysis']
    )

    # Combine them into a ParallelAgent
    concurrent_exploration = ParallelAgent(
        name="ConcurrentExploration",
        sub_agents=[analyze_pros, analyze_cons]
    )

    # 2. FAN-IN (Aggregation Task)
    # This agent runs after the parallel step and uses the data saved in the session.state
    reviewer_agent = Agent(
        name="Reviewer",
        model="gemini-2.5-flash",
        instruction="""You are an objective reviewer. Based on the following pros and cons, write a short final verdict.
        
        PROS: {pros_analysis}
        
        CONS: {cons_analysis}
        
        Provide only the final verdict.
        """
    )
    # 3. Combine into the full pipeline
    parallel_pipeline = SequentialAgent(
        name="AnalysisPipeline",
        sub_agents=[
            concurrent_exploration, # Runs first (concurrently)
            reviewer_agent          # Runs second (aggregates)
        ]
    )

    # --- Run the Agent ---
    from google.adk.runners import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types

    # A Runner handles the execution of an agent within a session
    runner = Runner(
        app_name="parallel_app",
        agent=parallel_pipeline,
        session_service=InMemorySessionService(),
        auto_create_session=True
    )

    # We need to inject the topic into the state so the templates work.
    # We can do this using the state_delta in run_async.
    topic = "remote work"
    print(f"--- Starting Parallel Agent Pipeline for: {topic} ---")
    
    async for event in runner.run_async(
        user_id="user1", 
        session_id="session1",
        new_message=types.Content(parts=[types.Part(text="Please begin the analysis.")]),
        state_delta={"topic": topic}
    ):
        if event.author != "user" and event.content:
            text_parts = [p.text for p in event.content.parts if p.text]
            if text_parts:
                print(f"[{event.author}]:\n{''.join(text_parts)}\n")

if __name__ == "__main__":
    asyncio.run(main())
