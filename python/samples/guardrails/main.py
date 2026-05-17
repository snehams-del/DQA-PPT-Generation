import asyncio
from dotenv import load_dotenv
from google.genai import types

from google.adk.runners import InMemoryRunner
from agent import root_agent
from security_plugins import InputGuardrailPlugin, OutputFilterPlugin

async def main():
    """Main entry point to run the agent with layered security plugins."""
    load_dotenv()

    print("Starting agent security demo...")
    print("Type your query and press Enter. Type 'exit' to quit.")

    # Instantiate all security plugins
    input_guardrail = InputGuardrailPlugin()
    output_filter = OutputFilterPlugin()

    plugins = [
        input_guardrail, # This plugin contains both Layer 2 (Regex) and Layer 3 (LLM Judge)
        output_filter,   # This plugin is Layer 4
    ]

    runner = InMemoryRunner(
        agent=root_agent,
        app_name='layered_security_app',
        plugins=plugins,
    )

    session = await runner.session_service.create_session(
        user_id='cli_user',
        app_name='layered_security_app',
    )

    while True:
        try:
            prompt = input("You: ")
            if prompt.lower() == 'exit':
                break

            message = types.Content(
                role='user', parts=[types.Part.from_text(text=prompt)]
            )

            final_response = ""
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=message
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    final_response = event.content.parts[0].text

            print(f"Agent: {final_response.strip()}")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

if __name__ == "__main__":
    asyncio.run(main())