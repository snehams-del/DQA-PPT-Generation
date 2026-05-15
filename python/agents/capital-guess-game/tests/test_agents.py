import pytest
import dotenv
from capital_guess_game.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_root_agent_offers_game():
    """Test that the root agent offers the capital guess game."""
    runner = InMemoryRunner(agent=root_agent, app_name="capital-guess-game")
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )

    # First interaction, user sends a greeting
    content = types.Content(parts=[types.Part(text="Hi")])
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text
            break

    assert "guessing the capital" in response
