import asyncio

from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

from blogger_agent import root_agent

app = App(name="blog_writer", root_agent=root_agent)


async def main() -> None:
    """Runs the agent with a sample query."""
    runner = InMemoryRunner(app=app)
    session = await runner.session_service.create_session(
        app_name=app.name, user_id="test_user", session_id="test_session"
    )

    queries = [
        "I want to write a blog post about the new features in the latest version of the ADK.",
        "looks good, write it",
        "1",
        "looks good, I approve",
        "yes",
        "my_new_blog_post.md",
    ]

    for query in queries:
        print(f">>> {query}")
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=UserContent(parts=[Part(text=query)]),
        ):
            if (
                event.is_final_response()
                and event.content
                and event.content.parts
            ):
                print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
